#!/usr/bin/python3

__metaclass__ = type


from ansible.errors import AnsibleFilterTypeError
from ansible.plugins.filter.core import combine

import base64
import itertools
import typing
import yaml


from ansible.module_utils._text import to_text


class FilterModule:

    @staticmethod
    def __is_cm_manifest(content: typing.Dict[str, typing.Any], name=None):
        if content and len(content) == 1 and "data" in content:
            return True

        if ("kind" not in content or "metadata" not in content) or content[
            "kind"
        ] != "ConfigMap":
            return False

        metadata = content["metadata"]
        # Check if the ConfigMap is targeting local configuration only
        local_config_annotation = metadata.get("annotations", {}).get(
            "config.kubernetes.io/local-config", None
        )
        if local_config_annotation is not True or local_config_annotation != "true":
            return False

        return name is not None and metadata.get("name", None) == name

    @staticmethod
    def __create_tuple(content: typing.Dict[str, typing.Any]):
        metadata = content.get("metadata", {})
        return (
            content.get("kind"),
            metadata.get("name", ""),
            metadata.get("namespace", ""),
            content.get("apiVersion", ""),
        )

    @classmethod
    def __extract_kustomize_config_map(cls, data, name=None, base_extra_patches=None):
        if not isinstance(data, list):
            raise AnsibleFilterTypeError(
                "cifmw_gen_kustomize_values_b64_combine requires list of dicts, "
                f"got {type(data)}"
            )
        if name and not isinstance(name, str):
            raise AnsibleFilterTypeError(
                "cifmw_gen_kustomize_values_b64_combine requires the optional name "
                f"to be a string, got {type(name)}"
            )
        if base_extra_patches and not isinstance(name, list):
            raise AnsibleFilterTypeError(
                "cifmw_gen_kustomize_values_b64_combine requires the optional base_extra_patches "
                f"to be a list, got {type(name)}"
            )
        raw_payloads = [base64.b64decode(payload) for payload in data]
        decoded_payloads = list(
            itertools.chain.from_iterable(
                [
                    yaml.load_all(
                        str(to_text(raw, errors="surrogate_or_strict")), yaml.SafeLoader
                    )
                    for raw in raw_payloads
                ]
            )
        )

        cm_patches = []
        grouped_manifests = {}
        for manifest in (base_extra_patches or []) + decoded_payloads:
            if cls.__is_cm_manifest(manifest, name):
                cm_patches.append(manifest)
            else:
                key = cls.__create_tuple(manifest)
                if key not in grouped_manifests:
                    grouped_manifests[key] = []
                grouped_manifests[key].append(manifest)

        return [
            combine(cm_patches),
            [combine(extra_manifest) for extra_manifest in grouped_manifests.values()],
        ]

    def filters(self):
        return {
            "cifmw_gen_kustomize_values_b64_combine": self.__extract_kustomize_config_map,
        }
