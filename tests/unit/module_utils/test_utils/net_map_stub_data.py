import ipaddress
import pathlib
import typing

import yaml
from ansible_collections.cifmw.general.plugins.module_utils.net_map import (
    networking_definition,
)

__TEST_FILES_DIR = pathlib.Path(__file__).parent.parent.joinpath("test_files")

NETWORK_1_NAME = "network-1"
NETWORK_2_NAME = "network-2"
NETWORK_3_NAME = "network-3"
NETWORK_1_IPV4_NET = ipaddress.IPv4Network("192.168.122.0/24")
NETWORK_2_IPV4_NET = ipaddress.IPv4Network("192.168.0.0/24")
NETWORK_3_IPV4_NET = ipaddress.IPv4Network("192.168.123.0/24")
NETWORK_1_IPV6_NET = ipaddress.IPv6Network("fdc0:8b54:108a:c949::/64")
NETWORK_2_IPV6_NET = ipaddress.IPv6Network("fd42:add0:b7d2:09b1::/64")
NETWORK_3_IPV6_NET = ipaddress.IPv6Network("fd5e:bdb2:6091:9306::/64")


def build_valid_network_definition(
    name: str,
    net_raw,
    add_multus: bool = False,
    add_netconfig: bool = False,
    add_metallb: bool = False,
) -> networking_definition.NetworkDefinition:
    if add_multus or add_netconfig or add_metallb:
        net_raw["tools"] = {}
    if add_multus:
        net_raw["tools"]["multus"] = {"range": {"start": 30, "end": 39}}
    if add_netconfig:
        net_raw["tools"]["netconfig"] = {
            "ranges": [
                {"start": 40, "end": 49},
                {"start": 100, "length": 10},
            ]
        }
    if add_metallb:
        net_raw["tools"]["metallb"] = {
            "ranges": [
                {"start": 60, "end": 69},
            ]
        }
    net_1 = networking_definition.NetworkDefinition(name, net_raw)
    return net_1


def build_valid_network_definition_set(
    add_multus: bool = False,
    add_netconfig: bool = False,
    add_metallb: bool = False,
    use_ipv4: bool = True,
    use_ipv6: bool = False,
    mixed_ip_versions: bool = False,
) -> typing.Dict[str, networking_definition.NetworkDefinition]:
    net_1_config = {"vlan": "122", "mtu": "9000"}
    if use_ipv4 and not use_ipv6:
        net_1_config["network"] = str(NETWORK_1_IPV4_NET)
    elif use_ipv6 and not use_ipv4 and not mixed_ip_versions:
        net_1_config["network-v6"] = str(NETWORK_1_IPV6_NET)
    elif use_ipv6 and use_ipv4:
        net_1_config["network-v4"] = str(NETWORK_1_IPV4_NET)
        if not mixed_ip_versions:
            net_1_config["network-v6"] = str(NETWORK_1_IPV6_NET)
    net_1 = build_valid_network_definition(
        NETWORK_1_NAME,
        net_1_config,
        add_metallb=add_metallb,
        add_multus=add_multus,
        add_netconfig=add_netconfig,
    )

    net_2_config = {"mtu": 1500}
    if use_ipv4 and not use_ipv6:
        net_2_config["network-v4"] = str(NETWORK_2_IPV4_NET)
    elif use_ipv6 and not use_ipv4:
        net_2_config["network"] = str(NETWORK_2_IPV6_NET)
    elif use_ipv6 and use_ipv4:
        net_2_config["network-v4"] = str(NETWORK_2_IPV4_NET)
        net_2_config["network-v6"] = str(NETWORK_2_IPV6_NET)
    net_2 = build_valid_network_definition(
        NETWORK_2_NAME,
        net_2_config,
        add_metallb=add_metallb,
        add_multus=add_multus,
        add_netconfig=add_netconfig,
    )

    net_3_config = {"vlan": 123, "mtu": 1500}
    if use_ipv4 and not use_ipv6:
        net_3_config["network-v4"] = str(NETWORK_3_IPV4_NET)
    elif use_ipv6 and not use_ipv4:
        net_3_config["network"] = str(NETWORK_3_IPV6_NET)
    elif use_ipv6 and use_ipv4:
        if not mixed_ip_versions:
            net_3_config["network-v4"] = str(NETWORK_3_IPV4_NET)
        net_3_config["network-v6"] = str(NETWORK_3_IPV6_NET)
    net_3 = build_valid_network_definition(
        NETWORK_3_NAME,
        net_3_config,
        add_metallb=add_metallb,
        add_multus=add_multus,
        add_netconfig=add_netconfig,
    )

    return {
        net_1.name: net_1,
        net_2.name: net_2,
        net_3.name: net_3,
    }


def build_valid_network_definition_and_templates_set(
    use_ipv4: bool = True,
    use_ipv6: bool = False,
    mixed_ip_versions: bool = False,
):
    networks_definitions = build_valid_network_definition_set(
        use_ipv4=use_ipv4, use_ipv6=use_ipv6, mixed_ip_versions=mixed_ip_versions
    )
    group_template_raw_1 = {
        "networks": {
            NETWORK_1_NAME: {"range": {"start": 1, "length": 29}},
            NETWORK_2_NAME: {
                "range": {"start": 0, "length": 60},
            },
            NETWORK_3_NAME: {},
        },
    }
    group_template_raw_2 = {
        "networks": {
            NETWORK_1_NAME: {"range": {"start": 30, "length": 30}},
            NETWORK_2_NAME: {
                "range": {"start": 60, "length": 50},
            },
            NETWORK_3_NAME: {},
        },
    }
    group_template_raw_3 = {
        "networks": {
            NETWORK_1_NAME: {"range": {"start": 60, "length": 40}},
            NETWORK_2_NAME: {
                "range": {"start": 110, "length": 20},
            },
            NETWORK_3_NAME: {
                "range": {"start": 0, "length": 256},
            },
        },
    }
    group_template_1 = networking_definition.GroupTemplateDefinition(
        "group-1", group_template_raw_1, networks_definitions
    )
    group_template_2 = networking_definition.GroupTemplateDefinition(
        "group-2", group_template_raw_2, networks_definitions
    )
    group_template_3 = networking_definition.GroupTemplateDefinition(
        "group-3", group_template_raw_3, networks_definitions
    )
    return (
        networks_definitions,
        {
            group_template_1.group_name: group_template_1,
            group_template_2.group_name: group_template_2,
            group_template_3.group_name: group_template_3,
        },
    )


def build_valid_network_definition_all_sets():
    (
        networks_definitions,
        host_templates,
    ) = build_valid_network_definition_and_templates_set()
    instance_definition_raw_1 = {
        "networks": {
            NETWORK_1_NAME: {"ip": "192.168.122.15"},
            NETWORK_2_NAME: {"ip": "192.168.0.15", "skip-nm-configuration": True},
        },
    }
    instance_definition_1 = networking_definition.InstanceDefinition(
        "instance-1", instance_definition_raw_1, networks_definitions
    )

    instance_definition_raw_2 = {
        "networks": {
            NETWORK_1_NAME: {"ip": "192.168.122.16"},
            NETWORK_2_NAME: {"ip": "192.168.0.16"},
            NETWORK_3_NAME: {"ip": "192.168.123.16"},
        },
    }
    instance_definition_2 = networking_definition.InstanceDefinition(
        "instance-2", instance_definition_raw_2, networks_definitions
    )

    instance_definition_raw_3 = {
        "skip-nm-configuration": True,
        "networks": {
            NETWORK_1_NAME: {"ip": "192.168.122.18"},
            NETWORK_2_NAME: {"ip": "192.168.0.18"},
            NETWORK_3_NAME: {"ip": "192.168.123.18"},
        },
    }
    instance_definition_3 = networking_definition.InstanceDefinition(
        "instance-3", instance_definition_raw_3, networks_definitions
    )

    return (
        networks_definitions,
        host_templates,
        (
            {
                instance_definition_1.name: instance_definition_1,
                instance_definition_2.name: instance_definition_2,
                instance_definition_3.name: instance_definition_3,
            }
        ),
    )


def get_test_file_path(file_name):
    assert __TEST_FILES_DIR.is_dir()
    file_path = __TEST_FILES_DIR.joinpath(file_name)
    assert file_path.exists()
    return file_path


def get_test_file_content(file_name: str) -> str:
    file_path = get_test_file_path(file_name)
    with open(file_path, "r") as file:
        return file.read()


def get_test_file_yaml_content(file_name: str) -> typing.Dict[str, typing.Any]:
    file_path = get_test_file_path(file_name)
    with open(file_path, "r") as file:
        return yaml.safe_load(file)
