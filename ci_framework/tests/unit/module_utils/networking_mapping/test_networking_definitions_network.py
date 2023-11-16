from __future__ import absolute_import, division, print_function

__metaclass__ = type

import ipaddress
import typing

import pytest
from ansible_collections.cifmw.general.plugins.module_utils.networking_mapping import (
    exceptions,
    networking_definition,
)


def validate_network_tool_range_from_raw(
    ip_net: typing.Union[ipaddress.IPv4Network, ipaddress.IPv6Network],
    tool_definition: networking_definition.SubnetBasedNetworkToolDefinition,
    tool_expected_ranges,
):
    assert tool_definition.get_ranges() == [
        networking_definition.HostNetworkRange.from_raw(ip_net, range_config)
        for range_config in tool_expected_ranges
    ]


def validate_network_definition_from_raw(net_name, net_config, network_definition):
    assert network_definition.name == net_name
    assert hash(network_definition)
    ip_net = ipaddress.ip_network(net_config["network"])
    assert network_definition.network == ip_net
    if "mtu" in net_config:
        assert network_definition.mtu == int(net_config["mtu"])
    if "vlan" in net_config:
        assert network_definition.vlan == int(net_config["vlan"])

    tools_config = net_config.get("tools", {})
    multus_config = tools_config.get("multus", None)
    if multus_config:
        assert network_definition.multus_config
        assert isinstance(
            network_definition.multus_config,
            networking_definition.MultusNetworkDefinition,
        )
        ranges_configs = [multus_config["range"]] if "range" in multus_config else []
        validate_network_tool_range_from_raw(
            ip_net, network_definition.multus_config, ranges_configs
        )

    metallb_config = tools_config.get("metallb", None)
    if metallb_config:
        assert network_definition.metallb_config
        assert isinstance(
            network_definition.metallb_config,
            networking_definition.MetallbNetworkDefinition,
        )
        validate_network_tool_range_from_raw(
            ip_net, network_definition.metallb_config, metallb_config.get("ranges", [])
        )

    netconfig_config = tools_config.get("netconfig", None)
    if netconfig_config:
        assert network_definition.netconfig_config
        assert isinstance(
            network_definition.netconfig_config,
            networking_definition.NetconfigNetworkDefinition,
        )
        validate_network_tool_range_from_raw(
            ip_net,
            network_definition.netconfig_config,
            netconfig_config.get("ranges", []),
        )


def test_network_definition_parse_ok():
    net_name = "testing-net"
    net_config = {"network": "192.168.122.0/24"}
    network_definition = networking_definition.NetworkDefinition(net_name, net_config)
    validate_network_definition_from_raw(net_name, net_config, network_definition)


def test_network_definition_parse_all_ok():
    net_name = "testing-net"
    net_config = {"network": "192.168.122.0/24", "vlan": 122, "mtu": 9000}
    network_definition = networking_definition.NetworkDefinition(net_name, net_config)
    validate_network_definition_from_raw(net_name, net_config, network_definition)


def test_network_definition_parse_int_conversion_all_ok():
    net_name = "testing-net"
    net_config = {"network": "192.168.122.0/24", "vlan": "122", "mtu": "9000"}
    network_definition = networking_definition.NetworkDefinition(net_name, net_config)
    validate_network_definition_from_raw(net_name, net_config, network_definition)


def test_network_definition_parse_all_tools_ok():
    net_name = "testing-net"
    net_config = {
        "network": "192.168.122.0/24",
        "vlan": "122",
        "mtu": "9000",
        "tools": {
            "multus": {
                "range": {
                    "start": "192.168.122.20",
                    "length": 10,
                },
            },
            "metallb": {
                "ranges": [
                    {
                        "start": "192.168.122.100",
                        "length": 20,
                    },
                    {
                        "start": "192.168.122.170",
                        "length": 30,
                    },
                ]
            },
            "netconfig": {
                "ranges": [
                    {
                        "start": "192.168.122.200",
                        "length": 40,
                    },
                    {
                        "start": "192.168.122.255",
                        "length": 1,
                    },
                ]
            },
        },
    }
    network_definition = networking_definition.NetworkDefinition(net_name, net_config)
    validate_network_definition_from_raw(net_name, net_config, network_definition)


def test_network_definition_parse_tools_ranges_collision_fail():
    net_name = "testing-net"
    ip_net = ipaddress.ip_network("192.168.122.0/24")
    colliding_range_config_1 = {
        "start": "192.168.122.170",
        "length": 30,
    }
    colliding_range_config_2 = {
        "start": "192.168.122.199",
        "length": 1,
    }

    net_config = {
        "network": str(ip_net),
        "tools": {
            "metallb": {
                "ranges": [
                    {
                        "start": "192.168.122.100",
                        "length": 20,
                    },
                    colliding_range_config_1,
                ]
            },
            "netconfig": {"ranges": [colliding_range_config_2]},
        },
    }
    with pytest.raises(exceptions.HostNetworkRangeCollisionValidationError) as exc_info:
        networking_definition.NetworkDefinition(net_name, net_config)
    assert net_name in str(exc_info.value)
    assert exc_info.value.range_1 == networking_definition.HostNetworkRange.from_raw(
        ip_net, colliding_range_config_1
    )
    assert exc_info.value.range_2 == networking_definition.HostNetworkRange.from_raw(
        ip_net, colliding_range_config_2
    )


def test_network_definition_parse_ranges_check_fail():
    net_name = "testing-net"
    net_config = {"network": "192.168.122.0/24", "vlan": "122", "mtu": "0"}
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.NetworkDefinition(net_name, net_config)
    assert exc_info.value.field == "mtu"
    assert exc_info.value.invalid_value == net_config["mtu"]

    net_config = {"network": "192.168.122.0/24", "vlan": 0, "mtu": "1500"}
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.NetworkDefinition(net_name, net_config)
    assert exc_info.value.field == "vlan"
    assert exc_info.value.invalid_value == net_config["vlan"]

    net_config = {"network": "192.168.122.0/24", "vlan": 4095, "mtu": "1500"}
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.NetworkDefinition(net_name, net_config)
    assert exc_info.value.field == "vlan"
    assert exc_info.value.invalid_value == net_config["vlan"]


def test_network_definition_parse_invalid_network_fail():
    net_name = "testing-net"
    net_config = {"network": "192.168.122.0/24s"}
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.NetworkDefinition(net_name, net_config)
    assert exc_info.value.field == "network"
    assert exc_info.value.invalid_value == net_config["network"]
