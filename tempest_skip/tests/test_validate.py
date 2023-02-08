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

from tempest_skip.tests import base
from tempest_skip.validate import Validate
from voluptuous.error import MultipleInvalid


class TestValidate(base.TestCase):
    def setUp(self):
        super(TestValidate, self).setUp()
        self.cmd = Validate(__name__, [])
        self.parser = self.cmd.get_parser(__name__)
        self.parser.skipped = False
        self.parser.allowed = False


class TestValidateAllowed(TestValidate):
    def setUp(self):
        super(TestValidateAllowed, self).setUp()

    def test_validate_passes(self):
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)

        valid_yaml = """
            jobs:
              - name: 'job1'
                tests:
                  - test1
                  - test2
                releases:
                  - master
              - name: 'job2'
                tests:
                  - another.test
                  - a.different.test
                releases:
                  - master
        """
        yaml_file = os.fdopen(fd, 'w')
        yaml_file.write(valid_yaml)
        yaml_file.close()

        self.parser.allowed = True
        self.parser.filename = path
        cmd_result = self.cmd.take_action(self.parser)

        self.assertEqual(cmd_result, None)

    def test_validate_fails(self):
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)

        valid_yaml = """
            jobs:
              - name: 'job1.will.fail'
                test:
                  - test1
                  - test2
              - name: 'job2'
                tests:
                  - another.test
                  - a.different.test
        """
        yaml_file = os.fdopen(fd, 'w')
        yaml_file.write(valid_yaml)
        yaml_file.close()

        self.parser.allowed = True
        self.parser.filename = path
        self.assertRaises(MultipleInvalid, self.cmd.take_action, self.parser)


class TestValidateSkipped(TestValidate):
    def setUp(self):
        super(TestValidateSkipped, self).setUp()

    def test_validate_passes(self):
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)

        valid_yaml = """
            known_failures:
              - test: 'tempest_skip.tests.test_validate'
                bz: 'https://bugzilla.redhat.com/1'
                lp: 'https://launchpad.net/bugs/1'
                deployment:
                  - 'undercloud'
                jobs:
                  - openstack-tempest-skip-job1
                  - openstack-tempest-skip-job2
                reason: 'This test is failing'
                releases:
                  - name: 'master'
                    lp: 'https://launchpad.net/bugs/1'
                    reason: 'Test with launchpad'
                    installers:
                      - 'tripleo'
                      - 'osp'
                  - name: 'train'
                    bz: 'https://bugzilla.redhat.com/1'
                    reason: 'Test with bugzilla'
                  - name: 'ussuri'
                    reason: 'Test without launchpad or bugzilla'
                    lp: 'https://launchpad.net/bugs/1'
        """
        yaml_file = os.fdopen(fd, 'w')
        yaml_file.write(valid_yaml)
        yaml_file.close()

        self.parser.skipped = True
        self.parser.filename = path
        cmd_result = self.cmd.take_action(self.parser)

        self.assertEqual(cmd_result, None)

    def test_validate_fails(self):
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)

        valid_yaml = """
            known_failures:
              - test: 'tempest_skip.tests.test_validate'
                bz: 'https://bugzilla.redhat.com/1'
                lp: 'https://launchpad.net/bugs/1'
                deployment:
                  - 'undercloud'
                jobs:
                  - openstack-tempest-skip-job1:
                    option: '1'
                  - openstack-tempest-skip-job2
                reason: 'This test is failing'
                releases:
                  - name: 'master'
                    lp: 'https://launchpad.net/bugs/1'
                    reason: 'Test with launchpad'
                  - name: 'train'
                    bz: 'https://bugzilla.redhat.com/1'
                    reason: 'Test with bugzilla'
                  - name: 'ussuri'
                    reason: 'Test without launchpad or bugzilla'
        """
        yaml_file = os.fdopen(fd, 'w')
        yaml_file.write(valid_yaml)
        yaml_file.close()

        self.parser.skipped = True
        self.parser.filename = path
        self.assertRaises(MultipleInvalid, self.cmd.take_action, self.parser)
