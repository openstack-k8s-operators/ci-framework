# Copyright 2020 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging

from cliff.lister import Lister
import yaml


class ListYaml(Lister):
    """Command to list the tests to be skipped, using a YAML file, based on
       release and/or job"""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.debug('Running list_yaml command')
        yaml_file = yaml.safe_load(open(parsed_args.file))
        tests = []
        if len(yaml_file) > 0:
            for test in yaml_file.get('known_failures', []):
                will_append_job = False
                will_append_release = False
                if parsed_args.job:
                    will_append_job = parsed_args.job in test.get('jobs', [])
                if parsed_args.release:
                    for release in test.get('releases', []):
                        if release.get('name') == parsed_args.release:
                            will_append_release = True
                            break
                # First case: no job or release passed
                if not parsed_args.job and not parsed_args.release:
                    tests.append(test.get('test'))
                # Second case: job parsed, but no release
                if parsed_args.job and not parsed_args.release:
                    if will_append_job:
                        tests.append(test.get('test'))
                # Third case: release passed but no job
                if not parsed_args.job and parsed_args.release:
                    if will_append_release:
                        tests.append(test.get('test'))
                # Fourth case: release and job passed
                if parsed_args.job and parsed_args.release:
                    if will_append_job and will_append_release:
                        tests.append(test.get('test'))
        return (('Test name',), ((test,) for test in tests))

    def get_parser(self, prog_name):
        parser = super(ListYaml, self).get_parser(prog_name)
        parser.add_argument('--file', dest='file',
                            required=True,
                            help='List the tests to be skipped in the '
                                 'YAML file'
                            )
        parser.add_argument('--job', dest='job',
                            help='List the tests to be skipped in the '
                                 'given job'
                            )
        parser.add_argument('--release', dest='release',
                            help='List the tests to be skipped in the '
                                 'given release'
                            )
        return parser
