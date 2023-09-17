#!/usr/bin/python

# Copyright: (c) 2023, Arx Cruz <acruz@redhat.com>
# Apache License Version 2.0 (see LICENSE)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: tempest_list_allowed

short_description: Parse filtered tests to tempest

description:
  - Parse filtered tests to be executed by tempest

options:
  yaml_file:
    description:
    - Path to a yaml file containing the tests in openstack-tempest-skiplist
      format
    required: True
    type: str
  job:
    description:
    - Name of the job to be used in the filter.
    required: False
    type: str
  groups:
    description:
    - List of groups to be used in the filter. It has more precedence than job
    required: False
    type: list
    elements: str
  release:
    description:
    - Release version
    type: str
    default: master

author:
  - Arx Cruz (@arxcruz)

"""

EXAMPLES = r"""
- name: Get list of allowed tests
  tempest_list_allowed:
    yaml_file: /tmp/allowed.yaml
    job: tripleo-ci-centos-8-standalone
    groups:
     - default
"""

RETURN = r"""
allowed_tests:
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


def _filter_allowed_tests(groups, release, job, yaml_file):
    tests = []
    if yaml_file:
        if groups:
            everything = yaml_file.get("groups", [])
            for group in groups:
                group_tests = list(
                    filter(lambda x: x.get("name", "") == group, everything)
                )
                group_tests = list(
                    filter(
                        lambda x: any(
                            r in ["all", release] for r in x.get("releases", [])
                        ),
                        group_tests,
                    )
                )
                if len(group_tests) > 0:
                    tests = tests + group_tests
        if job:
            everything = yaml_file.get("jobs", [])
            job_tests = list(filter(lambda x: x.get("name", "") == job, everything))
            job_tests = list(
                filter(
                    lambda x: any(r in ["all", release] for r in x.get("releases", [])),
                    job_tests,
                )
            )
            if len(job_tests) > 0:
                tests = job_tests
    return [t for sublist in tests for t in sublist.get("tests", [])]


def main():
    module_args = {
        "yaml_file": {"type": "str", "required": True},
        "job": {"type": "str", "required": False},
        "groups": {"type": "list", "elements": "str"},
        "release": {"type": "str", "default": "master"},
    }

    result = {"changed": True, "message": "", "allowed_tests": []}

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)
    if not module.params["yaml_file"]:
        module.fail_json(msg="A yaml file must be provided!")

    if not module.params["job"] and not module.params["groups"]:
        module.fail_json(msg="You must specify either job or group parameter!")

    with open(module.params["yaml_file"]) as yf:
        _yaml_file = yaml.safe_load(yf)

    _groups = module.params["groups"]
    _release = module.params["release"]
    _job = module.params["job"]

    tests = _filter_allowed_tests(_groups, _release, _job, _yaml_file)

    allowed_tests = tests

    result.update({"allowed_tests": allowed_tests})
    module.exit_json(**result)


if __name__ == "__main__":
    main()
