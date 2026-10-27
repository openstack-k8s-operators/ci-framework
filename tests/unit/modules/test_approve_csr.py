# Copyright: (c) 2024, Red Hat

# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

from unittest.mock import patch

from ansible_collections.cifmw.general.tests.unit.utils import (
    ModuleBaseTestCase,
    set_module_args,
    AnsibleExitJson,
    AnsibleFailJson,
)
from ansible_collections.cifmw.general.plugins.modules import approve_csr


class TestApproveCSRCore(ModuleBaseTestCase):
    """Test core functionality of approve_csr module."""

    def test_negative_gathering_pending_requests(self):
        set_module_args({})
        expected_msg = "Failed to gather the list of pending requests"

        with patch.object(approve_csr.ApproveCSR, "execute_command") as run_cmd:
            _out = ""
            _err = "No binary found."
            rc = -1
            run_cmd.return_value = (rc, _out, _err)

            with self.assertRaises(AnsibleFailJson) as rst:
                approve_csr.run_module()

            result = rst.exception.args[0]

            self.assertEquals(result["msg"], expected_msg)
            self.assertTrue(result["failed"])

    def test_negative_approving_cert_requests(self):
        set_module_args({})
        _msg = "Unable to approve certificate request - test-cert-request."

        with patch.object(approve_csr.ApproveCSR, "execute_command") as run_cmd:
            _side_effect = [
                (0, "test-cert-request", ""),
                (1, "", "Unable to approve request."),
            ]
            run_cmd.side_effect = _side_effect

            with self.assertRaises(AnsibleFailJson) as rst:
                approve_csr.run_module()

            result = rst.exception.args[0]

            self.assertEquals(result["msg"], _msg)
            self.assertTrue(result["failed"])

    def test_one_iteration_on_wait(self):
        """Test when there is only one certificate request."""
        set_module_args(dict(quiet_period=2))

        with patch.object(approve_csr.ApproveCSR, "execute_command") as run_cmd:
            _side_effect = [
                (0, "test-cert-request", None),
                (0, "Success", None),
                (0, "", None),
            ]
            run_cmd.side_effect = _side_effect

            with self.assertRaises(AnsibleExitJson) as rst:
                approve_csr.run_module()

            self.assertTrue(rst.exception.args[0]["changed"])

    def test_multiple_iterations_on_wait(self):
        """Test when there are multiple certificate requests"""
        set_module_args(dict(quiet_period=12))

        with patch.object(approve_csr.ApproveCSR, "execute_command") as run_cmd:
            _side_effect = [
                (0, "test-cert-request", None),
                (0, "Success", None),
                (0, "test-cert-request-1", None),
                (0, "Success", None),
                (0, "", None),
                (0, "", None),
                (0, "", None),
            ]
            run_cmd.side_effect = _side_effect

            with self.assertRaises(AnsibleExitJson) as rst:
                approve_csr.run_module()

            self.assertTrue(rst.exception.args[0]["changed"])
            self.assertEquals(rst.exception.args[0]["rc"], 0)
