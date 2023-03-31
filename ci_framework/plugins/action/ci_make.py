# This specific action plugin needs a version of community.general collection
# providing this patch:
# https://github.com/ansible-collections/community.general/pull/6160
# While the "make" command will actually run, it won't be able to generate
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

ERR_UPDATE_COLLECTION = '''"command" not found in community.general.make.
Please update collection. The expected reproducer file will NOT be generated!
'''
TMPL_REPRODUCER = "#!/bin/bash\npushd %s\n%s\npopd\n"


class OutputException(Exception):
    def __init__(self, msg, stdout=None, stderr=None):
        super().__init__(msg)
        self.msg = msg
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        if not os.path.exists(self.msg):
            return "%s doesn't exist" % self.msg
        if not os.path.isdir(self.msg):
            return "%s isn't a directory" % self.msg
        if not os.access(self.msg, os.W_OK):
            return "%s isn't writable" % self.msg
        return 'Unknown error for %s' % self.msg


class ActionModule(ActionBase):
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
        # module
        output_dir = module_args.pop('output_dir')

        log_dir = os.path.join(output_dir, '../logs')

        # Ensure we're able to write in the output_dir. If this first check
        # fails, the actual OutputException will do some more tests to check
        # what is actually wrong with the output_dir (missing, not a directory,
        # or not writable)
        if not os.access(output_dir, os.W_OK):
            raise OutputException(output_dir)

        if not os.access(log_dir, os.W_OK):
            raise OutputException(log_dir)

        # Generate file using the community.general.make "command" output value
        # First get directory content and count files matching the fixed
        # pattern
        fnum = len(glob.glob('%s/ci_make_*' % output_dir))

        # Replace non-ASCII and spaces in ansible task name, and lower the
        # string
        t_name = re.sub(r'([^\x00-\x7F]|\s)+', '_', self._task._name).lower()
        fname = 'ci_make_%i_%s.sh' % (fnum, t_name)

        # Run module only if all conditions are here for file creation
        if not dry_run:
            m_ret = self._execute_module(module_name='community.general.make',
                                         module_args=module_args,
                                         task_vars=task_vars, tmp=tmp)
            # Log in plain file
            log_name = 'ci_make_%i_%s.log' % (fnum, t_name)
            f_log = os.path.join(log_dir, log_name)
            with open(f_log, 'w') as fh:
                fh.write('### STDOUT\n')
                fh.write(m_ret['stdout'])
                fh.write('\n### STDERR\n')
                fh.write(m_ret['stderr'])
        else:
            m_ret = {'command': json.dumps(module_args)}

        # This isn't needed anymore, let's free some resources
        del tmp

        # We can only check the "command" availability now, once the module
        # has been called, unfortunately.
        # TODO: consider if we can remove this check later
        scriptable = True
        if 'command' not in m_ret:
            Display().warning(ERR_UPDATE_COLLECTION)
            m_ret['command'] = json.dumps(module_args)
            scriptable = False

        # Write the reproducer script
        with open(os.path.join(output_dir, fname), 'w') as fh:
            if scriptable:
                fh.write(TMPL_REPRODUCER % (module_args['chdir'],
                                            m_ret['command']))
            else:
                fh.write(m_ret['command'])
        if scriptable:
            os.chmod(os.path.join(output_dir, fname), 0o755)

        # Return original module state
        return m_ret
