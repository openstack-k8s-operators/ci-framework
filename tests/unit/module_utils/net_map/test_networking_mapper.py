from __future__ import absolute_import, division, print_function

__metaclass__ = type


import pytest
from ansible_collections.cifmw.general.plugins.module_utils.net_map import (
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
        net_map_stub_data.TEST_HOSTVARS
    )
    mapped_content = mapper.map_networks(
        net_map_stub_data.get_test_file_yaml_content(test_input_config_file)
    )
    assert mapped_content == net_map_stub_data.get_test_file_json_content(
        test_golden_file
    )


def test_networking_mapper_search_domain_override_ok():
    networks_definitions_raw = (
        net_map_stub_data.build_valid_network_definition_set_raw()
    )
    mapper = networking_mapper.NetworkingDefinitionMapper(
        net_map_stub_data.TEST_HOSTVARS,
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
