#!/usr/bin/python

# Copyright: (c) 2025, Pablo Rodriguez <pabrodri@redhat.com>
# Apache License Version 2.0 (see LICENSE)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: pem_read
short_description: Reads a PEM file (that can list many certs)

description:
- Reads a PEM file (that can list many certs)
- OU or CN regexes can be provided to filter out the list

author:
  - Pablo Rodriguez (@pablintino)

options:
  path:
    description:
      - The path to the certificate file to be read
    required: True
    type: str
  ou_filter:
    description:
      - Regex that, if given, used to filter the list of certs by OU.
    required: False
    type: str
  cn_filter:
    description:
      - Regex that, if given, used to filter the list of certs by CN.
    required: False
    type: str

"""

EXAMPLES = r"""
- name: Get pem certs from crt file
  pem_read:
    path: "/etc/ssl/certs/ca-certificates.crt"
  register: _certs

- name: Get pem certs from crt file by OU
  pem_read:
    path: "/etc/ssl/certs/ca-certificates.crt"
    ou_filter: "Red Hat"
  register: _certs2
"""

RETURN = r"""
certs:
    description: The list of PEM files
    type: list
    returned: returned request
"""

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

import re
import typing

try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import serialization

    python_cryptography_installed = True
except ImportError:
    python_cryptography_installed = False


def filter_certs(input_certs, ou_filter=None, cn_filter=None):
    certs = []
    for cert in input_certs:
        ou = cert.subject.get_attributes_for_oid(NameOID.ORGANIZATIONAL_UNIT_NAME)
        cn = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        if (
            (ou and ou_filter and re.search(ou_filter, ou[0].value))
            or (cn and cn_filter and re.search(cn_filter, cn[0].value))
            or (not ou_filter and not cn_filter)
        ):
            certs.append(cert)
    return certs


def main():
    module_args = {
        "path": {"type": "str", "required": True},
        "ou_filter": {"type": "str", "required": False},
        "cn_filter": {"type": "str", "required": False},
    }

    result = {"changed": False, "certs": []}

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)
    if not python_cryptography_installed:
        module.fail_json(msg=missing_required_lib("cryptography"))

    path = module.params["path"]
    ou_filter = module.params.get("ou_filter", None)
    cn_filter = module.params.get("cn_filter", None)

    try:
        with open(path, "rb") as f:
            certs = filter_certs(
                x509.load_pem_x509_certificates(f.read()),
                ou_filter=ou_filter,
                cn_filter=cn_filter,
            )
            result["certs"].extend(
                [
                    cert.public_bytes(encoding=serialization.Encoding.PEM).decode(
                        "utf8"
                    )
                    for cert in certs
                ]
            )

    except Exception as e:
        module.fail_json(msg=f"Error fetching reading a PEM file {str(e)}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()
