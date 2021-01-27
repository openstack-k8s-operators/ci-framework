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

from oslotest import base


class TestCase(base.BaseTestCase):

    def write_yaml_file(self, file_content):
        fd, path = tempfile.mkstemp()
        self.addCleanup(os.remove, path)

        yaml_file = os.fdopen(fd, 'w')
        yaml_file.write(file_content)
        yaml_file.close()

        return path
