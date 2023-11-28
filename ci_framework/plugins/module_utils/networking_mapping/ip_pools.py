import ipaddress
import typing


from ansible_collections.cifmw.general.plugins.module_utils.networking_mapping import (
    exceptions,
    networking_definition,
)


class IPPool:
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
        reservation_ip = ipaddress.ip_address(reservation)
        if reservation_ip not in self.__range:
            raise exceptions.NetworkMappingError(
                f"Reservation {reservation} is out of range {self.__range}"
            )
        self.__reservations.add(reservation_ip)

    @property
    def range(self) -> networking_definition.HostNetworkRange:
        return self.__range

    def __contains__(self, element):
        return element in self.__range

    def get_ip(self) -> typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]:
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


class IPPoolsManager:
    def __init__(
        self,
        group_templates: typing.Dict[
            str, networking_definition.GroupTemplateDefinition
        ],
    ):
        self.__pools_table: typing.Dict[str, typing.Dict[str, IPPool]] = {}
        self.__assignations: typing.Dict[
            str,
            typing.Dict[
                str, typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]
            ],
        ] = {}
        self.__init(group_templates)

    def add_instance_reservation(
        self,
        network_name: str,
        reservation: typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address],
    ):
        for group_nets in self.__pools_table.values():
            net_pool = group_nets.get(network_name, None)
            if net_pool and (reservation in net_pool):
                net_pool.add_reservation(reservation)

    def get_ip(self, group_name, network_name, instance_name: str):
        assigned_ip = self.__assignations.get(network_name, {}).get(instance_name, None)
        if assigned_ip:
            return assigned_ip

        group_pools = self.__pools_table.get(group_name, None)
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
        if network_name not in self.__assignations:
            self.__assignations[network_name] = {}
        self.__assignations[network_name][instance_name] = ip

        return ip

    def __init(
        self,
        group_templates: typing.Dict[
            str, networking_definition.GroupTemplateDefinition
        ],
    ):
        for hosts_group, host_template in group_templates.items():
            if hosts_group not in self.__pools_table:
                self.__pools_table[hosts_group] = {}
            for net_name, host_template_net in host_template.networks.items():
                if host_template_net.range:
                    ip_pool = IPPool(
                        host_template_net.range,
                    )
                    self.__pools_table[hosts_group][
                        host_template_net.network.name
                    ] = ip_pool
