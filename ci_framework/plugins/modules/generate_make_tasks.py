#!/usr/bin/python

# Copyright Red Hat, Inc.
# Apache License Version 2.0 (see LICENSE

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: generate_make_tasks

short_description: Generate per Makefile target a dedicated task file

description:
- Generate per Makefile target a dedicated task file

options:
  install_yamls_path:
    description:
    - Absolute path to install_yamls repository.
    required: True
    type: str
  output_directory:
    description:
    - Absolute path to the output directory. It must exists.
    required: True
    type: str

author:
  - Chandan Kumar (@raukadah)
  - Cedric Jeanneret (@cjeanner)

'''

EXAMPLES = r'''
- name: Create output directory
  ansible.builtin.file:
    path: "{{ ansible_user_dir }}/make_installyamls/tasks"
    state: directory

- name: Generate make tasks
  generate_make_tasks:
    install_yamls_path: "{{ ansible_user_dir }}/src/github.com/openstack-k8s-operators/install_yamls/"
    output_directory: "{{ ansible_user_dir }}/make_installyamls/tasks"
'''

RETURN = r'''
success:
    description: Status of the module
    type: bool
    returned: always
    sample: True
'''

from ansible.module_utils.basic import AnsibleModule

import os


MAKE_TMPL = '''---
- name: Run `make %(target)s`
  ci_make:
    output_directory: "{{ cifmw_install_yamls_basedir }}/artifacts"
    chdir: "%(chdir)s"
    target: %(target)s
    dry_run: "{{ cifmw_install_yamls_dryrun|bool }}"
  environment: "{{ edpm_env }}"
'''

NO_OUTDIR = 'Directory %s does not exist. Please create it.'
NO_MAKEFILE = 'No makefile was parsed. Please check install_yamls path (%s).'


def main():
    mod_args = {
        'install_yamls_path': {'required': True, 'type': 'str'},
        'output_directory': {'required': True, 'type': 'str'},
    }
    module = AnsibleModule(
        argument_spec=mod_args,
        supports_check_mode=False
    )

    result = {
        'success': False,
        'changed': False,
        'error': '',
    }
    install_yamls = module.params.get('install_yamls_path')
    output_directory = module.params.get('output_directory')

    # Check for output dir
    if not os.path.isdir(output_directory):
        result['error'] = NO_OUTDIR % output_directory
        module.fail_json(msg=result['error'])

    # Read the content of the makefiles and extract targets
    targets = []
    for makefiles in ['Makefile', 'devsetup/Makefile']:
        makefile_path = os.path.join(install_yamls, makefiles)
        if os.path.exists(makefile_path):
            makefile_chdir = os.path.dirname(makefile_path)
            with open(makefile_path) as f:
                targets = [line.split('.PHONY:')[1].strip() for line in f.readlines() if '.PHONY:' in line]

            # Ensure we parsed some Makefiles
            if len(targets) == 0:
                result['error'] = NO_MAKEFILE % install_yamls
                module.fail_json(msg=result['error'])

            # Generate playbooks
            for target in targets:
                output = f'make_{target}.yaml'
                with open(os.path.join(output_directory, output), 'w') as fs:
                    fs.write(MAKE_TMPL % {'target': target, 'chdir': makefile_chdir})

    result["success"] = True
    module.exit_json(**result)


if __name__ == '__main__':
    main()
