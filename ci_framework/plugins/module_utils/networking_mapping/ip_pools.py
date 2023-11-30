import ipaddress
import typing

from ansible_collections.cifmw.general.plugins.module_utils.networking_mapping import (
    exceptions,
    networking_definition,
)


class IPPool:
    """
    Manages IP assignations in a network range, defined by a HostNetworkRange.
    """

    def __init__(
        self,
        ip_range: networking_definition.HostNetworkRange,
        reservations: typing.List[
            typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address, str]
        ] = None,
    ) -> None:
        self.__index = 0
        self.__range = ip_range
        self.__reservations = set()
        self.__parse_reservations(reservations)

    def add_reservation(
        self,
        reservation: typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address, str],
    ):
        """Adds an IP as reserved

         The IPPool takes this into account when giving addresses in such a way
         it's never returned.

        Args:
            reservation: The IP to reserve

        Raises:
            exceptions.NetworkMappingError: If the IP is out of the range of the pool.

        """
        reservation_ip = ipaddress.ip_address(reservation)
        if reservation_ip not in self.__range:
            raise exceptions.NetworkMappingError(
                f"Reservation {reservation} is out of range {self.__range}"
            )
        self.__reservations.add(reservation_ip)

    @property
    def range(self) -> networking_definition.HostNetworkRange:
        """The range of IPs of the pool"""
        return self.__range

    def get_ip(self) -> typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]:
        """Request a new IP

        Returns: A new IPv4/v6 from the pool

        Raises:
            exceptions.NetworkMappingError: If the IPPool is exhausted.
        """
        while self.__index < self.__range.length:
            ip = self.__range.start_ip + self.__index
            self.__index = self.__index + 1
            if ip not in self.__reservations:
                return ip

        raise exceptions.NetworkMappingError(f"IP Pool for {self.__range} exhausted")

    def __parse_reservations(
        self,
        reservations: typing.List[
            typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address, str]
        ] = None,
    ):
        for reservation in reservations or []:
            self.add_reservation(reservation)

    def __contains__(self, element):
        return element in self.__range


class IPPoolsManager:
    """Manages IPPools for a set of GroupTemplateDefinitions.

    This class serves as an entry point for manipulating IPPools
    in a centralized way.

    """

    def __init__(
        self,
        group_templates: typing.Dict[
            str, networking_definition.GroupTemplateDefinition
        ],
    ):
        """Instantiates the IPPoolsManager and its IPPools

        Args:
            group_templates: The list of GroupTemplateDefinition for
                which the IPPools should be created.
        """
        self.__pools_table_v4: typing.Dict[str, typing.Dict[str, IPPool]] = {}
        self.__pools_table_v6: typing.Dict[str, typing.Dict[str, IPPool]] = {}
        self.__assignations_v4: typing.Dict[
            str,
            typing.Dict[str, typing.Union[ipaddress.IPv4Address]],
        ] = {}
        self.__assignations_v6: typing.Dict[
            str,
            typing.Dict[str, typing.Union[ipaddress.IPv6Address]],
        ] = {}
        self.__init(group_templates)

    def add_instance_reservation(
        self,
        network_name: str,
        reservation: typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address],
    ):
        """Adds an IPv4/v6 as reserved in a network.

        This method adds the given IP to all the pools of the
        given network as reserved.

        Args:
            network_name: The name of the network were the IP should be reserved.
            reservation: THe IP to set as reserved.

        """
        pool_table = (
            self.__pools_table_v6 if reservation.version == 6 else self.__pools_table_v4
        )
        for group_nets in pool_table.values():
            net_pool = group_nets.get(network_name, None)
            if net_pool and (reservation in net_pool):
                net_pool.add_reservation(reservation)

    def get_ipv4(
        self, group_name, network_name, instance_name: str
    ) -> ipaddress.IPv4Address:
        """Fetches an IPv4 address for a group's instance in a given net

        If the instance already has an IPv4 for that group and network, the
        existing value will be returned.

        Args:
            group_name: The group for which IP is requested
            network_name: The network for which IP is requested
            instance_name: The name of the instance for which IP is requested

        Returns: The requested IPv4.

        Raises:
            exceptions.NetworkMappingError: If any of the following conditions:
                The group doesn't exist.
                The network doesn't exist for the given group.
                The underlying IPPool is exhausted.

        """
        return self.__get_ip(
            self.__pools_table_v4,
            self.__assignations_v4,
            group_name,
            network_name,
            instance_name,
        )

    def get_ipv6(
        self, group_name, network_name, instance_name: str
    ) -> ipaddress.IPv6Address:
        """Fetches an IPv6 address for a group's instance in a given net

        If the instance already has an IPv6 for that group and network, the
        existing value will be returned.

        Args:
            group_name: The group for which IP is requested
            network_name: The network for which IP is requested
            instance_name: The name of the instance for which IP is requested

        Returns: The requested IPv6.

        Raises:
            exceptions.NetworkMappingError: If any of the following conditions:
                The group doesn't exist.
                The network doesn't exist for the given group.
                The underlying IPPool is exhausted.

        """
        return self.__get_ip(
            self.__pools_table_v6,
            self.__assignations_v6,
            group_name,
            network_name,
            instance_name,
        )

    @staticmethod
    def __get_ip(
        pools_table: typing.Dict[str, typing.Dict[str, IPPool]],
        assignations_table: typing.Dict[
            str,
            typing.Dict[
                str, typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]
            ],
        ],
        group_name,
        network_name,
        instance_name: str,
    ):
        assigned_ip = assignations_table.get(network_name, {}).get(instance_name, None)
        if assigned_ip:
            return assigned_ip

        group_pools = pools_table.get(group_name, None)
        if not group_pools:
            raise exceptions.NetworkMappingError(
                f"Cannot assign IP to group {group_name} "
                "cause there is no IP pool for it"
            )

        ip_pool = group_pools.get(network_name, None)
        if not ip_pool:
            raise exceptions.NetworkMappingError(
                f"Cannot assign IP to {network_name} in {group_name} "
                f"group cause there is no IP pool for it"
            )

        ip = ip_pool.get_ip()
        if network_name not in assignations_table:
            assignations_table[network_name] = {}
        assignations_table[network_name][instance_name] = ip

        return ip

    def __init(
        self,
        group_templates: typing.Dict[
            str, networking_definition.GroupTemplateDefinition
        ],
    ):
        for hosts_group, host_template in group_templates.items():
            if hosts_group not in self.__pools_table_v4:
                self.__pools_table_v4[hosts_group] = {}
            if hosts_group not in self.__pools_table_v6:
                self.__pools_table_v6[hosts_group] = {}
            for net_name, host_template_net in host_template.networks.items():
                if host_template_net.ipv4_range:
                    self.__pools_table_v4[hosts_group][
                        host_template_net.network.name
                    ] = IPPool(host_template_net.ipv4_range)
                if host_template_net.ipv6_range:
                    self.__pools_table_v6[hosts_group][
                        host_template_net.network.name
                    ] = IPPool(host_template_net.ipv6_range)
