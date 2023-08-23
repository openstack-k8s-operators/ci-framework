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
import os
import pathlib
import subprocess
import tempfile


__TMP_TARGET_NAME = "cifmw_dump_vars"
__TMPL_DUMP_VARS_TARGET = '''
.PHONY: %(target)s
%(target)s:
\tprintf "%(cmd)s" >> %(out_file)s
'''


def __get_makefile_raw_variables(makefile_path):
    with open(makefile_path, "r") as f:
        return set([line.split('?=')[0].rstrip() for line in f.readlines() if '?=' in line and (not line.startswith("#"))])


def __get_makefile_variables(makefile_path):
    makefile_variables = __get_makefile_raw_variables(makefile_path)
    with open(makefile_path, "r") as makefile_f, tempfile.TemporaryDirectory() as temp_dir, open(os.path.join(temp_dir, "Makefile"), "w") as temp_makefile_f:
        # Copy the Makefile content to the new temporal one
        makefile_lines = makefile_f.readlines()
        temp_makefile_f.writelines(makefile_lines)

        # Prepare a single printf command that will dump each known variable to a file
        var_dump_cmd = "\\n".join(["{0}: ${{{1}}}".format(var_name, var_name) for var_name in makefile_variables])

        # Create the injected target that will dump the variables to a file using the previous command
        vars_out_path = os.path.join(temp_dir, "vars")
        target_data = __TMPL_DUMP_VARS_TARGET % {
            "target": __TMP_TARGET_NAME,
            "cmd": var_dump_cmd,
            "out_file": vars_out_path,
        }

        # Write the injected target to the temporal Makefile
        temp_makefile_f.write(target_data)
        temp_makefile_f.flush()

        # Call the injected target
        subprocess.run(["make", __TMP_TARGET_NAME], check=False, cwd=temp_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Read and parse the resulting dump file
        with open(vars_out_path, "r") as vars_content:
            vars_dict = {}
            for vars_line in vars_content.readlines():
                line_split = vars_line.strip().split(":", 1)
                vars_dict[line_split[0]] = line_split[1].lstrip() if len(line_split) > 1 else None
            return vars_dict


def __get_makefiles_vars(root_path):
    base_path = pathlib.Path(root_path)
    if not base_path.is_dir():
        return None
    makefiles_vars = {}
    for path in base_path.rglob('Makefile'):
        makefiles_vars.update(__get_makefile_variables(path))

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
        result['msg'] = f"Error! Makefiles base path {makefiles_root} not found"
        module.fail_json(**result)
        return

    result['makefiles_values'] = makefiles_vars
    module.exit_json(**result)


if __name__ == '__main__':
    main()
