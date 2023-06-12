# Requires `community.general` collection v6.5.0 or higher.
# Otherwise the "make" command will actually run, it won't be able to generate
# the needed file.
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import glob
import json
import os
import re

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleActionFail
from ansible.module_utils import basic
from ansible.utils.display import Display

TMPL_REPRODUCER = '''#!/bin/bash
pushd %(chdir)s
%(exports)s
%(cmd)s
popd
'''


class ActionModule(ActionBase):
    def extract_env(self, task_vars):
        env_content = task_vars['environment']
        exports = []
        if 'environment' not in task_vars:
            return exports

        for env in env_content:
            if isinstance(env, str):
                # Lazy way to check the environment. We may need to iterate on that
                # one, especially if we set actual default() that need to be used.
                # Issue is, at this point the environment isn't "interpreted" in
                # Ansible, meaning we end with raw content. So if we pass this:
                # make_ceph_environment: "{{ foo | default('bar') }}" we end with
                # that string, and not the result...
                key = env.replace('{{', '').replace('}}', '').strip()
                if key in task_vars:
                    try:
                        exports.extend([f'export {k}={v}' for k, v in task_vars[key].items()])
                    except AttributeError:
                        env_data = task_vars[key]
                        Display().warning((
                            'An error occurred while extracting environment value.'
                            f'The orginal data: {env} was transformed to {key}.'
                            f'The extracted value is: {env_data}'
                        ))
            elif isinstance(env, dict):
                exports.extend([f'export {k}={v}' for k, v in env.items()])
        return exports

    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)
        module_args = self._task.args.copy()

        # The output_dir is mandatory - at least for now. Later we may
        # just display a warning stating the script/reproducer won't exist
        if 'output_dir' not in module_args:
            raise AnsibleActionFail('output_dir parameter is missing')

        # Are we running dry-run?
        dry_run = False
        if 'dry_run' in module_args:
            dry_run = basic.boolean(module_args.pop('dry_run'))

        # Remove output_dir param from the params we'll pass down to the
        # module, and generate log dir path.
        output_dir = module_args.pop('output_dir')
        log_dir = os.path.join(output_dir, '../logs')

        # Generate file using the community.general.make "command" output value
        # First get directory content and count files matching the fixed
        # pattern
        fnum = len(glob.glob(f'{output_dir}/ci_make_*'))

        # Replace non-ASCII and spaces in ansible task name, and lower the
        # string
        t_name = re.sub(r'([^\x00-\x7F]|\s)+', '_', self._task._name).lower()
        fname = f'ci_make_{fnum:03}_{t_name}.sh'

        # Create a new task for file management (log, and reproducer script)
        # We copy the existing task, remove all of the params, and we'll add
        # our custom ones when needed.
        file_task = self._task.copy()
        for remove in ['output_dir', 'dry_run', 'make', 'target', 'chdir',
                       'file', 'jobs', 'params']:
            file_task.args.pop(remove, None)

        # Run module only if all conditions are here for file creation
        if not dry_run:
            m_ret = self._execute_module(module_name='community.general.make',
                                         module_args=module_args,
                                         task_vars=task_vars, tmp=tmp)
            # Log in plain file
            log_name = f'ci_make_{fnum:03}_{t_name}.log'
            f_log = os.path.join(log_dir, log_name)
            stdout = m_ret['stdout']
            stderr = m_ret['stderr']
            log_content = f'### STDOUT\n{stdout}\n### STDERR\n{stderr}'
            file_task.args.update({
                'dest': f_log,
                'content': log_content,
            })
            Display().debug(f'Pushing {f_log}')

            cp_log = self._shared_loader_obj.action_loader.get(
                'ansible.builtin.copy',
                task=file_task,
                connection=self._connection,
                play_context=self._play_context,
                loader=self._loader,
                templar=self._templar,
                shared_loader_obj=self._shared_loader_obj
            )
            m_ret.update(cp_log.run(task_vars=task_vars))
        else:
            m_ret = {'command': json.dumps(module_args)}

        # We can only check the "command" availability now, once the module
        # has been called, unfortunately.
        scriptable = True
        if 'command' not in m_ret:
            m_ret['command'] = json.dumps(module_args)
            scriptable = False

        # Write the reproducer script
        exports = self.extract_env(task_vars)
        s_file = os.path.join(output_dir, fname)
        copy_args = {'dest': s_file}
        if scriptable:
            data = {
                'chdir': module_args['chdir'],
                'cmd': m_ret['command'],
                'exports': '\n'.join(exports)
            }
            copy_args['content'] = TMPL_REPRODUCER % data
            copy_args['mode'] = '0755'
        else:
            copy_args['content'] = json.dumps(task_vars['environment']) + m_ret['command']

        file_task.args.update(copy_args)
        Display().debug(f'Pushing {s_file}')
        cp_script = self._shared_loader_obj.action_loader.get(
            'ansible.builtin.copy',
            task=file_task,
            connection=self._connection,
            play_context=self._play_context,
            loader=self._loader,
            templar=self._templar,
            shared_loader_obj=self._shared_loader_obj
        )
        m_ret.update(cp_script.run(task_vars=task_vars))

        # Return original module state
        return m_ret
