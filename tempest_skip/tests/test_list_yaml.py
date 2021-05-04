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
from tempest_skip.list_yaml import ListSkippedYaml


class TestListSkippedYaml(base.TestCase):
    def setUp(self):
        super(TestListSkippedYaml, self).setUp()
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
              - test: 'tempest_skip.tests.test_list_yaml_4'
                deployment:
                  - 'overcloud'
                releases:
                  - name: 'train'
                    reason: 'Test failing on train release'
                    lp: 'https://bugs.launchpad.net/tripleo/+bug/1832166'
                    installers:
                      - 'osp'
                jobs:
                  - 'job3'
              - test: 'tempest_skip.tests.test_list_yaml_5'
                deployment:
                  - 'overcloud'
                releases:
                  - name: 'train'
                    reason: 'Test failing on train release'
                    lp: 'https://bugs.launchpad.net/tripleo/+bug/1832166'
                    installers:
                      - 'osp'
                      - 'tripleo'
                  - name: 'wallaby'
                    reason: 'Test failing on train release'
                    lp: 'https://bugs.launchpad.net/tripleo/+bug/1832166'
                jobs: []
        """
        self.path = self.write_yaml_file(self.list_file)

        self.cmd = ListSkippedYaml(__name__, [])
        self.parser = self.cmd.get_parser(__name__)
        self.parser.file = self.path
        self.parser.release = None
        self.parser.deployment = None
        self.parser.job = None
        self.parser.installer = 'tripleo'

    def test_list_yaml(self):
        cmd_result = self.cmd.take_action(self.parser)

        exptected = [('tempest_skip.tests.test_list_yaml',),
                     ('tempest_skip.tests.test_list_yaml_2',),
                     ('tempest_skip.tests.test_list_yaml_3',),
                     ('tempest_skip.tests.test_list_yaml_5',)]
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(exptected, list_tests)

    def test_list_yaml_with_release(self):
        self.parser.release = 'train'
        self.parser.job = None

        cmd_result = self.cmd.take_action(self.parser)
        exptected = [('tempest_skip.tests.test_list_yaml_3',),
                     ('tempest_skip.tests.test_list_yaml_5',)]
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(exptected, list_tests)

    def test_list_yaml_with_deployment(self):
        self.parser.deployment = 'undercloud'

        cmd_result = self.cmd.take_action(self.parser)
        expected = [('tempest_skip.tests.test_list_yaml_3',)]
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(expected, list_tests)

        self.parser.deployment = 'notfound'
        cmd_result = self.cmd.take_action(self.parser)
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual([], list_tests)

        self.parser.deployment = 'undercloud'
        self.parser.release = 'master'
        cmd_result = self.cmd.take_action(self.parser)
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual([], list_tests)

        self.parser.deployment = 'undercloud'
        self.parser.release = 'train'
        cmd_result = self.cmd.take_action(self.parser)
        expected = [('tempest_skip.tests.test_list_yaml_3',)]
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(expected, list_tests)

    def test_list_yaml_with_installer(self):
        self.parser.installer = 'osp'
        self.parser.release = 'master'
        cmd_result = self.cmd.take_action(self.parser)
        expected = [('tempest_skip.tests.test_list_yaml',),
                    ('tempest_skip.tests.test_list_yaml_2',)]
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(expected, list_tests)

    def test_list_yaml_with_installer_and_deployment(self):
        self.parser.installer = 'osp'
        self.parser.deployment = 'overcloud'
        cmd_result = self.cmd.take_action(self.parser)
        expected = [('tempest_skip.tests.test_list_yaml',),
                    ('tempest_skip.tests.test_list_yaml_2',),
                    ('tempest_skip.tests.test_list_yaml_3',),
                    ('tempest_skip.tests.test_list_yaml_4',),
                    ('tempest_skip.tests.test_list_yaml_5',)]
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(expected, list_tests)

    def test_list_yaml_with_installer_and_invalid_deployment(self):
        self.parser.installer = 'osp'
        self.parser.deployment = 'underclouds'
        cmd_result = self.cmd.take_action(self.parser)
        expected = []
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(expected, list_tests)

    def test_list_yaml_with_release_not_found(self):
        self.parser.release = 'not-found'
        self.parser.job = None

        cmd_result = self.cmd.take_action(self.parser)
        exptected = []
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(exptected, list_tests)

    def test_list_yaml_with_job(self):
        self.parser.job = 'job1'
        cmd_result = self.cmd.take_action(self.parser)
        exptected = [('tempest_skip.tests.test_list_yaml',),
                     ('tempest_skip.tests.test_list_yaml_2',),
                     ('tempest_skip.tests.test_list_yaml_3',),
                     ('tempest_skip.tests.test_list_yaml_5',)]
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(exptected, list_tests)

    def test_list_yaml_with_job_not_found(self):
        self.parser.job = 'job2'
        cmd_result = self.cmd.take_action(self.parser)
        exptected = [('tempest_skip.tests.test_list_yaml',),
                     ('tempest_skip.tests.test_list_yaml_2',),
                     ('tempest_skip.tests.test_list_yaml_5',)]
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(exptected, list_tests)

    def test_list_yaml_with_release_and_job(self):
        self.parser.job = 'job1'
        self.parser.release = 'train'
        cmd_result = self.cmd.take_action(self.parser)
        exptected = [('tempest_skip.tests.test_list_yaml_3',),
                     ('tempest_skip.tests.test_list_yaml_5',)]
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(exptected, list_tests)

    def test_list_yaml_with_release_and_job_not_found(self):
        self.parser.job = 'job2'
        self.parser.release = 'not-found'
        cmd_result = self.cmd.take_action(self.parser)
        exptected = []
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(exptected, list_tests)
