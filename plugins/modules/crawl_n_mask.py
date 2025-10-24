#!/usr/bin/python

# Copyright Red Hat, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# core logic borrowed from https://github.com/openstack-k8s-operators/openstack-must-gather/blob/main/pyscripts/mask.py
# and modified to a module according to our requirement
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: crawl_n_mask

short_description: This module mask secrets in yaml files/dirs

version_added: "1.0.0"

description:
    - This module crawls over a directory (default) and find yaml files which may have secrets in it, and proceeds with masking it.
    - If you pass a yaml file, it will directly check and mask secret in it.
    - If you pass a directory, it will crawl the directory and find eligible files to mask.

options:
    path:
        description:
            - This is the target file/dir you want to mask.
        required: true
        type: path
    isdir:
        description:
            - Tells if the path is dir or not.
            - Supported options are True and False.
            - Set value to False if path is file, else True.
            - Defaults to False.
        required: false
        default: False
        type: bool

author:
    - Amartya Sinha (@amartyasinha)
"""

EXAMPLES = r"""
- name: Mask secrets in all yaml files within /home/zuul/logs
  crawl_n_mask:
    path: /home/zuul/logs
    isdir: True

- name: Mask my_secrets.yaml
  crawl_n_mask:
    path: /home/zuul/logs/my_secrets.yaml
"""

RETURN = r"""
success:
    description: Status of the execution
    type: bool
    returned: always
    sample: true
"""

import os
import re
import pathlib

from ansible.module_utils.basic import AnsibleModule

# ### To debug ###
# #  playbook:
#    ---
#    - name: test
#      hosts: localhost
#      tasks:
#        - name: Mask secrets in yaml log files
#          timeout: 3600
#          crawl_n_mask:
#            path: "/tmp/logs/"
#            isdir: true
#
# # args.json:
#   {"ANSIBLE_MODULE_ARGS": {"path": "/tmp/logs/", "isdir": true}}
#
# # execute:
#   python3 plugins/modules/crawl_n_mask.py ./args.json
################

# files which are yaml but do not end with .yaml or .yml
ALLOWED_YAML_FILES = [
    "Standalone",
]
# dirs which we do not want to scan
EXCLUDED_DIRS = [
    "openstack-k8s-operators-openstack-must-gather",
    "tmp",
    "venv",
    ".github",
]
# file extensions which we do not want to process
EXCLUDED_FILE_EXT = [
    ".py",
    ".html",
    ".DS_Store",
    ".tar.gz",
    ".zip",
    ".j2",
]
# keys in files whose values need to be masked
PROTECT_KEYS = [
    "literals",
    "PASSWORD",
    "Password",
    "password",
    "_pwd",
    "_PWD",
    "Token",
    "Secret",
    "secret",
    "SECRET",
    "Authkey",
    "authkey",
    "private_key",
    "privatekey",
    "Passphrase",
    "passphrase",
    "PASSPHRASE",
    "encryption_key",
    "ENCRYPTION_KEY",
    "HeatAuthEncryptionKey",
    "oc_login_command",
    "METADATA_SHARED_SECRET",
    "KEYSTONE_FEDERATION_CLIENT_SECRET",
    "rabbit",
    "database_connection",
    "slave_connection",
    "sql_connection",
    "cifmw_openshift_login_password",
    "cifmw_openshift_login_token",
    "BarbicanSimpleCryptoKEK",
    "OctaviaHeartbeatKey",
    "server-ca-passphrase",
    "KeystoneFernetKeys",
    "KeystoneFernetKey",
    "KeystoneCredential",
    "DesignateRndcKey",
    "CephRgwKey",
    "CephClusterFSID",
    "CephClientKey",
    "BarbicanSimpleCryptoKek",
    "HashSuffix",
    "RabbitCookie",
    "erlang_cookie",
    "ClientKey",
    "swift_store_key",
    "secret_key",
    "heartbeat_key",
    "fernet_keys",
    "sshkey",
    "keytab_base64",
]
# connection keys which may be part of the value itself
CONNECTION_KEYS = [
    "rabbit",
    "database_connection",
    "slave_connection",
    "sql_connection",
]
# Masking string
MASK_STR = "**********"

# regex of excluded file extensions
excluded_file_ext_regex = r"(^.*(%s).*)" % "|".join(EXCLUDED_FILE_EXT)


def handle_walk_errors(e):
    raise e


def crawl(module, path) -> bool:
    """
    Crawler function which will crawl through the log directory
    and find eligible files for masking.
    """
    changed = False
    base_path = os.path.normpath(path)
    for root, _, files in os.walk(base_path, onerror=handle_walk_errors):
        # Get relative path from our base path
        rel_path = os.path.relpath(root, base_path)

        # Check if any parent directory (not the root) is excluded
        if any(part in EXCLUDED_DIRS for part in rel_path.split(os.sep)):
            continue
        for f in files:
            if not re.search(excluded_file_ext_regex, f):
                if mask(module, os.path.join(root, f)):
                    # even if one file is masked, the final result will be True
                    changed = True
    return changed


def _get_masked_string(value):
    if len(value) <= 4:
        return value[:2] + MASK_STR
    return value[:2] + MASK_STR + value[-2:]


def format_masked(prefix, value, suffix, extension):
    return (
        f"{prefix}'{value}'{suffix}"
        if extension == "yaml"
        else f'{prefix}"{value}"{suffix}'
    )


def partial_mask(value, extension):
    """
    Check length of the string. If it is too long, take 2 chars
    from beginning, then add mask string and add 2 chars from the
    end.
    If value is short, take just 2 chars and add mask string
    """
    if not value.strip():
        return
    if "'" in value or extension == "json":
        parsed_value = value.split('"') if extension == "json" else value.split("'")
        if len(parsed_value) > 2 and parsed_value[1] != "":
            prefix = parsed_value[0]
            value = _get_masked_string(parsed_value[1])
            suffix = parsed_value[2]
            return format_masked(prefix, value, suffix, extension)
    else:
        match = re.match(r"^(\s*)(.*?)(\n?)$", value)
        if match:
            parts = list(match.groups())
            prefix = parts[0]
            value = _get_masked_string(parts[1])
            suffix = parts[2]
            return format_masked(prefix, value, suffix, extension)


def mask(module, path: str) -> bool:
    """
    Function responsible to begin masking on a provided
    log file. It checks for file type, and calls
    respective masking methods for that file.
    """
    changed = False
    if path.endswith("json"):
        changed = mask_file(module, path, "json")
    elif (
        path.endswith((tuple(["yaml", "yml"])))
        or os.path.basename(path).split(".")[0] in ALLOWED_YAML_FILES
    ):
        changed = mask_file(module, path, "yaml")
    return changed


def mask_by_extension(infile, outfile, changed, extension) -> bool:
    """
    Read the file, search for colon (':'), take value and
    mask sensitive data
    """
    for line in infile:
        # Skip lines without colon
        if ":" not in line:
            outfile.write(line)
            continue
        key, sep, value = line.partition(":")
        comparable_key = key.strip().replace('"', "")
        masked_value = value
        for word in PROTECT_KEYS:
            if comparable_key == word.strip():
                masked = partial_mask(value, extension)
                if not masked:
                    continue
                masked_value = masked_value.replace(value, masked)
                changed = True

        outfile.write(f"{key}{sep}{masked_value}")
    return changed


def replace_file(temp_path, file_path, changed):
    if changed:
        temp_path.replace(file_path)
    else:
        temp_path.unlink(missing_ok=True)


def mask_file(module, path, extension) -> bool:
    """
    Create temporary file, replace sensitive string with masked,
    then replace the tmp file with original.
    """

    changed = False
    file_path = pathlib.Path(path)
    temp_path = file_path.with_suffix(".tmp")
    try:
        with file_path.open("r", encoding="utf-8") as infile:
            with temp_path.open("w", encoding="utf-8") as outfile:
                changed = mask_by_extension(infile, outfile, changed, extension)
                replace_file(temp_path, file_path, changed)
                return changed
    except Exception as e:
        print(f"An unexpected error occurred on masking file {file_path}: {e}")


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        path=dict(type="path", required=True), isdir=dict(type="bool", default=False)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    changed = False
    result = dict(changed=changed)

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    params = module.params
    path = params["path"]
    isdir = params["isdir"]

    # validate if the path exists and no wrong value of isdir and path is
    # provided
    if not os.path.exists(path):
        module.fail_json(msg="Provided path doesn't exist", path=path)
    if os.path.isdir(path) != isdir:
        module.fail_json(msg="Value of isdir/path is incorrect. Please check it")

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    if isdir:
        # craw through the provided directly and then
        # process eligible files individually
        changed = crawl(module, path)

    if not isdir and not re.search(excluded_file_ext_regex, path):
        changed = mask(module, path)

    result.update(changed=changed)
    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


if __name__ == "__main__":
    run_module()
