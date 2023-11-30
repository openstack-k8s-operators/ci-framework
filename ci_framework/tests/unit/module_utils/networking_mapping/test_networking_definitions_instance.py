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


def test_instance_definition_parse_networks_no_tools_v4_ok():
    networks_definitions = (
        networking_mapping_stub_data.build_valid_network_definition_set()
    )
    instance_name = "instance-3"
    first_net = list(networks_definitions.values())[0]
    second_net = list(networks_definitions.values())[1]
    third_net = list(networks_definitions.values())[2]
    instance_definition_raw = {
        "skip-nm-configuration": True,
        "networks": {
            first_net.name: {
                "ip": networking_mapping_stub_data.NETWORK_1_IPV4_NET[18],
                "skip-nm-configuration": True,
            },
            second_net.name: {"skip-nm-configuration": True},
            third_net.name: {},
        },
    }
    instance_definition = networking_definition.InstanceDefinition(
        instance_name, instance_definition_raw, networks_definitions
    )

    assert hash(instance_definition)
    assert instance_definition.skip_nm_configuration
    assert instance_definition.name == instance_name
    assert isinstance(instance_definition.networks, dict)
    assert len(instance_definition.networks) == len(instance_definition_raw["networks"])

    # Ensure nets were parsed
    assert networking_mapping_stub_data.NETWORK_1_NAME in instance_definition.networks
    assert networking_mapping_stub_data.NETWORK_2_NAME in instance_definition.networks
    assert networking_mapping_stub_data.NETWORK_3_NAME in instance_definition.networks

    # Ensure each parsed net has the proper values
    instance_definition_net_1 = instance_definition.networks[first_net.name]
    assert first_net == instance_definition_net_1.network
    assert instance_definition_net_1.skip_nm_configuration
    assert instance_definition_net_1.ipv4 == ipaddress.ip_address("192.168.122.18")
    assert instance_definition_net_1.ipv6 is None

    instance_definition_net_2 = instance_definition.networks[second_net.name]
    assert second_net == instance_definition_net_2.network
    assert instance_definition_net_2.skip_nm_configuration
    assert instance_definition_net_2.ipv4 is None
    assert instance_definition_net_2.ipv6 is None

    group_template_net_3 = instance_definition.networks[third_net.name]
    assert third_net == group_template_net_3.network
    assert not group_template_net_3.skip_nm_configuration
    assert group_template_net_3.ipv4 is None
    assert group_template_net_3.ipv6 is None


def test_instance_definition_parse_networks_no_tools_v6_ok():
    networks_definitions = (
        networking_mapping_stub_data.build_valid_network_definition_set(
            use_ipv6=True, use_ipv4=True
        )
    )
    instance_name = "instance-3"
    first_net = list(networks_definitions.values())[0]
    second_net = list(networks_definitions.values())[1]
    third_net = list(networks_definitions.values())[2]
    instance_definition_raw = {
        "skip-nm-configuration": True,
        "networks": {
            first_net.name: {
                "ip": networking_mapping_stub_data.NETWORK_1_IPV6_NET[77],
                "skip-nm-configuration": True,
            },
            second_net.name: {"skip-nm-configuration": True},
            third_net.name: {
                "ip-v6": networking_mapping_stub_data.NETWORK_3_IPV6_NET[100],
            },
        },
    }
    instance_definition = networking_definition.InstanceDefinition(
        instance_name, instance_definition_raw, networks_definitions
    )

    assert hash(instance_definition)
    assert instance_definition.skip_nm_configuration
    assert instance_definition.name == instance_name
    assert isinstance(instance_definition.networks, dict)
    assert len(instance_definition.networks) == len(instance_definition_raw["networks"])

    # Ensure nets were parsed
    assert networking_mapping_stub_data.NETWORK_1_NAME in instance_definition.networks
    assert networking_mapping_stub_data.NETWORK_2_NAME in instance_definition.networks
    assert networking_mapping_stub_data.NETWORK_3_NAME in instance_definition.networks

    # Ensure each parsed net has the proper values
    instance_definition_net_1 = instance_definition.networks[first_net.name]
    assert first_net == instance_definition_net_1.network
    assert instance_definition_net_1.skip_nm_configuration
    assert (
        instance_definition_net_1.ipv6
        == networking_mapping_stub_data.NETWORK_1_IPV6_NET[77]
    )
    assert instance_definition_net_1.ipv4 is None

    instance_definition_net_2 = instance_definition.networks[second_net.name]
    assert second_net == instance_definition_net_2.network
    assert instance_definition_net_2.skip_nm_configuration
    assert instance_definition_net_2.ipv4 is None
    assert instance_definition_net_2.ipv6 is None

    group_template_net_3 = instance_definition.networks[third_net.name]
    assert third_net == group_template_net_3.network
    assert not group_template_net_3.skip_nm_configuration
    assert (
        group_template_net_3.ipv6
        == networking_mapping_stub_data.NETWORK_3_IPV6_NET[100]
    )
    assert group_template_net_3.ipv4 is None


def test_instance_definition_parse_networks_no_tools_mixed_ok():
    networks_definitions = (
        networking_mapping_stub_data.build_valid_network_definition_set(
            use_ipv6=True, use_ipv4=True, mixed_ip_versions=True
        )
    )
    instance_name = "instance-3"
    first_net = list(networks_definitions.values())[0]
    second_net = list(networks_definitions.values())[1]
    third_net = list(networks_definitions.values())[2]
    instance_definition_raw = {
        "skip-nm-configuration": True,
        "networks": {
            networking_mapping_stub_data.NETWORK_1_NAME: {
                "ip": networking_mapping_stub_data.NETWORK_1_IPV4_NET[77],
                "skip-nm-configuration": True,
            },
            networking_mapping_stub_data.NETWORK_2_NAME: {
                "skip-nm-configuration": True,
                "ip-v4": networking_mapping_stub_data.NETWORK_2_IPV4_NET[77],
                "ip-v6": networking_mapping_stub_data.NETWORK_2_IPV6_NET[77],
            },
            networking_mapping_stub_data.NETWORK_3_NAME: {
                "ip-v6": networking_mapping_stub_data.NETWORK_3_IPV6_NET[77],
            },
        },
    }
    instance_definition = networking_definition.InstanceDefinition(
        instance_name, instance_definition_raw, networks_definitions
    )

    assert hash(instance_definition)
    assert instance_definition.skip_nm_configuration
    assert instance_definition.name == instance_name
    assert isinstance(instance_definition.networks, dict)
    assert len(instance_definition.networks) == len(instance_definition_raw["networks"])

    # Ensure nets were parsed
    assert networking_mapping_stub_data.NETWORK_1_NAME in instance_definition.networks
    assert networking_mapping_stub_data.NETWORK_2_NAME in instance_definition.networks
    assert networking_mapping_stub_data.NETWORK_3_NAME in instance_definition.networks

    # Ensure each parsed net has the proper values
    instance_definition_net_1 = instance_definition.networks[
        networking_mapping_stub_data.NETWORK_1_NAME
    ]
    assert first_net == instance_definition_net_1.network
    assert instance_definition_net_1.skip_nm_configuration
    assert (
        instance_definition_net_1.ipv4
        == networking_mapping_stub_data.NETWORK_1_IPV4_NET[77]
    )
    assert instance_definition_net_1.ipv6 is None

    instance_definition_net_2 = instance_definition.networks[
        networking_mapping_stub_data.NETWORK_2_NAME
    ]
    assert second_net == instance_definition_net_2.network
    assert instance_definition_net_2.skip_nm_configuration
    assert (
        instance_definition_net_2.ipv4
        == networking_mapping_stub_data.NETWORK_2_IPV4_NET[77]
    )
    assert (
        instance_definition_net_2.ipv6
        == networking_mapping_stub_data.NETWORK_2_IPV6_NET[77]
    )

    group_template_net_3 = instance_definition.networks[
        networking_mapping_stub_data.NETWORK_3_NAME
    ]
    assert third_net == group_template_net_3.network
    assert not group_template_net_3.skip_nm_configuration
    assert group_template_net_3.ipv4 is None
    assert (
        group_template_net_3.ipv6 == networking_mapping_stub_data.NETWORK_3_IPV6_NET[77]
    )


def test_instance_definition_parse_invalid_ip_fail():
    networks_definitions = (
        networking_mapping_stub_data.build_valid_network_definition_set()
    )
    instance_name = "instance-3"
    first_net = list(networks_definitions.values())[0]
    wrong_ips = ["192.168.123.18", "192.168.123.1A"]
    for wrong_ip in wrong_ips:
        instance_definition_raw = {
            "skip-nm-configuration": True,
            "networks": {
                first_net.name: {"ip": wrong_ip},
            },
        }
        with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
            networking_definition.InstanceDefinition(
                instance_name, instance_definition_raw, networks_definitions
            )
        assert exc_info.value.field == "ip"
        assert exc_info.value.invalid_value == wrong_ip


def test_instance_definition_parse_invalid_net_fail():
    instance_definition_raw = {
        "networks": {
            "does-not-exist-net": {"ip": "192.168.122.100"},
        },
    }
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.InstanceDefinition(
            "instance-3",
            instance_definition_raw,
            networking_mapping_stub_data.build_valid_network_definition_set(),
        )
    assert exc_info.value.invalid_value == "does-not-exist-net"
    assert "non-existing network " in str(exc_info.value)


def test_instance_definition_parse_invalid_ip_version_fail():
    stub_networks_definitions = (
        networking_mapping_stub_data.build_valid_network_definition_set(
            use_ipv6=True, use_ipv4=True, mixed_ip_versions=True
        )
    )

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.InstanceDefinition(
            "instance-3",
            {
                "networks": {
                    networking_mapping_stub_data.NETWORK_1_NAME: {
                        "ip": str(networking_mapping_stub_data.NETWORK_1_IPV6_NET[50])
                    },
                },
            },
            stub_networks_definitions,
        )
    assert exc_info.value.invalid_value == str(
        networking_mapping_stub_data.NETWORK_1_IPV6_NET[50]
    )
    assert networking_mapping_stub_data.NETWORK_1_NAME in str(exc_info.value)
    assert exc_info.value.field == "ip"
    assert "not configured to use ipv6" in str(exc_info.value).lower()

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.InstanceDefinition(
            "instance-3",
            {
                "networks": {
                    networking_mapping_stub_data.NETWORK_3_NAME: {
                        "ip": str(networking_mapping_stub_data.NETWORK_3_IPV4_NET[50])
                    },
                },
            },
            stub_networks_definitions,
        )
    assert exc_info.value.invalid_value == str(
        networking_mapping_stub_data.NETWORK_3_IPV4_NET[50]
    )
    assert networking_mapping_stub_data.NETWORK_3_NAME in str(exc_info.value)
    assert exc_info.value.field == "ip"
    assert "not configured to use ipv4" in str(exc_info.value).lower()

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.InstanceDefinition(
            "instance-3",
            {
                "networks": {
                    networking_mapping_stub_data.NETWORK_3_NAME: {
                        "ip-v6": str(
                            networking_mapping_stub_data.NETWORK_3_IPV4_NET[50]
                        )
                    },
                },
            },
            stub_networks_definitions,
        )
    assert exc_info.value.invalid_value == str(
        networking_mapping_stub_data.NETWORK_3_IPV4_NET[50]
    )
    assert exc_info.value.field == "ip-v6"
    assert "should be a ipv6" in str(exc_info.value).lower()

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.InstanceDefinition(
            "instance-3",
            {
                "networks": {
                    networking_mapping_stub_data.NETWORK_1_NAME: {
                        "ip-v4": str(
                            networking_mapping_stub_data.NETWORK_1_IPV6_NET[50]
                        )
                    },
                },
            },
            stub_networks_definitions,
        )
    assert exc_info.value.invalid_value == str(
        networking_mapping_stub_data.NETWORK_1_IPV6_NET[50]
    )
    assert exc_info.value.field == "ip-v4"
    assert "should be a ipv4" in str(exc_info.value).lower()
