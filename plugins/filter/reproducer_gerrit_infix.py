#!/usr/bin/python3

__metaclass__ = type

DOCUMENTATION = """
    name: reproducer_gerrit_infix
    short_description: Maps a hostname to the infix needed for cloning a repo
    for that hostname.
    description:
        - Maps a hostname to the infix needed for cloning a repo from that
          hostname.Some gerrit instances add an infix like "gerrit", or "r"
          to the repo clone url.
    options:
        _input:
            description:
                - repo hostname where we want to clone from.
            type: str
            required: true
"""

EXAMPLES = """
    - name: Get infix to clone repo from rdo gerrit
      ansible.builtin.set_fact:
        gerrit_infix: >-
            {{
              "review.rdoproject.org" | reproducer_gerrit_infix
            }}
"""

RETURN = """
  _value:
    description: The infix to add to the url to clone the repo.
    type: str
    sample:
      "gerrit/"

"""

from ansible.errors import AnsibleFilterTypeError


class FilterModule:
    @classmethod
    def __map_hostname_infix(cls, hostname):
        if not isinstance(hostname, str):
            raise AnsibleFilterTypeError(
                f"reproducer_gerrit_infix requires a str, got {type(hostname)}"
            )
        if "rdoproject" in hostname:
            return "r/"
        elif "code.eng" in hostname:
            return "gerrit/"
        return ""

    def filters(self):
        return {
            "reproducer_gerrit_infix": self.__map_hostname_infix,
        }
