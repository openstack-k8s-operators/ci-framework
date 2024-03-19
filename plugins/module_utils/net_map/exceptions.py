import typing

from ansible_collections.cifmw.general.plugins.module_utils.encoding import (
    ansible_encoding,
)


class NetworkMappingError(Exception, ansible_encoding.RawConvertibleObject):
    def __init__(self, message) -> None:
        super().__init__(message)
        self.message = message

    def to_raw(self) -> typing.Dict[str, typing.Any]:
        return ansible_encoding.decode_ansible_raw(vars(self))


class NetworkMappingValidationError(NetworkMappingError):
    def __init__(
        self,
        message,
        field=None,
        invalid_value=None,
        parent_name=None,
        parent_type=None,
    ) -> None:
        super().__init__(message)
        self.field = field
        self.invalid_value = invalid_value
        self.parent_name = parent_name
        self.parent_type = parent_type


class HostNetworkRangeCollisionValidationError(NetworkMappingValidationError):
    def __init__(self, message, range_1=None, range_2=None) -> None:
        super().__init__(message)
        self.range_1 = range_1
        self.range_2 = range_2

    def __str__(self):
        return str(vars(self))


class NetworkMappingTrunkParentValidationError(NetworkMappingValidationError):
    def __init__(
        self,
        message,
        field=None,
        invalid_value=None,
        parent_name=None,
        parent_type=None,
    ) -> None:
        super().__init__(message)
        self.field = field
        self.invalid_value = invalid_value
        self.parent_name = parent_name
        self.parent_type = parent_type
