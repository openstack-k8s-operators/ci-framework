import dataclasses
import ipaddress
import json
import re
import typing

from ansible_collections.cifmw.general.plugins.module_utils.net_map import (
    exceptions,
    networking_definition,
    networking_env_definitions,
)


@dataclasses.dataclass
class NetworkingMapperOptions:
    """
    Custom options for the NetworkingDefinitionMapper

    Attributes:
        search_domain_base: The domain to use when generating
            network's search domains based on their names.

    """

    search_domain_base: str = None


class NetMapperJsonEncoder(json.JSONEncoder):
    """
    JSON encoder for networks definitions mappings

    Allows encoding complex types contained in definitions
    as strings using the expected format.
    """

    def default(self, o):
        """
        Extends the default behaviour of JSONEncoder default method
        by allowing serializing IPv4Network, IPv6Network, IPv4Address,
        IPv6Address (extended CIDR notation) as string and dataclasses
        as plain dictionaries.

        Args:
            o: The object to encode as JSON.

        Returns: The encoded value of the object.

        """
        if o is None:
            return None
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, ipaddress.IPv6Address):
            return str(o.exploded)
        if isinstance(
            o,
            (
                ipaddress.IPv4Network,
                ipaddress.IPv6Network,
                ipaddress.IPv4Address,
            ),
        ):
            return str(o)
        return super().default(o)


def _map_host_network_range_to_output(
    host_net_range: networking_definition.HostNetworkRange,
) -> typing.Union[
    networking_env_definitions.MappedIpv4NetworkRange,
    networking_env_definitions.MappedIpv6NetworkRange,
]:
    args = [
        host_net_range.start_ip,
        host_net_range.start_host,
        host_net_range.end_ip,
        host_net_range.start_host + host_net_range.length - 1,
        host_net_range.length,
    ]
    return (
        networking_env_definitions.MappedIpv4NetworkRange(*args)
        if host_net_range.network.version == 4
        else networking_env_definitions.MappedIpv6NetworkRange(*args)
    )


class NetworkingNetworksMapper:
    """
    Handles the mapping of the Networking Definition networks section.
    """

    __DEFAULT_SEARCH_DOMAIN_BASE = "example.com"

    def __init__(
        self,
        options: NetworkingMapperOptions,
    ):
        self.__options = options

    def map_networks(
        self,
        network_definitions: typing.Dict[str, networking_definition.NetworkDefinition],
    ) -> typing.Dict[str, networking_env_definitions.MappedNetwork]:
        """
        Maps a dictionary of networking_definition.NetworkDefinition into
         a dictionary of mapped networks.

        The resulting mapping is a dictionary that only contains primitive types.

        Args:
            network_definitions: The networking_definition.NetworkDefinition dict
                to map to networking_env_definitions.MappedNetwork.

        Returns: The mapped networks as a dictionary.
        """
        return {
            net_name: self.__map_single_net(net_name, net_def)
            for net_name, net_def in network_definitions.items()
        }

    def __map_single_net(
        self, net_name: str, net_def: networking_definition.NetworkDefinition
    ) -> networking_env_definitions.MappedNetwork:
        return networking_env_definitions.MappedNetwork(
            net_name,
            self.__build_search_domain(net_def),
            self.__build_network_tools(net_def),
            net_def.ipv4_dns,
            net_def.ipv6_dns,
            network_v4=net_def.ipv4_network,
            network_v6=net_def.ipv6_network,
            gw_v4=net_def.ipv4_gateway,
            gw_v6=net_def.ipv6_gateway,
            vlan_id=net_def.vlan,
            mtu=net_def.mtu,
        )

    def __build_search_domain(
        self, net_def: networking_definition.NetworkDefinition
    ) -> str:
        if net_def.search_domain:
            return net_def.search_domain
        base_name = (
            self.__options.search_domain_base or self.__DEFAULT_SEARCH_DOMAIN_BASE
        )
        sanitized_net_name = re.sub(r"[^a-zA-Z\d\-.]", "-", net_def.name).rstrip("-")
        return f"{sanitized_net_name}.{base_name.lstrip('.')}"

    def __build_network_tools(
        self, net_def: networking_definition.NetworkDefinition
    ) -> networking_env_definitions.MappedNetworkTools:
        metallb = (
            self.__build_network_tool_common(
                net_def, networking_env_definitions.MappedMetallbNetworkConfig
            )
            if net_def.metallb_config
            else None
        )
        multus = (
            self.__build_network_tool_common(
                net_def, networking_env_definitions.MappedMultusNetworkConfig
            )
            if net_def.multus_config
            else None
        )
        netconfig = (
            self.__build_network_tool_common(
                net_def, networking_env_definitions.MappedNetconfigNetworkConfig
            )
            if net_def.metallb_config
            else None
        )

        return networking_env_definitions.MappedNetworkTools(metallb, multus, netconfig)

    @staticmethod
    def __build_network_tool_common(
        net_def: networking_definition.NetworkDefinition, tool_type: typing.Type
    ) -> typing.Union[
        networking_env_definitions.MappedMetallbNetworkConfig,
        networking_env_definitions.MappedMultusNetworkConfig,
        networking_env_definitions.MappedNetconfigNetworkConfig,
    ]:
        args_list = [
            [
                _map_host_network_range_to_output(ip_range)
                for ip_range in net_def.metallb_config.ranges_ipv4
            ],
            [
                _map_host_network_range_to_output(ip_range)
                for ip_range in net_def.metallb_config.ranges_ipv6
            ],
        ]
        return tool_type(*args_list)


class NetworkingDefinitionMapper:
    """
    Converts the Networking Definition into the Networking Environment Definition

    It handles Networking Definition and related parsings and mappings.
    """

    __FIELD_HOSTVARS_GROUPS = "groups"

    def __init__(
        self,
        host_vars: typing.Dict[str, typing.Any],
        options: NetworkingMapperOptions = None,
    ):
        """Initializes a NetworkingDefinitionMapper

        Args:
            host_vars: Ansible hostvars variable.
            options: Additional, optional, settings for the mapper.
        """
        self.__host_vars = host_vars
        self.__groups: typing.Dict[str, typing.List[str]] = host_vars[
            self.__FIELD_HOSTVARS_GROUPS
        ]
        self.__options = options or NetworkingMapperOptions()
        self.__networks_mapper = NetworkingNetworksMapper(self.__options)

    def map_networks(self, network_definition_raw: typing.Dict[str, typing.Any]):
        """
        Parses, validates and maps a Networking Definition into a network dictionary

        The resulting mapping is a dictionary that only contains primitive types.

        Args:
            network_definition_raw: The Networking Definition to map.

        Returns: The mapped networks as a dictionary.
        Raises:
            exceptions.NetworkMappingValidationError:
                If not provided, or it's not a dictionary.
        """
        if not isinstance(network_definition_raw, dict):
            raise exceptions.NetworkMappingValidationError(
                "network_definition_raw is a mandatory dict"
            )

        net_definition = networking_definition.NetworkingDefinition(
            network_definition_raw
        )

        networks = self.__networks_mapper.map_networks(net_definition.networks)
        return self.__safe_encode_to_primitives(networks)

    @classmethod
    def __encode_cleanup(cls, d: typing.Any) -> typing.Any:
        return {
            key: cls.__encode_cleanup(value) if isinstance(value, dict) else value
            for key, value in d.items()
            if value is not None
        }

    @classmethod
    def __safe_encode_to_primitives(cls, content: typing.Any) -> typing.Any:
        intermediate_repr = json.dumps(content, cls=NetMapperJsonEncoder)
        return cls.__encode_cleanup(json.loads(intermediate_repr))
