import abc
import typing

import yaml

from ansible.parsing.yaml.dumper import AnsibleDumper
from ansible.parsing.yaml.objects import AnsibleUnicode
from ansible.utils.unsafe_proxy import AnsibleUnsafe


class RawConvertibleObject(metaclass=abc.ABCMeta):
    def to_raw(self):
        pass


def decode_ansible_raw(data: typing.Any) -> typing.Any:
    """Converts an Ansible var to a python native one

    Ansible raw input args can contain AnsibleUnicodes or AnsibleUnsafes
    that are not intended to be manipulated directly.
    This function converts the given variable to a one that only contains
    python built-in types.

    Args:
        data: The usafe Ansible content to decode

    Returns: The python types based result

    """
    if isinstance(data, list):
        return [decode_ansible_raw(_data) for _data in data]
    elif isinstance(data, tuple):
        return tuple(decode_ansible_raw(_data) for _data in data)
    elif isinstance(data, RawConvertibleObject):
        return data.to_raw()
    if isinstance(data, dict):
        return {
            decode_ansible_raw(_data_k): decode_ansible_raw(_data_v)
            for _data_k, _data_v in data.items()
        }
    if isinstance(data, (AnsibleUnicode, AnsibleUnsafe)):
        return yaml.load(
            yaml.dump(
                data, Dumper=AnsibleDumper, default_flow_style=False, allow_unicode=True
            ),
            Loader=yaml.Loader,
        )

    return data
