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


DEFAULT_TESTS = ['smoke']


class ListSkippedYaml(Lister):
    """Command to list the tests to be skipped, using a YAML file, based on
       release and/or job"""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.debug('Running list_yaml command')
        yaml_file = yaml.safe_load(open(parsed_args.file))
        tests = []

        tests = self._filter_skipped_tests(parsed_args, yaml_file)
        return (('Test name',), ((test['test'],) for test in tests))

    def _filter_skipped_tests(self, parsed_args, yaml_file):
        if len(yaml_file) > 0:
            tests = yaml_file.get('known_failures', [])

            if parsed_args.job:
                tests = [test for test in tests
                         if (not test.get('jobs', []) or (
                             parsed_args.job in test.get('jobs')))]

            if parsed_args.release:
                tests = [test for test in tests
                         if [release for release in test.get('releases', [])
                             if release['name'] == parsed_args.release]]

            if parsed_args.installer:
                tests = [test for test in tests
                         if [release for release in test.get('releases', [])
                             if parsed_args.installer in
                             release.get('installers', ['tripleo', 'osp'])]]

            if parsed_args.deployment:
                tests = [test for test in tests
                         if (not test.get('deployment', []) or (
                             parsed_args.deployment in
                             test.get('deployment')))]
            return tests
        return []

    def get_parser(self, prog_name):
        parser = super(ListSkippedYaml, self).get_parser(prog_name)
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
        parser.add_argument('--installer', dest='installer',
                            default='tripleo', help='Tests to be skipped for '
                                                'a particular installer. Use '
                                                'tripleo for upstream, and osp'
                                                ' for downstream')
        return parser
