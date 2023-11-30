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


def test_host_network_range_ipv6_ok():
    ip_net = ipaddress.ip_network("fd7a:85d4:b712:58ea::/64")
    ip_range_1_start_index = 100
    ip_range_1_end_index = 4096
    range_1 = networking_definition.HostNetworkRange(
        ip_net,
        start=str(ip_net[ip_range_1_start_index]),
        end=str(ip_net[ip_range_1_end_index]),
    )
    assert range_1.start_ip == ip_net[ip_range_1_start_index]
    assert range_1.end_ip == ip_net[ip_range_1_end_index]
    assert range_1.length == (ip_range_1_end_index - ip_range_1_start_index + 1)
    assert range_1.network == ip_net
    assert hash(range_1)

    ip_range_2_start_index = 177
    ip_range_2_length = 1024
    range_2 = networking_definition.HostNetworkRange(
        str(ip_net), start=ip_net[ip_range_2_start_index], length=ip_range_2_length
    )
    assert range_2.end_ip == ip_net[ip_range_2_length + ip_range_2_start_index - 1]
    assert range_2.length == ip_range_2_length
    assert range_2.network == ip_net

    ip_range_3_start_index = 90
    ip_range_3_end_ip = ip_net[ip_range_3_start_index + 2047]
    range_3 = networking_definition.HostNetworkRange(
        ip_net, start=ip_range_3_start_index, end=ip_range_3_end_ip
    )
    assert range_3.start_ip == ip_net[ip_range_3_start_index]
    assert range_3.end_ip == ip_range_3_end_ip
    assert range_3.length == (
        int(ip_range_3_end_ip) - int(ip_net[ip_range_3_start_index]) + 1
    )
    assert range_3.network == ip_net

    ip_range_4_start_ip = ip_net.network_address
    ip_range_4_end_ip = ip_net.broadcast_address
    range_4 = networking_definition.HostNetworkRange(ip_net)
    assert range_4.start_ip == ip_range_4_start_ip
    assert range_4.end_ip == ip_range_4_end_ip
    assert range_4.length == ip_net.num_addresses
    assert range_4.network == ip_net

    ip_range_5_start_index = 1354
    ip_range_5_end_index = 2777
    range_5 = networking_definition.HostNetworkRange(
        ip_net, start=ip_range_5_start_index, end=str(ip_range_5_end_index)
    )
    assert range_5.start_ip == ip_net[ip_range_5_start_index]
    assert range_5.end_ip == ip_net[ip_range_5_end_index]
    assert range_5.length == (ip_range_5_end_index - ip_range_5_start_index + 1)
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


def test_host_network_range_from_raw_ipv6_ok():
    ip_net = ipaddress.ip_network("fd7a:85d4:b712:58ea::/64")

    ip_range_1_start_index = 100
    ip_range_1_end_index = 4096
    range_config_1 = {
        "start": str(ip_net[ip_range_1_start_index]),
        "end": str(ip_net[ip_range_1_end_index]),
    }
    range_1 = networking_definition.HostNetworkRange.from_raw(ip_net, range_config_1)
    assert range_1.start_ip == ip_net[ip_range_1_start_index]
    assert range_1.end_ip == ip_net[ip_range_1_end_index]
    assert range_1.length == ip_range_1_end_index - ip_range_1_start_index + 1
    assert range_1.network == ip_net
    assert hash(range_1)

    ip_range_2_start_index = 100
    ip_range_2_length = 4096
    range_config_2 = {
        "start": str(ip_net[ip_range_1_start_index]),
        "length": ip_range_2_length,
    }
    range_2 = networking_definition.HostNetworkRange.from_raw(ip_net, range_config_2)
    assert range_2.start_ip == ip_net[ip_range_2_start_index]
    assert range_2.end_ip == ip_net[ip_range_2_start_index + ip_range_2_length - 1]
    assert range_2.length == ip_range_2_length
    assert range_2.network == ip_net

    ip_range_3_start_index = 1777
    ip_range_3_end_ip = ip_net[ip_range_3_start_index + 2045]
    range_config_3 = {"start": ip_range_3_start_index, "end": str(ip_range_3_end_ip)}
    range_3 = networking_definition.HostNetworkRange.from_raw(ip_net, range_config_3)
    assert range_3.start_ip == ip_net[ip_range_3_start_index]
    assert range_3.end_ip == ip_range_3_end_ip
    assert range_3.length == (
        int(ip_range_3_end_ip) - int(ip_net[ip_range_3_start_index]) + 1
    )
    assert range_3.network == ip_net

    range_4 = networking_definition.HostNetworkRange.from_raw(ip_net, {})
    assert range_4.start_ip == ip_net[0]
    assert range_4.end_ip == ip_net[-1]
    assert range_4.length == ip_net.num_addresses
    assert range_4.network == ip_net

    ip_range_5_start_index = 1777
    ip_range_5_end_index = 2045
    range_config_5 = {"start": str(ip_range_5_start_index), "end": ip_range_5_end_index}
    range_5 = networking_definition.HostNetworkRange.from_raw(ip_net, range_config_5)
    assert range_5.start_ip == ip_net[ip_range_5_start_index]
    assert range_5.end_ip == ip_net[ip_range_5_end_index]
    assert range_5.length == ip_range_5_end_index - ip_range_5_start_index + 1
    assert range_5.network == ip_net

    range_config_6 = "1777-2045"
    range_6 = networking_definition.HostNetworkRange.from_raw(ip_net, range_config_6)
    assert range_6.network == ip_net
    assert range_6 == range_5

    ip_range_7_start_ip = ip_net[ip_range_5_start_index]
    ip_range_7_end_ip = ip_net[ip_range_5_end_index]
    range_config_7 = "-".join([str(ip_range_7_start_ip), str(ip_range_7_end_ip)])
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


def test_host_network_range_ipv6_fail():
    ip_net = ipaddress.ip_network("fd7a:85d4:b712:58ea::/64")
    case_1_start_ip = f"{ip_net[200]}ss"
    case_1_end_ip = f"{ip_net[2000]}"
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(
            ip_net, start=case_1_start_ip, end=case_1_end_ip
        )
    assert exc_info.value.invalid_value == case_1_start_ip
    assert exc_info.value.field == "start"

    case_2_start_ip = f"{ip_net[200]}"
    case_2_end_ip = f"{ip_net[2000]}ss"
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(
            ip_net, start=case_2_start_ip, end=case_2_end_ip
        )
    assert exc_info.value.invalid_value == case_2_end_ip
    assert exc_info.value.field == "end"

    case_3_end_ip = f"{ip_net[2000]}"
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(ip_net, start=-50, end=case_3_end_ip)
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

    small_net = ipaddress.ip_network("fd7a:85d4:b712:58ea::/126")
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(small_net, start=50, end="10")
    assert exc_info.value.invalid_value == 50
    assert exc_info.value.field == "start"
    assert "out of range" in str(exc_info.value)

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(
            small_net, start=str(ip_net[200]), end="10"
        )
    assert exc_info.value.invalid_value == str(ip_net[200])
    assert exc_info.value.field == "start"
    assert "out of range" in str(exc_info.value)

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(
            ip_net, start="0", length=ip_net.num_addresses + 1
        )
    assert exc_info.value.invalid_value == ip_net.num_addresses + 1
    assert exc_info.value.field == "length"
    assert "out of range" in str(exc_info.value)

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(small_net, start=3, end=str(ip_net[200]))
    assert exc_info.value.invalid_value == str(ip_net[200])
    assert exc_info.value.field == "end"
    assert "out of range" in str(exc_info.value)

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(small_net, start=2, end="200")
    assert exc_info.value.invalid_value == "200"
    assert exc_info.value.field == "end"
    assert "out of range" in str(exc_info.value)

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(ip_net, start=ip_net[100], end=30)
    assert exc_info.value.invalid_value == 30
    assert exc_info.value.field == "end"
    assert str(ip_net[100]) in str(exc_info.value)
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


def test_host_network_range_correct_family_fail():
    ip6_net = ipaddress.ip_network("fd7a:85d4:b712:58ea::/64")
    ip_net = ipaddress.ip_network("192.168.100.0/24")

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(ip_net, start=ip6_net[0], length=77)
    assert exc_info.value.invalid_value == ip6_net[0]
    assert exc_info.value.field == "start"
    assert "network family 4" in str(exc_info.value)

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(ip_net, start=0, end=ip6_net[100])
    assert exc_info.value.invalid_value == ip6_net[100]
    assert exc_info.value.field == "end"
    assert "network family 4" in str(exc_info.value)

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(ip6_net, start=ip_net[0], length=77)
    assert exc_info.value.invalid_value == ip_net[0]
    assert exc_info.value.field == "start"
    assert "network family 6" in str(exc_info.value)

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange(ip6_net, start=0, end=ip_net[100])
    assert exc_info.value.invalid_value == ip_net[100]
    assert exc_info.value.field == "end"
    assert "network family 6" in str(exc_info.value)


def test_host_network_range_get_version_from_raw_ok():
    assert (
        networking_definition.HostNetworkRange.get_version_from_raw(
            {
                "start": 90,
                "end": str(networking_mapping_stub_data.NETWORK_1_IPV4_NET[22]),
            }
        )
        == 4
    )

    assert (
        networking_definition.HostNetworkRange.get_version_from_raw(
            {"start": 90, "end": networking_mapping_stub_data.NETWORK_1_IPV4_NET[22]}
        )
        == 4
    )

    assert (
        networking_definition.HostNetworkRange.get_version_from_raw(
            {
                "start": str(networking_mapping_stub_data.NETWORK_1_IPV4_NET[22]),
                "end": 100,
            }
        )
        == 4
    )

    assert (
        networking_definition.HostNetworkRange.get_version_from_raw(
            {"start": networking_mapping_stub_data.NETWORK_1_IPV4_NET[22], "end": 100}
        )
        == 4
    )

    assert (
        networking_definition.HostNetworkRange.get_version_from_raw(
            {"start": 90, "end": 192}
        )
        is None
    )

    assert (
        networking_definition.HostNetworkRange.get_version_from_raw(
            {
                "start": str(networking_mapping_stub_data.NETWORK_1_IPV6_NET[77]),
                "end": 192,
            }
        )
        == 6
    )

    assert (
        networking_definition.HostNetworkRange.get_version_from_raw(
            {"start": networking_mapping_stub_data.NETWORK_1_IPV6_NET[77], "end": 192}
        )
        == 6
    )


def test_host_network_range_get_version_from_raw_mixed_fail():
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange.get_version_from_raw(
            {
                "start": networking_mapping_stub_data.NETWORK_1_IPV4_NET[77],
                "end": networking_mapping_stub_data.NETWORK_1_IPV6_NET[22],
            }
        )
    assert exc_info.value.invalid_value
    assert "range contains mixed IP versions" in str(exc_info.value)

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        networking_definition.HostNetworkRange.get_version_from_raw(
            {
                "start": networking_mapping_stub_data.NETWORK_1_IPV6_NET[77],
                "end": networking_mapping_stub_data.NETWORK_1_IPV4_NET[22],
            }
        )
    assert exc_info.value.invalid_value
    assert "range contains mixed IP versions" in str(exc_info.value)


def test_network_definition_parse_range_from_raw_ok():
    networks_stubs = networking_mapping_stub_data.build_valid_network_definition_set(
        mixed_ip_versions=True, use_ipv6=True, use_ipv4=True
    )
    ipv4_net = networks_stubs[networking_mapping_stub_data.NETWORK_1_NAME]
    ipv4_raw_range_1 = {
        "start": str(networking_mapping_stub_data.NETWORK_1_IPV4_NET[100]),
        "end": str(networking_mapping_stub_data.NETWORK_1_IPV4_NET[200]),
    }
    range_tuple_1 = ipv4_net.parse_range_from_raw(ipv4_raw_range_1)
    assert range_tuple_1
    assert len(range_tuple_1) == 2
    assert range_tuple_1[0] == networking_definition.HostNetworkRange(
        networking_mapping_stub_data.NETWORK_1_IPV4_NET,
        start=networking_mapping_stub_data.NETWORK_1_IPV4_NET[100],
        end=networking_mapping_stub_data.NETWORK_1_IPV4_NET[200],
    )
    assert not range_tuple_1[1]

    ipv4_6_net = networks_stubs[networking_mapping_stub_data.NETWORK_2_NAME]
    ipv4_6_raw_range_2 = {
        "start": 100,
        "end": 200,
    }
    range_tuple_2 = ipv4_6_net.parse_range_from_raw(ipv4_6_raw_range_2)
    assert range_tuple_2
    assert len(range_tuple_2) == 2
    assert range_tuple_2[0] == networking_definition.HostNetworkRange(
        networking_mapping_stub_data.NETWORK_2_IPV4_NET,
        start=networking_mapping_stub_data.NETWORK_2_IPV4_NET[100],
        end=networking_mapping_stub_data.NETWORK_2_IPV4_NET[200],
    )
    assert range_tuple_2[1] == networking_definition.HostNetworkRange(
        networking_mapping_stub_data.NETWORK_2_IPV6_NET,
        start=networking_mapping_stub_data.NETWORK_2_IPV6_NET[100],
        end=networking_mapping_stub_data.NETWORK_2_IPV6_NET[200],
    )

    ipv6_net = networks_stubs[networking_mapping_stub_data.NETWORK_3_NAME]
    ipv6_raw_range_1 = {
        "start": str(networking_mapping_stub_data.NETWORK_3_IPV6_NET[100]),
        "end": str(networking_mapping_stub_data.NETWORK_3_IPV6_NET[200]),
    }
    range_tuple_3 = ipv6_net.parse_range_from_raw(ipv6_raw_range_1)
    assert range_tuple_1
    assert len(range_tuple_3) == 2
    assert range_tuple_3[1] == networking_definition.HostNetworkRange(
        networking_mapping_stub_data.NETWORK_3_IPV6_NET,
        start=networking_mapping_stub_data.NETWORK_3_IPV6_NET[100],
        end=networking_mapping_stub_data.NETWORK_3_IPV6_NET[200],
    )
    assert not range_tuple_3[0]


def test_network_definition_parse_range_from_raw_fail():
    networks_stubs = networking_mapping_stub_data.build_valid_network_definition_set(
        mixed_ip_versions=True, use_ipv6=True, use_ipv4=True
    )
    ipv4_net = networks_stubs[networking_mapping_stub_data.NETWORK_1_NAME]
    ipv4_v6_net = networks_stubs[networking_mapping_stub_data.NETWORK_2_NAME]
    ipv6_net = networks_stubs[networking_mapping_stub_data.NETWORK_3_NAME]
    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        ipv4_v6_net.parse_range_from_raw(
            {
                "start": str(networking_mapping_stub_data.NETWORK_2_IPV6_NET[100]),
                "end": 200,
            },
            ip_version=4,
        )
    assert "v6 was given" in str(exc_info.value)

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        ipv4_v6_net.parse_range_from_raw(
            {
                "start": str(networking_mapping_stub_data.NETWORK_2_IPV4_NET[100]),
                "end": 200,
            },
            ip_version=6,
        )
    assert "v4 was given" in str(exc_info.value)

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        ipv4_net.parse_range_from_raw(
            {
                "start": str(networking_mapping_stub_data.NETWORK_1_IPV6_NET[100]),
                "end": 200,
            },
        )
    assert "ipv4 only" in str(exc_info.value).lower()

    with pytest.raises(exceptions.NetworkMappingValidationError) as exc_info:
        ipv6_net.parse_range_from_raw(
            {
                "start": str(networking_mapping_stub_data.NETWORK_3_IPV4_NET[100]),
                "end": 200,
            },
        )
    assert "ipv6 only" in str(exc_info.value).lower()
