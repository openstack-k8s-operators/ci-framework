"""Render stage settings without connecting to a Kubernetes cluster."""

from copy import deepcopy
from pathlib import Path
import unittest

from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar
import yaml

ROLE = Path(__file__).resolve().parents[3] / "roles/test_operator"


class TestStageSettings(unittest.TestCase):
    def setUp(self):
        self.defaults = yaml.safe_load((ROLE / "defaults/main.yml").read_text())

    def render(self, variable, overrides=None, **extra):
        stage = {
            key: deepcopy(self.defaults[key])
            for key in (
                "cifmw_test_operator_namespace",
                "cifmw_test_operator_privileged",
                "cifmw_test_operator_storage_class",
                "cifmw_test_operator_selinux_level",
                "cifmw_test_operator_log_pod_security_context",
            )
        }
        stage.update(overrides or {})
        variables = dict(self.defaults)
        variables.update(
            stage_vars_dict=stage,
            _stage_vars={"name": "fixture"},
            cifmw_default_registry="quay.io",
            cifmw_default_container_image_namespace="example",
            cifmw_default_container_image_tag="current",
            run_test_fw="ansibletest",
            test_operator_instance_name="ansibletest-fixture",
            _test_operator_volume_mounts=[],
            _test_operator_volumes=[],
        )
        variables.update(extra)
        return Templar(loader=DataLoader(), variables=variables).template(variable)

    def test_ansibletest_stage_security_and_storage(self):
        overrides = {
            "cifmw_test_operator_privileged": True,
            "cifmw_test_operator_storage_class": "crc-csi-hostpath-provisioner",
            "cifmw_test_operator_selinux_level": "s0:c1,c2",
        }
        fields = {
            key: self.defaults["cifmw_test_operator_ansibletest_config"]["spec"][key]
            for key in ("privileged", "storageClass", "SELinuxLevel")
        }
        cr = {"spec": self.render(fields, overrides)}
        self.assertTrue(cr["spec"]["privileged"])
        self.assertEqual(cr["spec"]["storageClass"], "crc-csi-hostpath-provisioner")
        self.assertEqual(cr["spec"]["SELinuxLevel"], "s0:c1,c2")
        other = {"spec": self.render(fields)}
        self.assertFalse(other["spec"]["privileged"])
        self.assertEqual(other["spec"]["storageClass"], "local-storage")

    def test_reader_security_context_is_stage_specific(self):
        context = {"runAsUser": 227, "seLinuxOptions": {"level": "s0:c1,c2"}}
        pod = self.render(
            self.defaults["cifmw_test_operator_log_pod_definition"],
            {"cifmw_test_operator_log_pod_security_context": context},
            omit="OMITTED",
        )
        self.assertEqual(pod["spec"]["securityContext"], context)
        other = self.render(
            self.defaults["cifmw_test_operator_log_pod_definition"], omit="OMITTED"
        )
        self.assertEqual(other["spec"]["securityContext"], "OMITTED")

    def test_timeout_depends_on_phase_including_last_retry(self):
        tasks = yaml.safe_load((ROLE / "tasks/run-test-operator-job.yml").read_text())
        block = next(task["block"] for task in tasks if "block" in task)
        check = next(
            task for task in block if task["name"].startswith("Check whether timed out")
        )
        expression = check["ansible.builtin.set_fact"]["testpod_timed_out"]
        for phase, expected in [
            ("Succeeded", False),
            ("Failed", False),
            ("Pending", True),
        ]:
            with self.subTest(phase=phase):
                result = self.render(
                    expression,
                    testpod={
                        "resources": [{"status": {"phase": phase}}],
                        "attempts": 3,
                    },
                    cifmw_test_operator_timeout=30,
                )
                self.assertEqual(result, expected)
        self.assertTrue(
            self.render(expression, testpod={"resources": [], "attempts": 3})
        )


if __name__ == "__main__":
    unittest.main()
