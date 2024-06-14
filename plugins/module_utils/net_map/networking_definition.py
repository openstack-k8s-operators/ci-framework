from __future__ import annotations

import copy
import dataclasses
import ipaddress
import typing

from ansible_collections.cifmw.general.plugins.module_utils.encoding import (
    ansible_encoding,
)

from ansible_collections.cifmw.general.plugins.module_utils.net_map import (
    exceptions,
)

__CONFIG_IP_VERSION_SUFFIX_4 = "v4"
__CONFIG_IP_VERSION_SUFFIX_6 = "v6"


def _raise_missing_field(
    value: typing.Any, field_name: str, parent_name: str = None, parent_type: str = None
):
    if not value:
        raise exceptions.NetworkMappingValidationError(
            f"'{field_name}' field is mandatory",
            field=field_name,
            invalid_value=value,
            parent_name=parent_name,
            parent_type=parent_type,
        )


def _validate_parse_int(
    field_name: str,
    raw_definition: typing.Dict[str, typing.Any],
    parent_name: str = None,
    parent_type: str = None,
    mandatory: bool = False,
    min_value: typing.Union[int, None] = None,
    max_value: typing.Union[int, None] = None,
) -> typing.Union[int, None]:
    if (not mandatory) and field_name not in raw_definition:
        return None
    elif field_name not in raw_definition:
        _raise_missing_field(
            None, field_name, parent_name=parent_name, parent_type=parent_type
        )
    raw_value = raw_definition[field_name]
    try:
        value = int(raw_value)
        if min_value is not None and value < min_value:
            raise exceptions.NetworkMappingValidationError(
                f"Invalid {field_name} value. Value is less than {min_value}",
                field=field_name,
                invalid_value=raw_value,
                parent_name=parent_name,
                parent_type=parent_type,
            )
        if max_value is not None and value > max_value:
            raise exceptions.NetworkMappingValidationError(
                f"Invalid {field_name} value. Value is more than {max_value}",
                field=field_name,
                invalid_value=raw_value,
            )
        return value
    except ValueError as err:
        raise exceptions.NetworkMappingValidationError(
            f"{raw_value} is not a valid integer",
            field=field_name,
            invalid_value=raw_value,
            parent_name=parent_name,
            parent_type=parent_type,
        ) from err


def _validate_parse_netadrr(
    field_name: str,
    raw_definition: typing.Dict[str, typing.Any],
    parent_name: str = None,
    parent_type: str = None,
    version: int = None,
) -> typing.Union[ipaddress.IPv4Network, ipaddress.IPv6Network]:
    raw_value = raw_definition[field_name]
    try:
        value = ipaddress.ip_network(raw_value)
        if version and value.version != version:
            raise exceptions.NetworkMappingValidationError(
                f"network address {value} should be of type v{version}",
                field=field_name,
                invalid_value=raw_value,
                parent_name=parent_name,
                parent_type=parent_type,
            )

        return value
    except ValueError as err:
        raise exceptions.NetworkMappingValidationError(
            "Invalid network value",
            field=field_name,
            invalid_value=raw_value,
            parent_name=parent_name,
            parent_type=parent_type,
        ) from err


def _validate_parse_field_type(
    field_name: str,
    raw_definition: typing.Dict[str, typing.Any],
    expected_type: typing.Type,
    parent_name: str = None,
    parent_type: str = None,
    mandatory: bool = False,
) -> typing.Any:
    if (not mandatory) and field_name not in raw_definition:
        return None
    elif field_name not in raw_definition:
        _raise_missing_field(
            None, field_name, parent_name=parent_name, parent_type=parent_type
        )

    raw_value = raw_definition[field_name]
    if not isinstance(raw_value, expected_type):
        raise exceptions.NetworkMappingValidationError(
            f"'{field_name}' must be of type {expected_type.__name__}",
            field=field_name,
            invalid_value=raw_value,
            parent_name=parent_name,
            parent_type=parent_type,
        )
    return raw_value


def _validate_parse_trunk_parent_field(
    field_name: str,
    raw_definition: typing.Dict[str, typing.Any],
    parent_name: str = None,
    parent_type: str = None,
    trunk_parents: set = None,
) -> typing.Any:
    if trunk_parents is None:
        trunk_parents = set()

    trunk_parent = _validate_parse_field_type(
        field_name,
        raw_definition,
        expected_type=str,
        parent_name=parent_name,
        parent_type=parent_type,
        mandatory=False,
    )
    if trunk_parent and trunk_parent not in trunk_parents:
        raise exceptions.NetworkMappingTrunkParentValidationError(
            message=(
                f"trunk parent '{trunk_parent}' does not exist in "
                f"'{parent_type}' '{parent_name}'"
            ),
            field=field_name,
            invalid_value=trunk_parent,
            parent_name=parent_name,
            parent_type=parent_type,
        )

    return trunk_parent


def _validate_fields_one_of(
    fields_list: typing.List[str],
    raw_definition: typing.Dict[str, typing.Any],
    parent_name: str = None,
    parent_type: str = None,
    alone_field: str = None,
    mandatory: bool = False,
) -> bool:
    fields_present = any(
        field_name in raw_definition.keys() for field_name in fields_list
    )
    if not mandatory and not fields_present:
        return False

    mandatory_fields = ",".join(fields_list).strip(",")
    if not fields_present:
        raise exceptions.NetworkMappingValidationError(
            f"at least one of {mandatory_fields} must be provided",
            parent_name=parent_name,
            parent_type=parent_type,
        )
    if alone_field and alone_field in raw_definition:
        rest = [
            field_name
            for field_name in raw_definition.keys()
            if field_name in fields_list and field_name != alone_field
        ]
        if rest:
            raise exceptions.NetworkMappingValidationError(
                f"{alone_field} cannot be used at the "
                f"same time are used {','.join(rest).strip(',')}",
                field=alone_field,
                invalid_value=raw_definition[alone_field],
                parent_name=parent_name,
                parent_type=parent_type,
            )

    return True


def _validate_parse_net_ip(
    raw_value: typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address, str, None],
    ipv4_network: typing.Optional[ipaddress.IPv4Network],
    ipv6_network: typing.Optional[ipaddress.IPv6Network],
    ip_version: int = None,
    field_name: str = None,
    parent_name: str = None,
    parent_type: str = None,
    validate_range: bool = True,
):
    if not raw_value:
        return None

    try:
        net_ip = ipaddress.ip_address(raw_value)
        if ip_version and net_ip.version != ip_version:
            raise exceptions.NetworkMappingValidationError(
                f"ip address {net_ip} should be a IPv{ip_version}",
                field=field_name,
                invalid_value=raw_value,
                parent_name=parent_name,
                parent_type=parent_type,
            )
        target_net = ipv4_network if net_ip.version == 4 else ipv6_network
        if not target_net:
            existing_net = ipv6_network if net_ip.version == 4 else ipv4_network
            raise exceptions.NetworkMappingValidationError(
                f"{net_ip} cannot be used in {existing_net} "
                f"because it's version v{net_ip.version}",
                invalid_value=raw_value,
                field=field_name,
                parent_name=parent_name,
                parent_type=parent_type,
            )

        if validate_range and net_ip not in target_net:
            raise exceptions.NetworkMappingValidationError(
                f"{net_ip} cannot be used because it's outside "
                f"of the range of {target_net}",
                invalid_value=raw_value,
                field=field_name,
                parent_name=parent_name,
                parent_type=parent_type,
            )
        return net_ip
    except ValueError as err:
        raise exceptions.NetworkMappingValidationError(
            f"{raw_value} is not a valid IP",
            invalid_value=raw_value,
            field=field_name,
            parent_name=parent_name,
            parent_type=parent_type,
        ) from err


def _validate_parse_raw_net_ip(
    instance_net_ip_raw,
    field_name: str,
    ipv4_network: typing.Optional[ipaddress.IPv4Network],
    ipv6_network: typing.Optional[ipaddress.IPv6Network],
    ip_version: int = None,
    validate_range: bool = True,
    parent_name: str = None,
    parent_type: str = None,
):
    return _validate_parse_net_ip(
        instance_net_ip_raw.get(field_name),
        ipv4_network,
        ipv6_network,
        ip_version=ip_version,
        validate_range=validate_range,
        field_name=field_name,
        parent_name=parent_name,
        parent_type=parent_type,
    )


def _validate_parse_raw_net_ip_list(
    raw_definition: typing.Dict[str, typing.Any],
    field_name: str,
    ipv4_network: typing.Optional[ipaddress.IPv4Network],
    ipv6_network: typing.Optional[ipaddress.IPv6Network],
    ip_version: int = None,
    validate_range: bool = True,
    parent_name: str = None,
    parent_type: str = None,
) -> typing.Union[
    typing.List[ipaddress.IPv4Address], typing.List[ipaddress.IPv6Address]
]:
    ip_raw_list = _validate_parse_field_type(
        field_name,
        raw_definition,
        list,
        parent_name=parent_name,
        parent_type=parent_type,
    )

    parsed_list = [
        _validate_parse_net_ip(
            raw_ip_value,
            ipv4_network,
            ipv6_network,
            validate_range=validate_range,
            field_name=field_name,
            parent_name=parent_name,
            parent_type=parent_type,
            ip_version=ip_version,
        )
        for raw_ip_value in (ip_raw_list or [])
    ]
    if parsed_list and len(set([parsed_ip.version for parsed_ip in parsed_list])) != 1:
        raise exceptions.NetworkMappingValidationError(
            "all IPs of the list should be of the same version",
            field=field_name,
            parent_name=parent_name,
            parent_type=parent_type,
        )

    return parsed_list


def _validate_parse_raw_net_ips(
    field_name: str,
    raw_definition: typing.Dict[str, typing.Any],
    ipv4_network: typing.Optional[ipaddress.IPv4Network],
    ipv6_network: typing.Optional[ipaddress.IPv6Network],
    parent_name: str = None,
    parent_type: str = None,
) -> typing.Tuple[ipaddress.IPv4Address, ipaddress.IPv6Address]:
    v4_field = f"{field_name}-{__CONFIG_IP_VERSION_SUFFIX_4}"
    v6_field = f"{field_name}-{__CONFIG_IP_VERSION_SUFFIX_6}"
    _validate_fields_one_of(
        [
            field_name,
            v4_field,
            v6_field,
        ],
        raw_definition,
        parent_name=parent_name,
        parent_type=parent_type,
        alone_field=field_name,
    )
    ipv6 = None
    ipv4 = None
    if field_name in raw_definition:
        net_ip = _validate_parse_raw_net_ip(
            raw_definition,
            field_name,
            ipv4_network,
            ipv6_network,
            parent_name=parent_name,
            parent_type=parent_type,
        )
        if net_ip.version == 4:
            ipv4 = net_ip
        else:
            ipv6 = net_ip
    else:
        ipv4 = _validate_parse_raw_net_ip(
            raw_definition,
            v4_field,
            ipv4_network,
            ipv6_network,
            ip_version=4,
            parent_name=parent_name,
            parent_type=parent_type,
        )
        ipv6 = _validate_parse_raw_net_ip(
            raw_definition,
            v6_field,
            ipv4_network,
            ipv6_network,
            ip_version=6,
            parent_name=parent_name,
            parent_type=parent_type,
        )
    return ipv4, ipv6


def _validate_parse_raw_net_ip_lists(
    field_name: str,
    raw_definition: typing.Dict[str, typing.Any],
    ipv4_network: typing.Optional[ipaddress.IPv4Network],
    ipv6_network: typing.Optional[ipaddress.IPv6Network],
    validate_range: bool = True,
    parent_name: str = None,
    parent_type: str = None,
) -> typing.Tuple[
    typing.List[ipaddress.IPv4Address], typing.List[ipaddress.IPv6Address]
]:
    v4_field = f"{field_name}-{__CONFIG_IP_VERSION_SUFFIX_4}"
    v6_field = f"{field_name}-{__CONFIG_IP_VERSION_SUFFIX_6}"
    _validate_fields_one_of(
        [
            field_name,
            v4_field,
            v6_field,
        ],
        raw_definition,
        parent_name=parent_name,
        parent_type=parent_type,
        alone_field=field_name,
    )
    ipv6_addresses = []
    ipv4_addresses = []
    if field_name in raw_definition:
        parsed_list = _validate_parse_raw_net_ip_list(
            raw_definition,
            field_name,
            ipv4_network,
            ipv6_network,
            validate_range=validate_range,
            parent_name=parent_name,
            parent_type=parent_type,
        )
        version = next((ip.version for ip in parsed_list), None)
        if version == 4:
            ipv4_addresses = parsed_list
        elif version == 6:
            ipv6_addresses = parsed_list
    else:
        ipv4_addresses = _validate_parse_raw_net_ip_list(
            raw_definition,
            v4_field,
            ipv4_network,
            ipv6_network,
            validate_range=validate_range,
            parent_name=parent_name,
            parent_type=parent_type,
            ip_version=4,
        )
        ipv6_addresses = _validate_parse_raw_net_ip_list(
            raw_definition,
            v6_field,
            ipv4_network,
            ipv6_network,
            validate_range=validate_range,
            parent_name=parent_name,
            parent_type=parent_type,
            ip_version=6,
        )
    return ipv4_addresses, ipv6_addresses


def check_host_network_ranges_collisions(
    ranges: typing.Sequence[HostNetworkRange],
) -> typing.Union[
    typing.Tuple[HostNetworkRange, HostNetworkRange], typing.Tuple[None, None]
]:
    """Checks if a list contains collading HostNetworkRange

    Args:
        ranges: List of HostNetworkRange to check

    Returns:
        A tuple with the first two colliding items or a size two
        empty tuple if no colliding ranges have been found.
    """
    ranges.sort(key=lambda x: x.start_host, reverse=False)
    for index in range(0, len(ranges) - 1):
        start = ranges[index].start_host
        length = ranges[index].length
        next_start = ranges[index + 1].start_host
        if (start + length) > next_start:
            return ranges[index], ranges[index + 1]
    return None, None


class HostNetworkRange(ansible_encoding.RawConvertibleObject):
    """Parser and validator of network ranges

    Handles the parsing and validation of a network range based on two
    paramerters: start and end/length.
    Supports both IPv4 and IPv6 networks.
    """

    __FIELD_RANGE_START = "start"
    __FIELD_RANGE_END = "end"
    __FIELD_RANGE_LENGTH = "length"

    def __init__(
        self,
        network: typing.Union[ipaddress.IPv4Network, ipaddress.IPv6Network, str],
        start: typing.Union[
            ipaddress.IPv4Address, ipaddress.IPv6Address, str, int, None
        ] = None,
        end: typing.Union[
            ipaddress.IPv4Address, ipaddress.IPv6Address, str, int, None
        ] = None,
        length: typing.Union[int, str, None] = None,
    ):
        """Creates a network range instance form it's net and limits.

        Creates a range instance for the provided network based on the
        given limits start and end (or length instead of end if provided).

        Args:
            network: The IPv4Network/IPv6Network this range belongs to
            start: The start of the range, as an integer that represents
                the first host index or as an IP
            end: The end of the range, as an integer that represents
                the last host index or as an IP. It Can be optional
                if length is provided
            length: The length of the range. Can be optional if end is
                given
        Raises:
            ValueError: If network is not provided
            exceptions.NetworkMappingValidationError:
                If the end of the range if behind the start.
                If start/end IP are not of the same family of the
                    given network.
                If the start/end/legnth ternary is out of range
                    of the network.
                If any format error exists of one of the inputs.
        """
        if not network:
            raise ValueError("network is a mandatory argument")
        self.__network = ipaddress.ip_network(network)
        self.__init_range_start(start)
        self.__init_range_end(end, length)

        if self.__start_ip > self.__end_ip:
            raise exceptions.NetworkMappingValidationError(
                f"range end {self.__end_ip} for {self.__network} "
                f"cannot be less than {self.__start_ip}",
                invalid_value=end,
                field=self.__FIELD_RANGE_END,
            )

    @property
    def start_host(self) -> int:
        """The start host index."""
        return self.__start_host

    @property
    def length(self) -> int:
        """The length of the range."""
        return self.__length

    @property
    def start_ip(self) -> typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]:
        """The start host IP."""
        return self.__start_ip

    @property
    def end_ip(self) -> typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]:
        """The end host IP."""
        return self.__end_ip

    @property
    def network(self) -> typing.Union[ipaddress.IPv4Network, ipaddress.IPv6Network]:
        """The network to which the range belongs to."""
        return self.__network

    @classmethod
    def get_version_from_raw(
        cls,
        raw_range: typing.Union[typing.Dict[str, typing.Any], str],
    ) -> typing.Union[int, None]:
        """Fetches the IP version of a range in dict format.

        Args:
            raw_range: The range as a dictionary that for which the
            version is requested.

        Returns:
            The version of the range or None if it can apply to
            both IPv4 and vIPv6.

        Raises:
            exceptions.NetworkMappingValidationError: If the range is
                malformatted and contains IPs poiting to IPv4 and IPv6
                at the same time.
        """
        if (
            cls.__FIELD_RANGE_START not in raw_range
            and cls.__FIELD_RANGE_END not in raw_range
        ):
            return None

        start_version = cls.__get_field_ip_net_version(
            raw_range.get(cls.__FIELD_RANGE_START, None)
        )
        end_version = cls.__get_field_ip_net_version(
            raw_range.get(cls.__FIELD_RANGE_END, None)
        )

        if start_version and end_version and (start_version != end_version):
            raise exceptions.NetworkMappingValidationError(
                "range contains mixed IP versions",
                invalid_value=raw_range,
            )

        return start_version or end_version

    def to_raw(self):
        """Returns a builtin types based dict representation of the object.

        Returns: A dictionary with the start IP of the range as a string with
            key start_ip and the IP as a string, the last included IP as
            end_ip also as a string and finally the network under the network
            key and as a string too.
        """
        return {
            "start_ip": str(self.__start_ip),
            "end_ip": str(self.__end_ip),
            "network": str(self.__network),
        }

    @classmethod
    def from_raw(
        cls,
        network: typing.Union[ipaddress.IPv4Network, ipaddress.IPv6Network],
        raw_range: typing.Union[typing.Dict[str, typing.Any], str],
    ) -> "HostNetworkRange":
        """Parses and validated a range from its dict representation.

        The range raw definition must adhere to the following format:
            start: <host-index or host IP>
            end: <host index or IP. Optional if length is given>
            length: <Range length. Optional if end is given>

        Args:
            network: The network to which the range belongs to.
            raw_range: The dictionary that contains the range data
                as key-values of its start, end and/or lenth.

        Returns:
            An instance of the given range.

        Raises:
            exceptions.NetworkMappingValidationError: When the format
                of the provided range fields is not correct.
        """
        if raw_range and not isinstance(raw_range, (dict, str)):
            raise exceptions.NetworkMappingValidationError(
                "raw_range argument must be a dict or a string",
                invalid_value=raw_range,
            )

        if isinstance(raw_range, str):
            range_split = raw_range.split("-")
            if len(range_split) != 2:
                raise exceptions.NetworkMappingValidationError(
                    f"range {raw_range} for {network} net "
                    "must be in the <START>-<END> format",
                    invalid_value=raw_range,
                )
            return HostNetworkRange(
                network,
                start=range_split[0],
                end=range_split[1],
            )

        return HostNetworkRange(
            network,
            start=raw_range.get(cls.__FIELD_RANGE_START, None),
            end=raw_range.get(cls.__FIELD_RANGE_END, None),
            length=raw_range.get(cls.__FIELD_RANGE_LENGTH, None),
        )

    def __init_range_end(self, end, length):
        """Parses and validates the end and length of the range

        If end is given length will be ignored and computed internally by taking
        the content of end, that will be parsend and converted to a builtin
        integer or IPv4 or IPv6 address.

        If the given end and/or length variables are correct, this method sets
        the internal end host index, end host IP and length.

        Args:
            end: The ending index/ip of the range.
            length: The length of the range. Ignored if end is given.

        Raises:
            exceptions.NetworkMappingValidationError: If the given end or length are
            not valid because of the following reasons:
                The given end IP family is not the same of the associated network.
                The given end is not a valid integer nor IP.
                The given length is not a valid integer or is less than zero.
                The given end or length is outside the associated network.

        """
        parsed_end, end_is_ip = self.__parse_validate_range_limit(
            end, self.__FIELD_RANGE_END
        )

        if end_is_ip and parsed_end.version != self.__network.version:
            raise exceptions.NetworkMappingValidationError(
                f"IP should match the range network family {self.__network.version}",
                invalid_value=end,
                field=self.__FIELD_RANGE_END,
            )

        if parsed_end and end_is_ip and parsed_end not in self.__network:
            raise exceptions.NetworkMappingValidationError(
                f"Range end IP {end} is out of range of {self.__network} network",
                invalid_value=end,
                field=self.__FIELD_RANGE_END,
            )
        if length is not None and (not end_is_ip) and (not parsed_end):
            try:
                if int(length) < 1:
                    raise exceptions.NetworkMappingValidationError(
                        f"length {length} for {self.__network} "
                        "network should be positive",
                        invalid_value=length,
                        field=self.__FIELD_RANGE_LENGTH,
                    )

                self.__length = int(length)
                self.__end_ip = self.__network[self.__length + self.start_host - 1]
            except IndexError as err:
                raise exceptions.NetworkMappingValidationError(
                    f"length {length} is out of range of {self.__network} network",
                    invalid_value=length,
                    field=self.__FIELD_RANGE_LENGTH,
                ) from err
            except ValueError as err:
                raise exceptions.NetworkMappingValidationError(
                    f"length {length} is not a valid integer",
                    invalid_value=length,
                    field=self.__FIELD_RANGE_LENGTH,
                ) from err
        elif parsed_end and end_is_ip:
            self.__end_ip = parsed_end
            self.__length = int(self.__end_ip) - int(self.__start_ip) + 1
        elif parsed_end and not end_is_ip:
            try:
                self.__length = parsed_end - self.__start_host + 1
                self.__end_ip = self.__network[parsed_end]
            except IndexError as err:
                raise exceptions.NetworkMappingValidationError(
                    f"end {parsed_end} is out of range of {self.__network} network",
                    invalid_value=end,
                    field=self.__FIELD_RANGE_END,
                ) from err
        else:
            self.__end_ip = self.__network[-1]
            self.__length = self.__network.num_addresses

    def __init_range_start(self, start):
        """Parses and validates the start of the range

        Takes one start variable and tries to get from it the starting index or IP
        of the range, that can be given as a string that represents an integer or
        and IPv4/6 or as a builtin integer or IP.

        If the given start is correct, this method sets the internal start index
        and IP.

        If no start is given, the first host of the network will be used as start.

        Args:
            start: The starting index/ip of the range.

        Raises:
            exceptions.NetworkMappingValidationError: If the given start is not valid
            because of the following reasons:
                The given start IP family is not the same of the associated network.
                The given start is not a valid integer nor IP.
                The starting host is outside the associated network.

        """
        parsed_start, start_is_ip = self.__parse_validate_range_limit(
            start, self.__FIELD_RANGE_START
        )

        if start_is_ip and parsed_start.version != self.__network.version:
            raise exceptions.NetworkMappingValidationError(
                f"IP should match the range network family {self.__network.version}",
                invalid_value=start,
                field=self.__FIELD_RANGE_START,
            )

        if parsed_start and start_is_ip and parsed_start not in self.__network:
            raise exceptions.NetworkMappingValidationError(
                f"Range start IP {start} is out of range of {self.__network} network",
                invalid_value=start,
                field=self.__FIELD_RANGE_START,
            )
        if parsed_start and not start_is_ip:
            self.__start_host = parsed_start
            try:
                self.__start_ip = self.__network[self.__start_host]
            except IndexError as err:
                raise exceptions.NetworkMappingValidationError(
                    f"Range start {parsed_start} is out of range "
                    f"of {self.__network} network",
                    invalid_value=start,
                    field=self.__FIELD_RANGE_START,
                ) from err
        elif parsed_start:
            self.__start_ip = parsed_start
            self.__start_host = int(self.__start_ip) - int(
                self.__network.network_address
            )
        else:
            self.__start_ip = self.__network[0]
            self.__start_host = 0

    def __parse_validate_range_limit(
        self,
        value: typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address, str],
        field_name: str,
    ) -> typing.Tuple[
        typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address, int, None], bool
    ]:
        if not value:
            return None, False
        if isinstance(value, ipaddress.IPv4Address) or isinstance(
            value, ipaddress.IPv6Address
        ):
            return value, True

        try:
            range_num_limit = int(value)
            if range_num_limit < 0:
                raise exceptions.NetworkMappingValidationError(
                    f"{field_name} {range_num_limit} is out of range "
                    f"of {self.__network} network",
                    invalid_value=value,
                    field=field_name,
                )
            return range_num_limit, False
        except ValueError:
            pass
        try:
            return ipaddress.ip_address(value), True
        except ValueError as err:
            raise exceptions.NetworkMappingValidationError(
                f"{self.__network.network_address} range contains a "
                f"{field_name} value, {value}, that not a valid",
                invalid_value=value,
                field=field_name,
            ) from err

    @staticmethod
    def __get_field_ip_net_version(raw_field: str) -> typing.Union[int, None]:
        if not raw_field:
            return None

        try:
            # Avoid that start/end integers are takes as IPv4
            # str allows passing IPs directly without converting to int
            # and making it fail, so they will be parsed after the except
            value = int(str(raw_field))
            if value is not None:
                return None
        except ValueError:
            pass

        try:
            return ipaddress.ip_network(raw_field).version
        except ValueError:
            return None

    def __contains__(self, element):
        ip = element
        try:
            ip = ipaddress.ip_address(element) if isinstance(element, str) else ip
        except ValueError:
            return False

        if (not isinstance(ip, ipaddress.IPv4Address)) and (
            not isinstance(ip, ipaddress.IPv6Address)
        ):
            return False

        return (
            ip in self.__network and (ip >= self.__start_ip) and (ip <= self.__end_ip)
        )

    def __hash__(self):
        return hash((self.__network, self.__start_ip, self.__end_ip))

    def __eq__(self, other):
        if not isinstance(other, HostNetworkRange):
            return False

        return (
            self.__start_ip == other.__start_ip
            and self.__network == other.__network
            and self.__end_ip == other.__end_ip
        )

    def __str__(self):
        return f"{self.__start_ip}-{self.__end_ip}"


class SubnetBasedNetworkToolDefinition:
    """
    Handles the parsing and validation of networking configuration for a tool
    that contains IP ranges (v4 and v6).

    This class is responsible for ensuring that the parsed ranges are part of
    the selected network and that their format contains a proper IPv4/6
    network address.
    """

    __FIELD_RANGES = "ranges"
    __FIELD_RANGES_IPV4 = "ranges-v4"
    __FIELD_RANGES_IPV6 = "ranges-v6"

    def __init__(
        self,
        network: NetworkDefinition,
        raw_config: typing.Dict[str, typing.Any],
        object_name: str,
    ):
        """Initializes a SubnetBasedNetworkToolDefinition instance.

        Args:
            network: The network to which the tool blongs to.
            raw_config: The dictionary that contains the ranges
                of the tool.
            object_name: The name of the parsed tool.
        """
        if not network:
            raise ValueError("network is a mandatory argument")
        self.__network = network
        self.__object_name = object_name
        self.__ipv4_ranges: typing.List[HostNetworkRange] = []
        self.__ipv6_ranges: typing.List[HostNetworkRange] = []
        self.__parse_raw(raw_config)

    def __parse_raw(self, raw_definition: typing.Dict[str, typing.Any]):
        _validate_fields_one_of(
            [
                self.__FIELD_RANGES,
                self.__FIELD_RANGES_IPV4,
                self.__FIELD_RANGES_IPV6,
            ],
            raw_definition,
            parent_name=self.__object_name,
            alone_field=self.__FIELD_RANGES,
        )

        self.__parse_raw_range_field(raw_definition, self.__FIELD_RANGES)
        self.__parse_raw_range_field(
            raw_definition, self.__FIELD_RANGES_IPV4, ip_version=4
        )
        self.__parse_raw_range_field(
            raw_definition, self.__FIELD_RANGES_IPV6, ip_version=6
        )

    def __parse_raw_range_field(
        self,
        raw_definition: typing.Dict[str, typing.Any],
        field_name: str,
        ip_version: int = None,
    ):
        if field_name in raw_definition:
            raw_ranges = _validate_parse_field_type(
                field_name,
                raw_definition,
                list,
                parent_name=self.__object_name,
            )

            for range_data in raw_ranges:
                ipv4_range, ipv6_range = self.__network.parse_range_from_raw(
                    range_data, ip_version=ip_version
                )
                if ipv4_range:
                    self.__ipv4_ranges.append(ipv4_range)
                if ipv6_range:
                    self.__ipv6_ranges.append(ipv6_range)

    @property
    def ranges_ipv4(self) -> typing.List[HostNetworkRange]:
        """The parsed IPv4 ranges."""
        return self.__ipv4_ranges

    @property
    def ranges_ipv6(self) -> typing.List[HostNetworkRange]:
        """The parsed IPv6 ranges."""
        return self.__ipv6_ranges

    def __hash__(self) -> int:
        return hash(
            (
                self.__network.name,
                tuple(self.__ipv4_ranges),
                tuple(self.__ipv6_ranges),
            )
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, SubnetBasedNetworkToolDefinition):
            return False

        return (
            self.__network.name == other.__network.name
            and self.__ipv4_ranges == other.__ipv4_ranges
            and self.__ipv6_ranges == other.__ipv6_ranges
        )


class MultusNetworkDefinition(SubnetBasedNetworkToolDefinition):
    """Parses and holds Multus configuration for a given network."""

    __OBJECT_NAME = "multus"

    def __init__(
        self,
        network: NetworkDefinition,
        raw_config: typing.Dict[str, typing.Any],
    ):
        super().__init__(network, raw_config, self.__OBJECT_NAME)


class MetallbNetworkDefinition(SubnetBasedNetworkToolDefinition):
    """Parses and holds Metallb configuration for a given network."""

    __OBJECT_NAME = "metallb"

    def __init__(
        self,
        network: NetworkDefinition,
        raw_config: typing.Dict[str, typing.Any],
    ):
        super().__init__(network, raw_config, self.__OBJECT_NAME)


class NetconfigNetworkDefinition(SubnetBasedNetworkToolDefinition):
    """Parses and holds NetConfig configuration for a given network."""

    __OBJECT_NAME = "netconfig"

    def __init__(
        self,
        network: NetworkDefinition,
        raw_config: typing.Dict[str, typing.Any],
    ):
        super().__init__(network, raw_config, self.__OBJECT_NAME)


class RouterDefinition:
    """Parser and validator of a signle router config element

    Handles the parsing and validation of a router item in the
    dict of routers of the Networking Definition.

    The network definition that this class parses should follow
    this format:

    .. code-block:: YAML

       <router-name>:
         external_network: <external gateway network: optional>
         networks:  <List of networks attached to the router>
           - <Network 1>

    Raises:
        ValueError: If name it's not provided.
        exceptions.NetworkMappingValidationError: When the format
            of the provided instance is not correct.
    """

    __OBJECT_NAME = "router"

    __FIELD_EXTERNAL_NETWORK = "external_network"
    __FIELD_NETWORKS = "networks"

    def __init__(self, name: str, raw_definition: typing.Dict[str, typing.Any]) -> None:
        """Initializes a RouterDefinition from dict with its parameters

        Args:
            name: The name of router.
            raw_definitions: The dictionary that contains the configuration
                of the router

        Raises:
            ValueError: If name is not provided.
        """
        if not name:
            raise ValueError("name is a mandatory argument")

        self.__name = name
        self.__external_network = None
        self.__networks = []
        self.__parse_raw(raw_definition)

    @property
    def name(self) -> str:
        """Name of the network."""
        return self.__name

    @property
    def external_network(self) -> typing.Optional[str]:
        """External gateway network"""
        return self.__external_network

    @property
    def networks(self) -> typing.List[str]:
        """List of networks to attach to the router"""
        return self.__networks

    def __parse_raw(self, raw_definition: typing.Dict[str, typing.Any]):
        self.__external_network = _validate_parse_field_type(
            self.__FIELD_EXTERNAL_NETWORK,
            raw_definition,
            str,
            parent_name=self.__name,
            parent_type=self.__OBJECT_NAME,
            mandatory=False,
        )

        self.__networks = _validate_parse_field_type(
            self.__FIELD_NETWORKS,
            raw_definition,
            list,
            parent_name=self.name,
            parent_type=self.__OBJECT_NAME,
            mandatory=True,
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.__name,
                self.__external_network,
                frozenset(self.__networks),
            )
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, RouterDefinition):
            return False

        return (
            self.__external_network == other.__external_network
            and self.__networks == other.__networks
            and self.__name == other.__name
        )


class NetworkDefinition:
    """Parser and validator of a single network config element

    Handles the parsing and validation of a network item in the
    dict of networks of the Networking Definition.

    The network definition that this class parses should follow
    this format:

    .. code-block:: YAML

        <network-name>:
            network: <net-ip/prefix>
            gateway: <net gateway: optional>
            dns:  <DNS servers list: optional>
                - <DNS IP 1>
            search-domain: <DNS search domain: optional>
            vlan: <vlan-id: optional>
            mtu: <mtu: optional>
            tools:
                multus: <MultusNetworkDefinition>
                metallb: <MetalbNetworkDefinition>
                netconfig: <NetconfigNetworkDefinition>
    """

    __OBJECT_TYPE_NAME = "network"

    __FIELD_NETWORK = "network"
    __FIELD_NETWORK_IPV4 = "network-v4"
    __FIELD_NETWORK_IPV6 = "network-v6"
    __FIELD_GATEWAY = "gateway"
    __FIELD_DNSS = "dns"
    __FIELD_SEARCH_DOMAIN = "search-domain"
    __FIELD_MTU = "mtu"
    __FIELD_VLAN_ID = "vlan"

    __FIELD_TOOLS = "tools"
    __FIELD_TOOLS_MULTUS = "multus"
    __FIELD_TOOLS_METALLB = "metallb"
    __FIELD_TOOLS_NETCONFIG = "netconfig"

    def __init__(self, name: str, raw_definition: typing.Dict[str, typing.Any]) -> None:
        """Initializes a NetworkDefinition from dict with its parameters

        Args:
            name: The name of the network.
            raw_definition: The dictionary that contains the configuration
                of the network.

        Raises:
            ValueError: If name is not provided.
            exceptions.NetworkMappingValidationError:
                If the given version is not configured for the network.
                If the content of the range is invalid.
        """
        if not name:
            raise ValueError("name is a mandatory argument")

        self.__name = name
        self.__vlan = None
        self.__mtu = None
        self.__ipv6_network = None
        self.__ipv4_network = None
        self.__ipv4_gateway = None
        self.__ipv6_gateway = None
        self.__search_domain = None
        self.__ipv4_dns = []
        self.__ipv6_dns = []
        self.__multus_config: typing.Union[MultusNetworkDefinition, None] = None
        self.__metallb_config: typing.Union[MetallbNetworkDefinition, None] = None
        self.__netconfig_config: typing.Union[NetconfigNetworkDefinition, None] = None
        self.__parse_raw(raw_definition)

    @property
    def name(self) -> str:
        """Name of the network."""
        return self.__name

    @property
    def vlan(self) -> typing.Union[int, None]:
        """VLAN ID, if the network is a VLAN."""
        return self.__vlan

    @property
    def mtu(self) -> typing.Optional[int]:
        """MTU, if using a non-default value."""
        return self.__mtu

    @property
    def multus_config(self) -> typing.Union[MultusNetworkDefinition, None]:
        """Multus configuration, if given"""
        return self.__multus_config

    @property
    def metallb_config(self) -> typing.Union[MetallbNetworkDefinition, None]:
        """Metallb configuration, if given"""
        return self.__metallb_config

    @property
    def netconfig_config(self) -> typing.Union[NetconfigNetworkDefinition, None]:
        """Netconfig configuration, if given"""
        return self.__netconfig_config

    @property
    def ipv4_network(self) -> typing.Union[ipaddress.IPv4Network, None]:
        """IPv4 network address"""
        return self.__ipv4_network

    @property
    def ipv6_network(self) -> typing.Union[ipaddress.IPv6Network, None]:
        """IPv6 network address"""
        return self.__ipv6_network

    @property
    def ipv4_gateway(self) -> typing.Optional[ipaddress.IPv4Address]:
        """IPv4 gateway"""
        return self.__ipv4_gateway

    @property
    def ipv6_gateway(self) -> typing.Optional[ipaddress.IPv6Address]:
        """IPv6 gateway"""
        return self.__ipv6_gateway

    @property
    def ipv4_dns(self) -> typing.List[ipaddress.IPv4Address]:
        """IPv4 DNS servers"""
        return self.__ipv4_dns

    @property
    def ipv6_dns(self) -> typing.List[ipaddress.IPv6Address]:
        """IPv6 DNS servers"""
        return self.__ipv6_dns

    @property
    def search_domain(self) -> typing.Optional[str]:
        """DNS search domain"""
        return self.__search_domain

    def parse_range_from_raw(
        self, raw_definition: typing.Dict[str, typing.Any], ip_version: int = None
    ) -> typing.Tuple[
        typing.Union[HostNetworkRange, None],
        typing.Union[HostNetworkRange, None],
    ]:
        """Creates HostNetworkRange for the network based on their definition

        Args:
            raw_definition:
            ip_version: IP version of the requested range. If not given the
                version will be inferred from the raw_definition.

        Returns: Tuple of the IPv4 and IPv6 ranges for the network.
            If version is specified and/or the network is configured to use
            a single IP version only one of the items of the tuple will be
            filled.

        Raises:
            exceptions.NetworkMappingValidationError:
                If the given version is not configured for the network.
                If the content of the range is invalid.

        """
        ipv4_net, ipv6_net = self.__pick_nets_from_raw(
            raw_definition, ip_version=ip_version
        )
        ipv4_range = (
            HostNetworkRange.from_raw(ipv4_net, raw_definition) if ipv4_net else None
        )
        ipv6_range = (
            HostNetworkRange.from_raw(ipv6_net, raw_definition) if ipv6_net else None
        )
        return ipv4_range, ipv6_range

    def __pick_nets_from_raw(
        self, raw_definition, ip_version: int = None
    ) -> typing.Tuple[
        typing.Union[ipaddress.IPv4Network, None],
        typing.Union[ipaddress.IPv6Network, None],
    ]:
        """Gets the built-in networks (IPv4/6) for the given raw range

        Gets the networks that applies for a range based on its IP version.

        Args:
            raw_definition: The range definition as a dict.
            ip_version: IP version of the requested range. If not given the
                version will be inferred from the raw_definition.

        Returns: A tuple with the IPv4 and IPv6 networks.
            If the range targets
            only the IPv4 net only that one is returned. Same for the IPv6 one.
            If the range targets both elements of the tuple are returned.

        Raises:
            exceptions.NetworkMappingValidationError:
                If the content of the range is invalid.
                If the range content doesn't match the requested IP version.
                If the network doesn't support the requested IP version.

        """
        # Fetch the IP version of the given range based on it's fields.
        range_version = HostNetworkRange.get_version_from_raw(raw_definition)

        # If given (can be empty if it applies to IPv4 and 6) check if it's
        # the expected one
        if range_version and ip_version and range_version != ip_version:
            raise exceptions.NetworkMappingValidationError(
                f"expected IPv{ip_version} range but "
                f"v{range_version} was given for net {self.__name}",
                invalid_value=str(raw_definition),
            )

        # If the network is not configured with the requested IP version
        # raise an explicit exception
        selected_version = range_version or ip_version
        if selected_version and (selected_version == 6 and not self.__ipv6_network):
            raise exceptions.NetworkMappingValidationError(
                f"IPv6 ranges are not supported in {self.__name} "
                "network cause it's IPv4 only",
                invalid_value=str(raw_definition),
            )
        if selected_version and (selected_version == 4 and not self.__ipv4_network):
            raise exceptions.NetworkMappingValidationError(
                f"IPv4 ranges are not supported in {self.__name} "
                "network cause it's IPv6 only",
                invalid_value=str(raw_definition),
            )
        if selected_version:
            return (
                self.__ipv4_network if selected_version == 4 else None,
                self.__ipv6_network if selected_version == 6 else None,
            )

        return self.__ipv4_network, self.__ipv6_network

    def __parse_raw(self, raw_definition: typing.Dict[str, typing.Any]):
        self.__parse_raw_network(raw_definition)
        self.__parse_raw_gateway(raw_definition)
        self.__parse_raw_dnss(raw_definition)

        self.__search_domain = _validate_parse_field_type(
            self.__FIELD_SEARCH_DOMAIN,
            raw_definition,
            str,
            parent_name=self.__name,
            parent_type=self.__OBJECT_TYPE_NAME,
            mandatory=False,
        )
        self.__mtu = _validate_parse_int(
            self.__FIELD_MTU,
            raw_definition,
            parent_name=self.__name,
            parent_type=self.__OBJECT_TYPE_NAME,
            min_value=1,
        )
        self.__vlan = _validate_parse_int(
            self.__FIELD_VLAN_ID,
            raw_definition,
            parent_name=self.__name,
            parent_type=self.__OBJECT_TYPE_NAME,
            min_value=1,
            max_value=4094,
        )

        self.__parse_tools(raw_definition)

    def __parse_raw_gateway(self, raw_definition):
        self.__ipv4_gateway, self.__ipv6_gateway = _validate_parse_raw_net_ips(
            self.__FIELD_GATEWAY,
            raw_definition,
            self.__ipv4_network,
            self.__ipv6_network,
            parent_type=self.__OBJECT_TYPE_NAME,
            parent_name=self.__name,
        )

    def __parse_raw_dnss(self, raw_definition):
        self.__ipv4_dns, self.__ipv6_dns = _validate_parse_raw_net_ip_lists(
            self.__FIELD_DNSS,
            raw_definition,
            self.__ipv4_network,
            self.__ipv6_network,
            validate_range=False,
            parent_type=self.__OBJECT_TYPE_NAME,
            parent_name=self.__name,
        )

    def __parse_raw_network(self, raw_definition):
        _validate_fields_one_of(
            [
                self.__FIELD_NETWORK,
                self.__FIELD_NETWORK_IPV4,
                self.__FIELD_NETWORK_IPV6,
            ],
            raw_definition,
            parent_name=self.__name,
            parent_type=self.__OBJECT_TYPE_NAME,
            alone_field=self.__FIELD_NETWORK,
            mandatory=True,
        )

        if self.__FIELD_NETWORK in raw_definition:
            parsed_net_ip = _validate_parse_netadrr(
                self.__FIELD_NETWORK,
                raw_definition,
                parent_name=self.__name,
                parent_type=self.__OBJECT_TYPE_NAME,
            )
            if parsed_net_ip.version == 6:
                self.__ipv6_network = parsed_net_ip
            else:
                self.__ipv4_network = parsed_net_ip

        if self.__FIELD_NETWORK_IPV6 in raw_definition:
            self.__ipv6_network = _validate_parse_netadrr(
                self.__FIELD_NETWORK_IPV6,
                raw_definition,
                parent_name=self.__name,
                parent_type=self.__OBJECT_TYPE_NAME,
                version=6,
            )

        if self.__FIELD_NETWORK_IPV4 in raw_definition:
            self.__ipv4_network = _validate_parse_netadrr(
                self.__FIELD_NETWORK_IPV4,
                raw_definition,
                parent_name=self.__name,
                parent_type=self.__OBJECT_TYPE_NAME,
                version=4,
            )

    def __parse_tools(self, raw_definition: typing.Dict[str, typing.Any]):
        tools_raw_config = _validate_parse_field_type(
            self.__FIELD_TOOLS,
            raw_definition,
            dict,
            parent_name=self.__name,
            parent_type=self.__OBJECT_TYPE_NAME,
            mandatory=False,
        )
        if tools_raw_config:
            self.__parse_tool_multus(tools_raw_config)
            self.__parse_tool_metallb(tools_raw_config)
            self.__parse_tool_netconfig(tools_raw_config)
            self.__check_tools_ranges()

    def __get_tools_ranges(
        self,
    ) -> typing.Tuple[typing.List[HostNetworkRange], typing.List[HostNetworkRange]]:
        ipv4_ranges = []
        ipv6_ranges = []
        for tool_config in [
            self.__multus_config,
            self.__metallb_config,
            self.__netconfig_config,
        ]:
            if tool_config:
                ipv4_ranges.extend(tool_config.ranges_ipv4)
                ipv6_ranges.extend(tool_config.ranges_ipv6)
        return ipv4_ranges, ipv6_ranges

    def __check_tools_ranges(self):
        ipv4_ranges, ipv6_ranges = self.__get_tools_ranges()
        if len(ipv4_ranges) > 1:
            (
                colliding_item1,
                colliding_item2,
            ) = check_host_network_ranges_collisions(ipv4_ranges)
            if colliding_item1:
                raise exceptions.HostNetworkRangeCollisionValidationError(
                    f"{self.__name} contains tools with IPv4 ranges that collides",
                    range_1=colliding_item1,
                    range_2=colliding_item2,
                )
        if len(ipv6_ranges) > 1:
            (
                colliding_item1,
                colliding_item2,
            ) = check_host_network_ranges_collisions(ipv6_ranges)
            if colliding_item1:
                raise exceptions.HostNetworkRangeCollisionValidationError(
                    f"{self.__name} contains tools with IPv6 ranges that collides",
                    range_1=colliding_item1,
                    range_2=colliding_item2,
                )

    def __parse_tool_multus(self, raw_definition: typing.Dict[str, typing.Any]):
        multus_raw_config = _validate_parse_field_type(
            self.__FIELD_TOOLS_MULTUS,
            raw_definition,
            dict,
            parent_name=self.__name,
            parent_type=self.__OBJECT_TYPE_NAME,
            mandatory=False,
        )
        if multus_raw_config:
            self.__multus_config = MultusNetworkDefinition(self, multus_raw_config)

    def __parse_tool_metallb(self, raw_definition: typing.Dict[str, typing.Any]):
        metallb_raw_config = _validate_parse_field_type(
            self.__FIELD_TOOLS_METALLB,
            raw_definition,
            dict,
            parent_name=self.__name,
            parent_type=self.__OBJECT_TYPE_NAME,
            mandatory=False,
        )
        if metallb_raw_config:
            self.__metallb_config = MetallbNetworkDefinition(self, metallb_raw_config)

    def __parse_tool_netconfig(self, raw_definition: typing.Dict[str, typing.Any]):
        netconfig_raw_config = _validate_parse_field_type(
            self.__FIELD_TOOLS_NETCONFIG,
            raw_definition,
            dict,
            parent_name=self.__name,
            parent_type=self.__OBJECT_TYPE_NAME,
            mandatory=False,
        )
        if netconfig_raw_config:
            self.__netconfig_config = NetconfigNetworkDefinition(
                self, netconfig_raw_config
            )

    def __hash__(self) -> int:
        return hash(
            (
                self.__ipv6_network,
                self.__ipv4_network,
                self.__name,
                self.__mtu,
                self.__vlan,
                self.__multus_config,
                self.__netconfig_config,
                self.__metallb_config,
            )
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, NetworkDefinition):
            return False

        return (
            self.__ipv6_network == other.__ipv6_network
            and self.__ipv4_network == other.__ipv4_network
            and self.__name == other.__name
            and self.__mtu == other.__mtu
            and self.__vlan == other.__vlan
            and self.__multus_config == other.__multus_config
            and self.__netconfig_config == other.__netconfig_config
            and self.__metallb_config == other.__metallb_config
        )


@dataclasses.dataclass(frozen=True)
class GroupTemplateNetworkDefinition:
    """
    Holds the configuration of a group for a given network.

    Attributes:
        network: The network the instance refers to.
        group_name: The group the instance refers to.
        ipv4_range: The IPv4 range of the group for the network.
        ipv6_range: The IPv6 range of the group for the network.
        skip_nm_configuration: Indicates if the instances of the
            group should skip configuring Network Manager for the
            given network.
        is_trunk_parent: indicates whether the instance nic for
            this network is a parent of the trunked VLANs.
        trunk_parent: if the network is a trunk in the target instances,
            it points to the GroupTemplateNetworkDefinition of that network.
    """

    network: NetworkDefinition
    group_name: str
    ipv6_range: HostNetworkRange = None
    ipv4_range: HostNetworkRange = None
    skip_nm_configuration: bool = None
    is_trunk_parent: bool = None
    trunk_parent: GroupTemplateNetworkDefinition = None

    def __hash__(self) -> int:
        return hash(
            (
                self.network,
                self.group_name,
                self.ipv4_range,
                self.ipv6_range,
                self.skip_nm_configuration,
                self.is_trunk_parent,
                self.trunk_parent,
            )
        )


class GroupTemplateDefinition:
    """Parser and validator of a group template

    Handles the parsing and validation of an individual group template
    of the Networking Definition.

    The group template definition that this class parses should follow
    this format:

    .. code-block:: YAML

        <group-name>:
            skip-nm-configuration: <true/false: defaults to False>

            # 'network-template' is an optional field that can hold
            # the base configuration for each network. If given, each
            # declared network content will use the variables defined
            # there as a base that can be overridden by each network
            # content
            network-template:   # Optional template

            networks:
                <network-name>:
                    skip-nm-configuration: <true/false: defaults to False>
                    # 'range' applies to all IPv4 and IPv6 nets of the declared
                    #  network. For more fine grade settings use the dedicated
                    # range-v4 and range-v6
                    range:      # shouldn't be declared if range-v4/v6 present
                        start:  <start index/ip>
                        end:    <end index/ip: optional if length given>
                        length: <size of the range: optional if end given>
                    range-v4:   # Only applies to the IPv4 network
                        start:  <start index/IPv4>
                        end:    <end index/IPv4: optional if length given>
                        length: <size of the range: optional if end given>
                    range-v6:   # Only applies to the IPv6 network
                        start:  <start index/IPv6>
                        end:    <end index/IPv4: optional if length given>
                        length: <size of the range: optional if end given>
    """

    __OBJECT_TYPE_NAME = "host-template"
    __FIELD_SKIP_NM = "skip-nm-configuration"
    __FIELD_NETWORKS = "networks"
    __FIELD_NETWORK_TEMPLATE = "network-template"
    __FIELD_NETWORK_SKIP_NM = "skip-nm-configuration"
    __FIELD_NETWORK_RANGE = "range"
    __FIELD_NETWORK_RANGE_IPV4 = "range-v4"
    __FIELD_NETWORK_RANGE_IPV6 = "range-v6"
    __FIELD_IS_TRUNK_PARENT = "is-trunk-parent"
    __FIELD_TRUNK_PARENT = "trunk-parent"

    def __init__(
        self,
        group_name,
        raw_definition: typing.Dict[str, typing.Any],
        network_definitions: typing.Dict[str, NetworkDefinition],
    ):
        """Initializes a GroupTemplateDefinition from dict with its parameters

         Args:
            group_name: The name of the group in the inventory
            raw_definition: The dictionary that contains the configuration
                of the group template.
            network_definitions: Dict of the existing NetworkDefinition

        Raises:
            ValueError: If group_name it's not provided.
            exceptions.NetworkMappingValidationError: When the format
                of the provided group template is not correct.
        """
        if not group_name:
            raise ValueError("group_name is a mandatory argument")
        self.__group_name = group_name

        self.__skip_nm_configuration: typing.Optional[bool] = None
        self.__groups_networks_definitions = {}
        self.__parse_raw(raw_definition, network_definitions)

    @property
    def networks(self) -> typing.Dict[str, GroupTemplateNetworkDefinition]:
        """List of the target networks and their settings for the group."""
        return self.__groups_networks_definitions

    @property
    def skip_nm_configuration(self) -> typing.Optional[bool]:
        """Indicates that Network Manager configuration should be
        skipped for all the networks of the group."""
        return self.__skip_nm_configuration

    @property
    def group_name(self) -> str:
        """Inventory group name."""
        return self.__group_name

    def __parse_raw(
        self,
        raw_definition: typing.Dict[str, typing.Any],
        network_definitions: typing.Dict[str, NetworkDefinition],
    ):
        self.__skip_nm_configuration = (
            bool(raw_definition[self.__FIELD_SKIP_NM])
            if self.__FIELD_SKIP_NM in raw_definition
            else None
        )

        networks = _validate_parse_field_type(
            self.__FIELD_NETWORKS,
            raw_definition,
            dict,
            parent_name=self.__group_name,
            parent_type=self.__OBJECT_TYPE_NAME,
            mandatory=False,
        )
        if networks:
            network_template_raw = (
                _validate_parse_field_type(
                    self.__FIELD_NETWORK_TEMPLATE,
                    raw_definition,
                    dict,
                    parent_name=self.__group_name,
                    parent_type=self.__OBJECT_TYPE_NAME,
                    mandatory=False,
                )
                or {}
            )

            # Firstly, process networks that won't be trunk parents
            trunk_parents = {
                net_name: net_data
                for net_name, net_data in networks.items()
                if net_data is not None and self.__FIELD_TRUNK_PARENT not in net_data
            }
            for network_name, network_data in trunk_parents.items():
                self.__parse_raw_net(
                    network_name,
                    network_data,
                    network_template_raw,
                    network_definitions,
                )

            # Process networks that are part of a trunk
            child_nets = dict(networks)
            map(child_nets.pop, trunk_parents)
            for network_name, network_data in child_nets.items():
                self.__parse_raw_net(
                    network_name,
                    network_data,
                    network_template_raw,
                    network_definitions,
                    trunk_parents=set(trunk_parents.keys()),
                )

    def __parse_raw_net(
        self,
        network_name: str,
        network_data: typing.Dict[str, typing.Any],
        network_template_raw: typing.Dict[str, typing.Any],
        network_definitions: typing.Dict[str, NetworkDefinition],
        trunk_parents: typing.Set[str] = None,
    ):
        network_definition = network_definitions.get(network_name, None)
        if not network_definition:
            raise exceptions.NetworkMappingValidationError(
                f"{self.__group_name} template points "
                f"to the non-existing network {network_name}",
                invalid_value=network_name,
            )

        original_net_data = network_data or {}
        networks_template = copy.deepcopy(network_template_raw or {})
        # In case the network declared a range overrides it entirely
        # by discarding the one from the template
        if (
            self.__FIELD_NETWORK_RANGE in original_net_data
            or self.__FIELD_NETWORK_RANGE_IPV4 in original_net_data
            or self.__FIELD_NETWORK_RANGE_IPV6 in original_net_data
        ):
            networks_template.pop(self.__FIELD_NETWORK_RANGE, None)
            networks_template.pop(self.__FIELD_NETWORK_RANGE_IPV4, None)
            networks_template.pop(self.__FIELD_NETWORK_RANGE_IPV6, None)

        templated_net_data = {**networks_template, **original_net_data}
        ipv4_network_range, ipv6_network_range = self.__parse_raw_net_ranges(
            templated_net_data, network_definition
        )

        skip_nm_configuration = (
            bool(templated_net_data[self.__FIELD_NETWORK_SKIP_NM])
            if self.__FIELD_NETWORK_SKIP_NM in templated_net_data
            else None
        )
        is_trunk_parent = _validate_parse_field_type(
            self.__FIELD_IS_TRUNK_PARENT,
            templated_net_data,
            bool,
            parent_name=self.__group_name,
            parent_type=self.__OBJECT_TYPE_NAME,
            mandatory=False,
        )

        trunk_parent_str = _validate_parse_trunk_parent_field(
            self.__FIELD_TRUNK_PARENT,
            templated_net_data,
            self.group_name,
            self.__OBJECT_TYPE_NAME,
            trunk_parents,
        )

        trunk_parent = (
            self.__groups_networks_definitions[trunk_parent_str]
            if trunk_parent_str
            else None
        )

        self.__groups_networks_definitions[network_name] = (
            GroupTemplateNetworkDefinition(
                network_definition,
                self.__group_name,
                ipv4_range=ipv4_network_range,
                ipv6_range=ipv6_network_range,
                skip_nm_configuration=skip_nm_configuration,
                is_trunk_parent=is_trunk_parent,
                trunk_parent=trunk_parent,
            )
        )

    def __parse_raw_net_ranges(
        self,
        raw_definition: typing.Dict[str, typing.Any],
        network_definition: NetworkDefinition,
    ) -> typing.Tuple[
        typing.Union[HostNetworkRange, None], typing.Union[HostNetworkRange, None]
    ]:
        ranges_present = _validate_fields_one_of(
            [
                self.__FIELD_NETWORK_RANGE,
                self.__FIELD_NETWORK_RANGE_IPV4,
                self.__FIELD_NETWORK_RANGE_IPV6,
            ],
            raw_definition,
            parent_name=self.__group_name,
            parent_type=self.__OBJECT_TYPE_NAME,
            alone_field=self.__FIELD_NETWORK_RANGE,
        )
        if not ranges_present:
            return None, None

        if self.__FIELD_NETWORK_RANGE in raw_definition:
            (
                ipv4_network_range,
                ipv6_network_range,
            ) = network_definition.parse_range_from_raw(
                raw_definition[self.__FIELD_NETWORK_RANGE]
            )
        else:
            ipv4_network_range = (
                network_definition.parse_range_from_raw(
                    raw_definition[self.__FIELD_NETWORK_RANGE_IPV4], ip_version=4
                )[0]
                if self.__FIELD_NETWORK_RANGE_IPV4 in raw_definition
                else None
            )

            ipv6_network_range = (
                network_definition.parse_range_from_raw(
                    raw_definition[self.__FIELD_NETWORK_RANGE_IPV6], ip_version=6
                )[1]
                if self.__FIELD_NETWORK_RANGE_IPV6 in raw_definition
                else None
            )
        return ipv4_network_range, ipv6_network_range

    def __hash__(self) -> int:
        return hash(
            (
                frozenset(self.__groups_networks_definitions.items()),
                self.__group_name,
                self.__skip_nm_configuration,
            )
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, GroupTemplateDefinition):
            return False

        return (
            self.__group_name == other.__group_name
            and self.__groups_networks_definitions
            == other.__groups_networks_definitions
            and self.__skip_nm_configuration == other.__skip_nm_configuration
        )


@dataclasses.dataclass(frozen=True)
class InstanceNetworkDefinition:
    network: NetworkDefinition
    ipv4: ipaddress.IPv4Address = None
    ipv6: ipaddress.IPv6Address = None
    skip_nm_configuration: bool = None
    is_trunk_parent: bool = None
    trunk_parent: InstanceNetworkDefinition = None

    def __hash__(self) -> int:
        return hash(
            (
                self.network,
                self.ipv4,
                self.ipv6,
                self.skip_nm_configuration,
                self.is_trunk_parent,
                self.trunk_parent,
            )
        )


class InstanceDefinition:
    """Parser and validator of an instance definition

    Handles the parsing and validation of an individual instance of the
    Networking Definition.

    The instance definition that this class parses should follow this
    format:

    .. code-block:: YAML

        <instance-name>:
            # Skip configuring Network Manager for all instance's nets
            skip-nm-configuration: <true/false: defaults to False>
            networks:
                <network-name>:
                    # Skip configuring Network Manager for this network and
                    # for this instance
                    skip-nm-configuration: <true/false: defaults to False>

                    # 'ip' that this instance should use for the given net
                    # Cannot be present if ip-v4/v6 are given
                    ip:      # shouldn't be declared if range-v4/v6 present

                    # 'ip-v4' and 'ip-v6' can be provided when the network
                    # is configured with IPv4 and IPv6 at the same time.
                    ip-v4:   <IPv4 IP>
                    ip-v6:   <IPv6 IP>
    """

    __OBJECT_TYPE_NAME = "instance"
    __FIELD_SKIP_NM = "skip-nm-configuration"
    __FIELD_NETWORKS = "networks"
    __FIELD_NETWORKS_IP = "ip"
    __FIELD_NETWORK_SKIP_NM = "skip-nm-configuration"
    __FIELD_IS_TRUNK_PARENT = "is-trunk-parent"
    __FIELD_TRUNK_PARENT = "trunk-parent"

    def __init__(
        self,
        name: str,
        raw_definition: typing.Dict[str, typing.Any],
        network_definitions: typing.Dict[str, NetworkDefinition],
    ):
        """Initializes an InstanceDefinition from dict with its parameters

        Args:
            name: The name of the instance in the inventory
            raw_definition: The dictionary that contains the configuration
                 of the instance.
            network_definitions: Dict of the existing NetworkDefinition

        Raises:
            ValueError: If group_name it's not provided.
            exceptions.NetworkMappingValidationError: When the format
                of the provided instance is not correct.
        """
        if not name:
            raise ValueError("name is a mandatory argument")

        self.__name = name
        self.__skip_nm_configuration: typing.Optional[bool] = None
        self.__instances_network_definitions = {}
        self.__parse_raw(raw_definition, network_definitions)

    @property
    def networks(self) -> typing.Dict[str, InstanceNetworkDefinition]:
        """List of the target networks and their settings, for instance."""
        return self.__instances_network_definitions

    @property
    def skip_nm_configuration(self) -> typing.Optional[bool]:
        """Indicates that Network Manager configuration should be skipped
        for all the networks of the instance."""
        return self.__skip_nm_configuration

    @property
    def name(self) -> str:
        """Instance name"""
        return self.__name

    def __parse_raw(
        self,
        raw_definition: typing.Dict[str, typing.Any],
        network_definitions: typing.Dict[str, NetworkDefinition],
    ):
        self.__skip_nm_configuration = (
            bool(raw_definition[self.__FIELD_SKIP_NM])
            if self.__FIELD_SKIP_NM in raw_definition
            else None
        )
        networks = raw_definition.get(self.__FIELD_NETWORKS, {})
        if not isinstance(networks, dict):
            raise exceptions.NetworkMappingValidationError(
                f"Field '{self.__FIELD_NETWORKS}' must be a dictionary",
                field=self.__FIELD_NETWORKS,
            )

        # Firstly, process networks that won't be trunk parents
        trunk_parents = {
            net_name: net_data
            for net_name, net_data in networks.items()
            if net_data is not None and self.__FIELD_TRUNK_PARENT not in net_data
        }
        for network_name, network_data in trunk_parents.items():
            self.__parse_raw_net(
                network_name,
                network_data,
                network_definitions,
            )

        # Process networks that are part of a trunk
        child_nets = dict(networks)
        map(child_nets.pop, trunk_parents)
        for network_name, network_data in child_nets.items():
            self.__parse_raw_net(
                network_name,
                network_data or {},
                network_definitions,
                trunk_parents=set(trunk_parents.keys()),
            )

    def __parse_raw_net(
        self,
        network_name: str,
        network_data: typing.Dict[str, typing.Any],
        network_definitions: typing.Dict[str, NetworkDefinition],
        trunk_parents: typing.Set[str] = None,
    ):
        network_definition = network_definitions.get(network_name, None)
        if not network_definition:
            raise exceptions.NetworkMappingValidationError(
                f"{self.__name} instance points to the "
                f"non-existing network {network_name}",
                invalid_value=network_name,
            )

        ipv4, ipv6 = _validate_parse_raw_net_ips(
            self.__FIELD_NETWORKS_IP,
            network_data,
            network_definition.ipv4_network,
            network_definition.ipv6_network,
            parent_type=self.__OBJECT_TYPE_NAME,
            parent_name=self.__name,
        )

        skip_nm_configuration = (
            bool(network_data[self.__FIELD_NETWORK_SKIP_NM])
            if self.__FIELD_NETWORK_SKIP_NM in network_data
            else None
        )

        is_trunk_parent = _validate_parse_field_type(
            self.__FIELD_IS_TRUNK_PARENT,
            network_data,
            bool,
            parent_type=self.__OBJECT_TYPE_NAME,
            parent_name=self.__name,
            mandatory=False,
        )

        trunk_parent = None
        if trunk_parents:
            trunk_parent_str = _validate_parse_trunk_parent_field(
                self.__FIELD_TRUNK_PARENT,
                network_data,
                self.name,
                self.__OBJECT_TYPE_NAME,
                trunk_parents,
            )

            trunk_parent = (
                self.__instances_network_definitions[trunk_parent_str]
                if trunk_parent_str
                else None
            )

        self.__instances_network_definitions[network_name] = InstanceNetworkDefinition(
            network_definition,
            ipv4=ipv4,
            ipv6=ipv6,
            skip_nm_configuration=skip_nm_configuration,
            is_trunk_parent=is_trunk_parent,
            trunk_parent=trunk_parent,
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.__name,
                frozenset(self.__instances_network_definitions.items()),
                self.__skip_nm_configuration,
            )
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, InstanceDefinition):
            return False

        return (
            self.__name == other.__name
            and self.__instances_network_definitions
            == other.__instances_network_definitions
            and self.__skip_nm_configuration == other.__skip_nm_configuration
        )


class NetworkingDefinition:
    """Parser and validator of the Networking Definition

    Handles the parsing and validation of the entire Networking Definition.

    The Networking Definition should follow this format:

    .. code-block:: YAML

        networks:
            <network-name>: <InstanceDefinition instance>
        group-templates:
            <group-name>: <GroupTemplateDefinition instance>
        instances:
            <instance-name>: <InstanceDefinition instance>
    """

    __FIELD_NETWORKS = "networks"
    __FIELD_GROUP_TEMPLATES = "group-templates"
    __FIELD_INSTANCES = "instances"
    __FIELD_ROUTERS = "routers"

    def __init__(self, raw_definition: typing.Dict[str, typing.Any]):
        """Initializes a NetworkingDefinition from dict with its parameters

        Args:
            raw_definition: The dictionary that contains the complete
                network definition.
        Raises:
            exceptions.NetworkMappingValidationError: When the format
                of the provided dictionary is not a valid Networking
                Definition.
        """
        self.__networks: typing.Dict[str, NetworkDefinition] = {}
        self.__group_templates: typing.Dict[str, GroupTemplateDefinition] = {}
        self.__instances = {}
        self.__routers = {}

        self.__parse_raw(raw_definition)

    @property
    def networks(self) -> typing.Dict[str, NetworkDefinition]:
        return self.__networks

    @property
    def group_templates(self) -> typing.Dict[str, GroupTemplateDefinition]:
        return self.__group_templates

    @property
    def instances(self) -> typing.Dict[str, InstanceDefinition]:
        return self.__instances

    @property
    def routers(self) -> typing.Dict[str, RouterDefinition]:
        return self.__routers

    def __parse_raw(self, raw_definition: typing.Dict[str, typing.Any]):
        networks_raw = (
            _validate_parse_field_type(
                self.__FIELD_NETWORKS,
                raw_definition,
                dict,
                mandatory=False,
            )
            or {}
        )

        group_templates_raw = (
            _validate_parse_field_type(
                self.__FIELD_GROUP_TEMPLATES,
                raw_definition,
                dict,
                mandatory=False,
            )
            or {}
        )

        instances_raw = (
            _validate_parse_field_type(
                self.__FIELD_INSTANCES,
                raw_definition,
                dict,
                mandatory=False,
            )
            or {}
        )

        routers_raw = (
            _validate_parse_field_type(
                self.__FIELD_ROUTERS,
                raw_definition,
                dict,
                mandatory=False,
            )
            or {}
        )

        self.__networks = {
            net_name: NetworkDefinition(net_name, net_raw)
            for net_name, net_raw in networks_raw.items()
        }
        self.__group_templates = {
            group_name: GroupTemplateDefinition(group_name, group_raw, self.__networks)
            for group_name, group_raw in group_templates_raw.items()
        }
        self.__instances = {
            instance_name: InstanceDefinition(
                instance_name, instance_raw, self.__networks
            )
            for instance_name, instance_raw in instances_raw.items()
        }
        self.__routers = {
            router_name: RouterDefinition(router_name, router_raw)
            for router_name, router_raw in routers_raw.items()
        }

        self.__check_overlapping_ranges()

    def __check_overlapping_ranges(self):
        ranges_by_net_ipv4: typing.Dict[str, typing.List[HostNetworkRange]] = {}
        ranges_by_net_ipv6: typing.Dict[str, typing.List[HostNetworkRange]] = {}
        for group_definition in self.__group_templates.values():
            for net_name, group_net_def in group_definition.networks.items():
                if net_name not in ranges_by_net_ipv4:
                    ranges_by_net_ipv4[net_name] = []
                if net_name not in ranges_by_net_ipv6:
                    ranges_by_net_ipv6[net_name] = []
                if group_net_def.ipv4_range:
                    ranges_by_net_ipv4[net_name].append(group_net_def.ipv4_range)
                if group_net_def.ipv6_range:
                    ranges_by_net_ipv6[net_name].append(group_net_def.ipv6_range)
        self.__check_overlapping_ranges_dict(ranges_by_net_ipv4)
        self.__check_overlapping_ranges_dict(ranges_by_net_ipv6)

    @staticmethod
    def __check_overlapping_ranges_dict(
        ranges_dict: typing.Dict[str, typing.List[HostNetworkRange]]
    ):
        for net_name, net_ranges in ranges_dict.items():
            if len(net_ranges) < 2:
                continue

            (
                colliding_item1,
                colliding_item2,
            ) = check_host_network_ranges_collisions(net_ranges)
            if colliding_item1:
                raise exceptions.HostNetworkRangeCollisionValidationError(
                    f"{net_name} contains ranges that collides",
                    range_1=colliding_item1,
                    range_2=colliding_item2,
                )

    def __hash__(self) -> int:
        return hash(
            (
                frozenset(self.__networks.items()),
                frozenset(self.__group_templates.items()),
                frozenset(self.__instances.items()),
            )
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, NetworkingDefinition):
            return False

        return (
            self.__networks == other.__networks
            and self.__instances == other.__instances
            and self.__group_templates == other.__group_templates
        )
