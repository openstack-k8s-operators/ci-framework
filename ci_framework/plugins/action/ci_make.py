# Requires `community.general` collection v6.5.0 or higher.
# Otherwise the 'make' command will actually run, it won't be able to generate
# the needed file.
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import glob
import json
import os
import typing
import re
import yaml

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleActionFail
from ansible.module_utils import basic
from ansible.parsing.yaml.dumper import AnsibleDumper
from ansible.utils.unsafe_proxy import AnsibleUnsafeText, AnsibleUnsafeBytes
from ansible.utils.display import Display


DOCUMENTATION = r"""
---
action: ci_make

short_description:

description:
- This moduel mostly wraps `community.general.make` and `ansible.builtin.copy`.
- It requires an additional parameter, `output_dir`, in order to output the `make` generated command.
- It also adds a new optional parameter, `dry_run`,
- allowing to NOT run `community.general.make` module, but get a file with the passed parameters.

options: Same as `community.general.make` except for output_dir and dry_run.
"""  # noqa

EXAMPLES = r"""
- name: Run pre-commit tests
    ci_make:
    chdir: "~/code/github.com/ci-framework-data"
    output_dir: /tmp/artifacts
    target: pre_commit
    params:
        USE_VENV: no
"""

RETURN = r"""
chdir:
  description:
    - The value of the module parameter I(chdir).
  type: str
  returned: success
command:
  description:
    - The command built and executed by the module.
  type: str
  returned: success
file:
  description:
    - The value of the module parameter I(file).
  type: str
  returned: success
jobs:
  description:
    - The value of the module parameter I(jobs).
  type: int
  returned: success
params:
  description:
    - The value of the module parameter I(params).
  type: dict
  returned: success
target:
  description:
    - The value of the module parameter I(target).
  type: str
  returned: success
dest:
    description: Destination file/path.
    returned: success
    type: str
    sample: /path/to/file.txt
src:
    description: Source file used for the copy on the target machine.
    returned: changed
    type: str
    sample: /home/httpd/.ansible/tmp/ansible-tmp-1423796390.97-147729857856000/source
md5sum:
    description: MD5 checksum of the file after running copy.
    returned: when supported
    type: str
    sample: 2a5aeecc61dc98c4d780b14b330e3282
checksum:
    description: SHA1 checksum of the file after running copy.
    returned: success
    type: str
    sample: 6e642bb8dd5c2e027bf21dd923337cbb4214f827
backup_file:
    description: Name of backup file created.
    returned: changed and if backup=yes
    type: str
    sample: /path/to/file.txt.2015-02-12@22:09~
gid:
    description: Group id of the file, after execution.
    returned: success
    type: int
    sample: 100
group:
    description: Group of the file, after execution.
    returned: success
    type: str
    sample: httpd
owner:
    description: Owner of the file, after execution.
    returned: success
    type: str
    sample: httpd
uid:
    description: Owner id of the file, after execution.
    returned: success
    type: int
    sample: 100
mode:
    description: Permissions of the target, after execution.
    returned: success
    type: str
    sample: "0644"
size:
    description: Size of the target, after execution.
    returned: success
    type: int
    sample: 1220
state:
    description: State of the target, after execution.
    returned: success
    type: str
    sample: file
"""  # noqa

TMPL_REPRODUCER = """#!/bin/bash
pushd %(chdir)s
%(exports)s
%(cmd)s
popd
"""


def decode_ansible_raw(data: typing.Any) -> typing.Any:
    """Converts an Ansible var to a python native one

    Ansible raw input args can contain AnsibleUnicodes or AnsibleUnsafes
    that are not intended to be manipulated directly.
    This function converts the given variable to a one that only contains
    python built-in types.

    Args:
        data: The usafe Ansible content to decode

    Returns: The python types based result

    """
    if isinstance(data, list):
        return [decode_ansible_raw(_data) for _data in data]
    elif isinstance(data, tuple):
        return tuple(decode_ansible_raw(_data) for _data in data)
    if isinstance(data, dict):
        return yaml.load(
            yaml.dump(
                data, Dumper=AnsibleDumper, default_flow_style=False, allow_unicode=True
            ),
            Loader=yaml.Loader,
        )
    if isinstance(data, AnsibleUnsafeText):
        return str(data)
    if isinstance(data, AnsibleUnsafeBytes):
        return bytes(data)
    return data


class ActionModule(ActionBase):
    def extract_env(self, task_vars):
        env_content = task_vars["environment"]
        exports = []
        if "environment" not in task_vars:
            return exports

        for env in env_content:
            if isinstance(env, str):
                # Lazy way to check the environment. We may need to iterate on
                # that one, especially if we set actual default() that need to
                # be used. Issue is, at this point the environment isn't
                # "interpreted" in Ansible, meaning we end with raw content.
                # So if we pass this:
                # make_ceph_environment: "{{ foo | default('bar') }}"
                # we end with that string, and not the result...
                key = env.replace("{{", "").replace("}}", "").strip()
                if key in task_vars:
                    try:
                        exports.extend(
                            [f"export {k}={v}" for k, v in task_vars[key].items()]
                        )
                    except AttributeError:
                        env_data = task_vars[key]
                        Display().warning(
                            (
                                "An error occurred while extracting "
                                "environment value."
                                f"The original data: {env} was transformed "
                                f"to {key}."
                                f"The extracted value is: {env_data}"
                            )
                        )
            elif isinstance(env, dict):
                exports.extend([f"export {k}={v}" for k, v in env.items()])
        return exports

    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)
        task_args = self._task.args.copy()

        # The output_dir is mandatory - at least for now. Later we may
        # just display a warning stating the script/reproducer won't exist
        if "output_dir" not in task_args:
            raise AnsibleActionFail("output_dir parameter is missing")

        # Are we running dry-run?
        dry_run = False
        if "dry_run" in task_args:
            dry_run = basic.boolean(task_args.pop("dry_run"))

        # Remove output_dir param from the params we'll pass down to the
        # module, and generate log dir path.
        output_dir = decode_ansible_raw(task_args.pop("output_dir"))
        log_dir = os.path.join(output_dir, "../logs")

        # Generate file using the community.general.make "command" output value
        # First get directory content and count files matching the fixed
        # pattern
        fnum = len(glob.glob(f"{output_dir}/ci_make_*"))

        # Replace non-ASCII and spaces in ansible task name, and lower the
        # string
        t_name = re.sub(r"([^\x00-\x7F]|\s)+", "_", self._task.name).lower()
        fname = f"ci_make_{fnum:03}_{t_name}.sh"

        # Create a new task for file management (log, and reproducer script)
        # We copy the existing task, remove all of the params, and we'll add
        # our custom ones when needed.
        file_task = self._task.copy()
        for remove in [
            "output_dir",
            "dry_run",
            "make",
            "target",
            "chdir",
            "file",
            "jobs",
            "params",
        ]:
            file_task.args.pop(remove, None)

        # Run module only if all conditions are here for file creation
        if not dry_run:
            m_ret = self._execute_module(
                module_name="community.general.make",
                module_args=task_args,
                task_vars=task_vars,
                tmp=tmp,
            )
            # Log in plain file
            log_name = f"ci_make_{fnum:03}_{t_name}.log"
            f_log = os.path.join(log_dir, log_name)
            stdout = m_ret["stdout"]
            stderr = m_ret["stderr"]
            log_content = f"### STDOUT\n{stdout}\n### STDERR\n{stderr}"
            file_task.args.update(
                {
                    "dest": f_log,
                    "content": log_content,
                }
            )
            Display().debug(f"Pushing {f_log}")

            cp_log = self._shared_loader_obj.action_loader.get(
                "ansible.builtin.copy",
                task=file_task,
                connection=self._connection,
                play_context=self._play_context,
                loader=self._loader,
                templar=self._templar,
                shared_loader_obj=self._shared_loader_obj,
            )
            m_ret.update(cp_log.run(task_vars=task_vars))
        else:
            m_ret = {"command": json.dumps(decode_ansible_raw(task_args))}

        # Write the reproducer script
        exports = self.extract_env(task_vars)
        s_file = os.path.join(output_dir, fname)
        copy_args = {"dest": s_file}

        data = {
            "chdir": task_args["chdir"],
            "cmd": m_ret.get("command", json.dumps(decode_ansible_raw(task_args))),
            "exports": "\n".join(exports),
        }
        copy_args["content"] = TMPL_REPRODUCER % data
        copy_args["mode"] = "0755"

        file_task.args.update(copy_args)
        Display().debug(f"Pushing {s_file}")
        cp_script = self._shared_loader_obj.action_loader.get(
            "ansible.builtin.copy",
            task=file_task,
            connection=self._connection,
            play_context=self._play_context,
            loader=self._loader,
            templar=self._templar,
            shared_loader_obj=self._shared_loader_obj,
        )
        m_ret.update(cp_script.run(task_vars=task_vars))

        # Return original module state
        return m_ret
