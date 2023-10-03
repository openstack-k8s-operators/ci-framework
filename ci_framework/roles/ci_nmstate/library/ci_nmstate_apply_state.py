#!/usr/bin/env python3

# Copyright: (c) 2023, Pablo Rodriguez <pabrodri@redhat.com>
# Apache License Version 2.0 (see LICENSE)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
  ---
  module: ci_nmstate_apply_state
  short_description: Apply a given nmstate state to the target host.
  description:
  - Apply a given nmstate state.
  options:
    state:
      description:
        - The nmstate state to apply.
        - It must follow the nmstate API U(https://nmstate.io/devel/api.html)
      required: True
      type: raw
  requirements:
    - libnmstate
  author:
    - Pablo Rodriguez (@pablintino)
"""

EXAMPLES = r"""
  # Apply some network config to eth0 using nmstate
  - name: Generate env var fact
    register: get_makefiles_env_out
    get_makefiles_env:
      state:
        dns-resolver:
          running:
            server:
              - 10.111.222.1
        routes:
          config:
          - destination: 0.0.0.0/0
            next-hop-address: 10.111.222.1
            next-hop-interface: eth0
        interfaces:
          - description: default
            ipv4:
              address:
              -   ip: 10.111.222.33
                  prefix-length: 24
              dhcp: false
              enabled: true
            ipv6:
              enabled: false
            mtu: 1500
            name: eth0
            state: up
            type: ethernet
"""

RETURN = r"""
  state:
    description: The nmstate state after applying the given state.
    type: raw
    returned: success
    sample:
      dns-resolver:
        running:
            server:
            - 10.111.222.1
      routes:
        config:
        - destination: 0.0.0.0/0
          next-hop-address: 10.111.222.1
          next-hop-interface: eth0
      hostname:
        config: test.node.lab.local
        running: test.node.lab.local
      interfaces:
        - description: default
          identifier: name
          ipv4:
            address:
            -   ip: 10.111.222.33
                prefix-length: 24
            auto-dns: true
            auto-gateway: true
            auto-route-table-id: 0
            auto-routes: true
            dhcp: false
            enabled: true
          ipv6:
            dhcp: false
            enabled: false
          mac-address: FA:16:3E:0A:20:87
          mtu: 1500
          name: eth0
          profile-name: System eth0
          state: up
          type: ethernet
"""

import sys

from ansible.module_utils.basic import AnsibleModule


try:
    from libnmstate import netapplier
    from libnmstate import netinfo
    from libnmstate.error import NmstateError

    HAS_LIBNMSTATE = True
except ImportError:
    HAS_LIBNMSTATE = False


def main():
    module = AnsibleModule(
        argument_spec={
            "state": {"required": True, "type": "raw"},
        },
        supports_check_mode=False,
    )

    if not HAS_LIBNMSTATE:
        module.fail_json(
            msg='Could not import "libnmstate" library. \
              libnmstate is required on PYTHONPATH to run this module',
            python=sys.executable,
            python_version=sys.version,
            python_system_path=sys.path,
        )

    result = {"success": False, "changed": False}

    try:
        previous_state = netinfo.show()

        target_state = module.params.get("state")
        netapplier.apply(target_state)

        final_state = netinfo.show()

        result["changed"] = previous_state != final_state
        result["state"] = final_state
    except NmstateError as err:
        module.fail_json(msg="Failure while applying nmstate state", exception=err)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
