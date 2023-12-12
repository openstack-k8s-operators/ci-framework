from __future__ import absolute_import, division, print_function

__metaclass__ = type

import ipaddress
import typing

import pytest
from ansible_collections.cifmw.general.plugins.module_utils.net_map import (
    exceptions,
    networking_definition,
)

from ansible_collections.cifmw.general.tests.unit.module_utils.test_utils import (
    net_map_stub_data,
)


def validate_network_tool_range_from_raw(
    ip_net4: typing.Union[ipaddress.IPv4Network, None],
    ip_net6: typing.Union[ipaddress.IPv6Network, None],
    tool_definition: networking_definition.SubnetBasedNetworkToolDefinition,
    tool_config: typing.Dict[str, typing.Any],
):
    v6_ranges = []
    v4_ranges = []
    for range_raw in tool_config.get("ranges", []):
        range_version = networking_definition.HostNetworkRange.get_version_from_raw(
            range_raw
        )
        if ip_net4 and ((not range_version) or range_version == 4):
            v4_ranges.append(range_raw)
        if ip_net6 and ((not range_version) or range_version == 6):
            v6_ranges.append(range_raw)

    for range_raw in tool_config.get("ranges-v6", []):
        v6_ranges.append(range_raw)
    for range_raw in tool_config.get("ranges-v4", []):
        v4_ranges.append(range_raw)
    for range_config in v4_ranges:
        assert ip_net4
        assert (
            networking_definition.HostNetworkRange.from_raw(ip_net4, range_config)
            in tool_definition.ranges_ipv4
        )
    for range_config in v6_ranges:
        assert ip_net6
        assert (
            networking_definition.HostNetworkRange.from_raw(ip_net6, range_config)
            in tool_definition.ranges_ipv6
        )


def validate_network_definition_from_raw_net_ips(
    net_config, network_definition
) -> typing.Tuple[
    typing.Union[ipaddress.IPv4Network, None], typing.Union[ipaddress.IPv6Network, None]
]:
    parsed_ip_net_4 = None
    parsed_ip_net_6 = None
    ip_non_versioned = net_config.get("network", None)
    if ip_non_versioned:
        parsed_ip_net = ipaddress.ip_network(ip_non_versioned)
        if parsed_ip_net.version == 6:
            assert network_definition.ipv6_network == parsed_ip_net
            assert not network_definition.ipv4_network
            parsed_ip_net_6 = parsed_ip_net
        else:
            assert network_definition.ipv4_network == parsed_ip_net
            assert not network_definition.ipv6_network
            parsed_ip_net_4 = parsed_ip_net

    ip_v4 = net_config.get("network-v4", None)
    if ip_v4:
        parsed_ip_net_4 = ipaddress.ip_network(ip_v4)
        assert network_definition.ipv4_network == parsed_ip_net_4
    elif not ip_non_versioned:
        assert not network_definition.ipv6_network

    ip_v6 = net_config.get("network-v6", None)
    if ip_v6:
        parsed_ip_net_6 = ipaddress.ip_network(ip_v6)
        assert network_definition.ipv6_network == parsed_ip_net_6
    elif not ip_non_versioned:
        assert not network_definition.ipv4_network

    return parsed_ip_net_4, parsed_ip_net_6


def validate_network_definition_from_raw_gateways(
    net_config,
    network_definition: networking_definition.NetworkDefinition,
    ipv4_net: typing.Optional[ipaddress.IPv4Network],
    ipv6_net: typing.Optional[ipaddress.IPv6Network],
):
    ip_non_versioned = net_config.get("gateway", None)
    if ip_non_versioned:
        parsed_ip_gw = ipaddress.ip_address(ip_non_versioned)
        if parsed_ip_gw.version == 6:
            assert network_definition.ipv6_gateway == parsed_ip_gw
            assert not network_definition.ipv4_gateway
            assert parsed_ip_gw in ipv6_net

        else:
            assert network_definition.ipv4_gateway == parsed_ip_gw
            assert not network_definition.ipv6_gateway
            assert parsed_ip_gw in ipv4_net

    ip_v4 = net_config.get("gateway-v4", None)
    if ip_v4:
        ipv4_gw = ipaddress.IPv4Address(ip_v4)
        assert network_definition.ipv4_gateway == ipv4_gw
        assert ipv4_gw in ipv4_net
    elif not ip_non_versioned:
        assert not network_definition.ipv4_gateway

    ip_v6 = net_config.get("network-v6", None)
    if ip_v6:
        ipv6_gw = ipaddress.IPv6Address(ip_v6)
        assert network_definition.ipv6_gateway == ipv6_gw
        assert ipv6_gw in ipv6_net
    elif not ip_non_versioned:
        assert not network_definition.ipv6_gateway


def validate_network_definition_from_raw(net_name, net_config, network_definition):
    assert network_definition.name == net_name
    assert hash(network_definition)

    ip_net_4, ip_net_6 = validate_network_definition_from_raw_net_ips(
        net_config, network_definition
    )
    validate_network_definition_from_raw_gateways(
        net_config, network_definition, ip_net_4, ip_net_6
    )

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
        validate_network_tool_range_from_raw(
            ip_net_4, ip_net_6, network_definition.multus_config, multus_config
        )

    metallb_config = tools_config.get("metallb", None)
    if metallb_config:
        assert network_definition.metallb_config
        assert isinstance(
            network_definition.metallb_config,
            networking_definition.MetallbNetworkDefinition,
        )
        validate_network_tool_range_from_raw(
            ip_net_4, ip_net_6, network_definition.metallb_config, metallb_config
        )

    netconfig_config = tools_config.get("netconfig", None)
    if netconfig_config:
        assert network_definition.netconfig_config
        assert isinstance(
            network_definition.netconfig_config,
            networking_definition.NetconfigNetworkDefinition,
        )
        validate_network_tool_range_from_raw(
            ip_net_4, ip_net_6, network_definition.netconfig_config, netconfig_config
        )


def test_network_definition_parse_ok():
    net_name = "testing-net"
    net_config = {"network": "192.168.122.0/24"}
    network_definition = networking_definition.NetworkDefinition(net_name, net_config)
    validate_network_definition_from_raw(net_name, net_config, network_definition)


def test_network_definition_parse_all_ok():
    net_name = "testing-net"
    net_config = {
        "network": "192.168.122.0/24",
        "gateway": "192.168.122.1",
        "vlan": 122,
        "mtu": 9000,
    }
    network_definition = networking_definition.NetworkDefinition(net_name, net_config)
    validate_network_definition_from_raw(net_name, net_config, network_definition)


def test_network_definition_parse_all_dual_stack_ok():
    net_name = "testing-net"
    net_config = {
        "network-v4": str(net_map_stub_data.NETWORK_1_IPV4_NET[1]),
        "network-v6": str(net_map_stub_data.NETWORK_1_IPV6_NET[1]),
        "gateway-v4": str(net_map_stub_data.NETWORK_1_IPV4_NET[1]),
        "gateway-v6": str(net_map_stub_data.NETWORK_1_IPV6_NET[1]),
        "vlan": 122,
        "mtu": 9000,
    }
    network_definition = networking_definition.NetworkDefinition(net_name, net_config)
    validate_network_definition_from_raw(net_name, net_config, network_definition)


def test_network_definition_parse_int_conversion_all_ok():
    net_name = "testing-net"
    net_config = {"network": "192.168.122.0/24", "vlan": "122", "mtu": "9000"}
    network_definition = networking_definition.NetworkDefinition(net_name, net_config)
    validate_network_definition_from_raw(net_name, net_config, network_definition)


def test_network_definition_parse_all_tools_v4_ok():
    net_name = "testing-net"
    net_config = {
        "network": "192.168.122.0/24",
        "gateway": "192.168.122.1",
        "vlan": "122",
        "mtu": "9000",
        "tools": {
            "multus": {
                "ranges": [
                    {
                        "start": "192.168.122.20",
                        "length": 10,
                    }
                ],
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


def test_network_definition_parse_all_tools_v6_ok():
    net_name = "testing-net"
    net_config = {
        "network": net_map_stub_data.NETWORK_1_IPV6_NET,
        "gateway": net_map_stub_data.NETWORK_1_IPV6_NET[1],
        "vlan": "122",
        "mtu": "9000",
        "tools": {
            "multus": {
                "ranges": [
                    {
                        "start": str(net_map_stub_data.NETWORK_1_IPV6_NET[20]),
                        "length": 10,
                    }
                ],
            },
            "metallb": {
                "ranges": [
                    {
                        "start": 100,
                        "length": 20,
                    },
                    {
                        "start": net_map_stub_data.NETWORK_1_IPV6_NET[170],
                        "length": 30,
                    },
                ]
            },
            "netconfig": {
                "ranges": [
                    {
                        "start": "200",
                        "end": net_map_stub_data.NETWORK_1_IPV6_NET[239],
                    },
                    {
                        "start": net_map_stub_data.NETWORK_1_IPV6_NET[255],
                        "end": net_map_stub_data.NETWORK_1_IPV6_NET[2048],
                    },
                ]
            },
        },
    }
    network_definition = networking_definition.NetworkDefinition(net_name, net_config)
    validate_network_definition_from_raw(net_name, net_config, network_definition)


def test_network_definition_parse_gateway_fail():
    net_config = {
        "network": "192.168.122.0/24",
        "gateway": "192.168.122.1s",
    }
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.NetworkDefinition("testing-net", net_config)
    assert exc_info.value.invalid_value == "192.168.122.1s"
    assert exc_info.value.field == "gateway"
    assert exc_info.value.parent_type == "network"
    assert exc_info.value.parent_name == "testing-net"
    assert "valid" in str(exc_info.value)

    net_config = {
        "network": "192.168.122.0/24",
        "gateway": str(net_map_stub_data.NETWORK_1_IPV6_NET[1]),
    }
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.NetworkDefinition("testing-net", net_config)
    assert exc_info.value.invalid_value == str(net_map_stub_data.NETWORK_1_IPV6_NET[1])
    assert exc_info.value.field == "gateway"
    assert exc_info.value.parent_type == "network"
    assert exc_info.value.parent_name == "testing-net"
    assert "version v6" in str(exc_info.value)

    net_config = {
        "network": str(net_map_stub_data.NETWORK_1_IPV6_NET),
        "gateway": str(net_map_stub_data.NETWORK_1_IPV4_NET[1]),
    }
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.NetworkDefinition("testing-net", net_config)
    assert exc_info.value.invalid_value == str(net_map_stub_data.NETWORK_1_IPV4_NET[1])
    assert exc_info.value.field == "gateway"
    assert exc_info.value.parent_type == "network"
    assert exc_info.value.parent_name == "testing-net"
    assert "version v4" in str(exc_info.value)

    net_config = {
        "network-v4": str(net_map_stub_data.NETWORK_1_IPV4_NET),
        "network-v6": str(net_map_stub_data.NETWORK_1_IPV6_NET),
        "gateway": str(net_map_stub_data.NETWORK_1_IPV4_NET[1]),
        "gateway-v6": str(net_map_stub_data.NETWORK_1_IPV6_NET[1]),
    }
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.NetworkDefinition("testing-net", net_config)
    assert exc_info.value.invalid_value == str(net_map_stub_data.NETWORK_1_IPV4_NET[1])
    assert exc_info.value.field == "gateway"
    assert exc_info.value.parent_type == "network"
    assert exc_info.value.parent_name == "testing-net"
    assert "same time" in str(exc_info.value)

    net_config = {
        "network-v4": str(net_map_stub_data.NETWORK_1_IPV4_NET),
        "network-v6": str(net_map_stub_data.NETWORK_1_IPV6_NET),
        "gateway": str(net_map_stub_data.NETWORK_1_IPV6_NET[1]),
        "gateway-v4": str(net_map_stub_data.NETWORK_1_IPV4_NET[1]),
    }
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.NetworkDefinition("testing-net", net_config)
    assert exc_info.value.invalid_value == str(net_map_stub_data.NETWORK_1_IPV6_NET[1])
    assert exc_info.value.field == "gateway"
    assert exc_info.value.parent_type == "network"
    assert exc_info.value.parent_name == "testing-net"
    assert "same time" in str(exc_info.value)

    net_config = {
        "network-v4": str(net_map_stub_data.NETWORK_1_IPV4_NET),
        "gateway": str(net_map_stub_data.NETWORK_2_IPV4_NET[1]),
    }
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.NetworkDefinition("testing-net", net_config)
    assert exc_info.value.invalid_value == str(net_map_stub_data.NETWORK_2_IPV4_NET[1])
    assert exc_info.value.field == "gateway"
    assert exc_info.value.parent_type == "network"
    assert exc_info.value.parent_name == "testing-net"
    assert "outside of the range" in str(exc_info.value)

    net_config = {
        "network": str(net_map_stub_data.NETWORK_1_IPV6_NET),
        "gateway-v6": str(net_map_stub_data.NETWORK_2_IPV6_NET[1]),
    }
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.NetworkDefinition("testing-net", net_config)
    assert exc_info.value.invalid_value == str(net_map_stub_data.NETWORK_2_IPV6_NET[1])
    assert exc_info.value.field == "gateway-v6"
    assert exc_info.value.parent_type == "network"
    assert exc_info.value.parent_name == "testing-net"
    assert "outside of the range" in str(exc_info.value)


def test_network_definition_parse_tools_ranges_collision_fail():
    net_name = "testing-net"

    for network_ip in (
        net_map_stub_data.NETWORK_1_IPV4_NET,
        net_map_stub_data.NETWORK_1_IPV6_NET,
    ):
        colliding_range_config_1 = {
            "start": str(network_ip[170]),
            "length": 30,
        }
        colliding_range_config_2 = {
            "start": str(network_ip[199]),
            "length": 1,
        }

        net_config = {
            "network": str(network_ip),
            "tools": {
                "metallb": {
                    "ranges": [
                        {
                            "start": str(network_ip[100]),
                            "length": 20,
                        },
                        colliding_range_config_1,
                    ]
                },
                "netconfig": {"ranges": [colliding_range_config_2]},
            },
        }
        with pytest.raises(
            exceptions.HostNetworkRangeCollisionValidationError
        ) as exc_info:
            networking_definition.NetworkDefinition(net_name, net_config)
        assert net_name in str(exc_info.value)
        assert "collides" in str(exc_info.value)
        assert (
            exc_info.value.range_1
            == networking_definition.HostNetworkRange.from_raw(
                network_ip, colliding_range_config_1
            )
        )
        assert (
            exc_info.value.range_2
            == networking_definition.HostNetworkRange.from_raw(
                network_ip, colliding_range_config_2
            )
        )


# Ensure dual stack ranges do not collide
def test_network_definition_parse_tools_ranges_collision_dual_stack_ok():
    net_name = "testing-net"
    colliding_range_config_1 = {
        "start": 170,
        "length": 30,
    }
    colliding_range_config_2 = {
        "start": 160,
        "length": 30,
    }

    net_config = {
        "network-v4": str(net_map_stub_data.NETWORK_1_IPV4_NET),
        "network-v6": str(net_map_stub_data.NETWORK_1_IPV6_NET),
        "tools": {
            "metallb": {
                "ranges-v4": [
                    {
                        "start": str(net_map_stub_data.NETWORK_1_IPV4_NET[100]),
                        "length": 20,
                    },
                    colliding_range_config_1,
                ]
            },
            "netconfig": {"ranges-v6": [colliding_range_config_2]},
        },
    }

    net_def_1 = networking_definition.NetworkDefinition(net_name, net_config)
    assert len(net_def_1.metallb_config.ranges_ipv4) == 2
    assert not net_def_1.metallb_config.ranges_ipv6
    assert all(
        net_range.network.version == 4
        for net_range in net_def_1.metallb_config.ranges_ipv4
    )

    assert not net_def_1.netconfig_config.ranges_ipv4
    assert len(net_def_1.netconfig_config.ranges_ipv6) == 1
    assert net_def_1.netconfig_config.ranges_ipv6[0].network.version == 6


def test_network_definition_parse_ranges_check_fail():
    net_name = "testing-net"
    for net_ip in [
        net_map_stub_data.NETWORK_1_IPV4_NET,
        net_map_stub_data.NETWORK_1_IPV6_NET,
    ]:
        net_config = {"network": str(net_ip), "vlan": "122", "mtu": "0"}
        with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
            networking_definition.NetworkDefinition(net_name, net_config)
        assert exc_info.value.field == "mtu"
        assert exc_info.value.invalid_value == net_config["mtu"]

        net_config = {"network": str(net_ip), "vlan": "122", "mtu": "1500s"}
        with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
            networking_definition.NetworkDefinition(net_name, net_config)
        assert exc_info.value.field == "mtu"
        assert exc_info.value.invalid_value == net_config["mtu"]

        net_config = {"network": str(net_ip), "vlan": 0, "mtu": "1500"}
        with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
            networking_definition.NetworkDefinition(net_name, net_config)
        assert exc_info.value.field == "vlan"
        assert exc_info.value.invalid_value == net_config["vlan"]

        net_config = {"network": str(net_ip), "vlan": 4095, "mtu": "1500"}
        with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
            networking_definition.NetworkDefinition(net_name, net_config)
        assert exc_info.value.field == "vlan"
        assert exc_info.value.invalid_value == net_config["vlan"]

        net_config = {"network": str(net_ip), "vlan": "10s", "mtu": "1500"}
        with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
            networking_definition.NetworkDefinition(net_name, net_config)
        assert exc_info.value.field == "vlan"
        assert exc_info.value.invalid_value == net_config["vlan"]


def test_network_definition_parse_invalid_network_fail():
    net_name = "testing-net"
    net_config_1 = {"network": f"{net_map_stub_data.NETWORK_1_IPV4_NET}s"}
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.NetworkDefinition(net_name, net_config_1)
    assert exc_info.value.field == "network"
    assert exc_info.value.invalid_value == net_config_1["network"]

    net_config_2 = {"network": f"{net_map_stub_data.NETWORK_1_IPV6_NET}sss"}
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.NetworkDefinition(net_name, net_config_2)
    assert exc_info.value.field == "network"
    assert exc_info.value.invalid_value == net_config_2["network"]


def test_network_definition_parse_invalid_network_ip_version_fail():
    net_config_1 = {"network-v4": f"{net_map_stub_data.NETWORK_1_IPV6_NET}"}
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.NetworkDefinition("testing-net", net_config_1)
    assert exc_info.value.field == "network-v4"
    assert exc_info.value.invalid_value == net_config_1["network-v4"]
    assert "of type v4" in str(exc_info.value)

    net_config_1 = {"network-v6": f"{net_map_stub_data.NETWORK_1_IPV4_NET}"}
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.NetworkDefinition("testing-net", net_config_1)
    assert exc_info.value.field == "network-v6"
    assert exc_info.value.invalid_value == net_config_1["network-v6"]
    assert "of type v6" in str(exc_info.value)

    net_config_1 = {
        "network": f"{net_map_stub_data.NETWORK_1_IPV4_NET}",
        "network-v6": f"{net_map_stub_data.NETWORK_1_IPV6_NET}",
    }
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.NetworkDefinition("testing-net", net_config_1)
    assert exc_info.value.field == "network"
    assert "network" in str(exc_info.value)
    assert "network-v6" in str(exc_info.value)
