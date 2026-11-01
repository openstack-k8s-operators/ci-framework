#!/usr/bin/python3

# Copyright: Contributors to the OpenStack-K8s-Operators project
# SPDX-License-Identifier: Apache-2.0

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
    name: osp_pod_pick
    short_description: Pick a pod name by index from an already label-filtered list
    description:
      - Helper for results already narrowed by Kubernetes label selectors
        (see the C(discover_osp_pod) role).
      - Does B(not) guess names from uniquePodNames hashes. Callers must query
        by C(component)/C(service) labels first.
    options:
        _input:
            description:
              - Pod name strings, or pod/resource dicts with C(metadata.name).
            type: list
            required: true
        index:
            description: Index after sorting names ascending (default C(0)).
            type: int
            default: 0
"""

EXAMPLES = """
    - name: Prefer the discover_osp_pod role for cluster queries
      ansible.builtin.include_role:
        name: discover_osp_pod
      vars:
        cifmw_discover_osp_pod_component: cinder-api
        cifmw_discover_osp_pod_service: cinder

    - name: Or pick an ordinal from an existing k8s_info result
      ansible.builtin.set_fact:
        cinder_api_pod: "{{ cinder_api_pods.resources | cifmw.general.osp_pod_pick }}"
"""

RETURN = """
  _value:
    description: Selected pod name.
    type: str
"""

from ansible.errors import AnsibleFilterError, AnsibleFilterTypeError
from ansible.module_utils._text import to_native


def _name(item):
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        meta = item.get("metadata") or {}
        name = meta.get("name")
        if isinstance(name, str) and name:
            return name
    raise AnsibleFilterTypeError(
        "osp_pod_pick expects pod name strings or dicts with metadata.name, got %s"
        % type(item)
    )


def osp_pod_pick(pods, index=0):
    if not isinstance(pods, list):
        raise AnsibleFilterTypeError(
            "osp_pod_pick requires a list, got %s" % type(pods)
        )
    try:
        index = int(index)
    except (TypeError, ValueError) as exc:
        raise AnsibleFilterTypeError(
            "osp_pod_pick index must be an int, got %s" % type(index)
        ) from exc
    if index < 0:
        raise AnsibleFilterTypeError("osp_pod_pick index must be >= 0")

    names = sorted(_name(p) for p in pods)
    if not names:
        raise AnsibleFilterError(
            "osp_pod_pick: empty pod list (query by component/service labels first)"
        )
    if index >= len(names):
        raise AnsibleFilterError(
            "osp_pod_pick: index %s out of range for %s"
            % (index, [to_native(n) for n in names])
        )
    return names[index]


class FilterModule:

    def filters(self):
        return {
            "osp_pod_pick": osp_pod_pick,
        }
