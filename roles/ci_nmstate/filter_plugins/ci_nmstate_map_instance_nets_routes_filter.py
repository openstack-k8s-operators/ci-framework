#!/usr/bin/env python3

__metaclass__ = type

DOCUMENTATION = """
  name: ci_nmstate_map_instance_nets_routes
  short_description: Maps CI-framework instance nets dict to a nmstate list of routes.
  description:
    - Maps CI-framework instance networks dict to a proper nmstate list of routes.
  options:
    _input:
      description:
        - CI-framework networks dictionary for a given instance.
        - Each key represents a network.
        - Each value represents properties of the interface attached to that network.
      type: dict
      required: true
"""

EXAMPLES = """
- name: Define data to work on in the examples below
  vars:
    instance_nets:
      default:
        connection: ci-private-network
        gw4: 192.168.122.1
        iface: eth1
        ip4: 192.168.122.100/24
        mac: fa:16:3e:e4:b3:55
        mtu: 1500
      internal-api:
        iface: eth1.20
        ip4: 172.17.0.100/24
        mac: 52:54:00:eb:ce:f2
        mtu: '1496'
        parent_iface: eth1
        vlan: 20
        gw4: 172.17.0.1
  ansible.builtin.set_fact:
    nmstate_interfaces: >-
      {{
        instance_nets | ci_nmstate_map_instance_nets_routes
      }}
"""

RETURN = """
  _value:
    description: The result of the query.
    type: list
    sample:
      - destination: 0.0.0.0/0
        next-hop-address: "192.168.122.1"
        next-hop-interface: "eth1"
      - destination: 0.0.0.0/0
        next-hop-address: "172.17.0.1"
        next-hop-interface: "eth1.20"
"""

import ipaddress


from ansible.errors import AnsibleFilterTypeError


class FilterModule:
    @staticmethod
    def __map_instance_gw(gw_interface, iface_name):
        if gw_interface:
            return {
                "destination": "0.0.0.0/0",
                "next-hop-address": str(gw_interface.ip),
                "next-hop-interface": iface_name,
            }

        return None

    @classmethod
    def __map_instance_default_gateway(cls, ci_instance_net, version):
        gw_str = ci_instance_net.get(f"gw{version}", ci_instance_net.get("gw", None))
        gw_interface = ipaddress.ip_interface(gw_str) if gw_str else None
        iface = ci_instance_net.get("iface", None)
        return (
            cls.__map_instance_gw(
                gw_interface
                if gw_interface and gw_interface.version == version
                else None,
                iface,
            )
            if iface
            else None
        )

    @classmethod
    def __map_instance_net_routes(cls, ci_instance_nets):
        if not isinstance(ci_instance_nets, dict):
            raise AnsibleFilterTypeError(
                "ci_nmstate_map_instance_routes requires a dict, "
                f"got {type(ci_instance_nets)}"
            )
        nmstate_routes = []
        for ci_instance_net in ci_instance_nets.values():
            nmstate_gw4 = cls.__map_instance_default_gateway(ci_instance_net, 4)
            if nmstate_gw4:
                nmstate_routes.append(nmstate_gw4)
            nmstate_gw6 = cls.__map_instance_default_gateway(ci_instance_net, 6)
            if nmstate_gw6:
                nmstate_routes.append(nmstate_gw6)

        return nmstate_routes

    def filters(self):
        return {
            "ci_nmstate_map_instance_nets_routes": self.__map_instance_net_routes,
        }
