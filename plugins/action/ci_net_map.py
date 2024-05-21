#!/usr/bin/env python3

# Copyright Red Hat, Inc.
# Apache License Version 2.0 (see LICENSE)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import typing

DOCUMENTATION = r"""
---
action: ci_net_map

short_description: Maps the Networking Definition to a Networking Env. Definition

description:
- Takes the Networking Definition, and based on Ansible facts and a set of
  rules, translates that info into a valid Networking Env. Definition.
- This task plugin requires networking facts to be present for every
  instance referenced in the Networking Definition.
- Partial mappings are allowed to allow infrastructure bootstrapping based on the
  mapping result even without already deployed instances.

options:
  networking_definition:
    description:
    - The Networking Definition as a dictionary.
    type: dict
    required: true
  interfaces_info:
    description:
    - Dict that contains the list of MAC addresses of each instance to be mapped.
    - Each dict entry is a list of dicts with at least a `mac` field.
    - Each item in the list is an interface in a given infrastructure network.
    - It's required for full maps.
    type: iterable
    required: false
  search_domain_base:
    description:
    - Domain name used for generating networks search domains.
    type: str
    default: example.com

"""

EXAMPLES = r"""
- name: Perform a partial map of the given Networking Definition
  cimf.general.ci_net_map:
    networking_definition:
      networks:
        ctlplane:
          network: "192.168.122.0/24"
          gateway: "192.168.122.1"
          dns:
            - "192.168.122.253"
            - "192.168.122.254"
          search-domain: "ctlplane.example.local"
          mtu: 1500
        tenant:
          network: "172.19.0.0/24"
          gateway-v4: "172.19.0.1"
          search-domain: "tenant.example.local"
          dns-v4:
            - "8.8.8.8"
            - "172.19.0.1"
          vlan: 22
          mtu: 1496
        group-templates:
          group-1:
            networks:
              ctlplane:
                range: "192.168.122.10-192.168.122.14"
              tenant:
                skip-nm-configuration: true
                range:
                  start: 10
                  length: 5
        instances:
          instance-1:
            networks:
              ctlplane:
                ip: "192.168.122.100"
              storage:
                skip-nm-configuration: true
                ip: "172.18.0.100"

- name: Perform a full map of the given Networking Definition
  cimf.general.ci_net_map:
    networking_definition:
      networks:
        ctlplane:
          network: "192.168.122.0/24"
          gateway: "192.168.122.1"
          dns:
            - "192.168.122.253"
            - "192.168.122.254"
          search-domain: "ctlplane.example.local"
          mtu: 1500
        tenant:
          network: "172.19.0.0/24"
          gateway-v4: "172.19.0.1"
          search-domain: "tenant.example.local"
          dns-v4:
            - "8.8.8.8"
            - "172.19.0.1"
          vlan: 22
          mtu: 1496
        group-templates:
          group-1:
            networks:
              ctlplane:
                range: "192.168.122.10-192.168.122.14"
              tenant:
                skip-nm-configuration: true
                range:
                  start: 10
                  length: 5
        instances:
          instance-1:
            networks:
              ctlplane:
                ip: "192.168.122.100"
              storage:
                skip-nm-configuration: true
                ip: "172.18.0.100"
    network_name: test-network
    interfaces_info:
      controller-0:
        - mac: fa:16:3e:12:4f:d1
          network: test-network
        - mac: aa:45:3e:ab:ff:e4
          network: test-network-2
      instance-0:
        - mac: fa:16:3e:c1:b2:e9
          network: test-network
      instance-1:
        - mac: fa:16:3e:3d:e5:cc
          network: test-network
        - mac: aa:45:3e:f9:00:c0
          network: test-network-2
"""

RETURN = r"""
networking_env_definition:
    description: The output Networking Environment Definition
    returned: success
    type: dict
    sample:
      networks:
        network-1:
          network_name: network-1
          search_domain: net-1.example.local
          tools:
            metallb:
              ipv4_ranges: []
              ipv6_ranges:
              - start: fdc0:8b54:108a:c949:0000:0000:0000:0011
                start_host: 17
                end: fdc0:8b54:108a:c949:0000:0000:0000:001a
                end_host: 26
                length: 10
            multus:
              ipv4_ranges:
              - start: 192.168.122.30
                start_host: 30
                end: 192.168.122.39
                end_host: 39
                length: 10
              ipv6_ranges:
              - start: fdc0:8b54:108a:c949:0000:0000:0000:001e
                start_host: 30
                end: fdc0:8b54:108a:c949:0000:0000:0000:0027
                end_host: 39
                length: 10
          dns_v4:
          - 192.168.122.253
          dns_v6:
          - fdc0:8b54:108a:c949:ffff:ffff:ffff:fffe
          network_v4: 192.168.122.0/24
          network_v6: fdc0:8b54:108a:c949::/64
          gw_v4: 192.168.122.1
          gw_v6: fdc0:8b54:108a:c949:0000:0000:0000:0001
          mtu: 1500
        network-2:
          network_name: network-2
          search_domain: net-2.example.local
          tools:
            metallb:
              ipv4_ranges:
              - start: 172.18.0.60
                start_host: 60
                end: 172.18.0.69
                end_host: 69
                length: 10
              ipv6_ranges: []
            netconfig:
              ipv4_ranges:
              - start: 172.18.0.40
                start_host: 40
                end: 172.18.0.49
                end_host: 49
                length: 10
          dns_v4:
          - 1.1.1.1
          dns_v6: []
          network_v4: 172.18.0.0/24
          gw_v4: 172.18.0.1
          vlan_id: 21
          mtu: 1496
      instances:
        instance-1:
          name: instance-1
          networks:
            network-1:
              network_name: network-1
              skip_nm: false
              mac_addr: 27:b9:47:74:b3:02
              interface_name: eth1
              ip_v4: 192.168.122.10
              ip_v6: fdc0:8b54:108a:c949:0000:0000:0000:000a
              mtu: 1500
          hostname: instance-1-hostname
        instance-2:
          name: instance-2
          networks:
            network-1:
              network_name: network-1
              skip_nm: false
              mac_addr: a1:69:da:21:aa:03
              interface_name: eth2
              ip_v4: 192.168.122.11
              ip_v6: fdc0:8b54:108a:c949:0000:0000:0000:000b
              mtu: 1500
          hostname: instance-2-hostname
complete_map:
    description: Tells if the output is the result of a full map (with instances_info)
    returned: success
    type: bool
"""

from ansible.errors import AnsibleActionFail
from ansible.plugins.action import ActionBase

from ansible_collections.cifmw.general.plugins.module_utils.encoding import (
    ansible_encoding,
)
from ansible_collections.cifmw.general.plugins.module_utils.net_map import (
    exceptions,
    networking_mapper,
)


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp

        task_args = ansible_encoding.decode_ansible_raw(self._task.args)
        networking_definition = task_args.get("networking_definition", None)
        if not networking_definition:
            raise AnsibleActionFail("networking_definition is a mandatory argument")

        mapper = networking_mapper.NetworkingDefinitionMapper(
            dict(task_vars["hostvars"]),
            task_vars["groups"],
            options=networking_mapper.NetworkingMapperOptions.from_dict(task_args),
        )

        try:
            mapping_result = mapper.map(
                networking_definition, interfaces_info=task_args.get("interfaces_info", None)
            )
            result["failed"] = False
            result["networking_env_definition"] = mapping_result
        except exceptions.NetworkMappingError as run_exception:
            result = {**result, **(run_exception.to_raw()), "failed": True}

        return result
