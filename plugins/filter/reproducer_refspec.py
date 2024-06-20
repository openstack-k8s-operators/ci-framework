#!/usr/bin/python3

__metaclass__ = type

DOCUMENTATION = """
    name: reproducer_refspec
    short_description: Maps repo information from zuul to a refspec.
    description:
        - Maps repo information from zuul to a refspec that should be
        used for pulling it with git.
    options:
        _input:
            description:
                - repo information from zuul variables.
            type: dict
            required: true
"""

EXAMPLES = """
    - name: Get refspec to clone repo from rdo gerrit
      ansible.builtin.set_fact:
        change_refspec: >-
            {{
              repo | reproducer_refspec
            }}
"""

RETURN = """
  _value:
    description: The refspec to pull the change.
    type: str
    sample:
      "refs/changes/15/449415/5"

"""

from ansible.errors import AnsibleFilterError, AnsibleFilterTypeError


class FilterModule:
    @classmethod
    def __map_repo_refspec(cls, repo):
        if not isinstance(repo, dict):
            raise AnsibleFilterTypeError(
                f"reproducer_refspec requires a dict, got {type(repo)}"
            )
        if "change" not in repo:
            # handle case pointing to main/master, e.g. a periodic job
            return ""
        change = repo["change"]
        if "project" not in repo:
            raise AnsibleFilterError(
                "repo information does not contain 'project' field"
            )
        if "canonical_hostname" not in repo["project"]:
            raise AnsibleFilterError(
                "repo information does not contain 'canonical_hostname' field"
            )
        hostname = repo["project"]["canonical_hostname"]
        if "rdoproject" in hostname or "code.eng" in hostname:
            if "patchset" not in repo:
                raise AnsibleFilterError(
                    "repo information does not contain 'patchset' field"
                )
            patchset = repo["patchset"]
            # changes coming from gerrit
            return f"refs/changes/{change[-2:]}/{change}/{patchset}"
        elif "gitlab" in hostname:
            return f"merge-requests/{change}/head"
        else:
            # changes coming from github
            return f"pull/{change}/head"

    def filters(self):
        return {
            "reproducer_refspec": self.__map_repo_refspec,
        }
