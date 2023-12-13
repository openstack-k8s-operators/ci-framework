import typing

import yaml

from ansible.parsing.yaml.dumper import AnsibleDumper
from ansible.utils.unsafe_proxy import AnsibleUnsafeText, AnsibleUnsafeBytes


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
    if isinstance(data, dict):
        return yaml.load(
            yaml.dump(
                data, Dumper=AnsibleDumper, default_flow_style=False, allow_unicode=True
            ),
            Loader=yaml.Loader,
        )
    if isinstance(data, AnsibleUnsafeText):
        return str(data)
    if isinstance(data, AnsibleUnsafeBytes):
        return bytes(data)
    return data
