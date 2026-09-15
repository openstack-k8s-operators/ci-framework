# Copyright: (c) 2026, Red Hat

# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

import os
import tempfile
import unittest.mock  # noqa: F401 - required so unittest.mock is loaded for utils.py

import yaml

from ansible_collections.cifmw.general.plugins.modules import (
    generate_cluster_image_policies,
)
from ansible_collections.cifmw.general.tests.unit.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleBaseTestCase,
    set_module_args,
)


class TestGenerateClusterImagePolicies(ModuleBaseTestCase):
    """Unit tests for the generate_cluster_image_policies module."""

    def _write_documents(self, path, documents):
        with open(path, "w", encoding="utf-8") as stream:
            yaml.safe_dump_all(documents, stream, sort_keys=False)

    def _read_documents(self, path):
        with open(path, "r", encoding="utf-8") as stream:
            return list(yaml.safe_load_all(stream))

    def test_generates_policies_from_digest_and_tag_mirrors(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = os.path.join(temp_dir, "cluster-resources")
            os.mkdir(input_dir)
            input_file = os.path.join(input_dir, "mirror-oc-mirror.yaml")
            output_file = os.path.join(temp_dir, "ClusterImagePolicies.yaml")

            self._write_documents(
                input_file,
                [
                    {
                        "apiVersion": "config.openshift.io/v1",
                        "kind": "ImageDigestMirrorSet",
                        "spec": {
                            "imageDigestMirrors": [
                                {
                                    "source": "registry.redhat.io/example/foo",
                                    "mirrors": [
                                        "mirror.example/foo",
                                        "mirror.example/foo",
                                    ],
                                },
                                {
                                    "source": "registry.redhat.io/example/bar",
                                    "mirrors": ["mirror.example/bar"],
                                },
                            ]
                        },
                    },
                    {
                        "apiVersion": "config.openshift.io/v1",
                        "kind": "ImageTagMirrorSet",
                        "spec": {
                            "imageTagMirrors": [
                                {
                                    "source": "registry.redhat.io/example/ubi",
                                    "mirrors": ["mirror.example/ubi"],
                                }
                            ]
                        },
                    },
                ],
            )

            set_module_args({"input_dir": input_dir, "output_file": output_file})
            with self.assertRaises(AnsibleExitJson) as context:
                generate_cluster_image_policies.main()

            result = context.exception.args[0]
            self.assertTrue(result["success"])
            self.assertTrue(result["changed"])

            policies = self._read_documents(output_file)
            self.assertEqual(len(policies), 3)

            policies_by_scope = {
                policy["spec"]["scopes"][0]: policy for policy in policies
            }
            self.assertEqual(
                set(policies_by_scope),
                {
                    "mirror.example/foo",
                    "mirror.example/bar",
                    "mirror.example/ubi",
                },
            )

            policy = policies_by_scope["mirror.example/foo"]
            self.assertEqual(policy["apiVersion"], "config.openshift.io/v1")
            self.assertEqual(policy["kind"], "ClusterImagePolicy")
            self.assertEqual(policy["spec"]["policy"]["type"], "sigstore")
            self.assertEqual(
                policy["spec"]["policy"]["rootOfTrust"]["policyType"],
                "PublicKey",
            )
            self.assertEqual(
                policy["spec"]["policy"]["rootOfTrust"]["publicKey"]["keyData"],
                generate_cluster_image_policies.SIGSTORE_KEY,
            )
            self.assertEqual(
                policy["spec"]["policy"]["signedIdentity"],
                {
                    "type": "RemapIdentity",
                    "matchPolicy": "RemapIdentity",
                    "remapIdentity": {
                        "prefix": "mirror.example/foo",
                        "signedPrefix": "registry.redhat.io/example/foo",
                    },
                },
            )

    def test_missing_input_directory_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = os.path.join(temp_dir, "does-not-exist")
            output_file = os.path.join(temp_dir, "ClusterImagePolicies.yaml")

            set_module_args({"input_dir": input_dir, "output_file": output_file})
            with self.assertRaises(AnsibleFailJson) as context:
                generate_cluster_image_policies.main()

            result = context.exception.args[0]
            self.assertTrue(result["failed"])
            self.assertIn(input_dir, result["msg"])

    def test_no_mirror_entries_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = os.path.join(temp_dir, "cluster-resources")
            os.mkdir(input_dir)
            input_file = os.path.join(input_dir, "empty-oc-mirror.yaml")
            output_file = os.path.join(temp_dir, "ClusterImagePolicies.yaml")
            self._write_documents(
                input_file,
                [
                    {
                        "apiVersion": "config.openshift.io/v1",
                        "kind": "ImageDigestMirrorSet",
                        "spec": {},
                    }
                ],
            )

            set_module_args({"input_dir": input_dir, "output_file": output_file})
            with self.assertRaises(AnsibleFailJson) as context:
                generate_cluster_image_policies.main()

            result = context.exception.args[0]
            self.assertTrue(result["failed"])
            self.assertIn("No cluster image policies were created", result["msg"])
            self.assertFalse(os.path.exists(output_file))
