#!/usr/bin/env python3
"""Package tracked working files from the Zuul checkout for an AnsibleTest Pod."""

import base64
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile


def package(source, bootstrap, destination):
    source = Path(source).resolve()
    destination = Path(destination)

    def git(*args):
        return subprocess.check_output(["git", "-C", str(source), *args])

    revision = git("rev-parse", "HEAD").decode().strip()
    files = sorted(set(git("ls-files", "-z").decode().rstrip("\0").split("\0")))
    for required in (
        "playbooks/run_lightspeed_tests.yaml",
        "pyproject.toml",
        "uv.lock",
    ):
        if required not in files or not (source / required).is_file():
            raise ValueError(f"Missing tracked test input: {required}")
    stream = io.BytesIO()
    with gzip.GzipFile(fileobj=stream, mode="wb", mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode="w") as archive:
            for name in files:
                path = source / name
                if not path.is_file() or path.is_symlink():
                    raise ValueError(f"Expected a regular tracked file: {name}")
                info = archive.gettarinfo(str(path), arcname=name)
                info.uid = info.gid = info.mtime = 0
                info.uname = info.gname = ""
                with path.open("rb") as content:
                    archive.addfile(info, content)
    data = stream.getvalue()
    bootstrap_text = Path(bootstrap).read_text()
    # Leave room for metadata and the bootstrap within Kubernetes' 1 MiB limit.
    if len(data) + len(bootstrap_text.encode()) > 900 * 1024:
        raise ValueError("Lightspeed source exceeds the ConfigMap size budget")
    checksum = hashlib.sha256(data).hexdigest()
    metadata = {
        "revision": revision,
        "tracked_changes": git(
            "status", "--porcelain", "--untracked-files=no"
        ).decode(),
        "sha256": checksum,
    }
    config = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "immutable": True,
        "data": {
            "run.yml": bootstrap_text,
            "source-revision.json": json.dumps(metadata, indent=2) + "\n",
        },
        "binaryData": {"source.tar.gz": base64.b64encode(data).decode()},
    }
    identity = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    config["metadata"] = {"name": "lightspeed-tests-source-" + identity[:16]}
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "source.tar.gz").write_bytes(data)
    (destination / "source-revision.json").write_text(
        json.dumps(metadata, indent=2) + "\n"
    )
    (destination / "configmap.json").write_text(json.dumps(config, indent=2) + "\n")


if __name__ == "__main__":
    package(*sys.argv[1:])
