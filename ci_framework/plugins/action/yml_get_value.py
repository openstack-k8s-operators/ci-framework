# Copyright Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
action: yml_get_value

short_description: Get  value from corresponding to  from yml files.

description:
- traverses through the specified parameter path, and extracts the specified
  value if it exists. It utilizes regular expressions to identify parts 
  of the parameter path that match a specific pattern.

options: Please refer to ansible.builtin.uri options

'''

EXAMPLES = r'''
- name: Get the url of reportportal server
  register: discovered_url
  yml_get_value:
    parameter_path: "job.parameters.hidden[name=INSTANCE_URL].default"
    file_path: "some path/file.yml"

where the content of the yml file is

- job:
    name: reportportal-update
    project-type: pipeline
    concurrent: true

    description: |
      Update ReportPortal with RHOSP Test & Deployment Results<br>

    parameters:
      - hidden:
          name: INSTANCE_URL
          default: https://reportportal.com
          description: D&O ReportPortal instance URL

      - hidden:
          name: TOKEN
          default: 12345
          description: D&O ReportPortal instance URL

dicsovered_url will contain "https://reportportal.com"
'''

RETURN = r'''
success:
    description: Status of the module
    type: bool
    returned: always
    sample: True
data:
    description: Dict grouping the various data the action fetches
    type: dict
    returned: always
'''

from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase
from ansible.module_utils.basic import missing_required_lib

import re
import yaml


class ActionModule(ActionBase):
    pattern = r'([^[]+)\[name=([^]]+)\]'     
    
    def parse_yaml_file(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            data = yaml.safe_load(content)
            return data

    def get_default_value(self, data, parameter_path):
        parts = parameter_path.split('.')
        current_data = data[0] # get first document from the file

        for part in parts:
            match = re.search(self.pattern, part)

            if match:
                parameter_type = match.group(1)
                name_value = match.group(2)

                for parameter in current_data:
                    if parameter.get(parameter_type, {}).get('name') == name_value:
                        current_data = parameter.get(parameter_type, {})
                        break
            else:
                try:
                    current_data = current_data.get(part, {})
                except AttributeError as e:
                    print(name_value, " not found")
                    return None
                
        return current_data

    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)
        module_args = self._task.args.copy()

        if 'parameter_path' not in module_args:
            raise AnsibleError('"parameter_path" parameter is mandatory')
        
        if 'file_path' not in module_args:
            raise AnsibleError('"file_path" parameter is mandatory')

        parameter_path = module_args.pop('parameter_path')
        file_path = module_args.pop('file_path')

        # Ensure we return content
        module_args['return_content'] = True
        # Ensure we run locally only
        task_vars['delegate_to'] = 'localhost'

        data = self.parse_yaml_file(file_path)
        default_value = self.get_default_value(data, parameter_path)

        if default_value is None:
            raise ValueError('Value not found')

        result = {
            'success': True,
            'changed': True,
            'error': '',
            'data': {
                'value': default_value,
            },
        }

        return result
