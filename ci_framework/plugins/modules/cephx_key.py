#!/usr/bin/python

# Copyright: (c) 2023, John Fulton <fulton@redhat.com>
# Apache License Version 2.0 (see LICENSE)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: cephx_key

short_description: Generate a random CephX authenticaton key

description:
- Generate a random CephX authenticaton key and return it

author:
  - John Fulton (@fultonj)
'''

EXAMPLES = r'''
- name: Generate a cephx key
  cephx_key:
  register: cephx

- name: Show cephx key
  debug:
    msg: "{{ cephx.key }}"
'''

RETURN = r'''
key:
    description: A random cephx authentication key
    type: dict
    returned: success
    sample:
        - KEY: AQC+vYNXgDAgAhAAc8UoYt+OTz5uhV7ItLdwUw==
'''


from ansible.module_utils.basic import AnsibleModule
import base64
import os
import struct
import time


def __create_cephx_key():
    # NOTE(fultonj): Taken from
    # https://github.com/ceph/ceph-deploy/blob/master/ceph_deploy/new.py#L21
    key = os.urandom(16)
    header = struct.pack("<hiih", 1, int(time.time()), 0, len(key))
    return base64.b64encode(header + key).decode('utf-8')


def main():
    mod_args = {}
    module = AnsibleModule(
        argument_spec=mod_args,
        supports_check_mode=False
    )

    result = {
        'changed': False,
        'error': ''
    }

    cephx_key = __create_cephx_key()
    if not cephx_key:
        result['msg'] = "Error: unable to create cephx key"
        module.fail_json(**result)
        return

    result['key'] = cephx_key
    module.exit_json(**result)


if __name__ == '__main__':
    main()
