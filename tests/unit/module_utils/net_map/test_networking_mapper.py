from __future__ import absolute_import, division, print_function

__metaclass__ = type

import copy

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
            "networking-definition-valid-all-tools-dual-stack.yml",
            "networking-definition-valid-all-tools-dual-stack-partial-map-out.json",
        ),
        (
            "networking-definition-valid.yml",
            "networking-definition-valid-partial-map-out.json",
        ),
        (
            "networking-definition-valid-all-tools-ipv6-only.yml",
            "networking-definition-valid-all-tools-ipv6-only-partial-map-out.json",
        ),
        (
            "networking-definition-valid-all-tools.yml",
            "networking-definition-valid-all-tools-partial-map-out.json",
        ),
    ],
)
def test_networking_mapper_full_partial_map_ok(
    test_input_config_file, test_golden_file
):
    mapper = networking_mapper.NetworkingDefinitionMapper(
        net_map_stub_data.TEST_HOSTVARS, net_map_stub_data.TEST_GROUPS
    )
    mapped_content = mapper.map_partial(
        net_map_stub_data.get_test_file_yaml_content(test_input_config_file)
    )
    assert mapped_content == net_map_stub_data.get_test_file_json_content(
        test_golden_file
    )


@pytest.mark.parametrize(
    "test_input_config_file,test_golden_file",
    [
        (
            "networking-definition-valid-all-tools-dual-stack.yml",
            "networking-definition-valid-all-tools-dual-stack-full-map-out.json",
        ),
        (
            "networking-definition-valid.yml",
            "networking-definition-valid-full-map-out.json",
        ),
        (
            "networking-definition-valid-all-tools-ipv6-only.yml",
            "networking-definition-valid-all-tools-ipv6-only-full-map-out.json",
        ),
        (
            "networking-definition-valid-all-tools.yml",
            "networking-definition-valid-all-tools-full-map-out.json",
        ),
    ],
)
def test_networking_mapper_full_map_ok(test_input_config_file, test_golden_file):
    mapper = networking_mapper.NetworkingDefinitionMapper(
        net_map_stub_data.TEST_HOSTVARS, net_map_stub_data.TEST_GROUPS
    )
    mapped_content = mapper.map_complete(
        net_map_stub_data.get_test_file_yaml_content(test_input_config_file),
        net_map_stub_data.TEST_IFACES_INFO,
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
        mapper.map_complete(
            net_map_stub_data.get_test_file_yaml_content(
                "networking-definition-valid-all-tools-dual-stack.yml"
            ),
            net_map_stub_data.TEST_IFACES_INFO,
        )
    assert "ansible_eth0" in str(exc_info.value)

    # Ensure that ansible_interfaces exists
    with pytest.raises(exceptions.NetworkMappingError) as exc_info:
        test_hostvars = copy.deepcopy(net_map_stub_data.TEST_HOSTVARS)
        test_hostvars[net_map_stub_data.INSTANCE_2_NAME].pop(
            net_map_stub_data.ANSIBLE_HOSTVARS_INTERFACES
        )
        mapper = networking_mapper.NetworkingDefinitionMapper(
            test_hostvars, net_map_stub_data.TEST_GROUPS
        )
        mapper.map_complete(
            net_map_stub_data.get_test_file_yaml_content(
                "networking-definition-valid-all-tools-dual-stack.yml"
            ),
            net_map_stub_data.TEST_IFACES_INFO,
        )
    assert "ansible_interfaces" in str(exc_info.value)

    # Ensure that ansible_hostname exists
    with pytest.raises(exceptions.NetworkMappingError) as exc_info:
        test_hostvars = copy.deepcopy(net_map_stub_data.TEST_HOSTVARS)
        test_hostvars[net_map_stub_data.INSTANCE_1_NAME].pop(
            net_map_stub_data.ANSIBLE_HOSTVARS_HOSTNAME
        )
        mapper = networking_mapper.NetworkingDefinitionMapper(
            test_hostvars, net_map_stub_data.TEST_GROUPS
        )
        mapper.map_complete(
            net_map_stub_data.get_test_file_yaml_content(
                "networking-definition-valid-all-tools-dual-stack.yml"
            ),
            net_map_stub_data.TEST_IFACES_INFO,
        )
    assert "ansible_hostname" in str(exc_info.value)


def test_networking_mapper_full_map_invalid_ifaces_info_fail():
    # Ensure that interfaces_info 'mac' field is mandatory
    with pytest.raises(exceptions.NetworkMappingError) as exc_info:
        mapper = networking_mapper.NetworkingDefinitionMapper(
            net_map_stub_data.TEST_HOSTVARS, net_map_stub_data.TEST_GROUPS
        )
        ifaces_info = copy.deepcopy(net_map_stub_data.TEST_IFACES_INFO)
        ifaces_info[net_map_stub_data.INSTANCE_1_NAME].pop(
            net_map_stub_data.TEST_IFACES_INFO_MAC_FIELD
        )
        mapper.map_complete(
            net_map_stub_data.get_test_file_yaml_content(
                "networking-definition-valid-all-tools-dual-stack.yml"
            ),
            ifaces_info,
        )
    assert "does not contain mac address" in str(exc_info.value)

    # Ensure that the ansible instance can be located by MAC
    with pytest.raises(exceptions.NetworkMappingError) as exc_info:
        mapper = networking_mapper.NetworkingDefinitionMapper(
            net_map_stub_data.TEST_HOSTVARS, net_map_stub_data.TEST_GROUPS
        )
        ifaces_info = copy.deepcopy(net_map_stub_data.TEST_IFACES_INFO)
        ifaces_info[net_map_stub_data.INSTANCE_1_NAME][
            net_map_stub_data.TEST_IFACES_INFO_MAC_FIELD
        ] = "ab:cd:de:f0:12:34"
        mapper.map_complete(
            net_map_stub_data.get_test_file_yaml_content(
                "networking-definition-valid-all-tools-dual-stack.yml"
            ),
            ifaces_info,
        )
    assert "not found" in str(exc_info.value)

    # Ensure that the all instances are present in ifaces_info
    with pytest.raises(exceptions.NetworkMappingError) as exc_info:
        mapper = networking_mapper.NetworkingDefinitionMapper(
            net_map_stub_data.TEST_HOSTVARS, net_map_stub_data.TEST_GROUPS
        )
        ifaces_info = copy.deepcopy(net_map_stub_data.TEST_IFACES_INFO)
        ifaces_info.pop(net_map_stub_data.INSTANCE_1_NAME)
        mapper.map_complete(
            net_map_stub_data.get_test_file_yaml_content(
                "networking-definition-valid-all-tools-dual-stack.yml"
            ),
            ifaces_info,
        )
    assert "does not contain information for instance-1" in str(exc_info.value)


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
        mapper.map_partial(
            net_def_raw,
        )
    assert (
        "networks network-2, network-3 for instance-1 instance are "
        "defined by multiple groups" == str(exc_info.value)
    )
