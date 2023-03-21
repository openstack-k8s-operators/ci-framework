#!/usr/bin/python

# Copyright: (c) 2023, Chandan Kumar <chkumar@redhat.com>
# Apache License Version 2.0 (see LICENSE)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: generate_make_env

short_description: Generate a YAML structure with env vars.

description:
- Generate a YAML structure with the environment variables used in
  install_yamls Makefiles.

options:
  install_yamls_path:
      description:
      - Full path of the install_yamls makefile.
      required: True
      type: str
  install_yamls_var:
      description:
      - List of exported install_yamls variable.
      required: true
      type: dict
  check_var:
      description:
      - Check the environment var exists in the makefile.
      required: false
      type: bool
      default: True
author:
  - Chandan Kumar (@raukadah)
  - Cedric Jeanneret (@cjeanner)
'''

EXAMPLES = r'''
# Create env var file
- name: Generate env var fact
  become: true
  generate_make_env:
    install_yamls_path: <path to make file>
    install_yamls_var:
        microshift: 1
'''

RETURN = r'''
sucess:
    description: env file created successfully
    type: bool
    returned: always
    sample: "True"
'''


from ansible.module_utils.basic import AnsibleModule
import os


# Return install_yamls vars
def _get_makefile_vars(install_yamls_path):
    parameters = {}
    for makefile in ['Makefile', 'devsetup/Makefile']:
        make_path = os.path.join(install_yamls_path, makefile)
        make_dir = os.path.dirname(make_path)
        if os.path.exists(make_path):
            with open(make_path) as f:
                parameters[make_dir] = [line.split('?=') for line in f.readlines() if '?=' in line]
                parameters[make_dir] = {k.strip().lower(): v.strip() for k, v in parameters[make_dir]}
                return parameters
    return None


# Check if vars exists in install_yamls or not
def _check_vars(install_yamls_path, users_var):
    var_not_found = []
    makefile_vars = _get_makefile_vars(install_yamls_path)
    if makefile_vars:
        for key in users_var.keys():
            if not any(key in makefile for makefile in makefile_vars):
                var_not_found.append(key)

    return var_not_found


# Create yaml file
def _generate_struct(users_var):
    return {k.upper(): v for k, v in users_var.items()}


# Run the module
def create_env_struct(makefile, check_var, users_var):
    unwanted_vars = []
    if check_var:
        unwanted_vars = _check_vars(makefile, users_var)
    if not unwanted_vars:
        return _generate_struct(users_var)


def main():
    mod_args = {
        'install_yamls_path': {'required': True, 'type': 'str'},
        'install_yamls_var': {'required': True, 'type': 'dict'},
        'check_var': {'required': False, 'type': 'bool', 'default': True},
    }
    module = AnsibleModule(
        argument_spec=mod_args,
        supports_check_mode=False
    )

    result = {
        'success': False,
        'changed': False,
        'error': '',
        'ansible_facts': {},
    }

    # Get the module output
    install_yamls = module.params.get("install_yamls_path")
    check_var = module.params.get("check_var")
    users_var = module.params.get("install_yamls_var")

    status = create_env_struct(install_yamls, check_var, users_var)

    if status:
        result["success"] = True
    else:
        result["msg"] = "Error! something went wrong while generating environment structure"
        module.fail_json(**result)

    result['ansible_facts']['edpm_env'] = status
    module.exit_json(**result)


if __name__ == '__main__':
    main()
