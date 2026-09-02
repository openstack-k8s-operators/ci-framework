#!/usr/bin/python3

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
    name: from_ini
    short_description: Read a key from INI-formatted text
    description:
      - Parse INI content with Python's C(configparser) using C(read_file),
        which is safe on Python 3.12 (C(readfp) was removed).
      - Use this instead of the C(ansible.builtin.ini) lookup when the
        controller Python is 3.12+ or when the INI text is already in a
        variable (for example after C(slurp)).
    options:
        _input:
            description: INI document as a string (or bytes).
            type: str
            required: true
        key:
            description: Option name to return.
            type: str
            required: true
        section:
            description: Section that contains the key.
            type: str
            default: global
        default:
            description: Value to return when the section or key is missing.
            type: str
            default: ""
"""

EXAMPLES = """
    - name: Read public_network from a rendered Ceph conf
      ansible.builtin.set_fact:
        public_network: >-
          {{
            lookup('ansible.builtin.file', conf_path)
            | cifmw.general.from_ini('public_network')
          }}

    - name: Read fsid from slurped ceph.conf
      ansible.builtin.set_fact:
        ceph_fsid: >-
          {{ (cephconf.content | b64decode) | cifmw.general.from_ini('fsid') }}
"""

RETURN = """
  _value:
    description: The option value, or I(default) when the key is absent.
    type: str
"""

import configparser
import io

from ansible.errors import AnsibleFilterError, AnsibleFilterTypeError
from ansible.module_utils._text import to_native, to_text


class FilterModule:

    @staticmethod
    def __from_ini(content, key, section="global", default=""):
        if not isinstance(content, (str, bytes)):
            raise AnsibleFilterTypeError(
                "from_ini requires INI content as a string, got %s" % type(content)
            )
        if not isinstance(key, str) or not key:
            raise AnsibleFilterTypeError(
                "from_ini requires a non-empty key name as a string, got %s" % type(key)
            )

        parser = configparser.ConfigParser(interpolation=None)
        try:
            parser.read_file(io.StringIO(to_text(content)))
        except configparser.Error as exc:
            raise AnsibleFilterError(
                "from_ini - failed to parse INI content: %s" % to_native(exc),
                orig_exc=exc,
            ) from exc

        if not parser.has_section(section) or not parser.has_option(section, key):
            return default
        return parser.get(section, key)

    def filters(self):
        return {
            "from_ini": self.__from_ini,
        }
