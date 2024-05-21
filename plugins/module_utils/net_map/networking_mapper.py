import collections
import dataclasses
import ipaddress
import json
import random
import re
import typing

from ansible_collections.cifmw.general.plugins.module_utils.net_map import (
    exceptions,
    ip_pools,
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
    interfaces_info_translations: typing.Dict[str, typing.List[str]] = None

    @classmethod
    def from_dict(cls, data: typing.Dict[str, typing.Any]) -> "NetworkingMapperOptions":
        """Creates a NetworkingMapperOptions from a dict.

        Unknown keys are ignored.

        Returns: The new NetworkingMapperOptions instance.

        """
        field_names = {field.name for field in dataclasses.fields(cls)}
        return cls(
            **{
                field_name: value
                for field_name, value in data.items()
                if field_name in field_names
            }
        )


class NetMapperJsonEncoder(json.JSONEncoder):
    """
    JSON encoder for networks definitions mappings

    Allows encoding complex types contained in definitions
    as strings using the expected format.
    """

    def default(self, o):
        """
        Extends the default behavior of JSONEncoder default method
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


class NetworkingInstanceMapper:
    """Converts the Networking Definition and facts into a MappedInstance

    Handles the conversion of the Networking Definition into a
    MappedInstance for a given instance.
    The mapper uses the Networking Definition as the main source of truth
    to generate a MappedInstance. However, it uses other pieces of information
    such as Ansible's gathered facts and the MAC address of the interface
    to support the mapping process.
    """

    def __init__(
        self,
        instance_name,
        pools_manager: ip_pools.IPPoolsManager,
        options: NetworkingMapperOptions = None,
        host_vars: typing.Dict[str, typing.Any] = None,
        group_templates: typing.Dict[
            str, networking_definition.GroupTemplateDefinition
        ] = None,
        instance_definition: networking_definition.InstanceDefinition = None,
        interfaces_info: typing.List[typing.Dict[str, typing.Any]] = None,
    ):
        """Initializes a NetworkingInstanceMapper

        Args:
           instance_name: The name of instance associated with the mapper.
           pools_manager: The ip_pools.IPPoolsManager instance.
           host_vars: Ansible's hostvars content.
           group_templates: A dict of all the
               networking_definition.GroupTemplateDefinition that applies
               to the instance. Optional.
           instance_definition: The networking_definition.InstanceDefinition
               of the instance. Optional.
           interfaces_info: A list of dicts of interface-related information. If given,
               each element must contain a `mac` field with the network interface
               MAC address of the instance.
        """
        self.__instance_name = instance_name
        self.__pools_manager = pools_manager
        self.__host_vars = host_vars
        self.__options = options
        self.__instance_definition: typing.Union[
            networking_definition.InstanceDefinition, None
        ] = instance_definition
        self.__group_templates: typing.Dict[
            str, networking_definition.GroupTemplateDefinition
        ] = (group_templates or {})
        self.__interfaces_info = interfaces_info or []
        self.__add_instance_reservation(instance_definition, pools_manager)

    @property
    def instance_name(self) -> str:
        """Name of the instance."""
        return self.__instance_name

    @staticmethod
    def __add_instance_reservation(
        instance_definition: networking_definition.InstanceDefinition,
        pools_manager: ip_pools.IPPoolsManager,
    ):
        if not instance_definition:
            return

        for net_name, instance_net in instance_definition.networks.items():
            if instance_net.ipv4:
                pools_manager.add_instance_reservation(net_name, instance_net.ipv4)
            if instance_net.ipv6:
                pools_manager.add_instance_reservation(net_name, instance_net.ipv6)

    def __map_instance_network(
        self,
        instance_net_definition: networking_definition.InstanceNetworkDefinition = None,
        group_net_def: networking_definition.GroupTemplateNetworkDefinition = None,
    ) -> networking_env_definitions.MappedInstanceNetwork:
        if not (instance_net_definition or group_net_def):
            raise exceptions.NetworkMappingError(
                "Mapper needs at least a group template or instance network "
                "definition to create an instance network"
            )

        net_def = (
            instance_net_definition.network
            if instance_net_definition
            else group_net_def.network
        )

        ipv4, ipv6 = self.__map_instance_network_ips(
            net_def.name, group_net_def, instance_net_definition
        )
        iface_data = self.__map_instance_network_interface_data(net_def)
        device_name = iface_data.get("device", None)
        interface_name = (
            f"{device_name}.{net_def.vlan}"
            if device_name and net_def.vlan
            else device_name
        )
        mtu = net_def.mtu if net_def.mtu is not None else iface_data.get("mtu", None)
        return networking_env_definitions.MappedInstanceNetwork(
            net_def.name,
            skip_nm=self.__map_instance_net_skip_nm(
                group_net_def, instance_net_definition
            ),
            ip_v4=ipv4,
            netmask_v4=net_def.ipv4_network.netmask if ipv4 else None,
            prefix_length_v4=net_def.ipv4_network.prefixlen if ipv4 else None,
            ip_v6=ipv6,
            netmask_v6=net_def.ipv6_network.netmask if ipv6 else None,
            prefix_length_v6=net_def.ipv6_network.prefixlen if ipv6 else None,
            mtu=int(mtu) if mtu else None,
            vlan_id=net_def.vlan,
            parent_interface=device_name if net_def.vlan else None,
            interface_name=interface_name,
            mac_addr=self.__map_instance_network_interface_mac(
                iface_data.get("macaddress", None), net_def
            ),
            is_trunk_parent=self.__map_instance_net_is_trunk_parent(
                group_net_def, instance_net_definition
            ),
            trunk_parent=self.__map_instance_net_trunk_parent(
                group_net_def, instance_net_definition
            ),
        )

    def __map_instance_net_skip_nm(
        self,
        group_net_def: typing.Optional[
            networking_definition.GroupTemplateNetworkDefinition
        ],
        instance_net_definition: typing.Optional[
            networking_definition.InstanceNetworkDefinition
        ],
    ):
        skip_nm = (
            instance_net_definition.skip_nm_configuration
            if instance_net_definition
            and instance_net_definition.skip_nm_configuration is not None
            else (
                group_net_def.skip_nm_configuration
                if group_net_def and group_net_def.skip_nm_configuration is not None
                else None
            )
        )
        if skip_nm is None:
            skip_nm = (
                self.__instance_definition.skip_nm_configuration
                if self.__instance_definition
                and self.__instance_definition.skip_nm_configuration is not None
                else False
            )
        return skip_nm

    def __map_instance_net_is_trunk_parent(
        self,
        group_net_def: typing.Optional[
            networking_definition.GroupTemplateNetworkDefinition
        ],
        instance_net_definition: typing.Optional[
            networking_definition.InstanceNetworkDefinition
        ],
    ):
        is_trunk_parent = (
            instance_net_definition.is_trunk_parent
            if instance_net_definition
            and instance_net_definition.is_trunk_parent is not None
            else (
                group_net_def.is_trunk_parent
                if group_net_def and group_net_def.is_trunk_parent is not None
                else None
            )
        )

        return is_trunk_parent

    def __map_instance_net_trunk_parent(
        self,
        group_net_def: typing.Optional[
            networking_definition.GroupTemplateNetworkDefinition
        ],
        instance_net_definition: typing.Optional[
            networking_definition.InstanceNetworkDefinition
        ],
    ):
        trunk_parent = (
            instance_net_definition.trunk_parent
            if instance_net_definition
            and instance_net_definition.trunk_parent is not None
            else (
                group_net_def.trunk_parent
                if group_net_def and group_net_def.trunk_parent is not None
                else None
            )
        )
        return trunk_parent

    @staticmethod
    def __map_instance_network_interface_mac(
        interface_mac: typing.Optional[str],
        net_def: networking_definition.NetworkDefinition,
    ) -> typing.Optional[str]:
        if interface_mac:
            return interface_mac
        random_inst = random.Random()
        random_inst.seed(a=net_def.name)
        mac_bytes = [
            0x52,
            0x54,
            0x00,
            random_inst.randint(0x00, 0x7F),
            random_inst.randint(0x00, 0xFF),
            random_inst.randint(0x00, 0xFF),
        ]

        return ":".join(map(lambda x: "%02x" % x, mac_bytes))

    def __map_instance_network_interface_data(
        self, net_def: networking_definition.NetworkDefinition
    ) -> typing.Optional[typing.Dict[str, typing.Any]]:
        interfaces_info_mac = None
        for iface_info in self.__interfaces_info:
            interfaces_info_net_name = iface_info.get("network", None)
            if not interfaces_info_net_name:
                raise exceptions.NetworkMappingError(
                    f"interface information for {self.__instance_name} instance "
                    "does not contain `network` field"
                )
            if interfaces_info_net_name == net_def.name or (
                net_def.name
                in (self.__options.interfaces_info_translations or {}).get(
                    interfaces_info_net_name, []
                )
            ):
                if "mac" not in iface_info:
                    raise exceptions.NetworkMappingError(
                        f"interface information for {self.__instance_name} instance and {interfaces_info_net_name} "
                        "network does not contain `mac` field"
                    )
                interfaces_info_mac = iface_info["mac"]
                break

        interface_data = {}
        if interfaces_info_mac:
            interface_data = (
                self.__map_instance_network_interface_ansible_data(interfaces_info_mac)
                or {}
            )
            if "macaddress" not in interface_data:
                interface_data["macaddress"] = interfaces_info_mac.lower()
        return interface_data

    def __map_instance_network_interface_ansible_data(
        self, interfaces_info_mac: typing.Optional[str]
    ) -> typing.Optional[typing.Dict[str, typing.Any]]:
        ansible_interfaces = self.__host_vars.get("ansible_interfaces", [])
        for iface_name in ansible_interfaces:
            # Ansible internally replaces `-` and `:` by _ to create safe facts names
            iface_fact_name = f"ansible_{iface_name}".replace("-", "_").replace(
                ":", "_"
            )
            ansible_iface_data = self.__host_vars.get(iface_fact_name, None)
            if not ansible_iface_data:
                raise exceptions.NetworkMappingError(
                    f"Ansible facts are inconsistent for {self.__instance_name} host. "
                    f"ansible_interfaces is present but {iface_fact_name} it's not."
                )
            mac = ansible_iface_data.get("macaddress", None)
            if mac and mac.lower() == interfaces_info_mac.lower():
                return ansible_iface_data
        return None

    def __map_instance_network_ips(
        self,
        net_name: str,
        group_net_def: typing.Optional[
            networking_definition.GroupTemplateNetworkDefinition
        ],
        instance_net_definition: typing.Optional[
            networking_definition.InstanceNetworkDefinition
        ],
    ):
        ipv4 = self.__map_instance_network_ipv4(
            group_net_def, instance_net_definition, net_name
        )
        ipv6 = self.__map_instance_network_ipv6(
            group_net_def, instance_net_definition, net_name
        )
        if not ipv4 and not ipv6:
            raise exceptions.NetworkMappingError(
                f"Mapper needs explicit IPs for {self.__instance_name}'s {net_name} "
                "network or an association group with a range declared"
            )
        return ipv4, ipv6

    def __map_instance_network_ipv4(
        self,
        group_net_def: typing.Optional[
            networking_definition.GroupTemplateNetworkDefinition
        ],
        instance_net_definition: typing.Optional[
            networking_definition.InstanceNetworkDefinition
        ],
        net_name: str,
    ) -> typing.Optional[ipaddress.IPv4Address]:
        ip = None
        if instance_net_definition and instance_net_definition:
            ip = instance_net_definition.ipv4

        elif group_net_def and group_net_def.ipv4_range:
            ip = self.__pools_manager.get_ipv4(
                group_net_def.group_name,
                net_name,
                self.__instance_name,
            )

        return ip

    def __map_instance_network_ipv6(
        self,
        group_net_def: typing.Optional[
            networking_definition.GroupTemplateNetworkDefinition
        ],
        instance_net_definition: typing.Optional[
            networking_definition.InstanceNetworkDefinition
        ],
        net_name: str,
    ) -> typing.Optional[ipaddress.IPv6Address]:
        ip = None
        if instance_net_definition and instance_net_definition:
            ip = instance_net_definition.ipv6

        elif group_net_def and group_net_def.ipv6_range:
            ip = self.__pools_manager.get_ipv6(
                group_net_def.group_name,
                net_name,
                self.__instance_name,
            )

        return ip

    def __map_instance_networks(
        self,
    ) -> typing.Dict[str, networking_env_definitions.MappedInstanceNetwork]:
        net_names_set = set()
        if self.__instance_definition:
            net_names_set.update(self.__instance_definition.networks.keys())

        group_template_nets = [
            (item.network.name, item)
            for sublist in self.__group_templates.values()
            for item in sublist.networks.values()
        ]

        group_template_net_names_list = [i[0] for i in group_template_nets]
        groups_duplications = [
            item
            for item, count in collections.Counter(
                group_template_net_names_list
            ).items()
            if count > 1
        ]
        if groups_duplications:
            duplications_str = ", ".join(groups_duplications).strip(",").strip(" ")
            raise exceptions.NetworkMappingError(
                f"networks {duplications_str} for {self.__instance_name} "
                "instance are defined by multiple groups"
            )

        instance_nets = {}
        net_names_set.update(group_template_net_names_list)
        for net_name in sorted(net_names_set):
            instance_net = (
                self.__instance_definition.networks.get(net_name, None)
                if self.__instance_definition
                else None
            )
            group_template = next(
                (
                    group_net_tuple[1]
                    for group_net_tuple in group_template_nets
                    if group_net_tuple[0] == net_name
                ),
                None,
            )
            instance_nets[net_name] = self.__map_instance_network(
                instance_net_definition=instance_net,
                group_net_def=group_template,
            )

        return instance_nets

    def map(
        self,
    ) -> networking_env_definitions.MappedInstance:
        """Builds the networking_env_definitions.MappedInstance.

        Returns:
            A mapped instance as networking_env_definitions.MappedInstance.

        Raises:
            exceptions.NetworkMappingError: If any inconsistency is found
                during the mapping process.
        """
        instance_nets = self.__map_instance_networks()
        hostname = self.__host_vars.get("ansible_hostname", None)
        return networking_env_definitions.MappedInstance(
            self.__instance_name,
            instance_nets,
            hostname=hostname,
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
                net_def.metallb_config,
                networking_env_definitions.MappedMetallbNetworkConfig,
            )
            if net_def.metallb_config
            else None
        )
        multus = (
            self.__build_network_tool_common(
                net_def.multus_config,
                networking_env_definitions.MappedMultusNetworkConfig,
            )
            if net_def.multus_config
            else None
        )
        netconfig = (
            self.__build_network_tool_common(
                net_def.netconfig_config,
                networking_env_definitions.MappedNetconfigNetworkConfig,
            )
            if net_def.netconfig_config
            else None
        )

        return networking_env_definitions.MappedNetworkTools(metallb, multus, netconfig)

    @staticmethod
    def __build_network_tool_common(
        tool_net_def: networking_definition.SubnetBasedNetworkToolDefinition,
        tool_type: typing.Type,
    ) -> typing.Union[
        networking_env_definitions.MappedMetallbNetworkConfig,
        networking_env_definitions.MappedMultusNetworkConfig,
        networking_env_definitions.MappedNetconfigNetworkConfig,
    ]:
        args_list = [
            [
                _map_host_network_range_to_output(ip_range)
                for ip_range in tool_net_def.ranges_ipv4
            ],
            [
                _map_host_network_range_to_output(ip_range)
                for ip_range in tool_net_def.ranges_ipv6
            ],
        ]
        return tool_type(*args_list)


class NetworkingRoutersMapper:
    """
    Handles the mapping of Networking Definition routers section
    """

    def map_routers(
        self,
        router_definitions: typing.Dict[str, networking_definition.RouterDefinition],
    ) -> typing.Dict[str, networking_env_definitions.MappedRouter]:
        return {
            router_name: self.__map_single_router(router_name, router_def)
            for router_name, router_def in router_definitions.items()
        }

    @staticmethod
    def __map_single_router(
        router_name: str, router_def: networking_definition.RouterDefinition
    ) -> networking_env_definitions.MappedRouter:
        return networking_env_definitions.MappedRouter(
            router_name,
            router_def.networks,
            router_def.external_network,
        )


class NetworkingDefinitionMapper:
    """
    Converts the Networking Definition into the Networking Environment Definition

    It handles Networking Definition and related parsings and mappings.
    """

    __FIELD_HOSTVARS_GROUPS = "groups"

    def __init__(
        self,
        host_vars: typing.Dict[str, typing.Any],
        groups: typing.Dict[str, typing.List[str]],
        options: NetworkingMapperOptions = None,
    ):
        """Initializes a NetworkingDefinitionMapper

        Args:
            host_vars: Ansible hostvars variable.
            groups: Ansible groups variable.
            options: Additional, optional, settings for the mapper.
        """
        self.__host_vars = host_vars
        self.__groups = groups
        self.__options = options or NetworkingMapperOptions()
        self.__networks_mapper = NetworkingNetworksMapper(self.__options)
        self.__routers_mapper = NetworkingRoutersMapper()

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
        net_definition = self.__parse_validate_net_definition(network_definition_raw)

        networks = self.__networks_mapper.map_networks(net_definition.networks)
        return self.__safe_encode_to_primitives(networks)

    def map_routers(self, network_definition_raw: typing.Dict[str, typing.Any]):
        """
        Parses, validates and maps a Networking Definition into a router dictionary

        The resulting mapping is a dictionary that only contains primitive types.

        Args:
            network_definition_raw: The Networking Definition to map.
        Returns: The mapped routers as a dictionary.
        Raises:
            exceptions.NetworkMappingValidationError:
                If not provided, or it's not a dictionary.
        """
        net_definition = self.__parse_validate_net_definition(network_definition_raw)
        routers = self.__routers_mapper.map_routers(net_definition.routers)

        return self.__safe_encode_to_primitives(routers)

    def map(
        self,
        network_definition_raw: typing.Dict[str, typing.Any],
        interfaces_info: typing.Dict[str, typing.Any] = None,
    ) -> typing.Dict[str, typing.Any]:
        """
        Parses, validates and maps a Networking Definition into a partially complete
        networking_env_definitions.NetworkingEnvironmentDefinition that doesn't contain
        information of an existing instance, such as MAC address, interface name, etc.

        The resulting mapping is a dictionary that only contains primitive types.

        Args:
            network_definition_raw: The Networking Definition to map.
            interfaces_info: Dict containing the MAC addresses of each instance.
             Optional.

        Returns: The Networking Environment Definition as a dictionary.
        Raises:
            exceptions.NetworkMappingValidationError:
                If network_definition_raw is not provided, or it's not a dictionary.
            exceptions.NetworkMappingError: If any inconsistency is found
                during the mapping process.
        """
        if interfaces_info is not None and not isinstance(interfaces_info, dict):
            raise exceptions.NetworkMappingValidationError(
                "interfaces_info must be a list of dicts"
            )

        net_definition = self.__parse_validate_net_definition(network_definition_raw)
        inst_groups_of_interest = self.__create_instances_dict(net_definition)
        pools_manager = ip_pools.IPPoolsManager(net_definition.group_templates)
        instance_mappers = self.__build_instances_net_mappers(
            inst_groups_of_interest,
            net_definition,
            pools_manager,
            interfaces_info=interfaces_info,
        )
        instances = {
            instance_mapper.instance_name: instance_mapper.map()
            for instance_mapper in instance_mappers
        }
        networks = self.__networks_mapper.map_networks(net_definition.networks)

        routers = self.__routers_mapper.map_routers(net_definition.routers)

        net_def_env = networking_env_definitions.NetworkingEnvironmentDefinition(
            networks, instances, routers
        )
        return self.__safe_encode_to_primitives(net_def_env)

    @staticmethod
    def __parse_validate_net_definition(
        network_definition_raw,
    ) -> networking_definition.NetworkingDefinition:
        if not isinstance(network_definition_raw, dict):
            raise exceptions.NetworkMappingValidationError(
                "network_definition_raw is a mandatory dict"
            )
        net_definition = networking_definition.NetworkingDefinition(
            network_definition_raw
        )
        return net_definition

    def __create_instances_dict(
        self, net_def: networking_definition.NetworkingDefinition
    ) -> typing.Dict[str, typing.List[str]]:
        instance_group_dict = {}
        for group_name, instances in self.__groups.items():
            # Skip groups that are not related/associated to networking
            if group_name not in net_def.group_templates:
                continue
            for instance_name in instances:
                if instance_name not in instance_group_dict:
                    instance_group_dict[instance_name] = []
                instance_group_dict[instance_name].append(group_name)
        for instance_name in net_def.instances.keys():
            if instance_name not in instance_group_dict:
                instance_group_dict[instance_name] = []
        return instance_group_dict

    def __build_instances_net_mappers(
        self,
        instance_groups: typing.Dict[str, typing.List[str]],
        net_definition: networking_definition.NetworkingDefinition,
        pools_manager: ip_pools.IPPoolsManager,
        interfaces_info: typing.Optional[
            typing.Dict[str, typing.List[typing.Dict[str, typing.Any]]]
        ] = None,
    ) -> typing.List[NetworkingInstanceMapper]:
        instance_nets_mappers: typing.List[NetworkingInstanceMapper] = []
        for instance_name, instance_groups in instance_groups.items():
            instance_definition = net_definition.instances.get(instance_name, None)

            groups_template_definitions = {
                group_template.group_name: group_template
                for group_template in net_definition.group_templates.values()
                if group_template.group_name in instance_groups
            }

            if interfaces_info is not None and instance_name not in interfaces_info:
                raise exceptions.NetworkMappingError(
                    f"interfaces_info does not contain information for {instance_name}"
                )
            elif interfaces_info is not None and instance_name not in self.__host_vars:
                raise exceptions.NetworkMappingError(
                    f"{instance_name} instance is not part of the Ansible inventory"
                )

            instance_interfaces_info = (
                interfaces_info[instance_name] if interfaces_info else None
            )
            if instance_interfaces_info is not None and not isinstance(
                instance_interfaces_info, list
            ):
                raise exceptions.NetworkMappingError(
                    f"interfaces_info for {instance_name} instance must be a list of dicts"
                )
            instance_nets_mappers.append(
                NetworkingInstanceMapper(
                    instance_name,
                    pools_manager,
                    self.__options,
                    self.__host_vars.get(instance_name, {}),
                    instance_definition=instance_definition,
                    group_templates=groups_template_definitions,
                    interfaces_info=instance_interfaces_info,
                )
            )

        instance_nets_mappers.sort(key=lambda entry: entry.instance_name.lower())
        return instance_nets_mappers

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
