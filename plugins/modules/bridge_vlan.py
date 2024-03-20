#!/usr/bin/python

# Copyright: (c) 2024, Pragadeeswaran <psathyan@redhat.com>
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: bridge_vlan

short_description: Attach VLAN ids to virtual network interfaces.
description: |
    This module adds VLAN ids to all virtual network interfaces attached
    to the specified virtual network. The virtual network has a physical
    network interface that is configured as a VLAN trunk port.

    The module sets the tasks return elements like changed and success
    to true when

        - Physical interface is configured for trunk VLAN
        - There are TAPs attached to the virtual network
        - All identified VLAN ids were applied to all identified interfaces

    The module sets the tasks to failed when

        - Physical interface is configured to forward multiple VLAN ids
        - There are TAPs attached to the virtual network
        - There was a failure allowing VLAN ids for one or more TAPs

    For any other conditions, the changed is marked as false and success is
    marked as true.

requirements:
  - nmcli
  - bridge
  - ip

options:
    networks:
        description: The name of the virtual networks.
        required: true
        type: list
        elements: str

author:
  - Pragadeeswaran (@psathyan)
"""


EXAMPLES = r"""
- name: Attach all configured VLANs to the interfaces of osp_trunk
  become: true
  bridge_vlan:
    networks:
      - osp_trunk
"""  # noqa


RETURN = r"""
success:
    description: Status of the execution
    type: bool
    returned: always
    sample: true
"""


from copy import deepcopy
from typing import Any, Dict, List, Optional

import json

from ansible.module_utils.basic import AnsibleModule


def get_taps(details: List[Dict[str, Any]]) -> List[str]:
    """Gather the list of TAP devices found in the given network details.

    Args:
        details: A list of mapping containing details of the ports attached to
                 a virtual network.

    Returns:
        A list of virtual network interface names having suffix as vnet.
    """
    return [_net["ifname"] for _net in details if _net["ifname"].startswith("vnet")]


def get_physical_iface(details: List[Dict[str, Any]]) -> Optional[str]:
    """Return the physical interface found in the given network details.

    Args:
        details: A list of mapping containing details of the ports attached to
                 a virtual network.

    Returns:
        A string representing the first interface name not having vnet suffix.
    """
    for _net in details:
        if not _net["ifname"].startswith("vnet"):
            return _net["ifname"]

    return None


class BridgeVlanCLI(object):
    """BridgeVlanCLI class acts as an interface to bridge vlan subcommand."""

    def __init__(self, module: AnsibleModule) -> None:
        self.module = module
        self.vnet_names = module.params["networks"]

    def execute_command(self, cmd, use_unsafe_shell=False, data=None) -> Any:
        return self.module.run_command(
            cmd, use_unsafe_shell=use_unsafe_shell, data=data
        )

    def _get_net_info(self, name: str) -> Any:
        """Collect the details of the provided network.

        Args:
            name: name of the network

        Returns:
            Tuple (rc, stdout, stderr) command execution information.
        """
        _cmd = [
            self.module.get_bin_path("ip", True),
            "-json",
            "link",
            "show",
            "master",
            name,
        ]
        return self.execute_command(cmd=_cmd)

    def _get_vlan_ids(self, name: str) -> List[str]:
        """Gather the VLAN IDs associated to the given iface.

        Args:
            name: name of the physical interface.

        Returns:
            A list containing VLAN ids in form of 3, 4, 5, 6-10
        """
        _cmd = [
            self.module.get_bin_path("nmcli", True),
            "-t",
            "-f",
            "bridge-port.vlans",
            "connection",
            "show",
            name,
        ]
        (rc, out, _) = self.execute_command(_cmd)
        _possible_vlans = out.strip().split(":")[1]

        if rc != 0 or not _possible_vlans:
            return []

        # Output: bridge-port.vlans:120-129, 502 pvid untagged
        # Output: bridge-port.vlans:120-129
        # Output: bridge-port.vlans:120, 121, 122, 123
        _vlans = _possible_vlans.split(",")
        if "pvid" in _vlans[-1]:
            # Remove the x pvid untagged which is the last
            _vlans.pop()

        return _vlans

    def _apply_vlans(self, vlans: List[Any], taps: List[Any]) -> bool:
        """Applies the provided VLANs for the given TAPs.

        Args:
            vlans: A list containing a string of VLAN ids
            taps: A list containing the names of TAP devices to which VLANs are applied.

        Return:
            True if successful else False
        """
        _success = True
        _base_cmd = [self.module.get_bin_path("bridge", True), "vlan", "add", "dev"]
        for _tap in taps:
            _tap_cmd = _base_cmd + [_tap, "vid"]
            for _vlan in vlans:
                _vlan_cmd = _tap_cmd + [_vlan]
                (_rc, _, _) = self.execute_command(_vlan_cmd)

                _success = _success and _rc != 0

        return _success

    def add_vlans(self) -> Dict[str, Any]:
        """Add the VLAN ids to the associated network.

        Returns:
            A mapping holding results of each network.
        """
        _result = dict(changed=False, failed=True, networks=dict())
        _success = None
        for _net in self.vnet_names:
            _rc, _out, _err = self._get_net_info(_net)
            if _rc != 0:
                _result["networks"][_net] = dict(failed=False, error=_err)
                continue

            net_info = json.loads(_out)
            taps = get_taps(net_info)
            if not taps:
                _result["networks"][_net] = dict(
                    error="No TAP interfaces found.",
                    failed=False,
                    changed=False,
                )
                continue

            iface = get_physical_iface(net_info)
            if not iface:
                _result["networks"][_net] = dict(
                    error="No physical interface found.", failed=False, changed=False
                )
                continue

            vlans = self._get_vlan_ids(iface)
            if not vlans:
                _result["networks"][_net] = dict(
                    error="Failed to gather the VLAN information.",
                    failed=False,
                    changed=False,
                )
                continue

            if self._apply_vlans(vlans, taps):
                _result["networks"][_net] = dict(iface=deepcopy(net_info))
                _result["networks"][_net]["result"] = {
                    "changed": True,
                    "success": True,
                    "failed": False,
                }
                _success = True if _success is None else _success
            else:
                _result["networks"][_net] = dict(iface=deepcopy(net_info))
                _result["networks"][_net]["result"] = {
                    "changed": False,
                    "success": False,
                    "failed": True,
                }
                _success = False

        # Set task level results
        _result["changed"] = False if _success is None else _success
        _result["success"] = True if _success is None else _success
        _result["failed"] = False if _success is None else not _success

        return _result


def run_module():
    _args = dict(networks=dict(required=True, type="list", elements="str"))

    _result = dict(success=True, changed=False, failed=False)

    _module = AnsibleModule(argument_spec=_args, supports_check_mode=True)

    if _module.check_mode:
        _module.exit_json(**_result)

    bridge = BridgeVlanCLI(_module)
    _result = bridge.add_vlans()

    _module.exit_json(**_result)


if __name__ == "__main__":
    run_module()
