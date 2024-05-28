from __future__ import absolute_import, division, print_function

__metaclass__ = type

import ipaddress

import pytest
from ansible_collections.cifmw.general.plugins.module_utils.net_map import (
    exceptions,
    networking_definition,
)

from ansible_collections.cifmw.general.tests.unit.module_utils.test_utils import (
    net_map_stub_data,
)


def test_networking_definition_colliding_ranges_fail():
    conflicting_net = ipaddress.ip_network("192.168.122.0/24")
    conflicting_net_name = "net-1"
    networking_definition_raw = {
        "networks": {
            conflicting_net_name: {
                "network": str(conflicting_net),
                "vlan": "122",
                "mtu": "9000",
            },
        },
        "group-templates": {
            "group-1": {
                "networks": {
                    conflicting_net_name: {"range": {"start": 0, "length": 30}},
                },
            },
            "group-2": {
                "networks": {
                    conflicting_net_name: {"range": {"start": 29, "length": 30}},
                },
            },
        },
    }

    with pytest.raises(exceptions.HostNetworkRangeCollisionValidationError) as exc_info:
        networking_definition.NetworkingDefinition(networking_definition_raw)

    assert exc_info.value.range_1 == networking_definition.HostNetworkRange(
        conflicting_net, start=0, end=29
    )
    assert exc_info.value.range_2 == networking_definition.HostNetworkRange(
        conflicting_net, start=29, length=30
    )
    assert conflicting_net_name in exc_info.value.message

    # Ensure the dict representation is fine
    raw_collision_exception = exc_info.value.to_raw()
    assert "range_1" in raw_collision_exception
    assert "range_2" in raw_collision_exception
    range_dict_1 = raw_collision_exception["range_1"]
    range_dict_2 = raw_collision_exception["range_2"]
    assert range_dict_1["start_ip"] == str(conflicting_net[0])
    assert range_dict_2["start_ip"] == str(conflicting_net[29])
    assert range_dict_1["end_ip"] == str(conflicting_net[29])
    assert range_dict_2["end_ip"] == str(conflicting_net[58])
    assert range_dict_1["network"] == str(conflicting_net)
    assert range_dict_2["network"] == str(conflicting_net)


def test_networking_definition_load_networking_definition_1_ok():
    raw_definition_1 = net_map_stub_data.get_test_file_yaml_content(
        "networking-definition-valid.yml"
    )
    test_net_1 = networking_definition.NetworkingDefinition(raw_definition_1)
    assert test_net_1
    assert len(test_net_1.networks) == 4
    assert len(test_net_1.group_templates) == 1
    assert len(test_net_1.instances) == 1
    assert all(
        net_name in test_net_1.networks
        for net_name in ("ctlplane", "internal-api", "storage", "tenant")
    )
    assert net_map_stub_data.GROUP_1_NAME in test_net_1.group_templates
    assert net_map_stub_data.INSTANCE_1_NAME in test_net_1.instances


def test_networking_definition_load_networking_definition_all_tools_ok():
    raw_definition_1 = net_map_stub_data.get_test_file_yaml_content(
        "networking-definition-valid-all-tools.yml"
    )
    test_net_1 = networking_definition.NetworkingDefinition(raw_definition_1)
    assert test_net_1
    assert len(test_net_1.networks) == 4
    assert len(test_net_1.group_templates) == 2
    assert len(test_net_1.instances) == 1
    assert all(
        net_name in test_net_1.networks
        for net_name in ("ctlplane", "internal-api", "storage", "tenant")
    )
    assert net_map_stub_data.GROUP_2_NAME in test_net_1.group_templates
    assert net_map_stub_data.GROUP_3_NAME in test_net_1.group_templates
    assert net_map_stub_data.INSTANCE_3_NAME in test_net_1.instances

    for net_name, net_def in test_net_1.networks.items():
        assert net_def.multus_config
        assert len(net_def.multus_config.ranges_ipv4) == 1
        assert not net_def.multus_config.ranges_ipv6

        assert net_def.metallb_config
        assert len(net_def.metallb_config.ranges_ipv4) == 1
        assert not net_def.metallb_config.ranges_ipv6

        assert net_def.netconfig_config
        assert len(net_def.netconfig_config.ranges_ipv4) == 2
        assert not net_def.netconfig_config.ranges_ipv6


def test_networking_definition_load_networking_definition_all_tools_dual_stack_ok():
    raw_definition_1 = net_map_stub_data.get_test_file_yaml_content(
        "networking-definition-valid-all-tools-dual-stack.yml"
    )
    test_net_1 = networking_definition.NetworkingDefinition(raw_definition_1)
    assert test_net_1
    assert len(test_net_1.networks) == 4
    assert len(test_net_1.group_templates) == 2
    assert len(test_net_1.instances) == 2

    # Check that the expected networks are in
    assert all(
        net_name in test_net_1.networks
        for net_name in ("network-1", "network-2", "network-3", "network-4")
    )
    assert "group-1" in test_net_1.group_templates
    assert "instance-1" in test_net_1.instances

    # Simple basic checks of network-1
    net1_def = test_net_1.networks["network-1"]
    net1_ip_netv4 = ipaddress.ip_network("192.168.122.0/24")
    net1_ip_netv6 = ipaddress.ip_network("fdc0:8b54:108a:c949::/64")
    assert net1_def.name == "network-1"
    assert net1_def.ipv4_network == net1_ip_netv4
    assert net1_def.ipv6_network == net1_ip_netv6
    assert net1_def.mtu == 1500
    assert not net1_def.vlan
    assert net1_def.metallb_config
    assert net1_def.multus_config
    assert net1_def.netconfig_config
    assert len(net1_def.multus_config.ranges_ipv4) == 1
    assert len(net1_def.multus_config.ranges_ipv6) == 1
    assert len(net1_def.netconfig_config.ranges_ipv4) == 2
    assert len(net1_def.netconfig_config.ranges_ipv6) == 1
    assert not net1_def.metallb_config.ranges_ipv4
    assert len(net1_def.metallb_config.ranges_ipv6) == 1

    # Simple basic checks of network-2
    net2_def = test_net_1.networks["network-2"]
    net2_ip_netv4 = ipaddress.ip_network("172.18.0.0/24")
    assert net2_def.name == "network-2"
    assert net2_def.ipv4_network == net2_ip_netv4
    assert not net2_def.ipv6_network
    assert net2_def.mtu == 1496
    assert net2_def.vlan == 21
    assert net2_def.metallb_config
    assert net2_def.netconfig_config
    assert not net2_def.multus_config
    assert len(net2_def.netconfig_config.ranges_ipv4) == 2
    assert not net2_def.netconfig_config.ranges_ipv6
    assert len(net2_def.metallb_config.ranges_ipv4) == 1
    assert not net2_def.metallb_config.ranges_ipv6

    # Simple basic checks of network-3
    net3_def = test_net_1.networks["network-3"]
    net3_ip_netv6 = ipaddress.ip_network("fd42:add0:b7d2:09b1::/64")
    assert net3_def.name == "network-3"
    assert net3_def.ipv6_network == net3_ip_netv6
    assert not net3_def.ipv4_network
    assert net3_def.mtu == 1496
    assert net3_def.vlan == 20
    assert net3_def.metallb_config
    assert net3_def.netconfig_config
    assert net3_def.multus_config
    assert len(net3_def.multus_config.ranges_ipv6) == 1
    assert not net3_def.multus_config.ranges_ipv4
    assert len(net3_def.netconfig_config.ranges_ipv6) == 2
    assert not net3_def.netconfig_config.ranges_ipv4
    assert len(net3_def.metallb_config.ranges_ipv6) == 1
    assert not net3_def.metallb_config.ranges_ipv4

    # Simple basic checks of network-4
    net4_def = test_net_1.networks["network-4"]
    net4_ip_netv4 = ipaddress.ip_network("172.19.0.0/24")
    net4_ip_netv6 = ipaddress.ip_network("fd5e:bdb2:6091:9306::/64")
    assert net4_def.name == "network-4"
    assert net4_def.ipv6_network == net4_ip_netv6
    assert net4_def.ipv4_network == net4_ip_netv4
    assert not net4_def.mtu
    assert net4_def.vlan == 22
    assert net4_def.metallb_config
    assert net4_def.netconfig_config
    assert net4_def.multus_config
    assert len(net4_def.multus_config.ranges_ipv6) == 1
    assert len(net4_def.multus_config.ranges_ipv4) == 1
    assert len(net4_def.netconfig_config.ranges_ipv6) == 1
    assert len(net4_def.netconfig_config.ranges_ipv4) == 2
    assert len(net4_def.metallb_config.ranges_ipv6) == 1
    assert len(net4_def.metallb_config.ranges_ipv4) == 1

    # Simple basic checks of the group template
    group1_def = test_net_1.group_templates["group-1"]
    assert group1_def.group_name == "group-1"
    assert group1_def.skip_nm_configuration is None
    assert len(group1_def.networks) == 3
    assert "network-2" in group1_def.networks
    assert "network-3" in group1_def.networks
    assert "network-4" in group1_def.networks
    group1_net2_def = group1_def.networks["network-2"]
    assert group1_net2_def.ipv4_range
    assert not group1_net2_def.ipv6_range

    group1_net3_def = group1_def.networks["network-3"]
    assert group1_net3_def.ipv6_range
    assert not group1_net3_def.ipv4_range

    group1_net4_def = group1_def.networks["network-4"]
    assert group1_net4_def.ipv6_range
    assert group1_net4_def.ipv4_range

    # Simple basic checks of the explicit instance
    instance1_def = test_net_1.instances["instance-1"]
    assert instance1_def.name == "instance-1"
    assert instance1_def.skip_nm_configuration is None
    assert len(instance1_def.networks) == 2
    assert "network-3" in instance1_def.networks
    assert "network-4" in instance1_def.networks
    instance1_net1_def = instance1_def.networks["network-3"]
    assert instance1_net1_def.ipv6
    assert not instance1_net1_def.ipv4
    instance1_net3_def = instance1_def.networks["network-4"]
    assert not instance1_net3_def.ipv6
    assert instance1_net3_def.ipv4


def test_networking_definition_load_networking_definition_all_tools_ipv6_only_ok():
    raw_definition_1 = net_map_stub_data.get_test_file_yaml_content(
        "networking-definition-valid-all-tools-ipv6-only.yml"
    )
    test_net_1 = networking_definition.NetworkingDefinition(raw_definition_1)
    assert test_net_1
    assert len(test_net_1.networks) == 4
    assert len(test_net_1.group_templates) == 3
    assert len(test_net_1.instances) == 1

    # Check that the expected networks are in
    assert all(
        net_name in test_net_1.networks
        for net_name in ("network-1", "network-2", "network-3", "network-4")
    )
    assert "group-1" in test_net_1.group_templates
    assert "instance-1" in test_net_1.instances

    # Simple basic checks of network-1
    net1_def = test_net_1.networks["network-1"]
    net1_ip_netv6 = ipaddress.ip_network("fdc0:8b54:108a:c949::/64")
    assert net1_def.name == "network-1"
    assert not net1_def.ipv4_network
    assert net1_def.ipv6_network == net1_ip_netv6
    assert net1_def.mtu == 1500
    assert not net1_def.vlan
    assert net1_def.metallb_config
    assert net1_def.multus_config
    assert net1_def.netconfig_config
    assert not net1_def.multus_config.ranges_ipv4
    assert not net1_def.metallb_config.ranges_ipv4
    assert not net1_def.netconfig_config.ranges_ipv4
    assert len(net1_def.multus_config.ranges_ipv6) == 1
    assert len(net1_def.netconfig_config.ranges_ipv6) == 2
    assert len(net1_def.metallb_config.ranges_ipv6) == 1

    # Simple basic checks of network-2
    net2_def = test_net_1.networks["network-2"]
    net2_ip_netv6 = ipaddress.ip_network("fd5e:bdb2:6091:9306::/64")
    assert net2_def.name == "network-2"
    assert net2_def.ipv6_network == net2_ip_netv6
    assert not net2_def.ipv4_network
    assert net2_def.vlan == 21
    assert net2_def.metallb_config
    assert net2_def.netconfig_config
    assert not net2_def.multus_config
    assert not net2_def.netconfig_config.ranges_ipv4
    assert not net2_def.metallb_config.ranges_ipv4
    assert len(net2_def.netconfig_config.ranges_ipv6) == 1
    assert len(net2_def.metallb_config.ranges_ipv6) == 1

    # Simple basic checks of network-3
    net3_def = test_net_1.networks["network-3"]
    net3_ip_netv6 = ipaddress.ip_network("fd42:add0:b7d2:09b1::/64")
    assert net3_def.name == "network-3"
    assert net3_def.ipv6_network == net3_ip_netv6
    assert not net3_def.ipv4_network
    assert net3_def.mtu == 1496
    assert net3_def.vlan == 20
    assert net3_def.metallb_config
    assert net3_def.netconfig_config
    assert net3_def.multus_config
    assert not net3_def.multus_config.ranges_ipv4
    assert not net3_def.netconfig_config.ranges_ipv4
    assert not net3_def.metallb_config.ranges_ipv4
    assert len(net3_def.multus_config.ranges_ipv6) == 1
    assert len(net3_def.netconfig_config.ranges_ipv6) == 1
    assert len(net3_def.metallb_config.ranges_ipv6) == 1

    # Simple basic checks of network-4
    net4_def = test_net_1.networks["network-4"]
    net4_ip_netv6 = ipaddress.ip_network("fd98:6d1a:86e7:d5e5::/64")
    assert net4_def.name == "network-4"
    assert net4_def.ipv6_network == net4_ip_netv6
    assert not net4_def.ipv4_network
    assert not net4_def.mtu
    assert net4_def.vlan == 22
    assert not net4_def.metallb_config
    assert not net4_def.netconfig_config
    assert not net4_def.multus_config

    # Simple basic checks of the group templates
    group1_def = test_net_1.group_templates["group-1"]
    assert group1_def.group_name == "group-1"
    assert group1_def.skip_nm_configuration is None
    assert len(group1_def.networks) == 1
    assert "network-1" in group1_def.networks

    group1_net1_def = group1_def.networks["network-1"]
    assert group1_net1_def.ipv6_range
    assert not group1_net1_def.ipv4_range

    group2_def = test_net_1.group_templates["group-2"]
    group1_net2_def = group2_def.networks["network-2"]
    assert group1_net2_def.ipv6_range
    assert not group1_net2_def.ipv4_range

    group3_def = test_net_1.group_templates["group-3"]
    group3_net3_def = group3_def.networks["network-3"]
    group3_net4_def = group3_def.networks["network-3"]
    assert group3_net3_def.ipv6_range
    assert not group3_net3_def.ipv4_range
    assert group3_net4_def.ipv6_range
    assert not group3_net4_def.ipv4_range

    # Simple basic checks of the explicit instance
    instance1_def = test_net_1.instances["instance-1"]
    assert instance1_def.name == "instance-1"
    assert instance1_def.skip_nm_configuration is None
    assert len(instance1_def.networks) == 2
    assert "network-1" in instance1_def.networks
    assert "network-3" in instance1_def.networks
    instance1_net1_def = instance1_def.networks["network-1"]
    assert instance1_net1_def.ipv6
    assert not instance1_net1_def.ipv4
    instance1_net3_def = instance1_def.networks["network-3"]
    assert instance1_net3_def.ipv6
    assert not instance1_net3_def.ipv4
