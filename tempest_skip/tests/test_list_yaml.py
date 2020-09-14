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

import os
import tempfile

from cliff.lister import Lister
from tempest_skip.tests import base
from tempest_skip.list_yaml import ListYaml


class TestListYamlRelease(Lister):

    def get_parser(self, prog_name):
        parser = super(TestListYamlRelease, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        tests = ['tempest_skip.tests.test_list_yaml',
                 'tempest_skip.tests.test_list_yaml_2']
        return (('Test name', ), ((test,) for test in tests))


class TestListYaml(base.TestCase):
    def setUp(self):
        super(TestListYaml, self).setUp()
        self.list_file = """
            known_failures:
              - test: 'tempest_skip.tests.test_list_yaml'
                deployment: 'overcloud'
                releases:
                  - name: 'master'
                    reason: 'It can be removed when bug for OVN is repaired'
                    lp: 'https://bugs.launchpad.net/tripleo/+bug/1832166'
                jobs: []
              - test: 'tempest_skip.tests.test_list_yaml_2'
                deployment: 'overcloud'
                releases:
                  - name: 'master'
                    reason: 'This test was enabled recently on ovn'
                    lp: 'https://bugs.launchpad.net/tripleo/+bug/1832166'
                jobs: []
              - test: 'tempest_skip.tests.test_list_yaml_3'
                deployment: 'overcloud'
                releases:
                  - name: 'train'
                    reason: 'Test failing on train release'
                    lp: 'https://bugs.launchpad.net/tripleo/+bug/1832166'
                jobs:
                  - 'job1'
        """
        self.path = self.write_yaml_file(self.list_file)

        self.cmd = ListYaml(__name__, [])
        self.parser = self.cmd.get_parser(__name__)
        self.parser.file = self.path
        self.parser.release = None
        self.parser.job = None

    def write_yaml_file(self, file_content):
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)

        yaml_file = os.fdopen(fd, 'w')
        yaml_file.write(file_content)
        yaml_file.close()

        return path

    def test_list_yaml(self):
        cmd_result = self.cmd.take_action(self.parser)

        exptected = [('tempest_skip.tests.test_list_yaml',),
                     ('tempest_skip.tests.test_list_yaml_2',),
                     ('tempest_skip.tests.test_list_yaml_3',)]
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(exptected, list_tests)

    def test_list_yaml_with_release(self):
        self.parser.release = 'train'
        self.parser.job = None

        cmd_result = self.cmd.take_action(self.parser)
        exptected = [('tempest_skip.tests.test_list_yaml_3',)]
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(exptected, list_tests)

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
                     ('tempest_skip.tests.test_list_yaml_3',)]
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(exptected, list_tests)

    def test_list_yaml_with_job_not_found(self):
        self.parser.job = 'job2'
        cmd_result = self.cmd.take_action(self.parser)
        exptected = [('tempest_skip.tests.test_list_yaml',),
                     ('tempest_skip.tests.test_list_yaml_2',)]
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(exptected, list_tests)

    def test_list_yaml_with_release_and_job(self):
        self.parser.job = 'job1'
        self.parser.release = 'train'
        cmd_result = self.cmd.take_action(self.parser)
        exptected = [('tempest_skip.tests.test_list_yaml_3',)]
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(exptected, list_tests)

    def test_list_yaml_with_release_and_job_not_found(self):
        self.parser.job = 'job2'
        self.parser.release = 'not-found'
        cmd_result = self.cmd.take_action(self.parser)
        exptected = []
        list_tests = [test for test in cmd_result[1]]
        self.assertEqual(exptected, list_tests)
