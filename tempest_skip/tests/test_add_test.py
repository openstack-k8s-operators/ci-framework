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

import mock

from tempest_skip.add_test import AddTest
from tempest_skip.tests import base
import yaml


class TestAddFile(base.TestCase):
    def setUp(self):
        super(TestAddFile, self).setUp()
        self.list_file = """
            known_failures:
              - test: 'tempest_skip.tests.test_list_yaml'
                deployment:
                  - 'overcloud'
                releases:
                  - name: 'master'
                    reason: 'It can be removed when bug for OVN is repaired'
                    lp: 'https://bugs.launchpad.net/tripleo/+bug/1832166'
                jobs: []
              - test: 'tempest_skip.tests.test_list_yaml_2'
                deployment:
                 - 'overcloud'
                releases:
                  - name: 'master'
                    reason: 'This test was enabled recently on ovn'
                    lp: 'https://bugs.launchpad.net/tripleo/+bug/1832166'
                jobs: []
              - test: 'tempest_skip.tests.test_list_yaml_3'
                deployment:
                  - 'overcloud'
                  - 'undercloud'
                releases:
                  - name: 'train'
                    reason: 'Test failing on train release'
                    lp: 'https://bugs.launchpad.net/tripleo/+bug/1832166'
                jobs:
                  - 'job1'
        """

        self.path = self.write_yaml_file(self.list_file)
        self.cmd = AddTest(__name__, [])
        self.parser = self.cmd.get_parser(__name__)
        self.parser.file = self.path

        self.parser.job = None
        self.parser.release = 'master'
        self.parser.lp = 'https://launchpad.net/bug/12345'
        self.parser.bz = None
        self.parser.reason = 'A good reason'
        self.parser.deployment = 'overcloud'
        self.tests_list = ['tempest_skip.tests.test1',
                           'tempest_skip.tests.test2',
                           'tempest_skip.tests.test3']

    @mock.patch('inquirer.Checkbox')
    @mock.patch('inquirer.prompt')
    @mock.patch('tempest_skip.add_test.AddTest._get_tests_list')
    def test_add_test_new_test(self, tests_list, prompt_mock, checkbox_mock):
        self.parser.test = 'tempest_skip.tests'
        tests_list.return_value = self.tests_list
        prompt_mock.return_value = {'list_tests': ['tempest_skip.tests.test3']}
        self.cmd.take_action(self.parser)
        checkbox_mock.assert_called_once()
        prompt_mock.assert_called_once()
        yaml_file = yaml.safe_load(open(self.path))
        # There are 3 tests in the skip file, adding one more test, should be 4
        self.assertEqual(4, len(yaml_file['known_failures']))

    @mock.patch('tempest_skip.add_test.AddTest._get_tests_list')
    def test_add_test_already_exist(self, tests_list):
        self.parser.test = 'tempest_skip.tests.test_list_yaml'

        tests_list.return_value = self.tests_list

        self.cmd.take_action(self.parser)
        yaml_file = yaml.safe_load(open(self.path))
        self.assertEqual(3, len(yaml_file['known_failures']))

    @mock.patch('inquirer.Checkbox')
    @mock.patch('inquirer.prompt')
    @mock.patch('tempest_skip.add_test.AddTest._get_tests_list')
    def test_add_test_no_prompt(self, tests_list, prompt_mock, checkbox_mock):
        self.parser.test = 'tempest_skip.tests.test1'
        tests_list.return_value = self.tests_list
        prompt_mock.return_value = {'list_tests': ['tempest_skip.tests.test3']}
        self.cmd.take_action(self.parser)
        checkbox_mock.assert_not_called()
        prompt_mock.assert_not_called()
        yaml_file = yaml.safe_load(open(self.path))
        # There are 3 tests in the skip file, adding one more test, should be 4
        self.assertEqual(4, len(yaml_file['known_failures']))
