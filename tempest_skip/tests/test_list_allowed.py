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

from tempest_skip.tests import base
from tempest_skip.list_allowed import ListAllowedYaml


class TestListYamlAllowed(base.TestCase):
    def setUp(self):
        super(TestListYamlAllowed, self).setUp()
        self.list_file = """
            groups:
              - name: group1
                tests:
                  - test_group_1
                  - test_group_2
                releases:
                  - master
            jobs:
              - name: job1
                tests:
                  - test1
                  - test2
                  - test3
                releases:
                  - master
                  - another
              - name: job2
                tests:
                  - test4
                  - test5
                releases:
                  - master
        """

        self.path = self.write_yaml_file(self.list_file)

        self.cmd = ListAllowedYaml(__name__, [])

        self.parser = self.cmd.get_parser(__name__)
        self.parser.file = self.path
        self.parser.release = None
        self.parser.deployment = None
        self.parser.job = None
        self.parser.group = None
        self.parser.release = 'master'

    def test_list_allowed_with_job(self):
        self.parser.job = 'job1'
        cmd_result = self.cmd.take_action(self.parser)
        expected = [('test1',), ('test2',), ('test3',)]
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(expected, list_tests)

    def test_list_allowed_without_job(self):
        cmd_result = self.cmd.take_action(self.parser)
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual([], list_tests)

    def test_list_allowed_with_no_job(self):
        self.parser.job = 'no-exist'
        cmd_result = self.cmd.take_action(self.parser)
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual([], list_tests)

    def test_list_allowed_with_group(self):
        self.parser.group = 'group1'
        cmd_result = self.cmd.take_action(self.parser)
        expected = [('test_group_1',), ('test_group_2',)]
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(expected, list_tests)

    def test_list_allowed_with_no_group(self):
        self.parser.group = 'no-exist'
        cmd_result = self.cmd.take_action(self.parser)
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual([], list_tests)

    def test_list_allowed_with_no_release(self):
        self.parser.release = 'no-exist'
        cmd_result = self.cmd.take_action(self.parser)
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual([], list_tests)

    def test_list_allowed_with_no_release_but_job(self):
        self.parser.release = 'no-exist'
        self.parser.job = 'job2'
        cmd_result = self.cmd.take_action(self.parser)
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual([], list_tests)
