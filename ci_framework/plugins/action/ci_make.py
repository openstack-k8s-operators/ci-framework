# This specific action plugin needs a version of community.general collection
# providing this patch:
# https://github.com/ansible-collections/community.general/pull/6160
# While the "make" command will actually run, it won't be able to generate
# the needed file.
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleActionFail, AnsibleError
from ansible.utils.display import Display

ERR_UPDATE_COLLECTION = '''"command" not found in community.genera.make output.
Please update collection. The expected reproducer file will NOT be generated!
'''


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)
        module_args = self._task.args.copy()

        if 'output_dir' not in module_args:
            raise AnsibleActionFail('output_dir parameter is missing')

        output_dir = module_args.pop('output_dir')
        # Check for directory
        if not os.path.exists(output_dir):
            raise AnsibleError("%s doesn't exist" % output_dir)
        if not os.path.isdir(output_dir):
            raise AnsibleError("%s isn't a directory" % output_dir)
        if not os.access(output_dir, os.W_OK):
            raise AnsibleError("%s isn't writable" % output_dir)

        # Run module only if all conditions are here for file creation
        mod_ret = self._execute_module(module_name='community.general.make',
                                       module_args=module_args,
                                       task_vars=task_vars, tmp=tmp)
        del tmp
        if 'command' not in mod_ret:
            Display().warning(ERR_UPDATE_COLLECTION)
            return mod_ret

        # Generate file - with this PR, the module will output the built
        # command: https://github.com/ansible-collections/community.general/pull/6160
        # First get directory content and count files
        fnum = len([n for n in os.listdir(output_dir)
                   if os.path.isfile(os.path.join(output_dir, n))])
        clean_task_name = self._task._name.replace(' ', '_').lower()
        fname = '%i_%s.sh' % (fnum, clean_task_name)
        with open(os.path.join(output_dir, fname), 'w') as fh:
            fh.write('#!/bin/sh\n' + mod_ret['command'] + '\n')
        os.chmod(os.path.join(output_dir, fname), 0o755)

        return mod_ret
