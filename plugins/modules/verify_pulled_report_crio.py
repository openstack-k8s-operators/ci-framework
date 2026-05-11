#!/usr/bin/python

# Copyright Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: verify_pulled_report_crio

short_description: Enrich pulled_images_report with CRI-O pull evidence

description:
  - Reads the YAML produced by the env_op_images pulled-images report role task.
  - "Parses CRI-O journal lines for C(msg=\"Pulled image: ...@sha256:...\")."
  - Adds per-row verification fields using trusted mirror domains from
    C(summary.mirror_rules).
  - When images carry a C(node) field, evidence is matched against the
    specific node's CRI-O log first.  If the digest is only found on a
    different node the entry is counted as a cross-node mismatch.
  - Log files are expected to follow the C(<node-name>.crio.log) naming
    convention produced by the role task.

options:
  report_path:
    description: Path to C(pulled_images_report.yaml) (input).
    required: true
    type: str
  output_path:
    description: Path for the enriched YAML report (output).
    required: true
    type: str
  log_paths:
    description:
      - Explicit list of log files to parse (e.g. per-node CRI-O logs).
      - Combined with files found under I(log_dir) when set.
    required: false
    type: list
    elements: str
    default: []
  log_dir:
    description:
      - Directory containing CRI-O log files matching I(log_glob).
    required: false
    type: str
  log_glob:
    description: Glob under I(log_dir). Used only when I(log_dir) is set.
    required: false
    default: "*.crio.log"
    type: str

author:
  - Nemanja Marjanovic (@nemarjan)

notes:
  - Requires PyYAML on the controller (same as other cifmw.general modules).
"""

EXAMPLES = r"""
- name: Enrich pulled report using fetched node logs
  cifmw.general.verify_pulled_report_crio:
    report_path: "{{ cifmw_env_op_images_pulled_report_path }}"
    log_dir: "{{ cifmw_env_op_images_crio_logs_dir }}"
    output_path: "{{ cifmw_env_op_images_verified_report_path }}"
"""

RETURN = r"""
changed:
  description: Whether the output file was written.
  type: bool
  returned: always
trusted_mirrors:
  description: Hostnames extracted from mirror rules in the report summary.
  type: list
  elements: str
  returned: always
log_files:
  description: Number of log files read.
  type: int
  returned: always
entries_with_digest:
  description: Image rows that had a sha256 digest in C(image_id).
  type: int
  returned: always
cross_node_entries:
  description: >-
    Image rows where evidence was found only on a different node
    than where the pod ran.
  type: int
  returned: always
nodes_with_evidence:
  description: >-
    Node names that had at least one C(Pulled image) log entry.
  type: list
  elements: str
  returned: always
"""

import glob
import os
import re

import yaml
from ansible.module_utils.basic import AnsibleModule

LOG_PATTERN = re.compile(
    r'msg="Pulled image: (?P<actual_uri>[^@\s]+)@(?P<id>sha256:[a-f0-9]+)"'
)
SHA256_PATTERN = re.compile(r"sha256:[a-f0-9]+")


def _node_from_path(path):
    """Derive node name from the ``<node>.crio.log`` naming convention."""
    basename = os.path.basename(path)
    suffix_pos = basename.find(".crio.log")
    if suffix_pos > 0:
        return basename[:suffix_pos]
    return os.path.splitext(basename)[0]


def _domain_from_uri(uri):
    """Return the registry host (+ optional port) from an image URI."""
    return uri.split("/")[0].strip()


def _apply_evidence(img, actual_uri, evidence_node, trusted_mirrors):
    """Set common verification fields on an image row that has log evidence."""
    actual_domain = _domain_from_uri(actual_uri)
    img["node_verified_image_origin"] = (
        "mirror" if actual_domain in trusted_mirrors else "source"
    )
    img["log_evidence_uri"] = actual_uri
    img["log_evidence_node"] = evidence_node
    return actual_domain


def _collect_log_evidence(paths, module):
    """Parse CRI-O logs into per-node and global evidence dicts.

    Returns:
        per_node: ``{node_name: {sha256_digest: pull_uri}}``
        global_evidence: ``{sha256_digest: (pull_uri, node_name)}``
            (last writer wins across nodes for the global dict)
    """
    per_node = {}
    global_evidence = {}
    for path in paths:
        node = _node_from_path(path)
        node_ev = per_node.setdefault(node, {})
        try:
            with open(path, "r") as f:
                for line in f:
                    match = LOG_PATTERN.search(line)
                    if match:
                        digest = match.group("id")
                        uri = match.group("actual_uri")
                        node_ev[digest] = uri
                        global_evidence[digest] = (uri, node)
        except IOError as exc:
            module.fail_json(
                msg="Cannot read CRI-O log file {0}: {1}".format(path, str(exc))
            )
    return per_node, global_evidence


def run_module():
    module_args = dict(
        report_path=dict(type="str", required=True),
        output_path=dict(type="str", required=True),
        log_paths=dict(type="list", required=False, elements="str", default=[]),
        log_dir=dict(type="str", required=False),
        log_glob=dict(type="str", required=False, default="*.crio.log"),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    report_path = module.params["report_path"]
    output_path = module.params["output_path"]
    log_paths = module.params["log_paths"] or []
    log_dir = module.params["log_dir"]
    log_glob = module.params["log_glob"]

    paths = list(log_paths)
    if log_dir:
        paths.extend(sorted(glob.glob(os.path.join(log_dir, log_glob))))

    if not paths:
        module.fail_json(
            msg="No CRI-O log files: set log_paths and/or log_dir with matching files."
        )

    try:
        with open(report_path, "r") as f:
            data = yaml.safe_load(f)
    except IOError as exc:
        module.fail_json(
            msg="Cannot read report {0}: {1}".format(report_path, str(exc))
        )
    except yaml.YAMLError as exc:
        module.fail_json(msg="Invalid YAML in report: {0}".format(str(exc)))

    if not isinstance(data, dict):
        module.fail_json(msg="Report root must be a mapping (dict).")

    trusted_mirrors = set()
    summary_section = data.get("summary") or {}
    for rule in summary_section.get("mirror_rules") or []:
        if not isinstance(rule, dict):
            continue
        mirror_url = rule.get("mirror")
        if mirror_url:
            domain = _domain_from_uri(mirror_url)
            if domain:
                trusted_mirrors.add(domain)

    per_node_evidence, global_evidence = _collect_log_evidence(paths, module)

    images_list = data.get("images") or []
    entries_with_digest = 0
    cross_node_entries = 0
    for img in images_list:
        if not isinstance(img, dict):
            continue
        image_id = img.get("image_id") or ""
        sha_match = SHA256_PATTERN.search(image_id)
        if not sha_match:
            continue
        entries_with_digest += 1
        img_sha = sha_match.group(0)
        img_node = img.get("node") or ""

        node_local_hit = (
            img_node
            and img_node in per_node_evidence
            and img_sha in per_node_evidence[img_node]
        )

        if node_local_hit:
            actual_uri = per_node_evidence[img_node][img_sha]
            _apply_evidence(img, actual_uri, img_node, trusted_mirrors)
        elif img_sha in global_evidence:
            actual_uri, evidence_node = global_evidence[img_sha]
            _apply_evidence(img, actual_uri, evidence_node, trusted_mirrors)
            if img_node:
                cross_node_entries += 1
        else:
            img["node_verified_image_origin"] = "cached/unknown"
            img["log_evidence_uri"] = None
            img["log_evidence_node"] = None

    nodes_with_evidence = sorted(n for n, ev in per_node_evidence.items() if ev)
    result = dict(
        changed=False,
        trusted_mirrors=sorted(trusted_mirrors),
        log_files=len(paths),
        entries_with_digest=entries_with_digest,
        cross_node_entries=cross_node_entries,
        nodes_with_evidence=nodes_with_evidence,
    )

    if module.check_mode:
        result["changed"] = True
        module.exit_json(**result)

    try:
        with open(output_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    except IOError as exc:
        module.fail_json(
            msg="Cannot write verified report {0}: {1}".format(output_path, str(exc))
        )

    result["changed"] = True
    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
