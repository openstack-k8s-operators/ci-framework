#!/usr/bin/env python3

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
    name: to_nice_yaml_all
    short_description: Convert list of variables to a single YAML string
    description:
    - Converts an Ansible variable into a YAML string representation.
    - This filter functions as a wrapper to the L(Python PyYAML library, https://pypi.org/project/PyYAML/)'s C(yaml.dump) function.
    - Ansible internally auto-converts YAML strings into variable structures so this plugin is used to force it into a YAML string.
    options:
        _input:
            description: A variable or expression that returns a data structure.
            type: raw
            required: true
        indent:
            description: Number of spaces to indent Python structures, mainly used for display to humans.
            type: integer
"""

EXAMPLES = """
    # dump variable in a template to create a YAML document
    {{ github_workflow | to_nice_yaml_all }}
"""

RETURN = """
  _value:
    description: The YAML serialized string representing the variable structure inputted.
    type: string
"""

import yaml

from ansible.module_utils._text import to_native, to_text
from ansible.errors import AnsibleFilterError
from ansible.parsing.yaml.dumper import AnsibleDumper


class FilterModule:

    @staticmethod
    def __to_nice_yaml_all(a, indent=4, *args, **kw):
        """Make verbose, human readable multi manifest yaml"""
        try:
            transformed = to_text(
                yaml.dump_all(
                    a,
                    Dumper=AnsibleDumper,
                    indent=indent,
                    allow_unicode=True,
                    default_flow_style=False,
                    **kw
                )
            )
        except Exception as e:
            raise AnsibleFilterError("to_nice_yaml_all - %s" % to_native(e), orig_exc=e)
        return to_text(transformed)

    def filters(self):
        return {
            "to_nice_yaml_all": self.__to_nice_yaml_all,
        }
