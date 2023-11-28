from __future__ import absolute_import, division, print_function

__metaclass__ = type

import ipaddress

import pytest
from ansible_collections.cifmw.general.plugins.module_utils.networking_mapping import (
    exceptions,
    networking_definition,
)

from ansible_collections.cifmw.general.tests.unit.module_utils.test_utils import (
    networking_mapping_stub_data,
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


def test_networking_definition_load_networking_definition_1_ok():
    raw_definition_1 = networking_mapping_stub_data.get_test_file_yaml_content(
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
    assert "crc" in test_net_1.group_templates
    assert "instance-1" in test_net_1.instances


def test_networking_definition_load_networking_definition_all_tools_ok():
    raw_definition_1 = networking_mapping_stub_data.get_test_file_yaml_content(
        "networking-definition-valid-all-tools.yml"
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
    assert "crc" in test_net_1.group_templates
    assert "instance-1" in test_net_1.instances

    for net_name, net_def in test_net_1.networks.items():
        assert net_def.multus_config
        assert len(net_def.multus_config.get_ranges()) == 1

        assert net_def.metallb_config
        assert len(net_def.metallb_config.get_ranges()) == 1

        assert net_def.netconfig_config
        assert len(net_def.netconfig_config.get_ranges()) == 2


def test_networking_definition_groups_network_template_ok():
    raw_definition_1 = networking_mapping_stub_data.get_test_file_yaml_content(
        "networking-definition-valid.yml"
    )
    test_net_1 = networking_definition.NetworkingDefinition(raw_definition_1)
    assert test_net_1
    raw_definition_2 = networking_mapping_stub_data.get_test_file_yaml_content(
        "networking-definition-valid-network-template.yml"
    )
    test_net_2 = networking_definition.NetworkingDefinition(raw_definition_2)
    # Both are equivalent, as the second is the "network-template" of
    # the first one
    assert test_net_2 == test_net_1
    # Check that both hashes are the same
    # Redundant, but serves as a test to check
    # that they properly implement __hash__
    assert hash(test_net_2) == hash(test_net_1)
