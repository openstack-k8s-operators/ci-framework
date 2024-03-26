#!/usr/bin/python

# Copyright: (c) 2024, Red Hat
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: approve_csr
short_description: Automated approval of pending certificate requests in OCP.
description: |
    This module approves any pending certificate requests and waits for a
    specified quiet period, defaulting to 3 minutes if not specified. During
    this quiet period, any new certificate approval request queued will be
    automatically approved and the quiet period timer reset. The module
    exits when no requests are observed for the specified quiet period.
requirements:
    - oc
options:
    k8s_config:
        description:
            - Absolute path to the kube config file.
            - Defaults to environment defined KUBECONFIG.
        required: false
        type: path
    quiet_period:
        description: Maximum time in which no events are observed.
        required: false
        default: 180
        type: int
author:
    - Pragadeeswaran (@psathyan)
"""

EXAMPLES = r"""
- name: Approve all pending certificate requests
  approve_csr:
    k8s_config: "{{ lookup('env', 'KUBECONFIG') }}"
"""

RETURN = r"""
result:
    description: status of the execution
    returned: success
    type: complex
    contains:
        stdout:
            description: Captured standard output.
            type: str
        stderr:
            description: Captured standard error.
            type: str
        rc:
            description: The returned status code.
            type: int
"""


from copy import deepcopy
from datetime import datetime, timedelta
from time import sleep
from typing import Any, List

from ansible.module_utils.basic import AnsibleModule


class ApproveCSR:
    """Automatic CSR approval utility."""

    def __init__(self, module: AnsibleModule) -> None:
        """Instance initialization method."""
        self.module: AnsibleModule = module
        self.k8s_config: str = module.params["k8s_config"]
        self.quiet_period: str = module.params["quiet_period"]
        self._base_cmd: List[str] = [self.module.get_bin_path("oc", required=True)]

    @property
    def base_cmd(self) -> List[str]:
        """Returns the base command."""
        return deepcopy(self._base_cmd)

    def execute_command(self, cmd, use_unsafe_shell=False, data=None) -> Any:
        shell_env = None
        if self.k8s_config:
            shell_env = dict(KUBECONFIG=self.k8s_config)

        return self.module.run_command(
            cmd, use_unsafe_shell=use_unsafe_shell, data=data, environ_update=shell_env
        )

    def _get_pending_requests(self) -> List[str]:
        """Return the list of pending certificate requests."""
        _cmd = self.base_cmd + [
            "get",
            "csr",
            "-o",
            "go-template='{{range.items}}{{if not .status}}"
            + '{{.metadata.name}}{{"\\n"}}{{end}}{{end}}\'',
        ]
        rc, out, err = self.execute_command(_cmd)
        if rc != 0:
            self.module.fail_json(
                msg="Failed to gather the list of pending requests",
                rc=rc,
                stdout=out,
                stderr=err,
                cmd=_cmd,
            )

        if not out.strip("'").strip("\n"):
            return []

        return out.strip("'").splitlines()

    def _approve_csr(self, requests: List[str]) -> bool:
        """Approve all pending certificate requests.

        Args:
            requests (list) a list of certificate requests to approve.

        Return:
            True on success else False
        """
        for csr in requests:
            if not csr.strip("\n"):
                continue

            _csr_cmd = self.base_cmd + [
                "adm",
                "certificate",
                "approve",
                csr.strip("\n"),
            ]
            r, o, e = self.execute_command(_csr_cmd)

            if r != 0:
                self.module.fail_json(
                    msg=f"Unable to approve certificate request - {csr}.",
                    rc=r,
                    stdout=o,
                    stderr=e,
                    cmd=_csr_cmd,
                )

        return True

    def wait_on_requests(self) -> None:
        """Waits on approval request event for specified period."""

        if self.module.check_mode:
            self.module.exit_json(changed=False, rc=0, stdout="Dry run - no checks.")

        expire_after = datetime.now() + timedelta(seconds=self.quiet_period)
        while expire_after > datetime.now():
            cert_approval_list = self._get_pending_requests()
            if cert_approval_list:
                approve_status = self._approve_csr(cert_approval_list)

                if not approve_status:
                    break

                expire_after = datetime.now() + timedelta(seconds=self.quiet_period)

            sleep(10)

        self.module.exit_json(
            changed=True,
            rc=0,
            stdout="Successfully approved all pending certificate requests.",
        )


def run_module():
    _args = dict(
        k8s_config=dict(required=False, type="path"),
        quiet_period=dict(required=False, type="int", default=180),
    )
    _module = AnsibleModule(argument_spec=_args, supports_check_mode=True)

    cli = ApproveCSR(_module)
    cli.wait_on_requests()


if __name__ == "__main__":
    run_module()
