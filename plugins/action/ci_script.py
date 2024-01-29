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
    extra_args:
        description: extra {key:value} exported to the environment before running the script.
        required: false
        type: dict
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
    script: |
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
import json
import pathlib
import re
import uuid


from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleActionFail
from ansible.module_utils import basic

from ansible_collections.cifmw.general.plugins.module_utils.encoding import (
    ansible_encoding,
)

TMPL_SCRIPT = """#!/bin/bash
set -euo pipefail
%(opts)s
exec > >(tee -i %(logpath)s) 2>&1
%(pushcmd)s
%(extra_args)s
%(content)s
%(popcmd)s
"""


class ActionModule(ActionBase):
    __OUTPUT_DIR_ARG = "output_dir"
    __SCRIPT_ARG = "script"
    __DRY_RUN_ARG = "dry_run"
    __EXTRA_ARGS_ARG = "extra_args"
    __CHDIR_ARG = "chdir"

    __CIFMW_PLUGIN_ARGS = [
        __OUTPUT_DIR_ARG,
        __SCRIPT_ARG,
        __DRY_RUN_ARG,
        __EXTRA_ARGS_ARG,
        __CHDIR_ARG
    ]

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

    # extra_args is a dict and we generate 'export key1="value1"\nexport key2="value2"'
    @staticmethod
    def __build_exports(extra_args):
        _extra_args = ""
        if extra_args:
            for k, v in extra_args.items():
                _extra_args += 'export {key}="{value}"\n'.format(key=k, value=v)
        return _extra_args.rstrip("\n")

    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        task_args = ansible_encoding.decode_ansible_raw(self._task.args)
        output_dir = (
            pathlib.Path(task_args.get(self.__OUTPUT_DIR_ARG))
            if self.__OUTPUT_DIR_ARG in task_args
            else None
        )
        if not output_dir:
            raise AnsibleActionFail(f"{self.__OUTPUT_DIR_ARG} parameter is missing")

        if self.__SCRIPT_ARG not in task_args:
            raise AnsibleActionFail(f"{self.__SCRIPT_ARG} parameter is missing")

        file_task = self._task.copy()

        # Remove custom options from our plugin that are not part of Ansible's one
        for arg_name in self.__CIFMW_PLUGIN_ARGS:
            file_task.args.pop(arg_name, None)

        fnum = len(glob.glob(f"{output_dir}/ci_script_*"))
        t_name = re.sub(r"([^\x00-\x7F]|\s)+", "_", self._task.name).lower()
        chdir_path = task_args.get("chdir", None)
        script_template_data = {
            "extra_args": self.__build_exports(
                task_args.get(self.__EXTRA_ARGS_ARG, None)
            ),
            "content": task_args[self.__SCRIPT_ARG],
            "logpath": output_dir.parent.joinpath(
                "logs", f"ci_script_{fnum:03}_{t_name}.log"
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

        file_task.args.update(
            {"_raw_params": script_path_str, self.__CHDIR_ARG: output_dir.as_posix()}
        )

        # Are we running dry-run?
        if not basic.boolean(task_args.get(self.__DRY_RUN_ARG, False)):
            return self._shared_loader_obj.action_loader.get(
                "ansible.builtin.script",
                task=file_task,
                connection=self._connection,
                play_context=self._play_context,
                loader=self._loader,
                templar=self._templar,
                shared_loader_obj=self._shared_loader_obj,
            ).run(task_vars=task_vars)
        return {"command": json.dumps(ansible_encoding.decode_ansible_raw(task_args))}
