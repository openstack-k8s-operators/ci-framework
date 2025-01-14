#!/usr/bin/python

# Copyright: (c) 2025, Pablo Rodriguez <pabrodri@redhat.com>
# Apache License Version 2.0 (see LICENSE)

__metaclass__ = type

DOCUMENTATION = r"""
---
module: url_request
short_description: Downloads/fetches the content of a SPNEGO secured URL
extends_documentation_fragment:
    - files

description:
- Downloads/fetches the content of a SPNEGO secured URL
- A kerberos ticket should be already issued

author:
  - Adrian Fusco (@afuscoar)
  - Pablo Rodriguez (@pablintino)

options:
  url:
    description:
      - The URL to retrieve the content from
    required: True
    type: str
  verify_ssl:
    description:
      - Enables/disables using TLS to reach the URL
    required: False
    type: bool
    default: true
  dest:
    description:
      - Path to the destination file/dir where the content should be downloaded
      - If not provided the content won't be written into disk
    required: False
    type: str

"""

EXAMPLES = r"""
- name: Get some content
  url_request:
    url: "http://someurl.local/resource"
    dest: "{{ ansible_user_dir }}/content.raw"
    mode: "0644"
  register: _fetched_content

- name: Show base64 content
  debug:
    msg: "{{ _fetched_content.response_b64 }}"
"""

RETURN = r"""
status_code:
    description: HTTP response code
    type: int
    returned: returned request
content_type:
    description: HTTP response Content-Type header content
    type: str
    returned: returned request
headers:
    description: HTTP response headers
    type: dict
    returned: returned request
response_b64:
    description: Returned content base64 encoded
    type: str
    returned: successful request
response_json:
    description: Returned content as a dict
    type: str
    returned: successful request that returned application/json
path:
    description: Written file path
    type: str
    returned: successful request
"""

import base64
import os.path
import re

from ansible.module_utils.basic import AnsibleModule


try:
    from requests import get, head

    python_requests_installed = True
except ImportError:
    python_requests_installed = False
try:
    from requests_kerberos import HTTPKerberosAuth, OPTIONAL

    python_requests_kerberos_installed = True
except ImportError:
    python_requests_kerberos_installed = False


def _validate_auth_module(module, url, verify_ssl):
    if python_requests_kerberos_installed:
        # The module are loaded if requires, no need to validate if it's necessary or not
        return
    response = head(url=url, verify=verify_ssl, allow_redirects=True, timeout=30)
    # If the response in a 401 or 403 we need to authenticate
    if response.status_code in [401, 403]:
        # Kerberos module not present, fail
        module.fail_json(
            msg="requests_kerberos required for this module to authenticate against the given url"
        )


def main():
    module_args = {
        "url": {"type": "str", "required": True},
        "verify_ssl": {"type": "bool", "default": True},
        "dest": {"type": "str", "required": False},
    }

    result = {
        "changed": False,
    }

    module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=False, add_file_common_args=True
    )

    if not python_requests_installed:
        module.fail_json(msg="requests required for this module.")

    url = module.params["url"]
    verify_ssl = module.params["verify_ssl"]

    _validate_auth_module(module, url, verify_ssl)
    if python_requests_kerberos_installed:
        auth = HTTPKerberosAuth(mutual_authentication=OPTIONAL)
    else:
        auth = None

    try:
        response = get(url=url, auth=auth, verify=verify_ssl, allow_redirects=True)

        result["status_code"] = response.status_code
        result["headers"] = dict(response.headers)
        result["content_type"] = response.headers.get("Content-Type", None)

        if response.status_code < 200 or response.status_code >= 300:
            module.fail_json(
                msg=f"Error fetching the information {response.status_code}: {response.text}"
            )

        result["response_b64"] = base64.b64encode(response.content)
        if "application/json" in result["content_type"]:
            try:
                result["response_json"] = response.json()
            except ValueError as e:
                module.fail_json(msg=f"Error with the JSON response: {str(e)}")

        if "dest" in module.params:
            dest = module.params["dest"]
            if (
                os.path.exists(dest)
                and os.path.isdir(dest)
                and "content-disposition" in response.headers
            ):
                # Destination is a directory but the filename is available in Content-Disposition
                filename = re.findall(
                    "filename=(.+)", response.headers["content-disposition"]
                )
                dest = filename[0] if filename else None
            elif os.path.exists(dest) and os.path.isdir(dest):
                # Destination is a directory but we cannot guess the filename from Content-Disposition
                dest = None

            if not dest:
                # Reached if dest points to a directory and:
                #  - Content-Disposition not available
                #  - Cannot extract the filename part from the Content-Disposition header
                module.fail_json(
                    msg="Destination points to a directory and the filename cannot be retrieved from the response"
                )

            exists = os.path.exists(dest)
            original_sha1 = module.sha1(dest) if exists else None
            with open(dest, mode="wb") as file:
                file.write(response.content)
            file_args = module.load_file_common_arguments(module.params, path=dest)
            result["changed"] = (
                (not exists)
                or (module.sha1(dest) != original_sha1)
                or module.set_fs_attributes_if_different(file_args, result["changed"])
            )
            result["path"] = dest

    except Exception as e:
        module.fail_json(msg=f"Error fetching the information: {str(e)}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()
