from __future__ import absolute_import, division, print_function

__metaclass__ = type

import typing

import pytest
from ansible_collections.cifmw.general.plugins.module_utils.net_map import (
    exceptions,
    networking_definition,
)
from ansible_collections.cifmw.general.tests.unit.module_utils.test_utils import (
    net_map_stub_data,
)


def test_group_template_definition_parse_simple_ok():
    networks_definitions = net_map_stub_data.build_valid_network_definition_set()
    inventory_group = "instances-group-1"
    group_template_definition_raw = {}
    group_template_definition = networking_definition.GroupTemplateDefinition(
        inventory_group, group_template_definition_raw, networks_definitions
    )
    assert not group_template_definition.skip_nm_configuration
    assert group_template_definition.group_name == inventory_group
    assert isinstance(group_template_definition.networks, dict)


def __generate_validate_base_group_template(
    networks_definitions, raw_definition: typing.Dict[str, typing.Any] = None
):
    inventory_group = "instances-group-1"
    group_template_definition_raw = (
        {
            "skip-nm-configuration": True,
            "networks": {
                net_map_stub_data.NETWORK_1_NAME: {
                    "range": {"start": 100, "length": 30}
                },
                net_map_stub_data.NETWORK_2_NAME: {
                    "range": {"start": 150, "length": 60},
                    "skip-nm-configuration": True,
                },
                net_map_stub_data.NETWORK_3_NAME: {},
            },
        }
        if not raw_definition
        else raw_definition
    )
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
    assert net_map_stub_data.NETWORK_1_NAME in group_template_definition.networks
    assert net_map_stub_data.NETWORK_2_NAME in group_template_definition.networks
    assert net_map_stub_data.NETWORK_3_NAME in group_template_definition.networks
    return group_template_definition


def test_group_template_definition_parse_networks_v4_ok():
    stub_networks_definitions = net_map_stub_data.build_valid_network_definition_set(
        use_ipv4=True, use_ipv6=False
    )

    group_template_definition = __generate_validate_base_group_template(
        stub_networks_definitions
    )

    # Ensure each parsed net has the proper values
    group_template_net_1 = group_template_definition.networks[
        net_map_stub_data.NETWORK_1_NAME
    ]
    assert (
        stub_networks_definitions[net_map_stub_data.NETWORK_1_NAME]
        == group_template_net_1.network
    )
    assert not group_template_net_1.skip_nm_configuration
    assert group_template_net_1.ipv4_range == networking_definition.HostNetworkRange(
        group_template_net_1.network.ipv4_network, start=100, length=30
    )
    assert group_template_net_1.ipv6_range is None

    group_template_net_2 = group_template_definition.networks[
        net_map_stub_data.NETWORK_2_NAME
    ]
    assert (
        stub_networks_definitions[net_map_stub_data.NETWORK_2_NAME]
        == group_template_net_2.network
    )
    assert group_template_net_2.skip_nm_configuration
    assert group_template_net_2.ipv4_range == networking_definition.HostNetworkRange(
        group_template_net_2.network.ipv4_network, start=150, length=60
    )
    assert group_template_net_2.ipv6_range is None

    group_template_net_3 = group_template_definition.networks[
        net_map_stub_data.NETWORK_3_NAME
    ]
    assert (
        stub_networks_definitions[net_map_stub_data.NETWORK_3_NAME]
        == group_template_net_3.network
    )
    assert not group_template_net_3.skip_nm_configuration
    assert group_template_net_3.ipv4_range is None
    assert group_template_net_3.ipv6_range is None


def test_group_template_definition_parse_networks_v6_ok():
    stub_networks_definitions = net_map_stub_data.build_valid_network_definition_set(
        use_ipv4=False, use_ipv6=True
    )

    group_template_definition = __generate_validate_base_group_template(
        stub_networks_definitions
    )

    # Ensure each parsed net has the proper values
    group_template_net_1 = group_template_definition.networks[
        net_map_stub_data.NETWORK_1_NAME
    ]
    assert (
        stub_networks_definitions[net_map_stub_data.NETWORK_1_NAME]
        == group_template_net_1.network
    )
    assert not group_template_net_1.skip_nm_configuration
    assert group_template_net_1.ipv6_range == networking_definition.HostNetworkRange(
        group_template_net_1.network.ipv6_network, start=100, length=30
    )
    assert group_template_net_1.ipv4_range is None

    group_template_net_2 = group_template_definition.networks[
        net_map_stub_data.NETWORK_2_NAME
    ]
    assert (
        stub_networks_definitions[net_map_stub_data.NETWORK_2_NAME]
        == group_template_net_2.network
    )
    assert group_template_net_2.skip_nm_configuration
    assert group_template_net_2.ipv6_range == networking_definition.HostNetworkRange(
        group_template_net_2.network.ipv6_network, start=150, length=60
    )
    assert group_template_net_2.ipv4_range is None

    group_template_net_3 = group_template_definition.networks[
        net_map_stub_data.NETWORK_3_NAME
    ]
    assert (
        stub_networks_definitions[net_map_stub_data.NETWORK_3_NAME]
        == group_template_net_3.network
    )
    assert not group_template_net_3.skip_nm_configuration
    assert group_template_net_3.ipv4_range is None
    assert group_template_net_3.ipv6_range is None


def test_group_template_definition_parse_networks_mixed_ok():
    stub_networks_definitions = net_map_stub_data.build_valid_network_definition_set(
        use_ipv4=True, use_ipv6=True, mixed_ip_versions=True
    )

    group_template_definition_raw = {
        "skip-nm-configuration": True,
        "networks": {
            net_map_stub_data.NETWORK_1_NAME: {"range": {"start": 100, "length": 30}},
            net_map_stub_data.NETWORK_2_NAME: {
                "range-v4": {"start": 150, "length": 60},
                "range-v6": {"start": 150, "length": 2048},
                "skip-nm-configuration": True,
            },
            net_map_stub_data.NETWORK_3_NAME: {
                "range-v6": {"start": 150, "length": 60}
            },
        },
    }

    group_template_definition = __generate_validate_base_group_template(
        stub_networks_definitions, raw_definition=group_template_definition_raw
    )

    # Ensure each parsed net has the proper values
    group_template_net_1 = group_template_definition.networks[
        net_map_stub_data.NETWORK_1_NAME
    ]
    assert (
        stub_networks_definitions[net_map_stub_data.NETWORK_1_NAME]
        == group_template_net_1.network
    )
    assert not group_template_net_1.skip_nm_configuration
    assert group_template_net_1.ipv4_range == networking_definition.HostNetworkRange(
        group_template_net_1.network.ipv4_network, start=100, length=30
    )
    assert group_template_net_1.ipv6_range is None

    group_template_net_2 = group_template_definition.networks[
        net_map_stub_data.NETWORK_2_NAME
    ]
    assert (
        stub_networks_definitions[net_map_stub_data.NETWORK_2_NAME]
        == group_template_net_2.network
    )
    assert group_template_net_2.skip_nm_configuration
    assert group_template_net_2.ipv6_range == networking_definition.HostNetworkRange(
        group_template_net_2.network.ipv6_network, start=150, length=2048
    )
    assert group_template_net_2.ipv4_range == networking_definition.HostNetworkRange(
        group_template_net_2.network.ipv4_network, start=150, length=60
    )

    group_template_net_3 = group_template_definition.networks[
        net_map_stub_data.NETWORK_3_NAME
    ]
    assert (
        stub_networks_definitions[net_map_stub_data.NETWORK_3_NAME]
        == group_template_net_3.network
    )
    assert not group_template_net_3.skip_nm_configuration
    assert group_template_net_3.ipv6_range == networking_definition.HostNetworkRange(
        group_template_net_3.network.ipv6_network, start=150, length=60
    )
    assert not group_template_net_3.ipv4_range


def test_group_template_definition_parse_invalid_range_fail():
    networks_definitions = net_map_stub_data.build_valid_network_definition_set()
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
            net_map_stub_data.build_valid_network_definition_set(),
        )
    assert exc_info.value.invalid_value == "does-not-exist-net"
    assert "non-existing network " in str(exc_info.value)
