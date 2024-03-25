# Copyright: (c) 2024, Red Hat

# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

import json

from unittest.mock import patch

from ansible_collections.cifmw.general.tests.unit.utils import (
    ModuleBaseTestCase,
    set_module_args,
    AnsibleExitJson,
    AnsibleFailJson,
)
from ansible_collections.cifmw.general.plugins.modules import bridge_vlan


class TestBridgeVLAN(ModuleBaseTestCase):
    """Test core functionality of configuring TAP."""

    def test_negative_missing_params(self):
        """Check failure when missing parameters."""
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            bridge_vlan.run_module()

    def test_negative_invalid_network(self):
        """Test when an invalid network is provided."""
        set_module_args({"networks": ["test-net"]})

        with patch.object(bridge_vlan.BridgeVlanCLI, "_get_net_info") as patch_func:
            _rc = -1
            _err = "Failed to gather network"
            patch_func.return_value = (_rc, "", _err)

            with self.assertRaises(AnsibleExitJson) as rst:
                bridge_vlan.run_module()

            result = rst.exception.args[0]
            self.assertFalse(result["failed"])

    def test_negative_network_with_no_physical_port(self):
        """Test when there is no port attached to the network."""
        set_module_args({"networks": ["test-net"]})
        _msg = "No physical interface found."

        with patch.object(bridge_vlan.BridgeVlanCLI, "_get_net_info") as patch_func:
            _rc = 0
            _data = [
                dict(ifindex=0, ifname="vnet0", master="test-net"),
                dict(ifindex=1, ifname="vnet1", master="test-net"),
            ]
            _out = json.dumps(_data)
            patch_func.return_value = (_rc, _out, None)

            with self.assertRaises(AnsibleExitJson) as rst:
                bridge_vlan.run_module()

            result = rst.exception.args[0]
            self.assertFalse(result["changed"])
            self.assertIn("test-net", result["networks"])
            self.assertEquals(result["networks"]["test-net"]["error"], _msg)

    def test_negative_network_with_no_tap(self):
        """Test when there is no port attached to the network."""
        set_module_args({"networks": ["test-net"]})
        _msg = "No TAP interfaces found."

        with patch.object(bridge_vlan.BridgeVlanCLI, "_get_net_info") as patch_func:
            _rc = 0
            _data = [dict(ifindex=0, ifname="ens1", master="test-net")]
            _out = json.dumps(_data)
            patch_func.return_value = (_rc, _out, None)

            with self.assertRaises(AnsibleExitJson) as rst:
                bridge_vlan.run_module()

            result = rst.exception.args[0]
            self.assertFalse(result["changed"])
            self.assertEquals(result["networks"]["test-net"]["error"], _msg)

    def test_negative_no_vlan_ids(self):
        """Test when there is no VLAN ids associated with the physical interface."""
        set_module_args({"networks": ["test-net"]})
        _msg = "Failed to gather the VLAN information."

        with patch.object(bridge_vlan.BridgeVlanCLI, "_get_net_info") as patch_func:
            _rc = 0
            _data = [
                dict(ifindex=0, ifname="vnet0", master="test-net"),
                dict(ifindex=1, ifname="vnet1", master="test-net"),
                dict(ifindex=2, ifname="ens1", master="test-net"),
            ]
            _out = json.dumps(_data)
            patch_func.return_value = (_rc, _out, None)

            with patch.object(bridge_vlan.BridgeVlanCLI, "_get_vlan_ids") as patch_vlan:
                patch_vlan.return_value = []
                with self.assertRaises(AnsibleExitJson) as rst:
                    bridge_vlan.run_module()

                result = rst.exception.args[0]
                self.assertFalse(result["changed"])
                self.assertEquals(result["networks"]["test-net"]["error"], _msg)

    def test_negative_failed_to_apply_vlan(self):
        """Test failure on applying VLANs to TAP."""
        set_module_args({"networks": ["test-net"]})

        with patch.object(bridge_vlan.BridgeVlanCLI, "_get_net_info") as patch_func:
            _rc = 0
            _data = [
                dict(ifindex=0, ifname="vnet0", master="test-net"),
                dict(ifindex=1, ifname="vnet1", master="test-net"),
                dict(ifindex=2, ifname="ens1", master="test-net"),
            ]
            _out = json.dumps(_data)
            patch_func.return_value = (_rc, _out, None)

            with patch.object(bridge_vlan.BridgeVlanCLI, "_get_vlan_ids") as patch_vlan:
                patch_vlan.return_value = [10]

                with patch.object(
                    bridge_vlan.BridgeVlanCLI, "_apply_vlans"
                ) as patch_apply:
                    patch_apply.return_value = False
                    with self.assertRaises(AnsibleExitJson) as rst:
                        bridge_vlan.run_module()

                    result = rst.exception.args[0]
                    self.assertFalse(result["changed"])
                    self.assertTrue(result["failed"])

    def test_apply_vlan_on_success(self):
        """Test apply vlan on success."""
        set_module_args({"networks": ["test-net"]})

        with patch.object(bridge_vlan.BridgeVlanCLI, "_get_net_info") as patch_func:
            _rc = 0
            _data = [
                dict(ifindex=0, ifname="vnet0", master="test-net"),
                dict(ifindex=1, ifname="vnet1", master="test-net"),
                dict(ifindex=2, ifname="ens1", master="test-net"),
            ]
            _out = json.dumps(_data)
            patch_func.return_value = (_rc, _out, None)

            with patch.object(bridge_vlan.BridgeVlanCLI, "_get_vlan_ids") as patch_vlan:
                patch_vlan.return_value = [10]

                with patch.object(
                    bridge_vlan.BridgeVlanCLI, "_apply_vlans"
                ) as patch_apply:
                    patch_apply.return_value = True
                    with self.assertRaises(AnsibleExitJson) as rst:
                        bridge_vlan.run_module()

                    result = rst.exception.args[0]

                    self.assertTrue(result["changed"])
                    self.assertTrue(result["success"])
                    self.assertFalse(result["failed"])
                    self.assertIn("test-net", result["networks"])
