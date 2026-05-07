#!/usr/bin/python

# Copyright: (c) 2023, John Fulton <fulton@redhat.com>
# Apache License Version 2.0 (see LICENSE)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: cephx_key

short_description: Generate a random CephX authentication key

description:
- Generate a random CephX authentication key and return it.
- Supports AES-128 (default, type=1, 16-byte key) and AES-256k (type=2, 32-byte key) ciphers.

options:
  cipher:
    description:
      - The cipher to use when generating the CephX key.
      - Use C(aes) for AES-128 (16-byte key, 40-char base64, type=1). This is the default.
      - Use C(aes256k) for AES-256k (32-byte key, 60-char base64, type=2).
    type: str
    default: aes
    choices: [aes, aes256k]

author:
  - John Fulton (@fultonj)
"""

EXAMPLES = r"""
- name: Generate a cephx key (AES-128, backward compatible default)
  cifmw.general.cephx_key:
  register: cephx

- name: Generate a cephx key with explicit AES-128 cipher
  cifmw.general.cephx_key:
    cipher: aes
  register: cephx

- name: Generate a cephx key with AES-256k cipher
  cifmw.general.cephx_key:
    cipher: aes256k
  register: cephx

- name: Show cephx key
  debug:
    msg: "{{ cephx.key }}"
"""

RETURN = r"""
key:
    description:
      - A random CephX authentication key encoded as base64.
      - AES-128 keys are 40 characters long (ending with ==).
      - AES-256k keys are 60 characters long (ending with =).
    type: str
    returned: success
    sample:
        - AQC+vYNXgDAgAhAAc8UoYt+OTz5uhV7ItLdwUw==
"""


from ansible.module_utils.basic import AnsibleModule
import base64
import os
import struct
import time


def __create_cephx_key(cipher="aes"):
    # NOTE(fultonj): Taken from
    # https://github.com/ceph/ceph-deploy/blob/master/ceph_deploy/new.py#L21
    if cipher == "aes256k":
        key_type = 2
        key = os.urandom(32)
    else:
        key_type = 1
        key = os.urandom(16)
    header = struct.pack("<hiih", key_type, int(time.time()), 0, len(key))
    return base64.b64encode(header + key).decode("utf-8")


def main():
    mod_args = {
        "cipher": {
            "type": "str",
            "default": "aes",
            "choices": ["aes", "aes256k"],
        }
    }
    module = AnsibleModule(argument_spec=mod_args, supports_check_mode=False)

    result = {"changed": False, "error": ""}

    cipher = module.params["cipher"]
    cephx_key = __create_cephx_key(cipher)
    if not cephx_key:
        result["msg"] = "Error: unable to create cephx key"
        module.fail_json(**result)
        return

    result["key"] = cephx_key
    module.exit_json(**result)


if __name__ == "__main__":
    main()
