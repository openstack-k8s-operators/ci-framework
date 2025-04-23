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
import yaml
from typing import Dict, Optional, Any, Union
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native

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

# general and connection regexes are used to match the pattern that should  ̰be
# applied to both Protect keys and connection keys, which is the same thing
# done in SoS reports
gen_regex = r"(\w*(%s)\s*=\s*)(.*)" % "|".join(PROTECT_KEYS)
con_regex = r"((%s)\s*://)(\w*):(.*)(@(.*))" % "|".join(CONNECTION_KEYS)

# regex of excluded file extensions
excluded_file_ext_regex = r"(^.*(%s).*)" % "|".join(EXCLUDED_FILE_EXT)

# regex of keys which will be checked against every key
# as in yaml files, we have data in format <key> = <value>
# if a key is sensitive, it will be found using this regex
key_regex = r"(%s)\d*$" % "|".join(PROTECT_KEYS)
regexes = [gen_regex, con_regex]


def handle_walk_errors(e):
    raise e


def crawl(module, path) -> bool:
    """
    Crawler function which will crawl through the log directory
    and find eligible files for masking.
    """
    changed = False
    for root, _, files in os.walk(path, onerror=handle_walk_errors):
        if any(excluded in root.split("/") for excluded in EXCLUDED_DIRS):
            continue

        for f in files:
            if not re.search(excluded_file_ext_regex, f):
                file_changed = mask(module, os.path.join(root, f))
                # even if one file is masked, the final result will be True
                if file_changed:
                    changed = True
    return changed


def mask(module, path: str) -> bool:
    """
    Method responsible to begin masking on a provided
    log file. It checks for file type, and calls
    respective masking methods for that file.
    """
    changed = False
    if (
        path.endswith((tuple(["yaml", "yml"])))
        or os.path.basename(path).split(".")[0] in ALLOWED_YAML_FILES
    ):
        changed = mask_yaml(module, path)
    return changed


def process_list(lst: list) -> None:
    """
    For each list we get in our yaml dict,
    this method will check the type of item.
    If the item in list is dict, it will call
    apply_mask method to process it, else if
    we get nested list, process_list will be
    recursively called.
    We are not checking for string as secrets
    are mainly in form <key>: <value> in dict,
    not in list as item.
    """
    for item in lst:
        if isinstance(item, dict):
            apply_mask(item)
        elif isinstance(item, list):
            process_list(item)


def apply_regex(value: str) -> str:
    """
    For each string value passed as argument, try
    to match the pattern according to the provided
    regexes and mask any potential sensitive info.
    """
    for pattern in regexes:
        value = re.sub(pattern, r"\1{}".format(MASK_STR), value, flags=re.I)
    return value


def apply_mask(yaml_dict: Dict[str, Any]) -> None:
    """
    Check and mask value if key of dict matches
    with key_regex, else perform action on data
    type of value. Call _process_list if value
    is of type list, call _apply_regex for strings,
    recursively call _apply_mask in case value is
    of type dict.
    """
    for k, v in yaml_dict.items():
        if re.findall(key_regex, str(k)):
            yaml_dict[k] = MASK_STR

        elif isinstance(v, str):
            yaml_dict[k] = apply_regex(v)

        elif isinstance(v, list):
            process_list(v)

        elif isinstance(v, dict):
            apply_mask(v)


def mask_yaml(module, path) -> bool:
    """
    Method to handle masking of yaml files.
    Begin with reading yaml and storing in
    list (check _read_yaml for return type
    info), then process the list to mask
    secrets, and then write the encoded
    data back.
    """
    yaml_content = read_yaml(module, path)
    changed = False
    if not yaml_content:
        return changed
    # we are directly calling _process_list as
    # yaml.safe_load_all returns an Iterator of
    # dictionaries which we have converted into
    # a list (return type of _read_yaml)
    process_list(yaml_content)

    changed = write_yaml(module, path, yaml_content)
    return changed


def read_yaml(module, file_path: str) -> Optional[Union[list, None]]:
    """
    Read and Load the yaml file for
    processing. Using yaml.safe_load_all
    to handle all documents within a
    single yaml file stream. Return
    type (Iterator) is parsed to list
    to make in-place change easy.
    """
    try:
        assert file_path is not None
        with open(file_path, "r") as f:
            return list(yaml.safe_load_all(f))
    except (FileNotFoundError, yaml.YAMLError) as e:
        module.warn("Error opening file: %s" % e)
    return


def write_yaml(module, path, encoded_secret: Any) -> bool:
    """
    Re-write the processed yaml file in
    the same path.
    Writing will occur only if there are
    changes to the content.
    """
    changed = False
    try:
        assert path is not None
        if read_yaml(module, path) != encoded_secret:
            with open(path, "w") as f:
                yaml.safe_dump_all(encoded_secret, f, default_flow_style=False)
                changed = True
    except (IOError, yaml.YAMLError) as e:
        module.fail_json(
            msg=f"Error writing to file: {to_native(e, nonstring='simplerepr')}",
            path=path,
        )
    return changed


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
        module.fail_json(msg=f"Provided path doesn't exist", path=path)
    if os.path.isdir(path) != isdir:
        module.fail_json(msg=f"Value of isdir/path is incorrect. Please check it")

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
