"""Source transport contracts; no network or Kubernetes access required."""

import base64
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest

SCRIPT = (
    Path(__file__).resolve().parents[3] / "hooks/playbooks/files/lightspeed-source.py"
)
spec = importlib.util.spec_from_file_location("lightspeed_source", SCRIPT)
source_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source_module)


class TestSourceArchive(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        for name in [
            "playbooks/run_lightspeed_tests.yaml",
            "pyproject.toml",
            "uv.lock",
        ]:
            path = self.repo / name
            path.parent.mkdir(exist_ok=True)
            path.write_text("initial\n")
        self.git("add", ".")
        self.git(
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-qm",
            "Fixture baseline",
        )
        self.bootstrap = self.root / "run.yml"
        self.bootstrap.write_text("---\n[]\n")
        self.output = self.root / "output"

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args])

    def package(self):
        source_module.package(self.repo, self.bootstrap, self.output)
        return json.loads((self.output / "configmap.json").read_text())

    def test_working_edits_and_indexed_additions_are_used(self):
        (self.repo / "uv.lock").write_text("tracked local edit\n")
        (self.repo / "added.py").write_text("new source\n")
        self.git("add", "added.py")
        (self.repo / "untracked-token").write_text("never archive this")
        config = self.package()
        archive_data = base64.b64decode(config["binaryData"]["source.tar.gz"])
        with tarfile.open(fileobj=io.BytesIO(archive_data), mode="r:gz") as archive:
            self.assertEqual(
                archive.extractfile("uv.lock").read(), b"tracked local edit\n"
            )
            self.assertIn("added.py", archive.getnames())
            self.assertNotIn("untracked-token", archive.getnames())
        metadata = json.loads(config["data"]["source-revision.json"])
        self.assertEqual(metadata["sha256"], hashlib.sha256(archive_data).hexdigest())
        self.assertEqual(
            metadata["revision"], self.git("rev-parse", "HEAD").decode().strip()
        )
        self.assertIn("uv.lock", metadata["tracked_changes"])

    def test_identical_inputs_produce_identical_configmap(self):
        before = self.package()
        os.utime(self.repo / "uv.lock", (100, 100))
        self.assertEqual(before, self.package())
        self.bootstrap.write_text("---\n- name: Updated bootstrap\n")
        self.assertNotEqual(
            before["metadata"]["name"], self.package()["metadata"]["name"]
        )

    def test_missing_required_input_is_rejected(self):
        (self.repo / "uv.lock").unlink()
        with self.assertRaisesRegex(ValueError, "Missing tracked test input"):
            self.package()

    def test_symlink_is_not_followed_into_private_files(self):
        (self.repo / "linked").symlink_to(self.bootstrap)
        self.git("add", "linked")
        with self.assertRaisesRegex(ValueError, "regular tracked file"):
            self.package()

    def test_oversize_configmap_is_rejected(self):
        (self.repo / "large").write_bytes(os.urandom(1024 * 1024))
        self.git("add", "large")
        with self.assertRaisesRegex(ValueError, "size budget"):
            self.package()


if __name__ == "__main__":
    unittest.main()
