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


class ListAllowedYaml(Lister):
    """Command to list the tests to be included, using a YAML file, based on
       release and/or job"""

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.debug('Running list_allowed command')
        yaml_file = yaml.safe_load(open(parsed_args.file))

        tests = self._filter_allowed_tests(parsed_args, yaml_file)
        return (('Test name',), ((test,) for
                test in tests))

    def _filter_allowed_tests(self, parsed_args, yaml_file):
        tests = []
        if len(yaml_file) > 0:
            if parsed_args.group:
                everything = yaml_file.get('groups', [])
                tests = list(filter(
                    lambda x:
                        x.get('name', '') == parsed_args.group, everything))
                tests = list(filter(
                    lambda x:
                        parsed_args.release in x.get('releases', []), tests))
            if parsed_args.job:
                everything = yaml_file.get('jobs', [])
                tests = list(filter(
                    lambda x: x.get('name', '') == parsed_args.job,
                    everything))
                tests = list(filter(
                    lambda x:
                        parsed_args.release in x.get('releases', []), tests))
        if len(tests) > 0:
            return tests[0].get('tests')
        return []

    def get_parser(self, prog_name):
        parser = super(ListAllowedYaml, self).get_parser(prog_name)
        parser.add_argument('--file', dest='file',
                            required=True,
                            help='List the tests to be included in the '
                                 'YAML file'
                            )
        group = parser.add_mutually_exclusive_group(required=True)

        group.add_argument('--job', dest='job',
                           help='List the tests to be included in the '
                                'given job'
                           )
        group.add_argument('--group', dest='group',
                           help='List the tests to be included in the '
                                'given group'
                           )
        parser.add_argument('--release', dest='release',
                            help='Filter the tests per release',
                            default='master')
        return parser
