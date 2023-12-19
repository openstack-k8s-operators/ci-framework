#!/usr/bin/python

# Copyright: (c) 2023, Arx Cruz <acruz@redhat.com>
# Apache License Version 2.0 (see LICENSE)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: tempest_list_skipped

short_description: Parse skipped tests from tempest

description:
  - Parse filtered tests to be skipped by tempest

options:
  yaml_file:
    description:
      - Path to a yaml file containing the skipped tests in
        openstack-tempest-skiplist format
    required: True
    type: str
  jobs:
    description:
      - List of the jobs to be used in the filter. Passing the jobs it will
        filter only tests that have the specified jobs in the jobs list.
    required: False
    type: list
    elements: str
  release:
    description:
      - Release name to be used in the filter. Default is set to 'master'
    required: False
    default: master
    type: str

author:
  - Arx Cruz (@arxcruz)

"""


EXAMPLES = r"""
- name: Get list of skipped tests
  tempest_list_skipped:
    yaml_file: /tmp/skipped.yaml
    job: edpm
    release: master
"""


RETURN = r"""
skipped_tests:
  description:
    - List of tests filtered
  returned: Always
  type: list
  sample: [
    "tempest.api.volume.test_volumes_snapshots.VolumesSnapshotTestJSON"
    ]
"""

from ansible.module_utils.basic import AnsibleModule
import yaml


def run_module():
    module_args = {
        "yaml_file": {"type": "str", "required": True},
        "jobs": {"type": "list", "required": False, "elements": "str"},
        "release": {"type": "str", "required": False, "default": "master"},
    }

    result = dict(changed=True, message="", skipped_tests=[])

    module = AnsibleModule(argument_spec=module_args)
    if not module.params["yaml_file"]:
        module.fail_json(msg="A yaml file must be provided!")

    _release = module.params["release"]
    _jobs = module.params["jobs"]
    with open(module.params["yaml_file"]) as yf:
        _yaml_file = yaml.safe_load(yf)

    tests = _filter_skipped_tests(_jobs, _release, _yaml_file)
    skipped_tests = tests

    result.update({"skipped_tests": skipped_tests})
    module.exit_json(**result)


def _filter_skipped_tests(jobs, release, yaml_file):
    if len(yaml_file) > 0:
        tests = yaml_file.get("known_failures", [])

        if jobs:
            tests = [
                test
                for test in tests
                if (not test.get("jobs", []))
                or ([job for job in jobs if job in test.get("jobs", [])])
            ]

        if release:
            tests = [
                test
                for test in tests
                if [rel for rel in test.get("releases", []) if rel["name"] == release]
            ]

        if len(tests) > 0:
            return [test.get("test") for test in tests]
    return []


def main():
    run_module()


if __name__ == "__main__":
    main()
