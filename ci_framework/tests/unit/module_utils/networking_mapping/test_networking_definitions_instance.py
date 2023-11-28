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


def test_instance_definition_parse_networks_no_tools_ok():
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
            first_net.name: {"ip": "192.168.122.18", "skip-nm-configuration": True},
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
    assert first_net.name in instance_definition.networks
    assert second_net.name in instance_definition.networks

    # Ensure each parsed net has the proper values
    instance_definition_net_1 = instance_definition.networks[first_net.name]
    assert first_net == instance_definition_net_1.network
    assert instance_definition_net_1.skip_nm_configuration
    assert instance_definition_net_1.ip == ipaddress.ip_address("192.168.122.18")

    instance_definition_net_2 = instance_definition.networks[second_net.name]
    assert second_net == instance_definition_net_2.network
    assert instance_definition_net_2.skip_nm_configuration
    assert instance_definition_net_2.ip is None

    group_template_net_3 = instance_definition.networks[third_net.name]
    assert third_net == group_template_net_3.network
    assert not group_template_net_3.skip_nm_configuration
    assert group_template_net_3.ip is None


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
