#!/usr/bin/env python3

# core logic borrowed from https://github.com/openstack-k8s-operators/openstack-must-gather/blob/main/pyscripts/mask.py
# and modified to match our use-case
import argparse
import os
import re
import yaml
import sys
from typing import Dict, Optional, Any, Union

# files which are yaml but do not end with .yaml or .yml
ALLOWED_YAML_FILES = [
    "Standalone",
]
# dirs which we do not want to scan
EXCLUDED_DIRS = [
    "openstack-k8s-operators-openstack-must-gather",
    "tmp",
    "venv",
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


class SecretMask:

    def __init__(self, path: Optional[Any] = None) -> None:
        self.path: Union[Any, None] = path

    def mask(self) -> None:
        """
        Method responsible to begin masking on a provided
        log file. It checks for file type, and calls
        respective masking methods for that file.
        """
        if (
            self.path.endswith((tuple(["yaml", "yml"])))
            or os.path.basename(self.path).split(".")[0] in ALLOWED_YAML_FILES
        ):
            self._mask_yaml()

    def _process_list(self, lst: list) -> None:
        for item in lst:
            if isinstance(item, dict):
                self._apply_mask(item)
            elif isinstance(item, list):
                self._process_list(item)

    def _apply_regex(self, value: str) -> str:
        """
        For each string value passed as argument, try
        to match the pattern according to the provided
        regexes and mask any potential sensitive info.
        """
        for pattern in regexes:
            value = re.sub(pattern, r"\1{}".format(MASK_STR), value, flags=re.I)
        return value

    def _apply_mask(self, yaml_dict: Dict[str, Any]) -> None:
        """
        Check and mask value if key of dict matches
        with key_regex, else perform action on data
        type of value. Call _process_list if value
        is of type list, call _apply_regex for strings,
        recursively call _apply_mask in case value is
        of type dict.
        """
        for k, v in yaml_dict.items():
            if re.findall(key_regex, k):
                yaml_dict[k] = MASK_STR

            elif isinstance(v, str):
                yaml_dict[k] = self._apply_regex(v)

            elif isinstance(v, list):
                self._process_list(v)

            elif isinstance(v, dict):
                self._apply_mask(v)

    def _mask_yaml(self) -> None:
        """
        Method to handle masking of yaml files.
        Begin with reading yaml and storing in
        list (check _read_yaml for return type
        info), then process the list to mask
        secrets, and then write the encoded
        data back.
        """
        yaml_list = self._read_yaml()

        if not yaml_list:
            return
        # we are directly calling _process_list as
        # yaml.safe_load_all returns an Iterator of
        # dictionaries which we have converted into
        # a list (return type of _read_yaml)
        self._process_list(yaml_list)

        self._write_yaml(yaml_list)

    def _read_yaml(self) -> Optional[Union[list, None]]:
        """
        Read and Load the yaml file for
        processing. Using yaml.safe_load_all
        to handle all documents within a
        single yaml file stream. Return
        type (Iterator) is parsed to list
        to make in-place change easy.
        """
        try:
            assert self.path is not None
            with open(self.path, "r") as f:
                return list(yaml.safe_load_all(f))
        except (FileNotFoundError, yaml.YAMLError) as e:
            print(f"Error while reading YAML: {e}")
            # sys.exit(-1)
        return None

    def _write_yaml(self, encoded_secret: Any) -> None:
        """
        Re-write the processed yaml file in
        the same path.
        Writing will occur only if there are
        changes to the content.
        """
        try:
            assert self.path is not None
            if self._read_yaml() != encoded_secret:
                with open(self.path, "w") as f:
                    yaml.safe_dump_all(encoded_secret, f, default_flow_style=False)
        except (IOError, yaml.YAMLError) as e:
            print(f"Error while writing the masked file: {e}")


def crawl(path) -> None:
    """
    Crawler function which will crawl through the log directory
    and find eligible files for masking.
    """
    for root, _, files in os.walk(path, onerror=handle_error):
        if any(excluded in root for excluded in EXCLUDED_DIRS):
            continue

        for f in files:
            if re.search(excluded_file_ext_regex, f) is None:
                SecretMask(os.path.join(root, f)).mask()


def handle_error(e):
    print(f"Error processing file {e}")


def parse_opts(argv: list[str]) -> argparse.Namespace:
    """
    Utility for the main function: it provides a way to parse
    options and return the arguments.
    """
    parser = argparse.ArgumentParser(description="Parameters")
    parser.add_argument(
        "-p",
        "--path",
        metavar="PATH",
        help="Path of the file where the masking \
                        should be applied",
    )
    parser.add_argument(
        "-d",
        "--dir",
        metavar="DIR_PATH",
        help="Path of the directory where the masking \
                        should be applied",
    )
    opts = parser.parse_args(argv[1:])
    return opts


if __name__ == "__main__":
    # parse the provided options
    OPTS = parse_opts(sys.argv)

    if OPTS.dir is not None and os.path.exists(OPTS.dir):
        # craw through the provided directly and then
        # process eligible files individually
        crawl(OPTS.dir)

    if (
        OPTS.path is not None
        and os.path.exists(OPTS.path)
        and re.search(excluded_file_ext_regex, OPTS.path) is None
    ):
        SecretMask(OPTS.path).mask()
