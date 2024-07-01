#!/usr/bin/python3

__metaclass__ = type

DOCUMENTATION = """
  name: ci_nmstate_map_instance_nets
  short_description: Maps a Networking Env. Definition instance into it's NMstate.
  description:
    - Maps a Networking Env. Definition instance into it's NMstate.
    - If no networks exist or the existing ones needs to be skipped empty is returned.
  options:
    _input:
      description:
        - Networking Env. Definition instance entry.
      type: dict
      required: true
    instance-name:
      description:
        - The instance to map.
      type: str
      required: true
"""

EXAMPLES = """
- name: Define data to work on in the examples below
  vars:
    net_env_def:
      networks:
        default:
            dns_v4:
            - 192.168.122.1
            dns_v6: []
            gw_v4: 192.168.122.1
            mtu: 1500
            network_name: default
            network_v4: 192.168.122.0/24
            search_domain: default.example.com
        internalapi:
          dns_v4: []
          dns_v6: []
          gw_v4: 172.17.0.1
          mtu: 1496
          network_name: internalapi
          network_v4: 172.17.0.0/24
          search_domain: internalapi.example.com
      instances:
        hostname: compute-0
        name: compute-0
        networks:
          default:
            interface_name: eth1
            ip_v4: 192.168.122.100
            netmask_v4: 255.255.255.0
            prefix_length_v4: 24
            mac_addr: fa:16:3e:e4:b3:55
            network_name: default
            skip_nm: false
            mtu: 1500
          internalapi:
            interface_name: eth1.20
            ip_v4: 172.17.0.100
            netmask_v4: 255.255.255.0
            prefix_length_v4: 24
            mac_addr: 52:54:00:eb:ce:f2
            mtu: 1496
            parent_interface: eth1
            vlan_id: 20
            skip_nm: false
  ansible.builtin.set_fact:
    nmstate_interfaces: >-
      {{
        instance_nets | ci_nmstate_map_instance_nets('compute-0')
      }}
"""

RETURN = """
  _value:
    description: The result of the query.
    type: list
    sample:
      interfaces:
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
        - description: internalapi
          ipv4:
            address:
              - ip: 172.17.0.100
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
      routes:
        config:
          - destination: 0.0.0.0/0
            next-hop-address: "192.168.122.1"
            next-hop-interface: "eth1"
          - destination: 0.0.0.0/0
            next-hop-address: "172.17.0.1"
            next-hop-interface: "eth1.20"
      dns-resolver:
        config:
          search:
            - default.example.com
            - internalapi.example.com
          server:
            - 192.168.122.1
            - 172.17.0.1
"""


from ansible.errors import AnsibleFilterTypeError


class FilterModule:
    @staticmethod
    def __map_instance_ip(ip_str, prefix_length):
        ip_field = {
            "enabled": ip_str is not None,
        }
        if ip_str:
            nmstate_addr_entry = {
                "ip": ip_str,
                "prefix-length": prefix_length,
            }
            ip_field["address"] = [nmstate_addr_entry]
        return ip_field

    @classmethod
    def __map_instance_ipv4(cls, instance_net_data):
        ip_str = instance_net_data.get("ip_v4", None)
        prefix_length = instance_net_data.get("prefix_length_v4", None)
        return {"ipv4": cls.__map_instance_ip(ip_str, prefix_length)}

    @classmethod
    def __map_instance_ipv6(cls, instance_net_data):
        ip_str = instance_net_data.get("ip_v6", None)
        prefix_length = instance_net_data.get("prefix_length_v6", None)
        return {"ipv6": cls.__map_instance_ip(ip_str, prefix_length)}

    @staticmethod
    def __map_instance_vlan(instance_net_data):
        if "vlan_id" not in instance_net_data:
            return {}
        content = {"type": "vlan", "vlan": {"id": int(instance_net_data["vlan_id"])}}

        if "parent_interface" in instance_net_data:
            content["vlan"]["base-iface"] = instance_net_data["parent_interface"]

        return content

    @classmethod
    def __map_instance_net_interface(cls, instance_net_data):
        network_name = instance_net_data["network_name"]
        nmstate_cfg = {"state": "up", "type": "ethernet", "description": network_name}

        iface = instance_net_data.get("interface_name", None)
        if iface:
            nmstate_cfg["name"] = iface
        mtu = instance_net_data.get("mtu", None)
        if mtu:
            nmstate_cfg["mtu"] = int(mtu)
        nmstate_cfg.update(cls.__map_instance_ipv4(instance_net_data))
        nmstate_cfg.update(cls.__map_instance_ipv6(instance_net_data))
        nmstate_cfg.update(cls.__map_instance_vlan(instance_net_data))

        return nmstate_cfg

    @classmethod
    def __map_instance_net_dnss(cls, net_env_def, intance_nets_defs):
        nmstate_nameservers = []
        nmstate_search_domains = []
        for instance_network_data in intance_nets_defs:
            network_data = net_env_def["networks"][
                instance_network_data["network_name"]
            ]
            ns_list = network_data.get("dns_v4", []) + network_data.get("dns_v6", [])
            for ns in ns_list:
                # Manual check instead of using set to preserve order
                if ns not in nmstate_nameservers:
                    nmstate_nameservers.append(ns)

            net_search_domain = network_data.get("search_domain", None)
            if net_search_domain and net_search_domain not in nmstate_search_domains:
                nmstate_search_domains.append(net_search_domain)
        return {
            "search": nmstate_search_domains,
            "server": nmstate_nameservers,
        }

    @staticmethod
    def __map_instance_gw(gw_interface: str, iface_name: str, version: int):
        if gw_interface:
            return {
                "destination": "0.0.0.0/0" if version == 4 else "::/0",
                "next-hop-address": gw_interface,
                "next-hop-interface": iface_name,
            }

        return None

    @classmethod
    def __map_instance_default_gateway(cls, ci_instance_net, network_data, version):
        gw_str = network_data.get(f"gw_v{version}", None)
        iface = ci_instance_net.get("interface_name", None)
        return (
            cls.__map_instance_gw(
                gw_str,
                iface,
                version,
            )
            if gw_str and iface
            else None
        )

    @classmethod
    def __map_instance_net_routes(cls, net_env_def, intance_nets_defs):
        nmstate_routes = []
        for ci_instance_net in intance_nets_defs:
            network_data = net_env_def["networks"][ci_instance_net["network_name"]]
            nmstate_gw4 = cls.__map_instance_default_gateway(
                ci_instance_net, network_data, 4
            )
            if nmstate_gw4:
                nmstate_routes.append(nmstate_gw4)
            nmstate_gw6 = cls.__map_instance_default_gateway(
                ci_instance_net, network_data, 6
            )
            if nmstate_gw6:
                nmstate_routes.append(nmstate_gw6)

        return nmstate_routes

    @classmethod
    def __map_instance_nets(cls, net_env_def, instance_name):
        if not isinstance(net_env_def, dict):
            raise AnsibleFilterTypeError(
                "ci_nmstate_map_instance_nets requires Networking "
                f"Environment Definition dict, got {type(net_env_def)}"
            )
        if not isinstance(instance_name, str):
            raise AnsibleFilterTypeError(
                "ci_nmstate_map_instance_nets requires a single "
                f"string argument as instance name, got {type(instance_name)}"
            )
        instance_net_env_def = net_env_def.get("instances", {}).get(instance_name, None)
        if not instance_net_env_def:
            raise AnsibleFilterTypeError(
                "ci_nmstate_map_instance_nets cannot map "
                f"{instance_name} case it's not part of the "
                "Networking Environment Definition."
            )

        intance_nets_defs = [
            net_data
            for net_data in instance_net_env_def.get("networks", {}).values()
            if not bool(net_data.get("skip_nm", False))
        ]

        interfaces = [
            cls.__map_instance_net_interface(net_data) for net_data in intance_nets_defs
        ]

        if not interfaces:
            return {}
        routes = cls.__map_instance_net_routes(net_env_def, intance_nets_defs)
        dns = cls.__map_instance_net_dnss(net_env_def, intance_nets_defs)
        return {
            "interfaces": interfaces,
            "routes": {
                "config": routes,
            },
            "dns-resolver": {
                "config": dns,
            },
        }

    def filters(self):
        return {
            "ci_nmstate_map_instance_nets": self.__map_instance_nets,
        }
