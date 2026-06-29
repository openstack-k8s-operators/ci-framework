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
#
# Optional key filtering (applied to the merged result):
#   --allow REGEX       keep only top-level keys matching this pattern
#   --reject REGEX      drop top-level keys matching this pattern
#   --reject-key KEY    drop this exact top-level key
#   --update-only       only update keys already present in BASE; ignore new
#                       keys from OVERRIDE entirely
#
# Filters are applied in order: allow first (if any), then reject patterns,
# then reject exact keys.  Multiple --reject / --reject-key flags are accepted.

from __future__ import annotations

import argparse
import re
import sys

try:
    import yaml
except ImportError:
    sys.stderr.write(
        "merge_yaml_override.py: PyYAML is required "
        "(e.g. dnf install python3-pyyaml or pip install pyyaml)\n"
    )
    sys.exit(1)


class DoubleQuoteDumper(yaml.SafeDumper):
    """YAML SafeDumper subclass;
    emits strings with double quotes when needed for readability."""

    pass


def _str_representer(dumper, data):
    """Take a SafeDumper and a str;
    return a YAML scalar node (literal | or double-quoted when needed)."""
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    if any(c in data for c in "{}[]%*&!@#"):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


DoubleQuoteDumper.add_representer(str, _str_representer)


def deep_merge(
    base: object, override: object, update_only: bool = False
) -> object:
    """Take two parsed values;
    return merge where both are dicts (recursive), else override wins.

    When update_only is True, only keys already present in base are
    updated; new keys from override are silently ignored."""
    if base is None:
        return override
    if override is None:
        return base
    if isinstance(base, dict) and isinstance(override, dict):
        out = dict(base)
        for key, val in override.items():
            if key in out:
                out[key] = deep_merge(out[key], val, update_only=update_only)
            elif not update_only:
                out[key] = val
        return out
    return override


def filter_keys(
    data: dict,
    allow: str | None = None,
    reject_patterns: list[str] | None = None,
    reject_keys: list[str] | None = None,
) -> dict:
    """Filter top-level keys from a dict.

    Args:
        data: mapping to filter.
        allow: if set, only keys matching this regex survive.
        reject_patterns: list of regexes; matching keys are dropped.
        reject_keys: list of exact key names to drop.

    Returns:
        filtered dict (new object, data is not mutated).
    """
    out = dict(data)

    if allow is not None:
        allow_re = re.compile(allow)
        out = {k: v for k, v in out.items() if allow_re.search(k)}

    if reject_patterns:
        combined_re = re.compile("|".join(reject_patterns))
        out = {k: v for k, v in out.items() if not combined_re.search(k)}

    if reject_keys:
        reject_set = set(reject_keys)
        out = {k: v for k, v in out.items() if k not in reject_set}

    return out


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Deep-merge two YAML mappings with optional key filtering. "
            "FILE2 wins on duplicate keys (nested dicts merged). "
            "Scalars and lists from FILE2 replace FILE1."
        ),
    )
    parser.add_argument("base", metavar="FILE1_BASE.yml", help="base YAML file")
    parser.add_argument(
        "override", metavar="FILE2_OVERRIDE.yml", help="override YAML file"
    )
    parser.add_argument(
        "output",
        metavar="MERGED_OUT.yml",
        nargs="?",
        default=None,
        help="output file (default: stdout)",
    )
    parser.add_argument(
        "--allow",
        metavar="REGEX",
        default=None,
        help="keep only top-level keys matching this pattern",
    )
    parser.add_argument(
        "--reject",
        metavar="REGEX",
        action="append",
        default=[],
        help="drop top-level keys matching this pattern (repeatable)",
    )
    parser.add_argument(
        "--reject-key",
        metavar="KEY",
        action="append",
        default=[],
        help="drop this exact top-level key (repeatable)",
    )
    parser.add_argument(
        "--update-only",
        action="store_true",
        default=False,
        help="only update keys already present in BASE; ignore new keys",
    )
    return parser.parse_args()


def main() -> None:
    """Merge YAML files, optionally filter keys, write output."""
    args = parse_args()

    with open(args.base, encoding="utf-8") as f:
        base = yaml.safe_load(f)
    with open(args.override, encoding="utf-8") as f:
        override = yaml.safe_load(f)

    if base is None:
        base = {}
    if override is None:
        override = {}

    if not isinstance(base, dict):
        sys.stderr.write(
            f"{args.base}: root must be a mapping, got {type(base).__name__}\n"
        )
        sys.exit(3)
    if not isinstance(override, dict):
        sys.stderr.write(
            f"{args.override}: root must be a mapping, got {type(override).__name__}\n"
        )
        sys.exit(3)

    merged = deep_merge(base, override, update_only=args.update_only)

    has_filters = args.allow or args.reject or args.reject_key
    if has_filters:
        merged = filter_keys(
            merged,
            allow=args.allow,
            reject_patterns=args.reject or None,
            reject_keys=args.reject_key or None,
        )

    dump_options = dict(
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )
    if args.output is None:
        yaml.dump(merged, sys.stdout, Dumper=DoubleQuoteDumper, **dump_options)
    else:
        with open(args.output, "w", encoding="utf-8") as out_f:
            yaml.dump(merged, out_f, Dumper=DoubleQuoteDumper, **dump_options)


if __name__ == "__main__":
    main()
