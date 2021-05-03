#!/usr/bin/python
# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ansible.module_utils.basic import AnsibleModule
from tempest_skip.list_allowed import ListAllowedYaml

import sys


ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}


DOCUMENTATION = '''
---
module: list_allowed
author:
  - "Arx Cruz (@arxcruz)
version_added: '2.9'
short_description:
  - Parse filtered tests from tempest
notes: []
requirements:
  - tempest-skip
options:
  yaml_file:
    description:
      - Path to a yaml file containing the tests in
        openstack-tempest-skiplist format
    required: True
    type: str
  job:
    description:
      - Name of the job to be used in the filter.
    required: False
    type: str
  group:
    description:
      - Group name to be used in the filter. It has more precedence than job
    required: False
    type: str
'''


EXAMPLES = '''
- name: Get list of allowed tests
  list_allowed:
    yaml_file: /tmp/allowed.yaml
    job: tripleo-ci-centos-8-standalone
    group: default
'''


RETURN = '''
allowed_tests:
  description:
    - List of tests filtered
  returned: Always
  type: list
  sample: [
    "tempest.api.volume.test_volumes_snapshots.VolumesSnapshotTestJSON"
    ]
'''


def run_module():
    module_args = dict(
        yaml_file=dict(type='str', required=True),
        job=dict(type='str', required=False, default=None),
        group=dict(type='str', required=False, default=None),
        release=dict(type='str', required=False, default="master")
    )

    result = dict(
        changed=True,
        message='',
        filtered_tests=[]
    )

    module = AnsibleModule(
        argument_spec=module_args
    )
    if not module.params['yaml_file']:
        module.fail_json(msg="A yaml file must be provided!")

    if not module.params['job'] and not module.params['group']:
        module.fail_json(msg="You must specify either job or group parameter!")

    cmd = ListAllowedYaml(__name__, sys.argv[1:])
    parser = cmd.get_parser(__name__)
    parser.file = module.params['yaml_file']
    parser.group = module.params['group']
    parser.release = module.params['release']
    parser.job = module.params['job']

    tests = cmd.take_action(parser)
    allowed_tests = [test[0] for test in tests[1]]

    result.update({'allowed_tests': allowed_tests})
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
