# Copyright Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import yaml
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from scripts.create_role_molecule import (
    get_project_paths,
    regenerate_molecule_zuul_jobs_yaml,
    regenerate_projects_zuul_jobs_yaml,
    merge_yaml_jobs_by_name,
)


class CreateRoleMoleculeTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = 1000
        # Create structure in tmp generated rir
        self.temp_dir = TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name)

        self.generated_paths = get_project_paths(self.project_dir)

        [
            Path(path).mkdir(parents=True, exist_ok=True)
            for path in self.generated_paths.values()
        ]

        # Create some roles directories
        role_no_molecule = self.generated_paths["roles_dir"] / "no_molecule"
        role_3_dir = self.generated_paths["roles_dir"] / "role_3" / "molecule"
        role_2_dir = self.generated_paths["roles_dir"] / "role_2" / "molecule"
        role_1_dir = self.generated_paths["roles_dir"] / "role_1" / "molecule"
        Path(role_1_dir).mkdir(parents=True, exist_ok=True)
        Path(role_2_dir).mkdir(parents=True, exist_ok=True)
        Path(role_3_dir).mkdir(parents=True, exist_ok=True)
        Path(role_no_molecule).mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_regenerate_projects_zuul_jobs_yaml(self):
        # Generate projects.yaml before merging
        projects_jobs_info = [
            {
                "project": {
                    "name": "openstack-k8s-operators/ci-framework",
                    "github-check": {
                        "jobs": [
                            "noop",
                            "ci-framework-crc-podified-edpm-baremetal",
                            "ci-framework-crc-podified-edpm-deployment",
                            "cifmw-end-to-end",
                            "cifmw-end-to-end-nobuild-tagged",
                            "cifmw-kuttl",
                            "cifmw-edpm-build-image",
                            "cifmw-content-provider-build-images",
                        ]
                    },
                }
            }
        ]
        with open(
            self.generated_paths["ci_templates_dir"] / "projects.yaml", "w"
        ) as projects_file:
            yaml.dump(projects_jobs_info, projects_file)

        # Regenerate zuul.d/projects.yaml with the previous data + roles
        # directories
        regenerate_projects_zuul_jobs_yaml(self.generated_paths)

        # Read the updated projects.yaml file
        with open(self.generated_paths["zuul_job_dir"] / "projects.yaml", "r") as file:
            updated_content = yaml.safe_load(file)

        expected_content = [
            {
                "project": {
                    "name": "openstack-k8s-operators/ci-framework",
                    "github-check": {
                        "jobs": [
                            "noop",
                            "ci-framework-crc-podified-edpm-baremetal",
                            "ci-framework-crc-podified-edpm-deployment",
                            "cifmw-end-to-end",
                            "cifmw-end-to-end-nobuild-tagged",
                            "cifmw-kuttl",
                            "cifmw-edpm-build-image",
                            "cifmw-content-provider-build-images",
                            "cifmw-molecule-role_2",
                            "cifmw-molecule-role_1",
                            "cifmw-molecule-role_3",
                        ]
                    },
                }
            }
        ]

        # We can't compare the list of jobs since the order matters. We need
        #  to convert it into a set
        updated_content[0]["project"]["github-check"]["jobs"] = set(
            updated_content[0]["project"]["github-check"]["jobs"]
        )
        expected_content[0]["project"]["github-check"]["jobs"] = set(
            expected_content[0]["project"]["github-check"]["jobs"]
        )
        self.assertEqual(updated_content, expected_content)

    def test_regenerate_molecule_zuul_jobs_yaml(self):
        # We need to load the molecule.yaml.j2 template.
        molecule_ci_template_dir = get_project_paths()["ci_templates_dir"]
        generated_paths = self.generated_paths
        generated_paths["ci_templates_dir"] = molecule_ci_template_dir

        molecule_example_jobs = [
            {
                "job": {
                    "name": "test_1",
                    "parent": "parent_test",
                    "vars": {"TEST_RUN": "role1"},
                }
            },
            {"job": {"name": "test_3", "nodeset": "test_centos_node"}},
        ]

        with open(
            generated_paths["ci_config_dir"] / "molecule.yaml", "w"
        ) as projects_file:
            yaml.dump(molecule_example_jobs, projects_file)

        regenerate_molecule_zuul_jobs_yaml(generated_paths)

        # Read the generated molecule.yaml file
        with open(self.generated_paths["zuul_job_dir"] / "molecule.yaml", "r") as file:
            generated_molecule_zuul_jobs = yaml.safe_load(file)

        expected_yaml_molecule = [
            {
                "job": {
                    "files": [
                        "^common-requirements.txt",
                        "^test-requirements.txt",
                        "^roles/role_2/(?!meta|README).*",
                        "^ci/playbooks/molecule.*",
                    ],
                    "name": "cifmw-molecule-role_2",
                    "parent": "cifmw-molecule-base",
                    "vars": {"TEST_RUN": "role_2"},
                }
            },
            {
                "job": {
                    "files": [
                        "^common-requirements.txt",
                        "^test-requirements.txt",
                        "^roles/role_1/(?!meta|README).*",
                        "^ci/playbooks/molecule.*",
                    ],
                    "name": "cifmw-molecule-role_1",
                    "parent": "cifmw-molecule-base",
                    "vars": {"TEST_RUN": "role_1"},
                }
            },
            {
                "job": {
                    "files": [
                        "^common-requirements.txt",
                        "^test-requirements.txt",
                        "^roles/role_3/(?!meta|README).*",
                        "^ci/playbooks/molecule.*",
                    ],
                    "name": "cifmw-molecule-role_3",
                    "parent": "cifmw-molecule-base",
                    "vars": {"TEST_RUN": "role_3"},
                }
            },
        ]

        # Since the order matters for the asserts is a little bit complicated
        # to test just with one assert
        for generated_dictionary in generated_molecule_zuul_jobs:
            # Check if each dictionary of generated jobs in the expected one
            self.assertIn(generated_dictionary, expected_yaml_molecule)
            # Find the corresponding expected dictionary that matches the
            # generated dictionary
            expected_dictionary = next(
                d for d in expected_yaml_molecule if d == generated_dictionary
            )
            self.compareMoleculeJobDictionaries(
                generated_dictionary, expected_dictionary
            )

    def compareMoleculeJobDictionaries(self, dict1, dict2):
        self.assertEqual(dict1["job"]["name"], dict2["job"]["name"])
        self.assertEqual(dict1["job"]["parent"], dict2["job"]["parent"])
        self.assertEqual(
            dict1["job"]["vars"]["TEST_RUN"], dict2["job"]["vars"]["TEST_RUN"]
        )
        self.assertCountEqual(dict1["job"]["files"], dict2["job"]["files"])

    def test_merge_yaml_jobs_by_name(self):
        job_list1 = [
            {"job": {"name": "test_1", "nodeset": "test_centos_node"}},
            {"job": {"name": "test_2", "nodeset": "test_centos_node"}},
            {
                "job": {
                    "name": "test_3",
                }
            },
        ]
        job_list2 = [
            {
                "job": {
                    "name": "test_1",
                    "parent": "parent_test",
                    "vars": {"TEST_RUN": "role1"},
                }
            },
            {"job": {"name": "test_3", "nodeset": "test_centos_node"}},
        ]
        expected_result = [
            {
                "job": {
                    "name": "test_1",
                    "nodeset": "test_centos_node",
                    "parent": "parent_test",
                    "vars": {"TEST_RUN": "role1"},
                }
            },
            {"job": {"name": "test_2", "nodeset": "test_centos_node"}},
            {"job": {"name": "test_3", "nodeset": "test_centos_node"}},
        ]
        merged_jobs = merge_yaml_jobs_by_name(job_list1, job_list2)
        self.assertEqual(merged_jobs, expected_result)


if __name__ == "__main__":
    unittest.main()
