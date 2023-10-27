#!/usr/bin/env python3

# Copyright Red Hat, Inc.
# Apache License Version 2.0 (see LICENSE)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
action: ci_kustomize

short_description: Applies a set of k8s Kustomizations to a set of manifests

description:
- Allows applying a set of Kustomizations to a given set of manifests using
  the kustomize or oc tools.
- kustomize or oc should be discoverable by in the PATH.
- This modules takes a set of manifest files pointed by I(target_path) and
  applies to them the set of kustomizations, if available.
- The kustomization result is always saved in a single file and passed to
  the caller in the O(result) field if success.
- Kustomizations can be passed by file and/or by I(kustomizations), they get
  applied one by one.
- Filesystem Kustomizations are searched by default in the I(target_path), but
  more search paths can be added by passing I(kustomizations_paths).
- Filesystem Kustomizations are applied by strictly alphabetical order.
- Kustomizations passed by I(kustomizations) are applied by apparition order.
- Kustomizations passed by I(kustomizations) are applied after the ones from
  filesystem by default, if the contrary is not told so by
  I(kustomization_files_goes_first).
- I(kustomizations) accepts a wide range of input types. More precisly: plain
  string, list of strings, dict with a single kustomization or list of dicts.
- By contraints of the kustomize tool there is no way to apply the given
  set of kustomizations to a set of more than one manifests, so, to avoid
  diverging the behaviour between single kustomization runs and the rest
  this module takes both sets of inputs and translates the result into
  a single file.

options:
  target_path:
    description:
    - Path to the directory where the manifest exists or the specific manifest
      to kustomize.
    type: str
    required: true
  kustomizations:
    description:
    - Kustomizations to apply in list of dicts, list of strings, dict or
      string format.
    type: iterable
  output_path:
    description:
    - The alternative path were Kustomization result should be copied.
    - If not given I(target_path) is used if it points to a file.
    - If I(target_path) points to a file 'cifmw-kustomization-result.yaml'
      in I(target_path) will be used.
    type: str
  kustomizations_paths:
    description:
    - Additional paths where Kustomizations should be searched.
    type: list
    elements: str
  preserve_workspace:
    description:
    - If true, the workspace is not deleted if success.
    - If failure this option is ignored and the workspace is preserved.
    type: bool
    default: false
  kustomization_files_goes_first:
    description:
    - If true, Kustomizations given by I(kustomizations) are applied before
      the ones from filesystem.
    type: bool
    default: true
  sort_ascending:
    description:
    - If true, file Kustomizations are ordered by ascending order of the file
      name. Descnding orther oherwise.
      the ones from filesystem.
    type: bool
    default: true
  skip_regexes:
    description:
    - List of regexes to filter out the discovered manifests and kustomizations.
    type: list
    elements: str
    default: []
  include_regexes:
    description:
    - List of regexes to filter in the discovered manifests and kustomizations.
    type: list
    elements: str
    default: []
"""

EXAMPLES = r"""
# Apply the kustomizations in `/home/user/source/k8s-manifets-dir` to the
# `target_path` manifest and output the result in `output_pat`
- name: Apply the file and variables kustomizations to multiple CRs
  ci_kustomize:
    target_path: /home/user/source/k8s-manifets-dir/manifest.yaml
    output_path: /home/user/source/k8s-manifets-dir/out.yaml

# Apply the given kustomizations in the kustomizations variable and in
# `/home/user/source/k8s-manifets-dir` and `extra_dir` dirs to the
# manifests available in the `target_path` dir
- name: Apply the file and variables kustomizations to multiple CRs
  ci_kustomize:
    target_path: /home/user/source/k8s-manifets-dir
    kustomizations:
      - apiVersion: kustomize.config.k8s.io/v1beta1
        kind: Kustomization
        patches:
          - patch: |-
              - op: replace
                path: /metadata/labels/release
                value: "1.2.3.4"
            target:
              kind: Deployment
      - |-
        ---
        apiVersion: kustomize.config.k8s.io/v1beta1
        kind: Kustomization
        patches:
        -   patch: |-
              - op: add
                path: /metadata/labels/app
                value: "my-app"
            target:
              kind: Deployment
        -   patch: |-
              - op: add
                path: /metadata/labels/app
                value: "my-app"
            target:
              kind: ConfigMap
        ---
        apiVersion: kustomize.config.k8s.io/v1beta1
        kind: Kustomization
        patches:
        -   patch: |-
              - op: add
                path: /metadata/annotations/imageregistry
                value: "https://hub.docker.com/"
            target:
              kind: Deployment
    kustomizations_paths:
      - /home/user/source/prod-kustomizations
"""

RETURN = r"""
count:
    description: Total number of Kustomizations applied
    returned: success
    type: int
    sample: 10
kustomizations_paths:
  description: Set of discovered and applied Kustomization files
  returned: success
  type: list
  sample:
  - /home/user/source/k8s/kustomization1.yaml
  - /home/user/source/k8s/kustomization.yml
output_path:
  description: Path to the result of the Kustomization
  returned: success
  type: str
  sample: /home/user/source/k8s/deployment-manifest.yaml
result:
  description: A list of the resulting Kustomized manifests.
  returned: success
  sample:
    - apiVersion: v1
      kind: ConfigMap
      metadata:
        name: testing-cm
      data:
        test1.properties: |
          test-var=test-value
    - apiVersion: v1
      kind: Secret
      metadata:
        name: testing-secret
      data:
        .secret-file: dmFsdWUtMg0KDQo=
"""

import fnmatch
import functools
import hashlib
import os
import re
import shutil
import subprocess
import typing


import dataclasses
import pathlib
import yaml


from ansible.plugins.action import ActionBase
from ansible.parsing.yaml.dumper import AnsibleDumper


@dataclasses.dataclass
class CifmwKustomizeResult:
    count: int
    kustomizations_paths: typing.List[str]
    output_path: str
    result: typing.List[typing.Dict[typing.Dict, typing.Any]]
    changed: bool


class CifmwKustomizeException(Exception):
    def __init__(self, error):
        super().__init__(error)
        self.error = str(error)

    def to_dict(self):
        return {"error": self.error}


class CifmwKustomizeArgsValidationException(CifmwKustomizeException):
    def __init__(self, error, argument, value=None):
        super().__init__(error)
        self.argument = argument
        self.value = value

    def to_dict(self):
        val = {
            "argument": self.argument,
        }

        if self.value:
            val["value"] = self.value

        return {**val, **(super().to_dict())}


class CifmwKustomizeContentValidationException(CifmwKustomizeException):
    def __init__(self, msg: str, kustomization_content=None):
        super().__init__(msg)
        self.kustomization_content = self.__safe_dump_content(kustomization_content)

    @staticmethod
    def __safe_dump_content(kustomization_content):
        if isinstance(kustomization_content, str):
            return kustomization_content

        try:
            # If a kustomization failed cause some validation
            # safely handle it as a string
            to_dump_content = (
                [kustomization_content]
                if isinstance(kustomization_content, dict)
                else kustomization_content
            )
            return yaml.dump_all(to_dump_content) if to_dump_content else None

        except yaml.YAMLError:
            return str(kustomization_content)

    def to_dict(self):
        val = {
            "kustomization": self.kustomization_content,
        }
        return {**val, **(super().to_dict())}


class CifmwKustomizeApplyKustomizationException(CifmwKustomizeException):
    def __init__(
        self,
        msg: str,
        details: str,
        kustomization: typing.Dict[str, typing.Any],
        kustomization_path,
    ):
        # Errors from kustomize are prefixed by "Error:" Get rid off that
        super().__init__(re.sub(r"(?is)^error\s?:", "", msg).strip())
        self.details = details
        self.kustomization = kustomization
        self.kustomization_path = str(
            kustomization_path.absolute()
            if isinstance(kustomization_path, pathlib.Path)
            else kustomization_path
        )

    def to_dict(self):
        val = {
            "details": self.details,
            "kustomization": self.kustomization,
            "kustomization_path": self.kustomization_path,
        }
        return {**val, **(super().to_dict())}


def sha1_file(file_path: typing.Union[str, os.PathLike]) -> str:
    sha1 = hashlib.sha1()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()


class CifmwKustomizeWrapper:
    __CI_KUSTOMIZE_CMD_OPTS = [".", "-o"]
    __CI_KUSTOMIZE_TOOLS_OPTS = {"kustomize": ["build"], "oc": ["kustomize"]}
    __CI_KUSTOMIZE_WORKSPACE_DIR_NAME = "cifmw-kustomize-workspace"
    __CI_KUSTOMIZE_FILES_GLOB_EXPRESSIONS = ["*.yaml", "*.yml"]
    __CI_KUSTOMIZE_FILE_API_VERSION = "kustomize.config.k8s.io"
    __CI_KUSTOMIZE_KIND_FIELD_NAME = "kind"
    __CI_KUSTOMIZE_API_VERSION_FIELD_NAME = "apiVersion"
    __CI_KUSTOMIZE_FILE_KIND = "Kustomization"
    __CI_KUSTOMIZE_DEFAULT_RESULT_FILE_NAME = "cifmw-kustomization-result.yaml"
    __CI_KUSTOMIZE_ENCODING = "utf-8"

    def __init__(
        self,
        target_path: typing.Union[str, os.PathLike],
        kustomizations: typing.Union[
            str, typing.Dict, typing.List[typing.Union[str, typing.Dict]]
        ] = None,
        kustomizations_paths: typing.List[typing.Union[str, os.PathLike]] = None,
        output_path: typing.Union[str, os.PathLike] = None,
        kustomization_files_goes_first: bool = True,
        tools_search_path: str = None,
        preserve_workspace: bool = False,
        sort_ascending: bool = True,
        skip_regexes: typing.List[str] = None,
        include_regexes: typing.List[str] = None,
    ):
        self.__validate_inputs(target_path, output_path, kustomizations_paths)

        self.target_path = pathlib.Path(target_path)
        target_base_path = (
            self.target_path.parent if self.target_path.is_file() else self.target_path
        )

        if output_path:
            self.output_path = pathlib.Path(output_path)
        elif self.target_path.is_file():
            self.output_path = self.target_path
        else:
            self.output_path = self.target_path.joinpath(
                self.__CI_KUSTOMIZE_DEFAULT_RESULT_FILE_NAME
            )

        self.__workspace_dir = target_base_path.joinpath(
            self.__CI_KUSTOMIZE_WORKSPACE_DIR_NAME
        )
        self.__target_workspace_file = self.__workspace_dir.joinpath(
            self.__CI_KUSTOMIZE_DEFAULT_RESULT_FILE_NAME
        )
        self.__kustomization_scan_paths = [target_base_path] + [
            pathlib.Path(path) for path in (kustomizations_paths or [])
        ]
        self.__kustomization_files_goes_first = kustomization_files_goes_first
        self.__preserve_workspace = preserve_workspace
        self.__sort_ascending = sort_ascending
        self.__skip_regexes = skip_regexes or []
        self.__include_regexes = include_regexes or []
        self.__input_kustomizations = self.__parse_kustomizations_input(kustomizations)
        self.__kustomize_cmd = self.__create_kustomize_build_command(
            self.__target_workspace_file, tools_search_path=tools_search_path
        )

    def __enter__(self):
        if self.__workspace_dir.exists():
            shutil.rmtree(self.__workspace_dir)
        self.__workspace_dir.mkdir()

        return self

    def __exit__(self, exc_type, _, __):
        if not (exc_type or self.__preserve_workspace):
            shutil.rmtree(self.__workspace_dir)

    @staticmethod
    def __validate_inputs(target_path, output_path, kustomizations_paths):
        if not target_path:
            raise CifmwKustomizeArgsValidationException(
                "target path is mandatory", "target_path"
            )

        if not os.path.exists(target_path):
            raise CifmwKustomizeArgsValidationException(
                "path does not exist",
                "target_path",
                value=target_path,
            )

        output_path = pathlib.Path(output_path) if output_path else None
        if output_path and output_path.exists() and output_path.is_dir():
            raise CifmwKustomizeArgsValidationException(
                "output file cannot point to a directory",
                "output_path",
                value=str(output_path.absolute()),
            )

        if kustomizations_paths and (
            (not isinstance(kustomizations_paths, list))
            or (
                not all(
                    (isinstance(path, str) or isinstance(path, pathlib.Path))
                    for path in kustomizations_paths
                )
            )
        ):
            raise CifmwKustomizeArgsValidationException(
                "kustomizations_paths should be a list of paths",
                "kustomizations_paths",
                value=kustomizations_paths,
            )

    def __copy_input_to_workspace(self):
        if self.target_path.is_dir():
            manifests_contents = self.__get_manifests_paths_from_dir_candidates(
                self.target_path,
                skip_paths=[self.output_path],
                skip_regexes=self.__skip_regexes,
                include_regexes=self.__include_regexes,
            )
            # Fetch all the individual manifests from the target dir and dump
            # them into a single file
            with self.__target_workspace_file.open(
                mode="w", encoding=self.__CI_KUSTOMIZE_ENCODING
            ) as outfile:
                combined_manifest_list = functools.reduce(
                    lambda x, y: x + y,
                    (cnt for cnt in manifests_contents.values()),
                    [],
                )
                yaml.dump_all(combined_manifest_list, outfile)
        else:
            shutil.copy(self.target_path, self.__target_workspace_file)

    @classmethod
    def __create_kustomize_build_command(
        cls, target_path, tools_search_path=None
    ) -> typing.List[str]:
        kustomize_cmd = [cls.__find_kustomize_tool(tools_search_path)]
        tool_name = os.path.basename(kustomize_cmd[0])
        if tool_name in cls.__CI_KUSTOMIZE_TOOLS_OPTS:
            kustomize_cmd.extend(cls.__CI_KUSTOMIZE_TOOLS_OPTS[tool_name])

        kustomize_cmd.extend(cls.__CI_KUSTOMIZE_CMD_OPTS)
        kustomize_cmd.append(str(target_path.absolute()))

        return kustomize_cmd

    @classmethod
    def __check_input_kustomizations(
        cls, kustomizations_list: typing.List[typing.Dict[str, typing.Any]]
    ):
        for kustomization_content in kustomizations_list:
            if cls.__CI_KUSTOMIZE_KIND_FIELD_NAME not in kustomization_content:
                raise CifmwKustomizeContentValidationException(
                    "Kustomization input contains a manifest without"
                    f" {cls.__CI_KUSTOMIZE_KIND_FIELD_NAME} field",
                    kustomization_content=kustomization_content,
                )
            if (
                kustomization_content[cls.__CI_KUSTOMIZE_KIND_FIELD_NAME]
                != cls.__CI_KUSTOMIZE_FILE_KIND
            ):
                raise CifmwKustomizeContentValidationException(
                    "Kustomization input contains a manifest with a"
                    f" {cls.__CI_KUSTOMIZE_KIND_FIELD_NAME} that is not"
                    f" {cls.__CI_KUSTOMIZE_FILE_KIND}",
                    kustomization_content=kustomization_content,
                )
            if cls.__CI_KUSTOMIZE_API_VERSION_FIELD_NAME not in kustomization_content:
                raise CifmwKustomizeContentValidationException(
                    "Kustomization input contains a manifest without"
                    f" {cls.__CI_KUSTOMIZE_API_VERSION_FIELD_NAME} field",
                    kustomization_content=kustomization_content,
                )
            if not kustomization_content[
                cls.__CI_KUSTOMIZE_API_VERSION_FIELD_NAME
            ].startswith(cls.__CI_KUSTOMIZE_FILE_API_VERSION):
                raise CifmwKustomizeContentValidationException(
                    "Kustomization input contains a manifest with a"
                    f" {cls.__CI_KUSTOMIZE_API_VERSION_FIELD_NAME} that is not"
                    f" {cls.__CI_KUSTOMIZE_FILE_API_VERSION}",
                    kustomization_content=kustomization_content,
                )

    @staticmethod
    def __load_string_based_kustomization(
        kustomization_content: str,
    ) -> typing.Dict[str, typing.Any]:
        # Try to parse the kustomizations as a string with multiple manifests
        try:
            return list(yaml.load_all(kustomization_content, Loader=yaml.Loader))
        except yaml.YAMLError as err:
            raise CifmwKustomizeContentValidationException(
                f"Failed to load a kustomization. YAML Error {str(err)}",
                kustomization_content=kustomization_content,
            ) from err

    @classmethod
    def __parse_kustomizations_input(
        cls,
        kustomizations: typing.Union[
            str, typing.Dict, typing.List[typing.Union[str, typing.Dict]]
        ],
    ) -> typing.List[typing.Dict[str, typing.Any]]:
        loaded_kustomizations = []

        if isinstance(kustomizations, str):
            loaded_kustomizations = cls.__load_string_based_kustomization(
                kustomizations
            )
        elif isinstance(kustomizations, dict):
            # Assume single kustomization was given
            loaded_kustomizations.append(kustomizations)
        elif isinstance(kustomizations, list) and all(
            (isinstance(item_value, str) or isinstance(item_value, dict))
            for item_value in kustomizations
        ):
            # The list of kustomizations is a list of strings or dicts
            for item_value in kustomizations:
                if isinstance(item_value, str):
                    loaded_kustomizations.extend(
                        cls.__load_string_based_kustomization(item_value)
                    )
                else:
                    loaded_kustomizations.append(item_value)

        elif not isinstance(kustomizations, type(None)):
            raise CifmwKustomizeException("Unsupported kustomizations list type")

        cls.__check_input_kustomizations(loaded_kustomizations)

        return loaded_kustomizations

    @staticmethod
    def __find_kustomize_tool(tools_search_path=None) -> str:
        tool_path = shutil.which("oc", path=tools_search_path) or shutil.which(
            "kustomize", path=tools_search_path
        )
        if tool_path:
            return tool_path

        raise CifmwKustomizeException("Cannot find oc nor kustomize in PATH")

    def __apply_kustomization(
        self, kustomization_content: typing.Dict[str, typing.Any], index: int
    ):
        kustomization_path = self.__workspace_dir.joinpath("kustomization.yaml")
        with kustomization_path.open(
            "w", encoding=self.__CI_KUSTOMIZE_ENCODING
        ) as kustomization_file:
            yaml.dump(kustomization_content, kustomization_file)

        run_result = subprocess.run(
            self.__kustomize_cmd,
            encoding="utf-8",
            capture_output=True,
            cwd=self.__workspace_dir,
            check=False,
        )
        if run_result.returncode:
            error = run_result.stderr or run_result.stdout
            error_header = error.splitlines()[0]
            raise CifmwKustomizeApplyKustomizationException(
                error_header,
                error,
                kustomization_content,
                kustomization_path,
            )

        kustomization_path.rename(kustomization_path.with_suffix(f".{index}.yml"))

    @classmethod
    def __dict_is_manifest(cls, content) -> bool:
        return (
            isinstance(content, dict)
            and (cls.__CI_KUSTOMIZE_KIND_FIELD_NAME in content)
            and (cls.__CI_KUSTOMIZE_API_VERSION_FIELD_NAME in content)
        )

    @classmethod
    def __is_kustomization_content(cls, manifest_content) -> bool:
        return (
            cls.__dict_is_manifest(manifest_content)
            and manifest_content[cls.__CI_KUSTOMIZE_KIND_FIELD_NAME]
            == cls.__CI_KUSTOMIZE_FILE_KIND
            and manifest_content[cls.__CI_KUSTOMIZE_API_VERSION_FIELD_NAME].startswith(
                cls.__CI_KUSTOMIZE_FILE_API_VERSION
            )
        )

    def __read_kustomize_candidates(
        self,
    ) -> typing.Dict[pathlib.Path, typing.List[typing.Any]]:
        resulting_files_content = {}
        for file_path in self.__get_all_yamls_in_scan_paths():
            try:
                with file_path.open("r", encoding=self.__CI_KUSTOMIZE_ENCODING) as file:
                    for manifest_content in yaml.load_all(file, Loader=yaml.Loader):
                        if self.__is_kustomization_content(manifest_content):
                            if file_path not in resulting_files_content:
                                resulting_files_content[file_path] = []
                            resulting_files_content[file_path].append(manifest_content)
            except yaml.YAMLError:
                continue

        return resulting_files_content

    @classmethod
    def __get_manifests_paths_from_dir_candidates(
        cls,
        base_dir: pathlib.Path,
        skip_paths: pathlib.Path = None,
        skip_regexes: typing.List[str] = None,
        include_regexes: typing.List[str] = None,
    ) -> typing.Dict[pathlib.Path, typing.List[typing.Any]]:
        resulting_files_content = {}
        for file_path in cls.__get_yaml_files_in_path(
            base_dir,
            skip_paths=skip_paths,
            skip_regexes=skip_regexes,
            include_regexes=include_regexes,
        ):
            file_content = file_path.read_text(encoding="utf-8")
            try:
                yaml_content = list(yaml.load_all(file_content, Loader=yaml.Loader))
                if all(
                    cls.__dict_is_manifest(manifest)
                    and (not cls.__is_kustomization_content(manifest))
                    for manifest in yaml_content
                ):
                    resulting_files_content[file_path] = yaml_content
            except yaml.YAMLError:
                continue
        return resulting_files_content

    def __set_target_kustomization_resource(
        self, kustomizations_list: typing.Dict[str, typing.Any]
    ):
        # Why this gross way of replacing the resources?
        # This plugin copies in it's initialization all the targeted
        # resources(or resource if a path to a file is given) always
        # to a single file inside the workspace dir, that's how it works.
        # Many input manifest files are translated into a single one, the
        # one copied into the workspace dir, so, replacing the original
        # content with a harcoded list that points to that file is fine.
        for kustomization_content in kustomizations_list:
            kustomization_content["resources"] = [self.__target_workspace_file.name]

    @classmethod
    def __get_yaml_files_in_path(
        cls,
        path: pathlib.Path,
        skip_paths: pathlib.Path = None,
        skip_regexes: typing.List[str] = None,
        include_regexes: typing.List[str] = None,
    ) -> typing.List[pathlib.Path]:
        avoid_paths = skip_paths or []
        results = []
        if (
            path.is_file()
            and path not in avoid_paths
            and any(
                fnmatch.fnmatch(path, e)
                for e in cls.__CI_KUSTOMIZE_FILES_GLOB_EXPRESSIONS
            )
        ):
            results.append(path)
        elif path.is_dir():
            results.extend(
                [
                    f
                    for f_ in [
                        path.glob(e) for e in cls.__CI_KUSTOMIZE_FILES_GLOB_EXPRESSIONS
                    ]
                    for f in f_
                    if f not in avoid_paths
                ]
            )

        # If include_regexes are given output only files that match a regex
        if include_regexes:
            results = [
                path
                for path in list(results)
                if any(
                    re.search(regex, str(path.absolute())) for regex in include_regexes
                )
            ]

        # Skip paths that matches skip_regexes
        return [
            path
            for path in results
            if not any(re.search(regex, str(path.absolute())) for regex in skip_regexes)
        ]

    def __get_all_yamls_in_scan_paths(self) -> typing.List[pathlib.Path]:
        return sorted(
            [
                f
                for f_ in [
                    self.__get_yaml_files_in_path(
                        path,
                        skip_regexes=self.__skip_regexes,
                        include_regexes=self.__include_regexes,
                    )
                    for path in self.__kustomization_scan_paths
                ]
                for f in f_
            ],
            key=lambda i: i.name,
            reverse=not self.__sort_ascending,
        )

    def __create_kustomization_list(self):
        files_candidates = self.__read_kustomize_candidates()
        files_kustomizations = [
            kustomization
            for file_kustomizations in files_candidates.values()
            for kustomization in file_kustomizations
        ]

        kustomizations = []
        if not self.__kustomization_files_goes_first:
            kustomizations = self.__input_kustomizations + files_kustomizations
        else:
            kustomizations = files_kustomizations + self.__input_kustomizations

        self.__set_target_kustomization_resource(kustomizations)

        return kustomizations, list(files_candidates.keys())

    def kustomize(self) -> CifmwKustomizeResult:
        original_output_path_hash = (
            sha1_file(self.output_path) if self.output_path.exists() else None
        )

        self.__copy_input_to_workspace()

        kustomizations, discovered_files = self.__create_kustomization_list()
        for index, kustomization in enumerate(kustomizations):
            self.__apply_kustomization(kustomization, index)

        shutil.copy(self.__target_workspace_file, self.output_path)

        changed = (not original_output_path_hash) or (
            original_output_path_hash != sha1_file(self.output_path)
        )

        output_content = list(
            yaml.safe_load_all(
                self.output_path.read_text(encoding=self.__CI_KUSTOMIZE_ENCODING)
            )
        )

        return CifmwKustomizeResult(
            len(kustomizations),
            [str(path.absolute()) for path in discovered_files],
            str(self.output_path.absolute()),
            output_content,
            changed,
        )


# Ansible raw input args can contain AnsibleUnicodes nested
# in dicts, this ensures we work with plain python types
def decode_ansible_raw_iterable(data):
    if isinstance(data, list):
        return [decode_ansible_raw_iterable(_data) for _data in data]
    if isinstance(data, dict):
        return yaml.load(
            yaml.dump(
                data, Dumper=AnsibleDumper, default_flow_style=False, allow_unicode=True
            ),
            Loader=yaml.Loader,
        )

    return data


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp

        target_path = self._task.args.get("target_path", None)
        kustomizations = decode_ansible_raw_iterable(
            self._task.args.get("kustomizations", None)
        )
        kustomizations_paths = self._task.args.get("kustomizations_paths", None)
        output_path = self._task.args.get("output_path", None)
        kustomization_files_goes_first = self._task.args.get(
            "kustomization_files_goes_first", True
        )
        preserve_workspace = self._task.args.get("preserve_workspace", False)
        sort_ascending = self._task.args.get("sort_ascending", True)
        skip_regexes = self._task.args.get("skip_regexes", None)
        include_regexes = self._task.args.get("include_regexes", None)
        final_environment = {}
        self._compute_environment_string(final_environment)

        try:
            with CifmwKustomizeWrapper(
                target_path,
                kustomizations=kustomizations,
                kustomizations_paths=kustomizations_paths,
                output_path=output_path,
                kustomization_files_goes_first=kustomization_files_goes_first,
                tools_search_path=final_environment.get("PATH", None),
                preserve_workspace=preserve_workspace,
                sort_ascending=sort_ascending,
                skip_regexes=skip_regexes,
                include_regexes=include_regexes,
            ) as kustomize:
                kustomize_result = kustomize.kustomize()
                result.update(dataclasses.asdict(kustomize_result))
                result["failed"] = False
        except CifmwKustomizeException as run_exception:
            result = {**result, **(run_exception.to_dict())}
            result["failed"] = True

        return result
