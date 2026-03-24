#!/usr/bin/env python3
#
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
#
# Merge two YAML files whose root is a mapping: keys from OVERRIDE replace BASE
# recursively for nested mappings; non-dict values (scalars, lists) are
# replaced entirely by OVERRIDE. Requires PyYAML (python3-pyyaml / python3-yaml
# on RPM systems).

from __future__ import annotations

import sys

try:
    import yaml
except ImportError:
    sys.stderr.write(
        "merge_yaml_override.py: PyYAML is required "
        "(e.g. dnf install python3-pyyaml or pip install pyyaml)\n")
    sys.exit(1)


def deep_merge(base: object, override: object) -> object:
    if base is None:
        return override
    if override is None:
        return base
    if isinstance(base, dict) and isinstance(override, dict):
        out = dict(base)
        for key, val in override.items():
            if key in out:
                out[key] = deep_merge(out[key], val)
            else:
                out[key] = val
        return out
    return override


def main() -> None:
    argc = len(sys.argv)
    if argc not in (3, 4):
        sys.stderr.write(
            f"usage: {sys.argv[0]} FILE1_BASE.yml FILE2_OVERRIDE.yml [MERGED_OUT.yml]\n"
            "  Deep-merge two YAML mappings: FILE2 wins on duplicate keys (nested dicts merged).\n"
            "  Scalars and lists from FILE2 replace FILE1. If MERGED_OUT is omitted, print to stdout.\n"
        )
        sys.exit(2)

    base_path, override_path = sys.argv[1], sys.argv[2]
    out_path = sys.argv[3] if argc == 4 else None

    with open(base_path, encoding="utf-8") as f:
        base = yaml.safe_load(f)
    with open(override_path, encoding="utf-8") as f:
        override = yaml.safe_load(f)

    if base is None:
        base = {}
    if override is None:
        override = {}

    if not isinstance(base, dict):
        sys.stderr.write(
            f"{base_path}: root must be a mapping, got {type(base).__name__}\n"
        )
        sys.exit(3)
    if not isinstance(override, dict):
        sys.stderr.write(
            f"{override_path}: root must be a mapping, got {type(override).__name__}\n"
        )
        sys.exit(3)

    merged = deep_merge(base, override)
    dump_kw = dict(
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )
    if out_path is None:
        yaml.safe_dump(merged, sys.stdout, **dump_kw)
    else:
        with open(out_path, "w", encoding="utf-8") as out_f:
            yaml.safe_dump(merged, out_f, **dump_kw)


if __name__ == "__main__":
    main()
