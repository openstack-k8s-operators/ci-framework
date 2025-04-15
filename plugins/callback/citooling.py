#!/usr/bin/python

# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Red Hat, Inc.
# Based on https://github.com/oVirt/ovirt-ansible-collection/blob/master/plugins/callback/stdout.py
# and https://github.com/ansible-collections/community.general/blob/main/plugins/callback/yaml.py

from __future__ import absolute_import, division, print_function

__metaclass__ = type

# Not only visible to ansible-doc, it also 'declares' the options the plugin
# requires and how to configure them.
# TODO Fix DOCUMENTATION to pass the ansible-test validate-modules
DOCUMENTATION = """
  name: citooling
  type: aggregate
  short_description: Output the log of ansible
  version_added: "2.0.0"
  description:
      - This callback output the log of ansible play tasks.
"""

from ansible.module_utils.common.text.converters import to_text
from ansible.utils.display import get_text_width
from ansible.plugins.callback import CallbackBase
import types


def banner(self, msg, color=None, cows=False):
    msg = to_text(msg).strip()
    self.display(msg, color=color)


class CallbackModule(CallbackBase):
    """
    This callback module output the information with a specific style.
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "aggregate"
    CALLBACK_NAME = "citooling"

    # only needed if you ship it and don't want to enable by default
    CALLBACK_NEEDS_WHITELIST = False

    def __init__(self):
        super(CallbackModule, self).__init__()
        self._display.banner = types.MethodType(banner, self._display)
        self.current_playbook = ""
        self.nested_playbook = False

    def v2_playbook_on_start(self, playbook):
        self.current_playbook = getattr(playbook, "_file_name", None)
        playbook_name = (
            self.current_playbook if self.current_playbook else "UNKNOWN"
        )
        self._display.banner(f"\nStarting playbook: {playbook_name}\n")

    def v2_playbook_on_play_start(self, play):
        self.nested_playbook = False
        self._display.banner(f"PLAY [{play.name}]")

    def runner_on_ok(self, host, res):
        cmd = res["cmd"]
        if type(cmd) is list:
            cmd = " ".join(str(x) for x in res["cmd"])
        stdout = res.get("stdout")
        end = res.get("end")
        delta = res.get("delta")

        if res.get("_ansible_no_log", False):
            self._display.display(
                f"OK: [host: {host}, playbook: {self.current_playbook}] => CENSORED"
            )
            return

        if cmd and "ansible-playbook" in cmd:
            self._display.display(
                f"=>  Nested playbook execution from "
                f"[host: {host}, playbook: {self.current_playbook}]"
                f"\n\t└── COMMAND: {cmd}\n"
            )
            self.nested_playbook = True

        if self.nested_playbook:
            self._display.display(
                f"\tOK: [nested play, host: {host}, playbook: {self.current_playbook}] "
                f"\t\n\t=> COMMAND: {cmd}\n\t=> OUTPUT: {stdout}\nEND - {end} - delta: {delta}"
            )
        else:
            self._display.display(
                f"OK: [host: {host}, playbook: {self.current_playbook}] "
                f"\n\t=> COMMAND: {cmd}\n\t=> OUTPUT: {stdout}\nEND - {end} - delta: {delta}"
            )

    def runner_on_failed(self, host, res, ignore_errors=False):
        if res.get("_ansible_no_log", False):
            self._display.display(
                f"FAILED: [host: {host}, playbook: {self.current_playbook}] => CENSORED"
            )
            return
        self._display.display(
            f"FAILED: [host: {host}, playbook: {self.current_playbook}] => {res}"
        )

    def runner_on_skipped(self, host, item=None):
        self._display.display(
            f"SKIPPED: [host: {host}, playbook: {self.current_playbook}]"
        )

    def runner_on_unreachable(self, host, res):
        self._display.display(
            f"UNREACHABLE: [host: {host}, playbook: {self.current_playbook}] => {res}"
        )

    def runner_on_async_failed(self, host, res, jid):
        self._display.display(
            f"ASYNC_FAILED: [host: {host}, playbook: {self.current_playbook}] "
            f"Job ID: {jid} => {res}"
        )

    def playbook_on_import_for_host(self, host, imported_file):
        self._display.display(
            f"IMPORTED: [host: {host}, playbook: {self.current_playbook}] => {imported_file}"
        )

    def playbook_on_not_import_for_host(self, host, missing_file):
        self._display.display(
            f"NOTIMPORTED: [host: {host}, playbook: {self.current_playbook}] => {missing_file}"
        )
