# Copyright: (c) 2024, Red Hat

# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function


__metaclass__ = type
import json
import unittest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes


def set_module_args(args) -> None:
    """Prepare the arguments so that they are picked during module create."""
    args["_ansible_remote_tmp"] = "/tmp"
    args["_ansible_keep_remote_files"] = False

    _args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(_args)


class AnsibleExitJson(Exception):
    """Exception to be raised by module.exit_json for tests to handle."""

    pass


class AnsibleFailJson(Exception):
    """Exception to be raised by module.fail_json for tests to handle."""

    pass


def exit_json(*args, **kwargs):
    """Patch for AnsibleModule.exit_json."""
    if "changed" not in kwargs.keys():
        kwargs["changed"] = False

    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    """Patch for AnsibleModule.fail_json."""
    kwargs["failed"] = True
    raise AnsibleFailJson(kwargs)


def get_bin_path(*args, **kwargs):
    """Patch for AnsibleModule.get_bin_path."""
    return "/usr/local/bin/flake-command"


class ModuleBaseTestCase(unittest.TestCase):
    """Base test class for unit testing."""

    def setUp(self) -> None:
        self.mock_module_helper = unittest.mock.patch.multiple(
            basic.AnsibleModule,
            exit_json=exit_json,
            fail_json=fail_json,
            get_bin_path=get_bin_path,
        )
        self.mock_module_helper.start()
        self.addClassCleanup(self.mock_module_helper.stop)
