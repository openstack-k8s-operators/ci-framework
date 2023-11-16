from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from ansible_collections.cifmw.general.plugins.module_utils.networking_mapping import (
    exceptions,
    networking_definition,
)
from ansible_collections.cifmw.general.tests.unit.module_utils.test_utils import (
    networking_mapping_stub_data,
)


def test_group_template_definition_parse_simple_ok():
    networks_definitions = (
        networking_mapping_stub_data.build_valid_network_definition_set()
    )
    inventory_group = "instances-group-1"
    group_template_definition_raw = {}
    group_template_definition = networking_definition.GroupTemplateDefinition(
        inventory_group, group_template_definition_raw, networks_definitions
    )
    assert not group_template_definition.skip_nm_configuration
    assert group_template_definition.group_name == inventory_group
    assert isinstance(group_template_definition.networks, dict)


def test_group_template_definition_parse_networks_ok():
    networks_definitions = (
        networking_mapping_stub_data.build_valid_network_definition_set()
    )
    inventory_group = "instances-group-1"
    first_net = list(networks_definitions.values())[0]
    second_net = list(networks_definitions.values())[1]
    third_net = list(networks_definitions.values())[2]
    group_template_definition_raw = {
        "skip-nm-configuration": True,
        "networks": {
            first_net.name: {"range": {"start": 100, "length": 30}},
            second_net.name: {
                "range": {"start": 150, "length": 60},
                "skip-nm-configuration": True,
            },
            third_net.name: {},
        },
    }
    group_template_definition = networking_definition.GroupTemplateDefinition(
        inventory_group, group_template_definition_raw, networks_definitions
    )
    assert hash(group_template_definition)
    assert group_template_definition.skip_nm_configuration
    assert group_template_definition.group_name == inventory_group
    assert isinstance(group_template_definition.networks, dict)
    assert len(group_template_definition.networks) == len(
        group_template_definition_raw["networks"]
    )

    # Ensure nets were parsed
    assert first_net.name in group_template_definition.networks
    assert second_net.name in group_template_definition.networks

    # Ensure each parsed net has the proper values
    group_template_net_1 = group_template_definition.networks[first_net.name]
    assert first_net == group_template_net_1.network
    assert not group_template_net_1.skip_nm_configuration
    assert group_template_net_1.range == networking_definition.HostNetworkRange(
        group_template_net_1.network.network, start=100, length=30
    )

    group_template_net_2 = group_template_definition.networks[second_net.name]
    assert second_net == group_template_net_2.network
    assert group_template_net_2.skip_nm_configuration
    assert group_template_net_2.range == networking_definition.HostNetworkRange(
        group_template_net_2.network.network, start=150, length=60
    )

    group_template_net_3 = group_template_definition.networks[third_net.name]
    assert third_net == group_template_net_3.network
    assert not group_template_net_3.skip_nm_configuration
    assert group_template_net_3.range is None


def test_group_template_definition_parse_invalid_range_fail():
    networks_definitions = (
        networking_mapping_stub_data.build_valid_network_definition_set()
    )
    inventory_group = "instances-group-1"
    first_net = list(networks_definitions.values())[0]

    # Test invalid start value
    group_template_definition_raw = {
        "networks": {
            first_net.name: {"range": {"start": -1, "length": 30}},
        },
    }

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.GroupTemplateDefinition(
            inventory_group, group_template_definition_raw, networks_definitions
        )
    assert exc_info.value.field == "start"
    assert exc_info.value.invalid_value == -1

    # Test invalid length value
    group_template_definition_raw = {
        "networks": {
            first_net.name: {"range": {"start": 10, "length": 0}},
        },
    }

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.GroupTemplateDefinition(
            inventory_group, group_template_definition_raw, networks_definitions
        )
    assert exc_info.value.field == "length"
    assert exc_info.value.invalid_value == 0


def test_group_template_definition_parse_invalid_net_fail():
    # Test invalid start value
    group_template_definition_raw = {
        "networks": {
            "does-not-exist-net": {"range": {"start": -1, "length": 30}},
        },
    }

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.GroupTemplateDefinition(
            "instances-group-1",
            group_template_definition_raw,
            networking_mapping_stub_data.build_valid_network_definition_set(),
        )
    assert exc_info.value.invalid_value == "does-not-exist-net"
    assert "non-existing network " in str(exc_info.value)
