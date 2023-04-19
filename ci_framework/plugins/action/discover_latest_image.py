# Copyright Red Hat, Inc.
# Apache License Version 2.0 (see LICENSE)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
action: discover_latest_image

short_description: Discover the latest image available on remote server.

description:
- Discover latest image matching a specific pattern on remote server.

options: Please refer to ansible.builtin.uri options

'''

EXAMPLES = r'''
- name: Get latest CentOS 9 Stream image
  register: discovered_images
  discover_latest_image:
    base_url: "https://cloud.centos.org/centos/{{ ansible_distribution_major_version }}-stream/x86_64/images/"
    image_prefix: "CentOS-Stream-GenericCloud-"
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

try:
    from bs4 import BeautifulSoup
except ImportError as imp_exc:
    BS4_IMPORT = imp_exc
else:
    BS4_IMPORT = None


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)
        module_args = self._task.args.copy()

        if BS4_IMPORT:
            raise AnsibleError(missing_required_lib('beautifulsoup4'))

        if 'image_prefix' not in module_args:
            raise AnsibleError('"image_prefix" parameter is mandatory')

        img_prefix = module_args.pop('image_prefix')

        result = {
            'success': False,
            'changed': False,
            'error': '',
            'data': {},
        }

        # Ensure we return content
        module_args['return_content'] = True
        # Ensure we run locally only
        task_vars['delegate_to'] = 'localhost'

        page = self._execute_module(module_name="ansible.builtin.uri",
                                    module_args=module_args,
                                    task_vars=task_vars,
                                    tmp=tmp)

        # Prepare matcher
        matcher = re.compile(rf'{img_prefix}.*\.qcow2$')

        # Start parsing
        parsed = BeautifulSoup(page['content'], 'html.parser')
        all_links = parsed.find_all('a')
        extracted = []
        for link in all_links:
            if matcher.match(link.get('href')):
                extracted.append(link.get('href'))

        latest_image = extracted[-1]
        base_url = module_args['url']
        module_args['url'] = f'{base_url}/{latest_image}.SHA256SUM'
        sha256sum = self._execute_module(module_name='ansible.builtin.uri',
                                         module_args=module_args,
                                         task_vars=task_vars,
                                         tmp=tmp)

        extracted_sha = sha256sum['content'].split('=')[1].strip()

        result['data'] = {
            'image_name': latest_image,
            'image_url': f'{base_url}/{latest_image}',
            'sha256': extracted_sha,
        }

        result["success"] = True
        result["changed"] = True
        return result
