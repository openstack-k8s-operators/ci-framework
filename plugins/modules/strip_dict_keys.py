#!/usr/bin/python

# Copyright: (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: strip_dict_keys
short_description: Remove top-level keys from a YAML file

description:
- Reads a YAML file, removes every top-level key that appears in any of the
  provided key-source YAML files, and writes the result back.

author:
  - Enrique Vallespi Gil (@evallesp)

options:
  src:
    description:
      - Path to the YAML file whose keys will be stripped.
    required: true
    type: str
  keys_from:
    description:
      - List of paths to YAML files whose top-level keys identify
        which keys to remove from I(src).
    required: true
    type: list
    elements: str
  dest:
    description:
      - Path to write the result. If omitted, I(src) is overwritten in place.
    required: false
    type: str
"""

EXAMPLES = r"""
- name: Strip keys from exclusion files out of reproducer-variables
  cifmw.general.strip_dict_keys:
    src: /tmp/reproducer-variables.yml
    keys_from:
      - /home/zuul/configs/excluded_vars.yaml
      - /home/zuul/configs/other_excluded.yaml

- name: Strip keys and write to a different file
  cifmw.general.strip_dict_keys:
    src: /tmp/reproducer-variables.yml
    keys_from:
      - /home/zuul/configs/excluded_vars.yaml
    dest: /tmp/stripped-variables.yml
"""

RETURN = r"""
removed_keys:
    description: The list of top-level keys that were removed.
    type: list
    returned: always
    sample: ["cifmw_discovered_image_url", "cifmw_other_var"]
src:
    description: The source file path.
    type: str
    returned: always
dest:
    description: The destination file path.
    type: str
    returned: always
"""

import os

import yaml

from ansible.module_utils.basic import AnsibleModule


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if data is not None else {}


def run_module():
    module_args = {
        "src": {"type": "str", "required": True},
        "keys_from": {
            "type": "list",
            "elements": "str",
            "required": True,
            "no_log": False,
        },
        "dest": {"type": "str", "required": False, "default": None},
    }

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    src = module.params["src"]
    keys_from = module.params["keys_from"]
    dest = module.params["dest"] or src

    if not os.path.isfile(src):
        module.fail_json(msg=f"Source file not found: {src}")

    try:
        base = load_yaml(src)
    except Exception as e:
        module.fail_json(msg=f"Failed to read source file {src}: {e}")

    if not isinstance(base, dict):
        module.fail_json(
            msg=f"{src}: root must be a YAML mapping, got {type(base).__name__}"
        )

    keys_to_remove = set()
    for kf in keys_from:
        if not os.path.isfile(kf):
            module.fail_json(msg=f"Keys-from file not found: {kf}")
        try:
            keys_data = load_yaml(kf)
        except Exception as e:
            module.fail_json(msg=f"Failed to read keys-from file {kf}: {e}")
        if isinstance(keys_data, dict):
            keys_to_remove.update(keys_data.keys())

    removed = sorted(k for k in keys_to_remove if k in base)
    filtered = {k: v for k, v in base.items() if k not in keys_to_remove}
    changed = len(removed) > 0

    if changed and not module.check_mode:
        try:
            with open(dest, "w", encoding="utf-8") as f:
                yaml.dump(
                    filtered,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                )
        except Exception as e:
            module.fail_json(msg=f"Failed to write destination file {dest}: {e}")

    module.exit_json(
        changed=changed,
        removed_keys=removed,
        src=src,
        dest=dest,
    )


def main():
    run_module()


if __name__ == "__main__":
    main()
