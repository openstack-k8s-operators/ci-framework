#!/usr/bin/python

# Copyright Red Hat, Inc.
# Apache License Version 2.0 (see LICENSE

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
action: ci_script

short_description: Runs a given script in string format remotely while providing logging

description:
    - Runs a string given script remotly while providing logging.
    - Logs are written to the `output_dir`/../logs folder.

options:
    output_dir:
        description: The path in where the script will be copied
        required: true
        type: str
    script:
        description: The shell script content to be run
        required: true
        type: str
    chdir:
        description: Change into this directory on the remote node before running the script.
        type: str
    creates:
        description: A filename on the remote node, when it already exists, this step will not be run.
        type: str
    decrypt:
        description: This option controls the autodecryption of source files using vault.
        type: bool
        default: true
    executable:
        description: Name or path of a executable to invoke the script with.
        type: str
    removes:
        description: A filename on the remote node, when it does not exist, this step will not be run.
        type: str
    debug:
        description: If true the script will, in addition, use bash tracing.
        type: bool
        default: false
"""  # noqa

EXAMPLES = r"""
- name: Run custom script
  register: script_output
  ci_script:
    output_dir: "/home/zuul/ci-framework-data/artifacts"
    cmd: |
      mkdir /home/zuul/test-dir
      cd /home/zuul/test-dir
      git clone https://github.com/openstack-k8s-operators/ci-framework.git
"""

RETURN = r"""
changed:
   description: Always true.
   returned: always
   type: bool
failed:
   description: True if the execution failed.
   returned: always
   type: bool
rc:
   description: Script return code.
   returned: always
   type: int
stderr:
    description: stderr output as string.
    returned: always
    type: str
stderr_line:
    description: stderr output as lines.
    returned: always
    type: list[str]
stdout:
    description: stdout output as string.
    returned: always
    type: str
stdout_line:
    description: stdout output as lines.
    returned: always
    type: list[str]
"""

import glob
import pathlib
import re
import uuid
import yaml
import typing


from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleActionFail

from ansible.parsing.yaml.dumper import AnsibleDumper
from ansible.utils.unsafe_proxy import AnsibleUnsafeText, AnsibleUnsafeBytes

TMPL_SCRIPT = """#!/bin/bash
set -euo pipefail
%(opts)s
exec > >(tee -i %(logpath)s) 2>&1
%(pushcmd)s
%(content)s
%(popcmd)s
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
    def __init__(self, **kwargs):
        super(ActionModule, self).__init__(**kwargs)
        self.__script_file_path = (
            pathlib.Path()
            .home()
            .joinpath("ansible", "tmp")
            .joinpath(uuid.uuid4().hex)
            .absolute()
        )
        self.__script_file_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def __build_options(task_vars):
        if task_vars.get("cifmw_debug", False) or task_vars.get(
            "cifmw_ci_script_debug", False
        ):
            return "set -x"
        return ""

    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        task_args = decode_ansible_raw(self._task.args)
        if "output_dir" not in task_args:
            raise AnsibleActionFail("output_dir parameter is missing")

        if "script" not in task_args:
            raise AnsibleActionFail("script parameter is missing")

        output_dir = pathlib.Path(task_args.pop("output_dir"))
        if not output_dir.is_dir():
            raise AnsibleActionFail("output_dir points to a non-existing directory")

        logs_dir = output_dir.parent.joinpath("logs")
        if not logs_dir.is_dir():
            raise AnsibleActionFail(f"logs dir, {logs_dir} doesn't exist")

        # Remove cmd if not passed, we are going to use _raw_params
        # to pass the cmd we create here
        if "cmd" in task_args:
            task_args.pop("cmd")

        fnum = len(glob.glob(f"{output_dir}/ci_script_*"))
        t_name = re.sub(r"([^\x00-\x7F]|\s)+", "_", self._task.name).lower()
        chdir_path = task_args.pop("chdir", None)
        script_template_data = {
            "content": task_args.pop("script"),
            "logpath": logs_dir.joinpath(
                f"ci_script_{fnum:03}_{t_name}.log"
            ).as_posix(),
            "opts": self.__build_options(task_vars),
            "pushcmd": f"pushd {chdir_path}" if chdir_path else "",
            "popcmd": "popd" if chdir_path else "",
        }

        script_path_str = self.__script_file_path.as_posix()
        with open(self.__script_file_path, "w") as tmp_script_file:
            script_content = TMPL_SCRIPT % script_template_data
            tmp_script_file.write(script_content)

        remote_script_path_str = output_dir.joinpath(
            f"ci_script_{fnum:03}_{t_name}.sh"
        ).as_posix()
        self._transfer_file(script_path_str, remote_script_path_str)
        self._fixup_perms2(
            [remote_script_path_str], self._play_context.remote_user, execute=True
        )

        file_task = self._task.copy()
        file_task.args.update(
            {"_raw_params": script_path_str, "chdir": output_dir.as_posix()}
        )

        return self._shared_loader_obj.action_loader.get(
            "ansible.builtin.script",
            task=file_task,
            connection=self._connection,
            play_context=self._play_context,
            loader=self._loader,
            templar=self._templar,
            shared_loader_obj=self._shared_loader_obj,
        ).run(task_vars=task_vars)
