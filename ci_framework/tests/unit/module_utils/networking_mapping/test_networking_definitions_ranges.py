from __future__ import absolute_import, division, print_function

__metaclass__ = type

import ipaddress

import pytest
from ansible_collections.cifmw.general.plugins.module_utils.networking_mapping import (
    exceptions,
    networking_definition,
)


def test_host_network_range_ok():
    ip_net = ipaddress.ip_network("192.168.100.0/24")
    range_1 = networking_definition.HostNetworkRange(
        ip_net, start="192.168.100.100", end="192.168.100.200"
    )
    assert range_1.start_ip == ipaddress.IPv4Address("192.168.100.100")
    assert range_1.end_ip == ipaddress.IPv4Address("192.168.100.200")
    assert range_1.length == 101
    assert range_1.network == ip_net
    assert hash(range_1)

    range_2 = networking_definition.HostNetworkRange(
        ip_net, start=ipaddress.ip_address("192.168.100.100"), length=77
    )
    assert range_2.start_ip == ipaddress.IPv4Address("192.168.100.100")
    assert range_2.end_ip == ipaddress.IPv4Address("192.168.100.176")
    assert range_2.length == 77
    assert range_2.network == ip_net

    range_3 = networking_definition.HostNetworkRange(
        ip_net, start=90, end=ipaddress.ip_address("192.168.100.100")
    )
    assert range_3.start_ip == ipaddress.IPv4Address("192.168.100.90")
    assert range_3.end_ip == ipaddress.IPv4Address("192.168.100.100")
    assert range_3.length == 11
    assert range_3.network == ip_net

    range_4 = networking_definition.HostNetworkRange(ip_net)
    assert range_4.start_ip == ipaddress.IPv4Address("192.168.100.0")
    assert range_4.end_ip == ipaddress.IPv4Address("192.168.100.255")
    assert range_4.length == 256
    assert range_4.network == ip_net

    range_5 = networking_definition.HostNetworkRange(ip_net, start=30, end="50")
    assert range_5.start_ip == ipaddress.IPv4Address("192.168.100.30")
    assert range_5.end_ip == ipaddress.IPv4Address("192.168.100.50")
    assert range_5.length == 21
    assert range_5.network == ip_net


def test_host_network_range_from_raw_ok():
    ip_net = ipaddress.ip_network("192.168.100.0/24")
    range_config_1 = {"start": "192.168.100.100", "end": "192.168.100.200"}
    range_1 = networking_definition.HostNetworkRange.from_raw(ip_net, range_config_1)
    assert range_1.start_ip == ipaddress.IPv4Address(range_config_1["start"])
    assert range_1.end_ip == ipaddress.IPv4Address(range_config_1["end"])
    assert range_1.length == 101
    assert range_1.network == ip_net
    assert hash(range_1)

    range_config_2 = {"start": "192.168.100.100", "length": 77}
    range_2 = networking_definition.HostNetworkRange.from_raw(ip_net, range_config_2)
    assert range_2.start_ip == ipaddress.IPv4Address(range_config_2["start"])
    assert range_2.end_ip == ipaddress.IPv4Address("192.168.100.176")
    assert range_2.length == 77
    assert range_2.network == ip_net

    range_config_3 = {"start": 90, "end": "192.168.100.100"}
    range_3 = networking_definition.HostNetworkRange.from_raw(ip_net, range_config_3)
    assert range_3.start_ip == ipaddress.IPv4Address("192.168.100.90")
    assert range_3.end_ip == ipaddress.IPv4Address(range_config_3["end"])
    assert range_3.length == 11
    assert range_3.network == ip_net

    range_4 = networking_definition.HostNetworkRange.from_raw(ip_net, {})
    assert range_4.start_ip == ip_net[0]
    assert range_4.end_ip == ip_net[-1]
    assert range_4.length == ip_net.num_addresses
    assert range_4.network == ip_net

    range_config_5 = {"start": "30", "end": 50}
    range_5 = networking_definition.HostNetworkRange.from_raw(ip_net, range_config_5)
    assert range_5.start_ip == ipaddress.IPv4Address("192.168.100.30")
    assert range_5.end_ip == ipaddress.IPv4Address("192.168.100.50")
    assert range_5.length == 21
    assert range_5.network == ip_net

    range_config_6 = "30-50"
    range_6 = networking_definition.HostNetworkRange.from_raw(ip_net, range_config_6)
    assert range_6.network == ip_net
    assert range_6 == range_5

    range_config_7 = "192.168.100.30-192.168.100.50"
    range_7 = networking_definition.HostNetworkRange.from_raw(ip_net, range_config_7)
    assert range_7.network == ip_net
    assert range_7 == range_5


def test_host_network_range_fail():
    ip_net = ipaddress.ip_network("192.168.100.0/24")
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(
            ip_net, start="192.168.100.100ss", end="192.168.100.200"
        )
    assert exc_info.value.invalid_value == "192.168.100.100ss"
    assert exc_info.value.field == "start"

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(
            ip_net, start="192.168.100.100", end="192.168.100.200ss"
        )
    assert exc_info.value.invalid_value == "192.168.100.200ss"
    assert exc_info.value.field == "end"

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(ip_net, start=-50, end="192.168.100.200")
    assert exc_info.value.invalid_value == -50
    assert exc_info.value.field == "start"

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(ip_net, start="50", end=-40)
    assert exc_info.value.invalid_value == -40
    assert exc_info.value.field == "end"

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(ip_net, start="50", length=-40)
    assert exc_info.value.invalid_value == -40
    assert exc_info.value.field == "length"

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(ip_net, start="50s", length=40)
    assert exc_info.value.invalid_value == "50s"
    assert exc_info.value.field == "start"

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(ip_net, start="50", length="10s")
    assert exc_info.value.invalid_value == "10s"
    assert exc_info.value.field == "length"

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(
            ipaddress.ip_network("192.168.122.0/28"), start=50, end="10"
        )
    assert exc_info.value.invalid_value == 50
    assert exc_info.value.field == "start"
    assert "out of range" in str(exc_info.value)

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(
            ipaddress.ip_network("192.168.122.0/28"), start="192.168.122.200", end="10"
        )
    assert exc_info.value.invalid_value == "192.168.122.200"
    assert exc_info.value.field == "start"
    assert "out of range" in str(exc_info.value)

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(ip_net, start="50", length=256)
    assert exc_info.value.invalid_value == 256
    assert exc_info.value.field == "length"
    assert "out of range" in str(exc_info.value)

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(
            ipaddress.ip_network("192.168.122.0/28"), start=10, end="192.168.100.255"
        )
    assert exc_info.value.invalid_value == "192.168.100.255"
    assert exc_info.value.field == "end"
    assert "out of range" in str(exc_info.value)

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(
            ipaddress.ip_network("192.168.122.0/28"), start=10, end="200"
        )
    assert exc_info.value.invalid_value == "200"
    assert exc_info.value.field == "end"
    assert "out of range" in str(exc_info.value)

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(
            ip_net, start=ipaddress.ip_address("192.168.100.50"), end=30
        )
    assert exc_info.value.invalid_value == 30
    assert exc_info.value.field == "end"
    assert "192.168.100.50" in str(exc_info.value)
    assert "less than" in str(exc_info.value)

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange.from_raw(ip_net, "2222-22222-2")
    assert exc_info.value.invalid_value == "2222-22222-2"
    assert "2222-22222-2" in str(exc_info.value)
    assert "<START>-<END>" in str(exc_info.value)


def test_host_network_range_in_ok():
    ip_net = ipaddress.ip_network("192.168.100.0/24")
    range_1 = networking_definition.HostNetworkRange(
        ip_net, start="192.168.100.100", end="192.168.100.200"
    )
    in_ip = ipaddress.ip_address("192.168.100.101")
    assert in_ip in range_1
    assert str(in_ip) in range_1
    out_low_ip_1 = ipaddress.ip_address("192.168.100.99")
    assert out_low_ip_1 not in range_1
    assert str(out_low_ip_1) not in range_1
    out_high_ip_1 = ipaddress.ip_address("192.168.100.201")
    assert out_high_ip_1 not in range_1
    assert str(out_high_ip_1) not in range_1

    # Unexpected types tests
    assert 1 not in range_1
    assert "dd23d" not in range_1
