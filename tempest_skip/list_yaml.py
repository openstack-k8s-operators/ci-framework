#!/usr/bin/python
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
            tests = yaml_file.get('known_failures', [])

            if parsed_args.job:
                self.parsed_job = parsed_args.job
                tests = list(filter(self._filter_jobs, tests))

            if parsed_args.release:
                new_tests = []
                for test in tests:
                    for release in test.get('releases', []):
                        if release.get('name') == parsed_args.release:
                            new_tests.append(test)
                tests = new_tests

            if parsed_args.deployment:
                self.parsed_deployment = parsed_args.deployment
                tests = list(filter(self._filter_deployment, tests))

        return (('Test name',), ((test['test'],) for test in tests))

    def _filter_deployment(self, test):
        if not test.get('deployment', []):
            return True
        if self.parsed_deployment in test.get('deployment'):
            return True
        return False

    def _filter_jobs(self, test):
        if not test.get('jobs', []):
            return True
        if self.parsed_job in test.get('jobs'):
            return True
        return False

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
        parser.add_argument('--deployment', dest='deployment',
                            help='List the tests to be skipped in the '
                                 'given deployment')
        return parser
