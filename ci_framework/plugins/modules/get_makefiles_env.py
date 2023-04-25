#!/usr/bin/python

# Copyright: (c) 2023, Chandan Kumar <chkumar@redhat.com>
# Apache License Version 2.0 (see LICENSE)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: get_makefiles_env

short_description: Recursively get Makefiles default variables.

description:
- Retrieves a dictionary with all the environment variables
  defined in the Makefiles under the given path.

options:
  base_path:
      description:
      - The base path on where to start picking Makefiles vars.
      required: True
      type: str
author:
  - Chandan Kumar (@raukadah)
  - Cedric Jeanneret (@cjeanner)
  - Pablo Rodriguez (@pablintino)
'''

EXAMPLES = r'''
# Recursively get all the variables of the Makefiles under /home/user
- name: Generate env var fact
  register: get_makefiles_env_out
  get_makefiles_env:
    base_path: /home/user
'''

RETURN = r'''
makefiles_values:
    description: The variables and the their default values for each Makefile
    type: dict
    returned: success
    sample:
        - NAMESPACE: openstack
          NETWORK_ISOLATION: true
'''


from ansible.module_utils.basic import AnsibleModule
import pathlib


def __get_makefiles_vars(root_path):
    base_path = pathlib.Path(root_path)
    if not base_path.is_dir():
        return None
    makefiles_vars = {}
    for path in base_path.rglob('Makefile'):
        with path.open() as f:
            lines_split = [line.split('?=') for line in f.readlines() if '?=' in line and not line.startswith('#')]
            for k, v in lines_split:
                makefiles_vars[k.strip()] = v.strip()

    return makefiles_vars


def main():
    mod_args = {
        'base_path': {'required': True, 'type': 'str'},
    }
    module = AnsibleModule(
        argument_spec=mod_args,
        supports_check_mode=False
    )

    result = {
        'changed': False,
        'error': ''
    }

    makefiles_root = module.params.get("base_path")
    makefiles_vars = __get_makefiles_vars(makefiles_root)
    if not makefiles_vars:
        result['msg'] = f"Error! Makefiles bae path {makefiles_root} not found"
        module.fail_json(**result)
        return

    result['makefiles_values'] = makefiles_vars
    module.exit_json(**result)


if __name__ == '__main__':
    main()
