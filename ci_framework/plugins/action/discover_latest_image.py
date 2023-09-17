# Copyright Red Hat, Inc.
# Apache License Version 2.0 (see LICENSE)

from __future__ import absolute_import, division, print_function
import re
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError

__metaclass__ = type

DOCUMENTATION = r"""
---
action: discover_latest_image

short_description: Discover the latest image available on remote server.

description:
- Discover latest image matching a specific pattern on remote server.

options: Please refer to ansible.builtin.uri options

"""

EXAMPLES = r"""
- name: Get latest CentOS 9 Stream image
  register: discovered_images
  discover_latest_image:
    base_url: "https://cloud.centos.org/centos/{{ ansible_distribution_major_version }}-stream/x86_64/images"
    image_prefix: "CentOS-Stream-GenericCloud-"
    images_file: "CHECKSUM"
"""  # noqa

RETURN = r"""
success:
    description: Status of the module
    type: bool
    returned: always
    sample: True
data:
    description: Dict grouping the various data the action fetches
    type: dict
    returned: always
"""


class ActionModule(ActionBase):
    IMAGES_FILES = [
        # e.g: https://cloud.centos.org/centos/9-stream/x86_64/images/CHECKSUM
        "CHECKSUM",
        "SHA256SUM",
        "SHA1SUM",
        "MD5SUM",
    ]

    def run(self, tmp=None, task_vars=None):
        super().run(tmp, task_vars)

        module_args = self._task.args.copy()

        if "image_prefix" not in module_args:
            raise AnsibleError('"image_prefix" parameter is mandatory')

        img_prefix = module_args.pop("image_prefix")

        images_files = self.IMAGES_FILES.copy()
        if "images_file" in module_args:
            images_files.insert(0, module_args.pop("images_file"))

        # Ensure we return content
        module_args["return_content"] = True
        # Ensure we run locally only
        task_vars["delegate_to"] = "localhost"

        base_image_url = module_args["url"]

        qcow2_image_pattern = re.compile(
            rf"(SHA256|SHA1|MD5) \(.*?({re.escape(img_prefix)}.*?\.qcow2)\)"
        )

        image_list = None
        for image_file in images_files:
            module_args["url"] = f"{base_image_url}/{image_file}"

            page = self._execute_module(
                module_name="ansible.builtin.uri",
                module_args=module_args,
                task_vars=task_vars,
                tmp=tmp,
            )

            if "failed" not in page:
                image_list = list(
                    filter(qcow2_image_pattern.match, page["content"].split("\n"))
                )
                break
        else:
            raise AnsibleError(
                "Error fetching the information from all checksum files."
            )

        if not image_list:
            raise AnsibleError(
                f"The image with the following prefix {img_prefix} "
                "can't be determined."
            )

        last_image = image_list[-1]

        image_name_hash_pattern = re.compile(r"(SHA256|SHA1|MD5) \((.*?)\) = (.*)")
        image_name_sha_match = image_name_hash_pattern.search(last_image)
        hash_algorithm = image_name_sha_match.group(1)
        image_name = image_name_sha_match.group(2)
        image_hash = image_name_sha_match.group(3)

        result = {
            "success": True,
            "changed": True,
            "error": "",
            "data": {
                "image_name": image_name,
                "image_url": f"{base_image_url}/{image_name}",
                "hash": image_hash,
                "hash_algorithm": hash_algorithm.lower(),
            },
        }

        return result
