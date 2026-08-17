import base64
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "roles/kustomize_deploy/files/osp_secret_manifest.py"


def load_module():
    spec = importlib.util.spec_from_file_location("osp_secret_manifest", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_manifest(path, docs):
    with open(path, "w") as handle:
        yaml.dump_all(docs, handle, default_flow_style=False)


@pytest.fixture
def osp_secret_module():
    return load_module()


@pytest.fixture
def manifest_path(tmp_path):
    return tmp_path / "control-plane.yaml"


class TestOspSecretManifestHelpers:
    def test_find_osp_secret_returns_matching_secret(self, osp_secret_module):
        docs = [
            {"kind": "Secret", "metadata": {"name": "other-secret"}},
            {
                "kind": "Secret",
                "metadata": {"name": "osp-secret", "namespace": "openstack2"},
            },
        ]
        secret = osp_secret_module.find_osp_secret(docs)
        assert secret["metadata"]["namespace"] == "openstack2"

    def test_get_secret_namespace(self, osp_secret_module):
        docs = [
            {
                "kind": "Secret",
                "metadata": {"name": "osp-secret", "namespace": "openstack2"},
            }
        ]
        assert osp_secret_module.get_secret_namespace(docs) == "openstack2"

    def test_get_secret_namespace_missing(self, osp_secret_module):
        docs = [{"kind": "Secret", "metadata": {"name": "osp-secret"}}]
        assert osp_secret_module.get_secret_namespace(docs) is None

    def test_get_secret_key_roundtrip(self, osp_secret_module):
        value = "sEFmdFjDUqRM2VemYslV5yGNWjokioJXsg8Nrlc3drU="
        docs = [
            {
                "kind": "Secret",
                "metadata": {"name": "osp-secret"},
                "data": {
                    "BarbicanSimpleCryptoKEK": base64.b64encode(value.encode()).decode()
                },
            }
        ]
        assert (
            osp_secret_module.get_secret_key(docs, "BarbicanSimpleCryptoKEK") == value
        )

    def test_apply_secret_keys_sets_missing_key(self, osp_secret_module, manifest_path):
        docs = [{"kind": "Secret", "metadata": {"name": "osp-secret"}, "data": {}}]
        write_manifest(manifest_path, docs)
        loaded = osp_secret_module.load_docs(manifest_path)
        changed, changed_keys = osp_secret_module.apply_secret_keys(
            loaded,
            {"BarbicanSimpleCryptoKEK": "generated-kek-value"},
        )
        assert changed is True
        assert changed_keys == ["BarbicanSimpleCryptoKEK"]
        assert (
            osp_secret_module.get_secret_key(loaded, "BarbicanSimpleCryptoKEK")
            == "generated-kek-value"
        )

    def test_apply_secret_keys_skips_identical_value(self, osp_secret_module):
        value = "same-kek-value"
        encoded = base64.b64encode(value.encode()).decode()
        docs = [
            {
                "kind": "Secret",
                "metadata": {"name": "osp-secret"},
                "data": {"BarbicanSimpleCryptoKEK": encoded},
            }
        ]
        changed, changed_keys = osp_secret_module.apply_secret_keys(
            docs,
            {"BarbicanSimpleCryptoKEK": value},
        )
        assert changed is False
        assert changed_keys == []


class TestOspSecretManifestCli:
    def test_has_exits_zero_when_secret_present(self, manifest_path):
        write_manifest(
            manifest_path,
            [{"kind": "Secret", "metadata": {"name": "osp-secret"}}],
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "has", str(manifest_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0

    def test_has_exits_nonzero_when_secret_missing(self, manifest_path):
        write_manifest(
            manifest_path,
            [{"kind": "Secret", "metadata": {"name": "other-secret"}}],
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "has", str(manifest_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 1

    def test_get_namespace_returns_manifest_namespace(self, manifest_path):
        write_manifest(
            manifest_path,
            [
                {
                    "kind": "Secret",
                    "metadata": {"name": "osp-secret", "namespace": "openstack2"},
                }
            ],
        )
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "get-namespace",
                str(manifest_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        assert result.stdout == "openstack2"

    def test_set_only_reports_changed_keys(
        self, manifest_path, osp_secret_module, tmp_path
    ):
        value = "existing-kek"
        encoded = base64.b64encode(value.encode()).decode()
        write_manifest(
            manifest_path,
            [
                {
                    "kind": "Secret",
                    "metadata": {"name": "osp-secret"},
                    "data": {"BarbicanSimpleCryptoKEK": encoded},
                }
            ],
        )
        keys_file = tmp_path / "keys.json"
        keys_file.write_text(json.dumps({"BarbicanSimpleCryptoKEK": value}))
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "set",
                str(manifest_path),
                str(keys_file),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        assert result.stdout == ""

        new_value = "new-kek-value"
        keys_file.write_text(json.dumps({"BarbicanSimpleCryptoKEK": new_value}))
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "set",
                str(manifest_path),
                str(keys_file),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        assert "Set: BarbicanSimpleCryptoKEK" in result.stdout
        loaded = osp_secret_module.load_docs(manifest_path)
        assert (
            osp_secret_module.get_secret_key(loaded, "BarbicanSimpleCryptoKEK")
            == new_value
        )
