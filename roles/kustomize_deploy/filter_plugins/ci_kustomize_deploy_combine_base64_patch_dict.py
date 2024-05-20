#!/usr/bin/env python3

__metaclass__ = type

import typing


DOCUMENTATION = """
  name: ci_kustomize_deploy_build_base64_patch_dict
  short_description: Creates a dictionary with a list of base64 patches as the nested element.
  options:
    _input:
      description:
        - The list of dicts to merge together.
      type: str
      required: true
"""

from ansible.errors import AnsibleFilterTypeError


class FilterModule:

    @staticmethod
    def __patch(
        base_content: typing.Dict[str, typing.Dict],
        patch: typing.Dict[str, typing.Dict],
    ):
        for stage_id, values in patch.items():
            stage_values = base_content.get(stage_id, {})
            base_content[stage_id] = stage_values
            for values_id, raw_content in values.items():
                content = (
                    raw_content if isinstance(raw_content, list) else [raw_content]
                )
                if values_id not in stage_values:
                    stage_values[values_id] = []
                stage_values[values_id].extend(content)

    @classmethod
    def __build_base64_patch_dict(
        cls, data: typing.List[typing.Dict[str, typing.Dict]]
    ) -> typing.Dict[str, typing.Any]:
        if not isinstance(data, list):
            raise AnsibleFilterTypeError(
                "ci_kustomize_deploy_combine_base64_patch_dict requires data to be a list of dicts"
            )

        result = {}
        for b64_patch_dict in data:
            cls.__patch(result, b64_patch_dict)
        return result

    def filters(self):
        return {
            "ci_kustomize_deploy_combine_base64_patch_dict": self.__build_base64_patch_dict,
        }
