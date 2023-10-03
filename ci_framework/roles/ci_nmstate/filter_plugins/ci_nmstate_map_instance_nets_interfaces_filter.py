#!/usr/bin/env python3

__metaclass__ = type

DOCUMENTATION = """
  name: ci_nmstate_map_instance_nets_interfaces
  short_description: Maps CI-framework instance nets dict to a nmstate interfaces list.
  description:
    - Maps CI-framework instance networks dict to a proper nmstate list of interfaces.
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
  ansible.builtin.set_fact:
    nmstate_interfaces: >-
      {{
        instance_nets | ci_nmstate_map_instance_nets_interfaces
      }}
"""

RETURN = """
  _value:
    description: The result of the query.
    type: list
    sample:
      - description: default
        ipv4:
          address:
            - ip: 192.168.122.100
              prefix-length: 24
              enabled: true
          ipv6:
              enabled: false
          mtu: 1500
          name: eth1
          state: up
          type: ethernet
      -   description: internal-api
          ipv4:
              address:
              -   ip: 172.17.0.100
                  prefix-length: 24
              enabled: true
          ipv6:
              enabled: false
          mtu: 1496
          name: eth1.20
          state: up
          type: vlan
          vlan:
              base-iface: eth1
              id: 20
"""

import ipaddress


from ansible.errors import AnsibleFilterTypeError


class FilterModule:
    @staticmethod
    def __map_instance_ip(ip_interface):
        ip_field = {
            "enabled": bool(ip_interface),
        }
        if ip_interface:
            nmstate_addr_entry = {
                "ip": str(ip_interface.ip),
                "prefix-length": ip_interface.network.prefixlen,
            }
            ip_field["address"] = [nmstate_addr_entry]
        return ip_field

    @classmethod
    def __map_instance_ipv4(cls, ci_instance_net):
        ip_str = ci_instance_net.get("ip4", ci_instance_net.get("ip", None))
        ip_interface = ipaddress.ip_interface(ip_str) if ip_str else None
        return {
            "ipv4": cls.__map_instance_ip(
                ip_interface if ip_interface and ip_interface.version == 4 else None
            )
        }

    @classmethod
    def __map_instance_ipv6(cls, ci_instance_net):
        ip_str = ci_instance_net.get("ip6", ci_instance_net.get("ip", None))
        ip_interface = ipaddress.ip_interface(ip_str) if ip_str else None
        return {
            "ipv6": cls.__map_instance_ip(
                ip_interface if ip_interface and ip_interface.version == 6 else None
            )
        }

    @staticmethod
    def __map_instance_vlan(ci_instance_net):
        if "vlan" not in ci_instance_net:
            return {}

        return {
            "type": "vlan",
            "vlan": {
                "id": int(ci_instance_net["vlan"]),
                "base-iface": ci_instance_net["parent_iface"],
            },
        }

    @classmethod
    def __map_instance_net(cls, ci_instance_net, net_name=None):
        nmstate_cfg = {"state": "up", "type": "ethernet"}

        network = ci_instance_net.get("connection", net_name)
        if network:
            nmstate_cfg["description"] = network
        iface = ci_instance_net.get("iface", None)
        if iface:
            nmstate_cfg["name"] = iface
        mtu = ci_instance_net.get("mtu", None)
        if mtu:
            nmstate_cfg["mtu"] = int(mtu)

        nmstate_cfg.update(cls.__map_instance_ipv4(ci_instance_net))
        nmstate_cfg.update(cls.__map_instance_ipv6(ci_instance_net))
        nmstate_cfg.update(cls.__map_instance_vlan(ci_instance_net))

        return nmstate_cfg

    @classmethod
    def __map_instance_nets_ifaces(cls, ci_instance_nets):
        if not isinstance(ci_instance_nets, dict):
            raise AnsibleFilterTypeError(
                "ci_nmstate_map_instance_nets_ifaces requires a dict, "
                f"got {type(ci_instance_nets)}"
            )

        return [
            cls.__map_instance_net(data, net_name=net_name)
            for net_name, data in ci_instance_nets.items()
        ]

    def filters(self):
        return {
            "ci_nmstate_map_instance_nets_interfaces": self.__map_instance_nets_ifaces,
        }
