#!/usr/bin/env python3

__metaclass__ = type

DOCUMENTATION = """
  name: ci_nmstate_map_instance_nets_dns
  short_description: Maps CI-framework instance networks dict to a nmstate DNS config.
  description:
    - Maps CI-framework instance networks dict to a proper nmstate DNS config.
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
        dns4: 192.168.122.1
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
        dns4: 172.17.0.1
  ansible.builtin.set_fact:
    nmstate_interfaces: >-
      {{
        instance_nets | ci_nmstate_map_instance_nets_dns
      }}
"""

RETURN = """
  _value:
    description: The result of the query.
    type: list
    sample:
      search: []
      server:
        - 192.168.122.1
        - 172.17.0.1
"""

import ipaddress


from ansible.errors import AnsibleFilterTypeError


class FilterModule:
    @classmethod
    def __map_instance_ip_dns(cls, ci_instance_net, version):
        result = []
        dns_cfg_list = []
        dns_entry = ci_instance_net.get(
            f"dns{version}", ci_instance_net.get("dns", None)
        )
        if isinstance(dns_entry, list):
            dns_cfg_list = dns_entry
        elif isinstance(dns_entry, str):
            dns_cfg_list = dns_entry.split(",")

        for dns_server in dns_cfg_list:
            dns_interface = ipaddress.ip_interface(dns_server) if dns_server else None
            if dns_interface and dns_interface.version == version:
                result.append(str(dns_interface.ip))

        return result

    @classmethod
    def __map_instance_net_dnss(cls, ci_instance_nets):
        if not isinstance(ci_instance_nets, dict):
            raise AnsibleFilterTypeError(
                "ci_nmstate_map_instance_nets_dns requires a dict, "
                f"got {type(ci_instance_nets)}"
            )
        nmstate_nameservers = []
        for ci_instance_net in ci_instance_nets.values():
            ns_list = cls.__map_instance_ip_dns(
                ci_instance_net, 4
            ) + cls.__map_instance_ip_dns(ci_instance_net, 6)
            for ns in ns_list:
                # Manual check instead of using set to preserve order
                if ns not in nmstate_nameservers:
                    nmstate_nameservers.append(ns)

        return {
            "search": [],
            "server": nmstate_nameservers,
        }

    def filters(self):
        return {
            "ci_nmstate_map_instance_nets_dns": self.__map_instance_net_dnss,
        }
