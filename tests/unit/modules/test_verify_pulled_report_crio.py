# Copyright: (c) 2025, Red Hat

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
from __future__ import absolute_import, division, print_function

import os
import tempfile

import yaml

from ansible_collections.cifmw.general.tests.unit.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleBaseTestCase,
    set_module_args,
)
from ansible_collections.cifmw.general.plugins.modules import (
    verify_pulled_report_crio,
)


class TestVerifyPulledReportCrio(ModuleBaseTestCase):
    def test_enriches_report_and_counts_cross_node(self):
        """
        GIVEN a pulled-images report with two digest entries across two nodes
              and CRI-O logs with "Trying to access" + "Pulled image" lines
        WHEN  the module processes the report against the logs
        THEN  it uses the "Trying to access" URI for origin verification,
              identifies trusted mirrors, and reports zero cross-node entries
        """
        _sha_a = "a" * 64
        _sha_b = "b" * 64
        report_data = {
            "summary": {
                "mirror_rules": [
                    {"mirror": "mirror.registry.example:5000/ns"},
                    {"mirror": "other.example/ns"},
                ]
            },
            "images": [
                {
                    "image_id": "quay.io/demo/app@sha256:" + _sha_a,
                    "node": "node-a",
                },
                {
                    "image_id": "quay.io/demo/other@sha256:" + _sha_b,
                    "node": "node-b",
                },
                {"image_id": "no-digest-here", "node": "node-a"},
            ],
        }

        with tempfile.TemporaryDirectory() as td:
            report_path = os.path.join(td, "pulled_images_report.yaml")
            output_path = os.path.join(td, "verified.yaml")
            log_a = os.path.join(td, "node-a.crio.log")
            log_b = os.path.join(td, "node-b.crio.log")

            with open(report_path, "w") as f:
                yaml.safe_dump(
                    report_data, f, default_flow_style=False, sort_keys=False
                )

            with open(log_a, "w") as f:
                f.write(
                    'level=info msg="Trying to access \\"'
                    "mirror.registry.example:5000/ns/app@sha256:" + _sha_a + '\\""\n'
                    'level=info msg="Pulled image: '
                    "quay.io/demo/app@sha256:" + _sha_a + '"\n'
                )

            with open(log_b, "w") as f:
                f.write(
                    'level=info msg="Pulled image: '
                    "quay.io/demo/other@sha256:" + _sha_b + '"\n'
                )

            set_module_args(
                dict(
                    report_path=report_path,
                    output_path=output_path,
                    log_paths=[log_a, log_b],
                )
            )

            with self.assertRaises(AnsibleExitJson) as rst:
                verify_pulled_report_crio.run_module()

            result = rst.exception.args[0]
            self.assertTrue(result["changed"])
            self.assertEqual(result["log_files"], 2)
            self.assertEqual(result["entries_with_digest"], 2)
            self.assertEqual(result["cross_node_entries"], 0)
            self.assertIn("node-a", result["nodes_with_evidence"])
            self.assertIn("node-b", result["nodes_with_evidence"])
            self.assertIn("mirror.registry.example:5000", result["trusted_mirrors"])

            with open(output_path, "r") as f:
                enriched = yaml.safe_load(f)

            img0 = enriched["images"][0]
            self.assertEqual(img0["log_evidence_node"], "node-a")
            self.assertEqual(
                img0["image_fetched_from"],
                "mirror.registry.example:5000/ns/app",
            )
            self.assertEqual(
                img0["image_canonical_name"],
                "quay.io/demo/app",
            )
            self.assertEqual(img0["node_verified_image_origin"], "mirror")
            self.assertEqual(
                img0["verification_reason"],
                "CRI-O contacted mirror and pull succeeded",
            )

            img1 = enriched["images"][1]
            self.assertEqual(img1["log_evidence_node"], "node-b")
            self.assertIsNone(img1["image_fetched_from"])
            self.assertEqual(img1["image_canonical_name"], "quay.io/demo/other")
            self.assertEqual(img1["node_verified_image_origin"], "source")
            self.assertEqual(
                img1["verification_reason"],
                "Pull confirmed, no Trying to access evidence"
                " (fallback to Pulled image)",
            )

    def test_cross_node_match_increments_counter(self):
        """
        GIVEN a pulled-images report listing an image on node-a
              and a CRI-O log that records the same digest on node-b
        WHEN  the module processes the report against the logs
        THEN  the cross_node_entries counter is incremented and the
              evidence node is set to the log's node (node-b)
        """
        _sha_c = "c" * 64
        report_data = {
            "summary": {"mirror_rules": [{"mirror": "mirror.example/ns"}]},
            "images": [
                {
                    "image_id": "quay.io/demo/app@sha256:" + _sha_c,
                    "node": "node-a",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as td:
            report_path = os.path.join(td, "pulled_images_report.yaml")
            output_path = os.path.join(td, "verified.yaml")
            log_b = os.path.join(td, "node-b.crio.log")

            with open(report_path, "w") as f:
                yaml.safe_dump(
                    report_data, f, default_flow_style=False, sort_keys=False
                )

            with open(log_b, "w") as f:
                f.write(
                    'level=info msg="Trying to access \\"'
                    "mirror.example/ns/app@sha256:" + _sha_c + '\\""\n'
                    'level=info msg="Pulled image: '
                    "quay.io/demo/app@sha256:" + _sha_c + '"\n'
                )

            set_module_args(
                dict(
                    report_path=report_path,
                    output_path=output_path,
                    log_paths=[log_b],
                )
            )

            with self.assertRaises(AnsibleExitJson) as rst:
                verify_pulled_report_crio.run_module()

            result = rst.exception.args[0]
            self.assertEqual(result["entries_with_digest"], 1)
            self.assertEqual(result["cross_node_entries"], 1)

            with open(output_path, "r") as f:
                enriched = yaml.safe_load(f)

            img0 = enriched["images"][0]
            self.assertEqual(img0["log_evidence_node"], "node-b")
            self.assertEqual(img0["node_verified_image_origin"], "mirror")

    def test_trying_to_access_overrides_pulled_image_for_origin(self):
        """
        GIVEN CRI-O logs where "Trying to access" shows a mirror URI but
              "Pulled image" shows the canonical source URI (normal CRI-O
              behaviour with ICSP/IDMS mirror rules)
        WHEN  the module processes the report
        THEN  node_verified_image_origin is "mirror" (from "Trying to access"),
              not "source" (which "Pulled image" alone would yield)
        """
        _sha = "d" * 64
        report_data = {
            "summary": {
                "mirror_rules": [
                    {
                        "source": "registry.redhat.io/rhoso-operators",
                        "mirror": (
                            "image-rbac-proxy.apps.example.com"
                            "/redhat-user-workloads/openstack-tenant"
                            "/openstack-18-0-21"
                        ),
                    }
                ]
            },
            "images": [
                {
                    "image_id": (
                        "registry.redhat.io/rhoso-operators"
                        "/swift-rhel9-operator@sha256:" + _sha
                    ),
                    "node": "master-1",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as td:
            report_path = os.path.join(td, "pulled_images_report.yaml")
            output_path = os.path.join(td, "verified.yaml")
            log_m1 = os.path.join(td, "master-1.crio.log")

            with open(report_path, "w") as f:
                yaml.safe_dump(
                    report_data, f, default_flow_style=False, sort_keys=False
                )

            with open(log_m1, "w") as f:
                f.write(
                    'level=info msg="Trying to access \\"'
                    "image-rbac-proxy.apps.example.com"
                    "/redhat-user-workloads/openstack-tenant"
                    "/openstack-18-0-21"
                    "/swift-operator@sha256:" + _sha + '\\""\n'
                    'level=info msg="Pulled image: '
                    "registry.redhat.io/rhoso-operators"
                    "/swift-rhel9-operator@sha256:" + _sha + '"\n'
                )

            set_module_args(
                dict(
                    report_path=report_path,
                    output_path=output_path,
                    log_paths=[log_m1],
                )
            )

            with self.assertRaises(AnsibleExitJson) as rst:
                verify_pulled_report_crio.run_module()

            result = rst.exception.args[0]
            self.assertEqual(result["entries_with_digest"], 1)
            self.assertEqual(result["cross_node_entries"], 0)
            self.assertIn(
                "image-rbac-proxy.apps.example.com", result["trusted_mirrors"]
            )

            with open(output_path, "r") as f:
                enriched = yaml.safe_load(f)

            img0 = enriched["images"][0]
            self.assertEqual(img0["node_verified_image_origin"], "mirror")
            self.assertEqual(
                img0["image_fetched_from"],
                "image-rbac-proxy.apps.example.com"
                "/redhat-user-workloads/openstack-tenant"
                "/openstack-18-0-21"
                "/swift-operator",
            )
            self.assertEqual(
                img0["image_canonical_name"],
                "registry.redhat.io/rhoso-operators/swift-rhel9-operator",
            )
            self.assertEqual(img0["log_evidence_node"], "master-1")
            self.assertEqual(
                img0["verification_reason"],
                "CRI-O contacted mirror and pull succeeded",
            )

    def test_fallback_to_pulled_image_when_no_trying_lines(self):
        """
        GIVEN CRI-O logs with only "Pulled image" lines (no "Trying to access")
        WHEN  the module processes the report
        THEN  it falls back to using the "Pulled image" URI for origin and
              sets log_evidence_tried_uri to None
        """
        _sha = "e" * 64
        report_data = {
            "summary": {"mirror_rules": [{"mirror": "mirror.example/ns"}]},
            "images": [
                {
                    "image_id": "quay.io/demo/app@sha256:" + _sha,
                    "node": "node-a",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as td:
            report_path = os.path.join(td, "pulled_images_report.yaml")
            output_path = os.path.join(td, "verified.yaml")
            log_a = os.path.join(td, "node-a.crio.log")

            with open(report_path, "w") as f:
                yaml.safe_dump(
                    report_data, f, default_flow_style=False, sort_keys=False
                )

            with open(log_a, "w") as f:
                f.write(
                    'level=info msg="Pulled image: '
                    "quay.io/demo/app@sha256:" + _sha + '"\n'
                )

            set_module_args(
                dict(
                    report_path=report_path,
                    output_path=output_path,
                    log_paths=[log_a],
                )
            )

            with self.assertRaises(AnsibleExitJson) as rst:
                verify_pulled_report_crio.run_module()

            with open(output_path, "r") as f:
                enriched = yaml.safe_load(f)

            img0 = enriched["images"][0]
            self.assertEqual(img0["node_verified_image_origin"], "source")
            self.assertIsNone(img0["image_fetched_from"])
            self.assertEqual(img0["image_canonical_name"], "quay.io/demo/app")
            self.assertEqual(img0["log_evidence_node"], "node-a")
            self.assertEqual(
                img0["verification_reason"],
                "Pull confirmed, no Trying to access evidence"
                " (fallback to Pulled image)",
            )

    def test_mirror_unavailable_fallback_to_source(self):
        """
        GIVEN CRI-O logs where "Trying to access" shows the source registry
              (not a mirror) because the mirror was unavailable and CRI-O
              fell back to contacting the source directly
        WHEN  the module processes the report
        THEN  node_verified_image_origin is "source" (the tried URI domain
              is not in trusted_mirrors)
        """
        _sha = "ab" * 32
        report_data = {
            "summary": {"mirror_rules": [{"mirror": "mirror.unavailable.example/ns"}]},
            "images": [
                {
                    "image_id": "registry.redhat.io/rhoso/app@sha256:" + _sha,
                    "node": "node-a",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as td:
            report_path = os.path.join(td, "pulled_images_report.yaml")
            output_path = os.path.join(td, "verified.yaml")
            log_a = os.path.join(td, "node-a.crio.log")

            with open(report_path, "w") as f:
                yaml.safe_dump(
                    report_data, f, default_flow_style=False, sort_keys=False
                )

            with open(log_a, "w") as f:
                f.write(
                    'level=info msg="Trying to access \\"'
                    "registry.redhat.io/rhoso/app@sha256:" + _sha + '\\""\n'
                    'level=info msg="Pulled image: '
                    "registry.redhat.io/rhoso/app@sha256:" + _sha + '"\n'
                )

            set_module_args(
                dict(
                    report_path=report_path,
                    output_path=output_path,
                    log_paths=[log_a],
                )
            )

            with self.assertRaises(AnsibleExitJson) as rst:
                verify_pulled_report_crio.run_module()

            result = rst.exception.args[0]
            self.assertEqual(result["entries_with_digest"], 1)
            self.assertEqual(result["cross_node_entries"], 0)

            with open(output_path, "r") as f:
                enriched = yaml.safe_load(f)

            img0 = enriched["images"][0]
            self.assertEqual(img0["node_verified_image_origin"], "source")
            self.assertEqual(
                img0["image_fetched_from"],
                "registry.redhat.io/rhoso/app",
            )
            self.assertEqual(
                img0["image_canonical_name"],
                "registry.redhat.io/rhoso/app",
            )
            self.assertEqual(img0["log_evidence_node"], "node-a")
            self.assertEqual(
                img0["verification_reason"],
                "CRI-O contacted source and pull succeeded",
            )

    def test_pull_failed_when_trying_without_pulled(self):
        """
        GIVEN CRI-O logs with multiple "Trying to access" lines for a digest
              but no "Pulled image" line (all pull attempts failed)
        WHEN  the module processes the report
        THEN  node_verified_image_origin is "pull_failed" and
              image_fetched_from is None
        """
        _sha = "f" * 64
        report_data = {
            "summary": {
                "mirror_rules": [
                    {
                        "source": "registry.redhat.io/rhoso",
                        "mirror": (
                            "image-rbac-proxy.apps.example.com"
                            "/redhat-user-workloads/openstack-tenant"
                            "/openstack-18-0-21"
                        ),
                    }
                ]
            },
            "images": [
                {
                    "image_id": (
                        "registry.redhat.io/rhoso"
                        "/openstack-rsyslog-rhel9@sha256:" + _sha
                    ),
                    "node": "master-0",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as td:
            report_path = os.path.join(td, "pulled_images_report.yaml")
            output_path = os.path.join(td, "verified.yaml")
            log_m0 = os.path.join(td, "master-0.crio.log")

            with open(report_path, "w") as f:
                yaml.safe_dump(
                    report_data, f, default_flow_style=False, sort_keys=False
                )

            with open(log_m0, "w") as f:
                for _attempt in range(4):
                    f.write(
                        'level=info msg="Trying to access \\"'
                        "image-rbac-proxy.apps.example.com"
                        "/redhat-user-workloads/openstack-tenant"
                        "/openstack-18-0-21"
                        "/openstack-rsyslog@sha256:" + _sha + '\\""\n'
                        'level=info msg="Trying to access \\"'
                        "registry.redhat.io/rhoso"
                        "/openstack-rsyslog-rhel9@sha256:" + _sha + '\\""\n'
                    )

            set_module_args(
                dict(
                    report_path=report_path,
                    output_path=output_path,
                    log_paths=[log_m0],
                )
            )

            with self.assertRaises(AnsibleExitJson) as rst:
                verify_pulled_report_crio.run_module()

            with open(output_path, "r") as f:
                enriched = yaml.safe_load(f)

            img0 = enriched["images"][0]
            self.assertEqual(img0["node_verified_image_origin"], "pull_failed")
            self.assertEqual(
                img0["verification_reason"],
                "CRI-O tried registries but pull never succeeded",
            )
            self.assertIsNone(img0["image_fetched_from"])
            self.assertIsNone(img0["image_canonical_name"])
            self.assertEqual(img0["log_evidence_node"], "master-0")

    def test_fails_when_no_log_files(self):
        """
        GIVEN an empty list of CRI-O log paths
        WHEN  the module is invoked
        THEN  it fails with an error indicating no log files were provided
        """
        set_module_args(
            dict(
                report_path="/tmp/in.yaml",
                output_path="/tmp/out.yaml",
                log_paths=[],
            )
        )

        with self.assertRaises(AnsibleFailJson) as rst:
            verify_pulled_report_crio.run_module()

        self.assertIn("No CRI-O log files", rst.exception.args[0]["msg"])

    def test_fails_when_log_file_unreadable(self):
        """
        GIVEN a log_paths entry that points to a non-existent file
        WHEN  the module tries to open it
        THEN  it fails with an error mentioning the file path
        """
        with tempfile.TemporaryDirectory() as td:
            report_path = os.path.join(td, "report.yaml")
            with open(report_path, "w") as f:
                yaml.safe_dump(
                    {"summary": {}, "images": []},
                    f,
                    default_flow_style=False,
                )

            missing_log = os.path.join(td, "ghost.crio.log")
            set_module_args(
                dict(
                    report_path=report_path,
                    output_path=os.path.join(td, "out.yaml"),
                    log_paths=[missing_log],
                )
            )

            with self.assertRaises(AnsibleFailJson) as rst:
                verify_pulled_report_crio.run_module()

            self.assertIn("Cannot read CRI-O log file", rst.exception.args[0]["msg"])
            self.assertIn("ghost.crio.log", rst.exception.args[0]["msg"])

    def test_fails_when_report_unreadable(self):
        """
        GIVEN a report_path that does not exist on disk
        WHEN  the module tries to open it
        THEN  it fails with an error mentioning the report path
        """
        with tempfile.TemporaryDirectory() as td:
            log_path = os.path.join(td, "node-a.crio.log")
            with open(log_path, "w") as f:
                f.write("")

            set_module_args(
                dict(
                    report_path=os.path.join(td, "no_such_report.yaml"),
                    output_path=os.path.join(td, "out.yaml"),
                    log_paths=[log_path],
                )
            )

            with self.assertRaises(AnsibleFailJson) as rst:
                verify_pulled_report_crio.run_module()

            self.assertIn("Cannot read report", rst.exception.args[0]["msg"])

    def test_fails_when_report_has_invalid_yaml(self):
        """
        GIVEN a report file whose contents are not valid YAML
        WHEN  the module tries to parse it
        THEN  it fails with an error about invalid YAML
        """
        with tempfile.TemporaryDirectory() as td:
            report_path = os.path.join(td, "bad.yaml")
            with open(report_path, "w") as f:
                f.write("{{: not: valid: yaml: [}")

            log_path = os.path.join(td, "node-a.crio.log")
            with open(log_path, "w") as f:
                f.write("")

            set_module_args(
                dict(
                    report_path=report_path,
                    output_path=os.path.join(td, "out.yaml"),
                    log_paths=[log_path],
                )
            )

            with self.assertRaises(AnsibleFailJson) as rst:
                verify_pulled_report_crio.run_module()

            self.assertIn("Invalid YAML in report", rst.exception.args[0]["msg"])

    def test_fails_when_report_root_is_not_a_dict(self):
        """
        GIVEN a report file whose YAML root is a list instead of a mapping
        WHEN  the module checks the structure
        THEN  it fails with an error about the root type
        """
        with tempfile.TemporaryDirectory() as td:
            report_path = os.path.join(td, "list.yaml")
            with open(report_path, "w") as f:
                yaml.safe_dump(
                    ["item1", "item2"],
                    f,
                    default_flow_style=False,
                )

            log_path = os.path.join(td, "node-a.crio.log")
            with open(log_path, "w") as f:
                f.write("")

            set_module_args(
                dict(
                    report_path=report_path,
                    output_path=os.path.join(td, "out.yaml"),
                    log_paths=[log_path],
                )
            )

            with self.assertRaises(AnsibleFailJson) as rst:
                verify_pulled_report_crio.run_module()

            self.assertIn("Report root must be a mapping", rst.exception.args[0]["msg"])
