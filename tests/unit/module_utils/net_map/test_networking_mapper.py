from __future__ import absolute_import, division, print_function

__metaclass__ = type

import copy
import json
import os.path

import pytest
from ansible_collections.cifmw.general.plugins.module_utils.net_map import (
    exceptions,
    networking_mapper,
)

from ansible_collections.cifmw.general.tests.unit.module_utils.test_utils import (
    net_map_stub_data,
)


@pytest.mark.parametrize(
    "test_input_config_file,test_golden_file",
    [
        (
            "networking-definition-valid-all-tools-dual-stack.yml",
            "networking-definition-valid-all-tools-dual-stack-networks-out.json",
        ),
        (
            "networking-definition-valid.yml",
            "networking-definition-valid-networks-out.json",
        ),
        (
            "networking-definition-valid-all-tools-ipv6-only.yml",
            "networking-definition-valid-all-tools-ipv6-only-networks-out.json",
        ),
        (
            "networking-definition-valid-all-tools.yml",
            "networking-definition-valid-all-tools-networks-out.json",
        ),
    ],
)
def test_networking_mapper_basic_networks_map_ok(
    test_input_config_file, test_golden_file
):
    mapper = networking_mapper.NetworkingDefinitionMapper(
        net_map_stub_data.TEST_HOSTVARS, net_map_stub_data.TEST_GROUPS
    )
    mapped_content = mapper.map_networks(
        net_map_stub_data.get_test_file_yaml_content(test_input_config_file)
    )
    assert mapped_content == net_map_stub_data.get_test_file_json_content(
        test_golden_file
    )


@pytest.mark.parametrize(
    "test_input_config_file,test_golden_file",
    [
        (
            "network-definition-valid-router-template.yml",
            "network-definition-valid-router-template-out.json",
        ),
    ],
)
def test_networking_mapper_basic_routers_map_ok(
    test_input_config_file, test_golden_file
):
    mapper = networking_mapper.NetworkingDefinitionMapper(
        net_map_stub_data.TEST_HOSTVARS, net_map_stub_data.TEST_GROUPS
    )
    mapped_content = mapper.map_routers(
        net_map_stub_data.get_test_file_yaml_content(test_input_config_file)
    )
    assert mapped_content == net_map_stub_data.get_test_file_json_content(
        test_golden_file
    )


@pytest.mark.parametrize(
    "test_input_config_file,test_golden_file,reduced_hosts",
    [
        pytest.param(
            "networking-definition-valid-all-tools-dual-stack.yml",
            "networking-definition-valid-all-tools-dual-stack-partial-reduced"
            "-map-out.json",
            True,
            id="reduced-dual-stack-all-tools",
        ),
        pytest.param(
            "networking-definition-valid-all-tools-dual-stack.yml",
            "networking-definition-valid-all-tools-dual-stack-partial-map-out.json",
            False,
            id="dual-stack-all-tools",
        ),
        pytest.param(
            "networking-definition-valid.yml",
            "networking-definition-valid-partial-map-out.json",
            False,
            id="no-tools",
        ),
        pytest.param(
            "networking-definition-valid-all-tools-ipv6-only.yml",
            "networking-definition-valid-all-tools-ipv6-only-partial-map-out.json",
            False,
            id="reduced-ipv6-only",
        ),
        pytest.param(
            "networking-definition-valid-all-tools-ipv6-only.yml",
            "networking-definition-valid-all-tools-ipv6-only-partial-"
            "reduced-map-out.json",
            True,
            id="ipv6-only",
        ),
        pytest.param(
            "networking-definition-valid-all-tools.yml",
            "networking-definition-valid-all-tools-partial-map-out.json",
            False,
            id="all-tools",
        ),
    ],
)
def test_networking_mapper_full_partial_map_ok(
    test_input_config_file: str, test_golden_file: str, reduced_hosts: bool
):
    mapper = networking_mapper.NetworkingDefinitionMapper(
        (
            net_map_stub_data.TEST_HOSTVARS
            if not reduced_hosts
            else net_map_stub_data.TEST_HOSTVARS_REDUCED
        ),
        (
            net_map_stub_data.TEST_GROUPS
            if not reduced_hosts
            else net_map_stub_data.TEST_GROUPS_REDUCED
        ),
    )
    mapped_content = mapper.map(
        net_map_stub_data.get_test_file_yaml_content(test_input_config_file)
    )
    assert mapped_content == net_map_stub_data.get_test_file_json_content(
        test_golden_file
    )


@pytest.mark.parametrize(
    "test_input_config_file,test_golden_file,test_interfaces_info",
    [
        (
            "networking-definition-valid-all-tools-dual-stack.yml",
            "networking-definition-valid-all-tools-dual-stack-full-map-out.json",
            None,
        ),
        (
            "networking-definition-valid.yml",
            "networking-definition-valid-full-map-out.json",
            None,
        ),
        (
            "networking-definition-valid-all-tools-ipv6-only.yml",
            "networking-definition-valid-all-tools-ipv6-only-full-map-out.json",
            net_map_stub_data.patch_interfaces_info_dicts(
                net_map_stub_data.TEST_IFACES_INFO,
                {
                    net_map_stub_data.INSTANCE_1_NAME: [
                        {
                            net_map_stub_data.TEST_IFACES_INFO_MAC_FIELD: net_map_stub_data.INSTANCE_1_ALTERNATE_MACADDR,
                            net_map_stub_data.TEST_IFACES_INFO_NETWORK_FIELD: "network-4",
                        },
                    ],
                    net_map_stub_data.INSTANCE_2_NAME: [
                        {
                            net_map_stub_data.TEST_IFACES_INFO_MAC_FIELD: net_map_stub_data.INSTANCE_2_ALTERNATE_MACADDR,
                            net_map_stub_data.TEST_IFACES_INFO_NETWORK_FIELD: "network-4",
                        },
                    ],
                    net_map_stub_data.INSTANCE_3_NAME: [
                        {
                            net_map_stub_data.TEST_IFACES_INFO_MAC_FIELD: net_map_stub_data.INSTANCE_3_ALTERNATE_MACADDR,
                            net_map_stub_data.TEST_IFACES_INFO_NETWORK_FIELD: "network-4",
                        },
                    ],
                },
            ),
        ),
        (
            "networking-definition-valid-all-tools.yml",
            "networking-definition-valid-all-tools-full-map-out.json",
            net_map_stub_data.patch_interfaces_info_dicts(
                net_map_stub_data.TEST_IFACES_INFO,
                {
                    net_map_stub_data.INSTANCE_1_NAME: [
                        {
                            net_map_stub_data.TEST_IFACES_INFO_MAC_FIELD: net_map_stub_data.INSTANCE_1_ALTERNATE_MACADDR,
                            net_map_stub_data.TEST_IFACES_INFO_NETWORK_FIELD: "tenant",
                        },
                    ],
                    net_map_stub_data.INSTANCE_2_NAME: [
                        {
                            net_map_stub_data.TEST_IFACES_INFO_MAC_FIELD: net_map_stub_data.INSTANCE_2_ALTERNATE_MACADDR,
                            net_map_stub_data.TEST_IFACES_INFO_NETWORK_FIELD: "tenant",
                        },
                    ],
                    net_map_stub_data.INSTANCE_3_NAME: [
                        {
                            net_map_stub_data.TEST_IFACES_INFO_MAC_FIELD: net_map_stub_data.INSTANCE_3_ALTERNATE_MACADDR,
                            net_map_stub_data.TEST_IFACES_INFO_NETWORK_FIELD: "tenant",
                        },
                    ],
                },
            ),
        ),
        (
            "network-definition-valid-all-tools-no-group-templates.yml",
            "network-definition-valid-all-tools-no-group-templates-out.json",
            None,
        ),
    ],
)
def test_networking_mapper_full_map_ok(
    test_input_config_file, test_golden_file, test_interfaces_info
):
    mapper = networking_mapper.NetworkingDefinitionMapper(
        net_map_stub_data.TEST_HOSTVARS,
        net_map_stub_data.TEST_GROUPS,
        options=networking_mapper.NetworkingMapperOptions(
            interfaces_info_translations={
                net_map_stub_data.NETWORK_1_NAME: ["ctlplane"]
            }
        ),
    )
    mapped_content = mapper.map(
        net_map_stub_data.get_test_file_yaml_content(test_input_config_file),
        test_interfaces_info or net_map_stub_data.TEST_IFACES_INFO,
    )
    assert mapped_content == net_map_stub_data.get_test_file_json_content(
        test_golden_file
    )


def test_networking_mapper_full_map_invalid_facts_fail():
    # Ensure that ansible_<interface> exists
    with pytest.raises(exceptions.NetworkMappingError) as exc_info:
        test_hostvars = copy.deepcopy(net_map_stub_data.TEST_HOSTVARS)
        test_hostvars[net_map_stub_data.INSTANCE_2_NAME].pop(
            net_map_stub_data.ANSIBLE_HOSTVARS_INTERFACE_ETH0
        )
        mapper = networking_mapper.NetworkingDefinitionMapper(
            test_hostvars, net_map_stub_data.TEST_GROUPS
        )
        mapper.map(
            net_map_stub_data.get_test_file_yaml_content(
                "networking-definition-valid-all-tools-dual-stack.yml"
            ),
            net_map_stub_data.TEST_IFACES_INFO,
        )
    assert "ansible_eth0" in str(exc_info.value)


def test_networking_mapper_full_map_missing_ansible_interfaces_ok():
    test_hostvars = copy.deepcopy(net_map_stub_data.TEST_HOSTVARS)
    test_hostvars[net_map_stub_data.INSTANCE_2_NAME].pop(
        net_map_stub_data.ANSIBLE_HOSTVARS_INTERFACES
    )
    mapper = networking_mapper.NetworkingDefinitionMapper(
        test_hostvars, net_map_stub_data.TEST_GROUPS
    )
    network_env = mapper.map(
        net_map_stub_data.get_test_file_yaml_content(
            "networking-definition-valid-all-tools-dual-stack.yml"
        ),
        net_map_stub_data.TEST_IFACES_INFO,
    )
    assert net_map_stub_data.INSTANCE_2_NAME in network_env["instances"]
    instance_2_nets = network_env["instances"][net_map_stub_data.INSTANCE_2_NAME][
        "networks"
    ]
    network_1 = instance_2_nets.get("network-1", None)
    network_3 = instance_2_nets.get("network-3", None)
    assert network_1
    assert network_3

    network_1_mac = network_1.get("mac_addr", None)
    assert (
        net_map_stub_data.TEST_IFACES_INFO[net_map_stub_data.INSTANCE_2_NAME][0][
            net_map_stub_data.TEST_IFACES_INFO_MAC_FIELD
        ]
        == network_1_mac
    )
    assert "interface_name" not in network_1
    assert "interface_name" not in network_3
    assert "mac_addr" in network_3


def test_networking_mapper_full_map_missing_ansible_hostname_ok():
    test_hostvars = copy.deepcopy(net_map_stub_data.TEST_HOSTVARS)
    test_hostvars[net_map_stub_data.INSTANCE_1_NAME].pop(
        net_map_stub_data.ANSIBLE_HOSTVARS_HOSTNAME
    )
    mapper = networking_mapper.NetworkingDefinitionMapper(
        test_hostvars, net_map_stub_data.TEST_GROUPS
    )
    network_env = mapper.map(
        net_map_stub_data.get_test_file_yaml_content(
            "networking-definition-valid-all-tools-dual-stack.yml"
        ),
        net_map_stub_data.TEST_IFACES_INFO,
    )
    assert net_map_stub_data.INSTANCE_1_NAME in network_env["instances"]
    assert "hostname" not in network_env["instances"][net_map_stub_data.INSTANCE_1_NAME]


def test_networking_mapper_map_invalid_ifaces_info_fail():
    # Ensure that interfaces_info 'mac' field is mandatory
    with pytest.raises(exceptions.NetworkMappingError) as exc_info:
        mapper = networking_mapper.NetworkingDefinitionMapper(
            net_map_stub_data.TEST_HOSTVARS, net_map_stub_data.TEST_GROUPS
        )
        ifaces_info = copy.deepcopy(net_map_stub_data.TEST_IFACES_INFO)
        ifaces_info[net_map_stub_data.INSTANCE_1_NAME][0].pop(
            net_map_stub_data.TEST_IFACES_INFO_MAC_FIELD
        )
        mapper.map(
            net_map_stub_data.get_test_file_yaml_content(
                "networking-definition-valid-all-tools-dual-stack.yml"
            ),
            ifaces_info,
        )
    assert "does not contain `mac` field" in str(exc_info.value)


def test_networking_mapper_full_map_mac_not_found_ok():
    # As the mapper works in best-effort mode, if the mac is
    # not found, the map will succeed fetching the mac from
    # the interfaces-info but not mapping ansible_facts
    # fields like the interface_name

    mapper = networking_mapper.NetworkingDefinitionMapper(
        net_map_stub_data.TEST_HOSTVARS, net_map_stub_data.TEST_GROUPS
    )
    ifaces_info = copy.deepcopy(net_map_stub_data.TEST_IFACES_INFO)
    iface_info_mac = "ab:cd:de:f0:12:34"
    ifaces_info[net_map_stub_data.INSTANCE_1_NAME][0][
        net_map_stub_data.TEST_IFACES_INFO_MAC_FIELD
    ] = iface_info_mac
    network_env = mapper.map(
        net_map_stub_data.get_test_file_yaml_content(
            "networking-definition-valid-all-tools-dual-stack.yml"
        ),
        ifaces_info,
    )
    assert net_map_stub_data.INSTANCE_1_NAME in network_env["instances"]
    instance_1_nets = network_env["instances"][net_map_stub_data.INSTANCE_1_NAME][
        "networks"
    ]
    network_1 = instance_1_nets.get("network-1", None)
    assert network_1
    assert iface_info_mac == network_1.get("mac_addr", None)
    assert "interface_name" not in network_1


def test_networking_mapper_search_domain_override_ok():
    networks_definitions_raw = (
        net_map_stub_data.build_valid_network_definition_set_raw()
    )
    mapper = networking_mapper.NetworkingDefinitionMapper(
        net_map_stub_data.TEST_HOSTVARS,
        net_map_stub_data.TEST_GROUPS,
        options=networking_mapper.NetworkingMapperOptions(
            search_domain_base="testing.local"
        ),
    )
    mapped_content = mapper.map_networks({"networks": networks_definitions_raw})
    assert mapped_content
    assert len(mapped_content) == len(networks_definitions_raw)
    for net_content in mapped_content.values():
        search_domain = net_content["search_domain"]
        assert search_domain.endswith("testing.local")

    overriden_search_domain = "testing-net.net"
    networks_definitions_raw[net_map_stub_data.NETWORK_1_NAME][
        "search-domain"
    ] = overriden_search_domain

    mapped_content = mapper.map_networks({"networks": networks_definitions_raw})
    assert mapped_content
    assert net_map_stub_data.NETWORK_1_NAME in mapped_content
    assert (
        mapped_content[net_map_stub_data.NETWORK_1_NAME]["search_domain"]
        == overriden_search_domain
    )


def test_networking_mapper_invalid_instance_fail():
    # Ensure that instances in the netdev are part of the inventory
    with pytest.raises(exceptions.NetworkMappingError) as exc_info:
        hostvars_copy = copy.deepcopy(net_map_stub_data.TEST_HOSTVARS)
        groups_copy = copy.deepcopy(net_map_stub_data.TEST_GROUPS)
        hostvars_copy.pop("instance-1")
        for group_name, instances_names in groups_copy.items():
            if "instance-1" in instances_names:
                instances_names.remove("instance-1")
                instances_names.append("non-existing-instance")
        mapper = networking_mapper.NetworkingDefinitionMapper(
            hostvars_copy, groups_copy
        )

        net_def_raw = net_map_stub_data.get_test_file_yaml_content(
            "networking-definition-valid-all-tools-dual-stack.yml"
        )
        # Replace instance-1 with a new non-existing instance in the
        # interfaces_info dict and net_def
        net_def_instances_raw = net_def_raw["instances"]
        net_def_instances_raw["non-existing-instance"] = net_def_instances_raw[
            "instance-1"
        ]
        net_def_instances_raw.pop("instance-1")
        ifaces_info = copy.deepcopy(net_map_stub_data.TEST_IFACES_INFO)
        ifaces_info["non-existing-instance"] = ifaces_info["instance-1"]
        ifaces_info.pop("instance-1")
        mapper.map(
            net_def_raw,
            ifaces_info,
        )
    assert "non-existing-instance instance is not part of the Ansible inventory" == str(
        exc_info.value
    )


def test_networking_mapper_map_duplicated_net_group_templates_fail():
    # Ensure that a network, for an instance, can be defined only
    # in a single group
    with pytest.raises(exceptions.NetworkMappingError) as exc_info:
        mapper = networking_mapper.NetworkingDefinitionMapper(
            net_map_stub_data.TEST_HOSTVARS, net_map_stub_data.TEST_GROUPS
        )
        net_def_raw = net_map_stub_data.get_test_file_yaml_content(
            "networking-definition-valid-all-tools-ipv6-only.yml"
        )
        net_def_raw["group-templates"]["group-1"]["networks"]["network-2"] = {}
        net_def_raw["group-templates"]["group-1"]["networks"]["network-3"] = {}
        mapper.map(
            net_def_raw,
        )
    assert (
        "networks network-2, network-3 for instance-1 instance are "
        "defined by multiple groups" == str(exc_info.value)
    )
