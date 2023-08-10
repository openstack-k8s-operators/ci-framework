# Copyright Red Hat, Inc.
# Apache License Version 2.0 (see LICENSE)

import os
from pathlib import Path
from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase

DOCUMENTATION = r'''
---
action: oc

short_description: Execute OpensShift Client commands - oc -.

description:
- This module searches the oc binary in, load the kubeconfig and execute the oc provided commands.
'''

EXAMPLES = r'''
- name: Display the current authenticated user
    oc:
    cmd: whoami -c
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

        # We're gonna use the shell module so we can pass same arguments
        # https://docs.ansible.com/ansible/latest/collections/ansible/builtin/shell_module.html#parameter-cmd
        if 'cmd' not in self._task.args or not self._task.args['cmd']:
            raise AnsibleError('"cmd" parameter is mandatory')

        # Get remote home, local or remote depending of the hosts
        user_home = Path(task_vars['ansible_user_dir']).resolve()

        # Check if the environment KUBECONFIG is assigned in the playbook, if not
        # we apply default one used in CRC
        kube_config = {
            'KUBECONFIG': user_home / '.crc/machines/crc/kubeconfig'
        }
        if not any('KUBECONFIG' in d for d in self._task.environment):
            self._task.environment.append(kube_config)

        additional_exec_paths = [
            str(user_home / '.crc/bin'),
            str(user_home / '.crc/bin/oc'),
        ]

        # We need to get the actual PATHs + append the additional ones
        # where the oc binary can be located
        self._task.environment.append(
            {
                'PATH': os.pathsep.join((additional_exec_paths + [task_vars['ansible_env']['PATH']]))
            }
        )

        self._task.args['_raw_params'] = self._task.args.pop('cmd')
        return self._shared_loader_obj.action_loader.get('ansible.builtin.shell',
                                                         task=self._task,
                                                         connection=self._connection,
                                                         play_context=self._play_context,
                                                         loader=self._loader,
                                                         templar=self._templar,
                                                         shared_loader_obj=self._shared_loader_obj).run(task_vars=task_vars)
