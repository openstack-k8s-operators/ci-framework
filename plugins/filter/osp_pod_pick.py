#!/usr/bin/python3

# Copyright: Contributors to the OpenStack-K8s-Operators project
# SPDX-License-Identifier: Apache-2.0

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re


DOCUMENTATION = """
    name: osp_pod_pick
    short_description: Pick a pod name by StatefulSet ordinal from a label-filtered list
    description:
      - Helper for results already narrowed by Kubernetes label selectors
        (see the C(discover_osp_pod) role).
      - Does B(not) guess names from uniquePodNames hashes. Callers must query
        by C(component)/C(service) labels first.
      - Orders by the trailing StatefulSet ordinal (C(-0), C(-1), ... C(-10)),
        not lexical string sort, so index 2 is ordinal 2 even when ordinal 10 exists.
    options:
        _input:
            description:
              - Pod name strings, or pod/resource dicts with C(metadata.name).
            type: list
            required: true
        index:
            description: StatefulSet ordinal to select (default C(0)).
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


_ORDINAL_RE = re.compile(r"-(\d+)$")


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


def _sort_key(name):
    """Order by trailing StatefulSet ordinal, then by full name."""
    match = _ORDINAL_RE.search(name)
    ordinal = int(match.group(1)) if match else -1
    return (ordinal, name)


def osp_pod_sort(pods):
    """Return pod names sorted by StatefulSet ordinal."""
    if not isinstance(pods, list):
        raise AnsibleFilterTypeError(
            "osp_pod_sort requires a list, got %s" % type(pods)
        )
    return sorted((_name(p) for p in pods), key=_sort_key)


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

    names = osp_pod_sort(pods)
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
            "osp_pod_sort": osp_pod_sort,
        }
