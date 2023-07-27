# Copyright Red Hat, Inc.
# Apache License Version 2.0 (see LICENSE)

import os
from pathlib import Path
from ansible.errors import AnsibleError
from ansible.module_utils.basic import get_bin_path
from ansible.module_utils.six import ensure_text
from ansible.plugins.action import ActionBase

DOCUMENTATION = r'''
---
action: oc

short_description: Execute OpensShift Client commands - oc -.

description:
- This module searches the oc binary, load the kubeconfig and execute the oc provided commands.
'''

EXAMPLES = r'''
- name: Display the current authenticated user
    oc_cmd:
    command: whoami -c
- name: Display the current authenticated user and get cluster information
      oc:
        cmd: |
          whoami -c
          cluster-info
'''

RETURN = r'''
success:
    description: Status of the module
    type: bool
    returned: always
    sample: True
stdout:
    description: List with the command execution result/s
    type: list
    returned: always
'''


class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        super().run(tmp, task_vars)
        module_args = self._task.args.copy()

        if 'cmd' not in module_args or not module_args['cmd']:
            raise AnsibleError('"cmd" parameter is mandatory')

        # Get remote home, local or remote depending of the hosts
        user_home = Path(task_vars['ansible_user_dir']).resolve()

        # Get cluster auth config path or take by default crc one
        kubeconfig_path = task_vars.get(
            'cifmw_kubeconfig', False) or user_home / ".crc/machines/crc/kubeconfig"
        os.environ["KUBECONFIG"] = str(kubeconfig_path)

        # Additional default paths
        additional_exec_paths = [
            str(user_home / '.crc/bin'),
            str(user_home / '.crc/bin/oc'),
        ]

        # We can provide additional PATHs
        cifmw_oc_path = task_vars.get('cifmw_oc_path', False)
        if cifmw_oc_path:
            additional_exec_paths.append(cifmw_oc_path)

        oc_binary = self._get_oc_binary(additional_exec_paths)

        # Used if we send one in-line command or several using pipe in ansible
        commands = module_args['cmd'].splitlines()
        oc_cmd_results = []
        for cmd in commands:
            oc_cmd_results.append(self._execute_command(f"{oc_binary} {cmd}"))

        module_args['return_content'] = True

        result = {
            'success': True,
            'changed': True,
            'error': '',
            'stdout': oc_cmd_results
        }

        return result

    def _execute_command(self, command):
        """
        Execute shell commands using Ansible built-in methods.
        """
        # We don't need to sanitize the input since it's done in this method
        command_result = self._low_level_execute_command(cmd=command)

        if command_result['rc'] != 0:
            # ensure_text just to avoid some decode problems
            stderr = ensure_text(command_result.get('stderr', ''))
            raise AnsibleError(
                f"{self._task.action}: failed to execute the command {command}. Return code: {command_result['rc']}. STDERR: {stderr}"
            )
        return ensure_text(command_result.get('stdout', '')).rstrip()

    def _get_oc_binary(self, additional_exec_paths=None):
        """
        Search for the 'oc' binary in different paths. By default, it searches using
        the defined paths in the get_bin_path Ansible function. Additional paths can be provided.
        Raises an error if not found.
        """
        return get_bin_path('oc', opt_dirs=additional_exec_paths)
