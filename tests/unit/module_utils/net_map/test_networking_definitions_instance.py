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


def test_instance_definition_parse_networks_no_tools_v4_ok():
    networks_definitions = net_map_stub_data.build_valid_network_definition_set()
    instance_name = "instance-3"
    first_net = list(networks_definitions.values())[0]
    second_net = list(networks_definitions.values())[1]
    third_net = list(networks_definitions.values())[2]
    instance_definition_raw = {
        "networks": {
            first_net.name: {
                "ip": net_map_stub_data.NETWORK_1_IPV4_NET[18],
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
    assert instance_definition.skip_nm_configuration is None
    assert instance_definition.name == instance_name
    assert isinstance(instance_definition.networks, dict)
    assert len(instance_definition.networks) == len(instance_definition_raw["networks"])

    # Ensure nets were parsed
    assert net_map_stub_data.NETWORK_1_NAME in instance_definition.networks
    assert net_map_stub_data.NETWORK_2_NAME in instance_definition.networks
    assert net_map_stub_data.NETWORK_3_NAME in instance_definition.networks

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
    assert group_template_net_3.skip_nm_configuration is None
    assert group_template_net_3.ipv4 is None
    assert group_template_net_3.ipv6 is None


def test_instance_definition_parse_networks_no_tools_v6_ok():
    networks_definitions = net_map_stub_data.build_valid_network_definition_set(
        use_ipv6=True, use_ipv4=True
    )
    instance_name = "instance-3"
    first_net = list(networks_definitions.values())[0]
    second_net = list(networks_definitions.values())[1]
    third_net = list(networks_definitions.values())[2]
    instance_definition_raw = {
        "skip-nm-configuration": False,
        "networks": {
            first_net.name: {
                "ip": net_map_stub_data.NETWORK_1_IPV6_NET[77],
                "skip-nm-configuration": True,
            },
            second_net.name: {"skip-nm-configuration": True},
            third_net.name: {
                "ip-v6": net_map_stub_data.NETWORK_3_IPV6_NET[100],
            },
        },
    }
    instance_definition = networking_definition.InstanceDefinition(
        instance_name, instance_definition_raw, networks_definitions
    )

    assert hash(instance_definition)
    assert instance_definition.skip_nm_configuration is False
    assert instance_definition.name == instance_name
    assert isinstance(instance_definition.networks, dict)
    assert len(instance_definition.networks) == len(instance_definition_raw["networks"])

    # Ensure nets were parsed
    assert net_map_stub_data.NETWORK_1_NAME in instance_definition.networks
    assert net_map_stub_data.NETWORK_2_NAME in instance_definition.networks
    assert net_map_stub_data.NETWORK_3_NAME in instance_definition.networks

    # Ensure each parsed net has the proper values
    instance_definition_net_1 = instance_definition.networks[first_net.name]
    assert first_net == instance_definition_net_1.network
    assert instance_definition_net_1.skip_nm_configuration
    assert instance_definition_net_1.ipv6 == net_map_stub_data.NETWORK_1_IPV6_NET[77]
    assert instance_definition_net_1.ipv4 is None

    instance_definition_net_2 = instance_definition.networks[second_net.name]
    assert second_net == instance_definition_net_2.network
    assert instance_definition_net_2.skip_nm_configuration
    assert instance_definition_net_2.ipv4 is None
    assert instance_definition_net_2.ipv6 is None

    group_template_net_3 = instance_definition.networks[third_net.name]
    assert third_net == group_template_net_3.network
    assert group_template_net_3.skip_nm_configuration is None
    assert group_template_net_3.ipv6 == net_map_stub_data.NETWORK_3_IPV6_NET[100]
    assert group_template_net_3.ipv4 is None


def test_instance_definition_parse_networks_no_tools_mixed_ok():
    networks_definitions = net_map_stub_data.build_valid_network_definition_set(
        use_ipv6=True, use_ipv4=True, mixed_ip_versions=True
    )
    instance_name = "instance-3"
    first_net = list(networks_definitions.values())[0]
    second_net = list(networks_definitions.values())[1]
    third_net = list(networks_definitions.values())[2]
    instance_definition_raw = {
        "skip-nm-configuration": True,
        "networks": {
            net_map_stub_data.NETWORK_1_NAME: {
                "ip": net_map_stub_data.NETWORK_1_IPV4_NET[77],
                "skip-nm-configuration": True,
            },
            net_map_stub_data.NETWORK_2_NAME: {
                "skip-nm-configuration": False,
                "ip-v4": net_map_stub_data.NETWORK_2_IPV4_NET[77],
                "ip-v6": net_map_stub_data.NETWORK_2_IPV6_NET[77],
            },
            net_map_stub_data.NETWORK_3_NAME: {
                "ip-v6": net_map_stub_data.NETWORK_3_IPV6_NET[77],
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
    assert net_map_stub_data.NETWORK_1_NAME in instance_definition.networks
    assert net_map_stub_data.NETWORK_2_NAME in instance_definition.networks
    assert net_map_stub_data.NETWORK_3_NAME in instance_definition.networks

    # Ensure each parsed net has the proper values
    instance_definition_net_1 = instance_definition.networks[
        net_map_stub_data.NETWORK_1_NAME
    ]
    assert first_net == instance_definition_net_1.network
    assert instance_definition_net_1.skip_nm_configuration
    assert instance_definition_net_1.ipv4 == net_map_stub_data.NETWORK_1_IPV4_NET[77]
    assert instance_definition_net_1.ipv6 is None

    instance_definition_net_2 = instance_definition.networks[
        net_map_stub_data.NETWORK_2_NAME
    ]
    assert second_net == instance_definition_net_2.network
    assert instance_definition_net_2.skip_nm_configuration is False
    assert instance_definition_net_2.ipv4 == net_map_stub_data.NETWORK_2_IPV4_NET[77]
    assert instance_definition_net_2.ipv6 == net_map_stub_data.NETWORK_2_IPV6_NET[77]

    group_template_net_3 = instance_definition.networks[
        net_map_stub_data.NETWORK_3_NAME
    ]
    assert third_net == group_template_net_3.network
    assert group_template_net_3.skip_nm_configuration is None
    assert group_template_net_3.ipv4 is None
    assert group_template_net_3.ipv6 == net_map_stub_data.NETWORK_3_IPV6_NET[77]


def test_instance_definition_parse_invalid_ip_fail():
    networks_definitions = net_map_stub_data.build_valid_network_definition_set()
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
            net_map_stub_data.build_valid_network_definition_set(),
        )
    assert exc_info.value.invalid_value == "does-not-exist-net"
    assert "non-existing network " in str(exc_info.value)


def test_instance_definition_parse_invalid_ip_version_fail():
    stub_networks_definitions = net_map_stub_data.build_valid_network_definition_set(
        use_ipv6=True, use_ipv4=True, mixed_ip_versions=True
    )

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.InstanceDefinition(
            "instance-3",
            {
                "networks": {
                    net_map_stub_data.NETWORK_1_NAME: {
                        "ip": str(net_map_stub_data.NETWORK_1_IPV6_NET[50])
                    },
                },
            },
            stub_networks_definitions,
        )
    assert exc_info.value.invalid_value == str(net_map_stub_data.NETWORK_1_IPV6_NET[50])
    assert str(net_map_stub_data.NETWORK_1_IPV4_NET) in str(exc_info.value)
    assert exc_info.value.field == "ip"
    assert exc_info.value.parent_type == "instance"
    assert exc_info.value.parent_name == "instance-3"
    assert "version v6" in str(exc_info.value).lower()

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.InstanceDefinition(
            "instance-3",
            {
                "networks": {
                    net_map_stub_data.NETWORK_3_NAME: {
                        "ip": str(net_map_stub_data.NETWORK_3_IPV4_NET[50])
                    },
                },
            },
            stub_networks_definitions,
        )
    assert exc_info.value.invalid_value == str(net_map_stub_data.NETWORK_3_IPV4_NET[50])
    assert str(net_map_stub_data.NETWORK_3_IPV6_NET) in str(exc_info.value)
    assert exc_info.value.field == "ip"
    assert exc_info.value.parent_type == "instance"
    assert exc_info.value.parent_name == "instance-3"
    assert "version v4" in str(exc_info.value).lower()

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.InstanceDefinition(
            "instance-3",
            {
                "networks": {
                    net_map_stub_data.NETWORK_3_NAME: {
                        "ip-v6": str(net_map_stub_data.NETWORK_3_IPV4_NET[50])
                    },
                },
            },
            stub_networks_definitions,
        )
    assert exc_info.value.invalid_value == str(net_map_stub_data.NETWORK_3_IPV4_NET[50])
    assert exc_info.value.field == "ip-v6"
    assert "should be a ipv6" in str(exc_info.value).lower()

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.InstanceDefinition(
            "instance-3",
            {
                "networks": {
                    net_map_stub_data.NETWORK_1_NAME: {
                        "ip-v4": str(net_map_stub_data.NETWORK_1_IPV6_NET[50])
                    },
                },
            },
            stub_networks_definitions,
        )
    assert exc_info.value.invalid_value == str(net_map_stub_data.NETWORK_1_IPV6_NET[50])
    assert exc_info.value.field == "ip-v4"
    assert "should be a ipv4" in str(exc_info.value).lower()


def test_instance_definition_parse_trunk_parent_ok():
    # Test valid trunk parent
    networks_definitions = net_map_stub_data.build_valid_network_definition_set()
    net_a = list(networks_definitions.values())[0]
    net_b = list(networks_definitions.values())[1]
    instance_definition_raw = {
        "networks": {
            net_a.name: {"trunk-parent": net_b.name},
            net_b.name: {"is-trunk-parent": True},
        },
    }

    instance_def = networking_definition.InstanceDefinition(
        "instance-1",
        instance_definition_raw,
        networks_definitions,
    )
    assert hash(instance_def)
    assert instance_def.name == "instance-1"
    assert isinstance(instance_def.networks, dict)
    assert len(instance_def.networks) == len(instance_definition_raw["networks"])
    # Ensure nets were parsed
    assert net_a.name in instance_def.networks
    assert net_b.name in instance_def.networks
    trunk_parent = instance_def.networks[net_a.name].trunk_parent
    assert isinstance(trunk_parent, networking_definition.InstanceNetworkDefinition)
    assert trunk_parent.network.name == net_b.name


def test_instance_definition_parse_trunk_parent_fail():
    # Test invalid trunk parent
    networks_definitions = net_map_stub_data.build_valid_network_definition_set()
    net_a = list(networks_definitions.values())[0]
    net_b = list(networks_definitions.values())[1]
    instance_definition_raw = {
        "networks": {
            net_a.name: {"is-trunk-parent": True},
            net_b.name: {"trunk-parent": "does-not-exist-parent"},
        },
    }

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.InstanceDefinition(
            "instance-1",
            instance_definition_raw,
            networks_definitions,
        )
    assert exc_info.value.invalid_value == "does-not-exist-parent"
    assert "does not exist in " in str(exc_info.value)


def test_instance_definition_parse_no_trunk_parent_fail():
    # Test invalid no is_trunk_parent
    networks_definitions = net_map_stub_data.build_valid_network_definition_set()
    net_a = list(networks_definitions.values())[0]
    net_b = list(networks_definitions.values())[1]
    instance_definition_raw = {
        "networks": {
            net_a.name: {},
            net_b.name: {"trunk-parent": "does-not-exist-parent"},
        },
    }

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.InstanceDefinition(
            "instance-1",
            instance_definition_raw,
            networks_definitions,
        )
    assert exc_info.value.invalid_value == "does-not-exist-parent"
    assert "does not exist in " in str(exc_info.value)


def test_instance_definition_parse_trunk_parent_no_trunks():
    # Test valid no trunks
    networks_definitions = net_map_stub_data.build_valid_network_definition_set()
    net_a = list(networks_definitions.values())[0]
    net_b = list(networks_definitions.values())[1]
    instance_definition_raw = {
        "networks": {
            net_a.name: {},
            net_b.name: {},
        },
    }

    instance_def = networking_definition.InstanceDefinition(
        "instance-1",
        instance_definition_raw,
        networks_definitions,
    )
    assert hash(instance_def)
    assert instance_def.name == "instance-1"
    assert isinstance(instance_def.networks, dict)
    assert len(instance_def.networks) == len(instance_definition_raw["networks"])
    # Ensure nets were parsed
    assert net_a.name in instance_def.networks
    assert net_b.name in instance_def.networks
    assert instance_def.networks[net_a.name].trunk_parent is None
