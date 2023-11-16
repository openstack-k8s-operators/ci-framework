import pathlib
import typing

import yaml
from ansible_collections.cifmw.general.plugins.module_utils.networking_mapping import (
    networking_definition,
)

__TEST_FILES_DIR = pathlib.Path(__file__).parent.parent.joinpath("test_files")


def build_valid_network_definition(
    name: str,
    net_raw,
    add_multus: bool = False,
    add_netconfig: bool = False,
    add_metallb: bool = False,
):
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
    add_multus: bool = False, add_netconfig: bool = False, add_metallb: bool = False
):
    net_1 = build_valid_network_definition(
        "network-1",
        {"network": "192.168.122.0/24", "vlan": "122", "mtu": "9000"},
        add_metallb=add_metallb,
        add_multus=add_multus,
        add_netconfig=add_netconfig,
    )

    net_2 = build_valid_network_definition(
        "network-2",
        {"network": "192.168.0.0/24", "mtu": 1500},
        add_metallb=add_metallb,
        add_multus=add_multus,
        add_netconfig=add_netconfig,
    )
    net_3 = build_valid_network_definition(
        "network-3",
        {"network": "192.168.123.0/24", "vlan": 123, "mtu": 1500},
        add_metallb=add_metallb,
        add_multus=add_multus,
        add_netconfig=add_netconfig,
    )

    return {
        net_1.name: net_1,
        net_2.name: net_2,
        net_3.name: net_3,
    }


def build_valid_network_definition_and_templates_set():
    networks_definitions = build_valid_network_definition_set()
    first_net = list(networks_definitions.values())[0]
    second_net = list(networks_definitions.values())[1]
    third_net = list(networks_definitions.values())[2]
    group_template_raw_1 = {
        "networks": {
            first_net.name: {"range": {"start": 1, "length": 29}},
            second_net.name: {
                "range": {"start": 0, "length": 60},
            },
            third_net.name: {},
        },
    }
    group_template_raw_2 = {
        "networks": {
            first_net.name: {"range": {"start": 30, "length": 30}},
            second_net.name: {
                "range": {"start": 60, "length": 50},
            },
            third_net.name: {},
        },
    }
    group_template_raw_3 = {
        "networks": {
            first_net.name: {"range": {"start": 60, "length": 40}},
            second_net.name: {
                "range": {"start": 110, "length": 20},
            },
            third_net.name: {
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
    first_net = list(networks_definitions.values())[0]
    second_net = list(networks_definitions.values())[1]
    third_net = list(networks_definitions.values())[2]
    instance_definition_raw_1 = {
        "networks": {
            first_net.name: {"ip": "192.168.122.15"},
            second_net.name: {"ip": "192.168.0.15", "skip-nm-configuration": True},
        },
    }
    instance_definition_1 = networking_definition.InstanceDefinition(
        "instance-1", instance_definition_raw_1, networks_definitions
    )

    instance_definition_raw_2 = {
        "networks": {
            first_net.name: {"ip": "192.168.122.16"},
            second_net.name: {"ip": "192.168.0.16"},
            third_net.name: {"ip": "192.168.123.16"},
        },
    }
    instance_definition_2 = networking_definition.InstanceDefinition(
        "instance-2", instance_definition_raw_2, networks_definitions
    )

    instance_definition_raw_3 = {
        "skip-nm-configuration": True,
        "networks": {
            first_net.name: {"ip": "192.168.122.18"},
            second_net.name: {"ip": "192.168.0.18"},
            third_net.name: {"ip": "192.168.123.18"},
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
