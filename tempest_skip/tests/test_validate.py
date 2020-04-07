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
import subprocess
import tempfile

from tempest_skip.tests import base


class TestValidate(base.TestCase):
    def setUp(self):
        super(TestValidate, self).setUp()

    def assertRunExit(self, cmd, expected):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate()
        msg = ("Running %s got an unexpected returncode\n"
               "Stdout: %s\nStderr: %s" % (' '.join(cmd), out, err))
        self.assertEqual(p.returncode, expected, msg)
        return out, err

    def test_validate_passes(self):
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)

        valid_yaml = """
            known_failures:
              - test: 'tempest_skip.tests.test_validate'
                bz: 'https://bugzilla.redhat.com/1'
                lp: 'https://launchpad.net/bugs/1'
                deployment: 'undercloud'
                jobs:
                  - openstack-tempest-skip-job1
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
                    lp: 'https://launchpad.net/bugs/1'
        """
        yaml_file = os.fdopen(fd, 'w')
        yaml_file.write(valid_yaml)
        yaml_file.close()

        self.assertRunExit(['tempest-skip', 'validate', '--file', path], 0)

    def test_validate_fails(self):
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)

        valid_yaml = """
            known_failures:
              - test: 'tempest_skip.tests.test_validate'
                bz: 'https://bugzilla.redhat.com/1'
                lp: 'https://launchpad.net/bugs/1'
                deployment: 'undercloud'
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

        self.assertRunExit(['tempest-skip', 'validate', '--file', path], 1)
