import dataclasses
import ipaddress
import typing


@dataclasses.dataclass(frozen=True)
class MappedIpv4NetworkRange:
    """Represents an IPv4 network range

    Attributes:
        start: The staring IP of the range.
        start_host: The index of the first host.
        end: The IP of the last host in range.
        end_host: The index of the last host.
        length: The number of IPs in the range.

    """

    start: ipaddress.IPv4Address
    start_host: int
    end: ipaddress.IPv4Address
    end_host: int
    length: int


@dataclasses.dataclass(frozen=True)
class MappedIpv6NetworkRange:
    """Represents an IPv6 network range

    Attributes:
        start: The staring IP of the range.
        start_host: The index of the first host.
        end: The IP of the last host in range.
        end_host: The index of the last host.
        length: The number of IPs in the range.

    """

    start: ipaddress.IPv6Address
    start_host: int
    end: ipaddress.IPv6Address
    end_host: int
    length: int


@dataclasses.dataclass(frozen=True)
class MappedInstanceNetwork:
    """Defines a network attached to an instance

    Attributes:
        network_name: The name of the network.
        skip_nm: Skip configuring the interface.
        ip_v4: IPv4 address of the interface. Optional if ip_v6 is given.
        netmask_v4: IPv4 netmask of the interface. Present if ip_v4 is given.
        prefix_length_v4: IPv4's interface prefix length. Present if ip_v4 is given.
        ip_v6: IPv6 address of the interface. Optional if ip_v4 is given.
        netmask_v6: IPv6 netmask of the interface. Present if ip_v6 is given.
        prefix_length_v6: IPv6's interface prefix length. Present if ip_v6 is given.
        mtu: MTU of the interface. Optional.
        vlan_id: VLAN ID. Filled if the attached network is a VLAN.
        mac_addr: The MAC address of the interface attached to the network.
            Filled if low-level information of the link is provided.
        interface_name: The name of the interface attached to the network.
            Filled if low-level information of the link is provided.
        parent_interface: The parent VLAN interface.
            Filled if the attached network is a VLAN and if low-level
            information of the link is provided.
    """

    network_name: str
    skip_nm: bool = False
    mac_addr: str = None
    interface_name: str = None
    ip_v4: ipaddress.IPv4Address = None
    netmask_v4: ipaddress.IPv4Address = None
    prefix_length_v4: int = None
    ip_v6: ipaddress.IPv6Address = None
    netmask_v6: ipaddress.IPv6Address = None
    prefix_length_v6: int = None
    mtu: typing.Optional[int] = None
    parent_interface: typing.Optional[str] = None
    vlan_id: typing.Optional[int] = None
    is_trunk_parent: typing.Optional[bool] = None
    trunk_parent: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True)
class MappedInstance:
    """Defines an instance and its attached networks

    Attributes:
        name: Name of the instance.
        networks: The networks attached to this instance.
        hostname: Hostname of the instance. Optional.
    """

    name: str
    networks: typing.Dict[str, MappedInstanceNetwork]
    hostname: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True)
class MappedMultusNetworkConfig:
    """Network configuration for Multus.

    Attributes:
        ipv4_ranges: IPv4 ranges assigned to Multus.
        ipv6_ranges: IPv6 ranges assigned to Multus.

    """

    ipv4_ranges: typing.List[MappedIpv4NetworkRange]
    ipv6_ranges: typing.List[MappedIpv6NetworkRange]


@dataclasses.dataclass(frozen=True)
class MappedMetallbNetworkConfig:
    """Network configuration for Metallb.

    Attributes:
        ipv4_ranges: IPv4 ranges assigned to Metallb.
        ipv6_ranges: IPv6 ranges assigned to Metallb.

    """

    ipv4_ranges: typing.List[MappedIpv4NetworkRange]
    ipv6_ranges: typing.List[MappedIpv6NetworkRange]


@dataclasses.dataclass(frozen=True)
class MappedNetconfigNetworkConfig:
    """Network configuration for Netconfig.

    Attributes:
        ipv4_ranges: IPv4 ranges assigned to Netconfig.
        ipv6_ranges: IPv6 ranges assigned to Netconfig.

    """

    ipv4_ranges: typing.List[MappedIpv4NetworkRange]
    ipv6_ranges: typing.List[MappedIpv6NetworkRange]


@dataclasses.dataclass(frozen=True)
class MappedNetworkTools:
    """Tool configurations for a network

    Attributes:
        metallb: Metallb config of a network. Optional.
        multus: Multus config of a network. Optional.
        netconfig: Netconfig config of a network. Optional.

    """

    metallb: typing.Optional[MappedMetallbNetworkConfig]
    multus: typing.Optional[MappedMultusNetworkConfig]
    netconfig: typing.Optional[MappedNetconfigNetworkConfig]


@dataclasses.dataclass(frozen=True)
class MappedNetwork:
    """Defines all the settings of a given network
    Attributes:
        network_name: The name of the network.
        search_domain: DNS search domain for the network.
        tools: Tools configurations for the network.
        dns_v4: IPv4 nameservers for the network.
        dns_v6: IPv6 nameservers for the network.
        network_v4: IPv4 network address. Optional if network_v6 is given.
        network_v6: IPv6 network address. Optional if network_v4 is given.
        gw_v4: IPv4 network gateway. Optional.
        gw_v6: IPv6 network gateway. Optional.
        vlan_id: VLAN ID. Filled if the network is a VLAN.
        mtu: MTU of the network. Optional.

    """

    network_name: str
    search_domain: str
    tools: MappedNetworkTools
    dns_v4: typing.List[ipaddress.IPv4Address]
    dns_v6: typing.List[ipaddress.IPv6Address]
    network_v4: typing.Optional[ipaddress.IPv4Network] = None
    network_v6: typing.Optional[ipaddress.IPv6Network] = None
    gw_v4: typing.Optional[ipaddress.IPv4Address] = None
    gw_v6: typing.Optional[ipaddress.IPv6Address] = None
    vlan_id: typing.Optional[int] = None
    mtu: typing.Optional[int] = None


@dataclasses.dataclass(frozen=True)
class MappedRouter:
    """Defines all the settings for a router
    Attributes:
        router_name: The name of the router
        networks: Networks attached to the router
        external_network: The external gateway network
    """

    router_name: str
    networks: typing.List[str]
    external_network: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True)
class NetworkingEnvironmentDefinition:
    """Mapped Networking Environment Definition

    Describes the network environment.

    Attributes:
        networks: The existing networks in the environment.
        instances: Networking related information for each instance.
        routers: Routers in the environment

    """

    networks: typing.Dict[str, MappedNetwork]
    instances: typing.Dict[str, typing.Dict[str, MappedInstance]]
    routers: typing.Dict[str, MappedRouter]
