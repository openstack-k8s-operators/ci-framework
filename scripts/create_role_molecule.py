#!/usr/bin/python3

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

from pathlib import Path
import yaml
import logging
from jinja2 import Environment, FileSystemLoader


def get_project_paths(project_dir=None):
    """
    Generate and return the path variables used in the script.

    Args:
        project_dir (str): Path of the project folder.

    Returns:
        dict: Dictionary containing the variables.
    """
    if project_dir is None:
        project_dir = Path(__file__).resolve().parent.parent

    script_dir = project_dir / "scripts"
    ci_templates_dir = project_dir / "ci" / "templates"
    ci_config_dir = project_dir / "ci" / "config"
    roles_dir = project_dir / "roles"
    zuul_job_dir = project_dir / "zuul.d"
    source_roles_docs_dir = project_dir / "docs" / "source" / "roles"

    project_paths = {
        "project_dir": project_dir,
        "script_dir": script_dir,
        "ci_templates_dir": ci_templates_dir,
        "ci_config_dir": ci_config_dir,
        "roles_dir": roles_dir,
        "zuul_job_dir": zuul_job_dir,
        "source_roles_docs_dir": source_roles_docs_dir,
    }

    return project_paths


def generate_zuul_job_role_yaml(roles_name, templates_dir, template_name):
    """
    Generate YAML structure for a Zuul job based on given role.

    Args:
        roles_name (str): Name of the role.
        templates_dir (str): Location of the templates.
        template_name (str): Name of the template to use.

    Returns:
        dict: YAML structure for the role.
    """
    template_loader = FileSystemLoader(searchpath=templates_dir)
    template_env = Environment(loader=template_loader)
    template = template_env.get_template(template_name)
    zuul_rendered_template_jobs = yaml.safe_load(template.render(role_names=roles_name))
    return zuul_rendered_template_jobs


def regenerate_projects_zuul_jobs_yaml(generated_paths):
    """
    Regenerate zuul.d/projects.yaml file with the name of each role
    under ci-framework/roles
    """
    with open(generated_paths["ci_templates_dir"] / "projects.yaml", "r") as file:
        projects_jobs_info = yaml.safe_load(file)

    # Add each role name after the generated content
    for role_directory in sorted(generated_paths["roles_dir"].iterdir()):
        if not role_directory.is_dir():
            logging.warning("Skipping %s. Not a role directory", role_directory.name)
            continue
        projects_jobs_info[0]["project"]["github-check"]["jobs"].append(
            f"cifmw-molecule-{role_directory.name}"
        )

    with open(generated_paths["zuul_job_dir"] / "projects.yaml", "w") as projects_file:
        yaml.dump(projects_jobs_info, projects_file)


def regenerate_molecule_zuul_jobs_yaml(generated_paths):
    """
    Regenerate zuul.d/molecule.yaml file with role-specific YAML structures.
    """
    role_directories = [
        entry.name
        for entry in generated_paths["roles_dir"].iterdir()
        if (entry.is_dir() and entry.joinpath("molecule").is_dir())
    ]
    molecule_yaml_zuul_jobs = generate_zuul_job_role_yaml(
        role_directories, generated_paths["ci_templates_dir"], "molecule.yaml.j2"
    )

    # Noop molecule jobs for proper dependencies
    noop_roles = [
        entry.name
        for entry in generated_paths["roles_dir"].iterdir()
        if (entry.is_dir() and not entry.joinpath("molecule").is_dir())
    ]
    noop_jobs = generate_zuul_job_role_yaml(
        noop_roles, generated_paths["ci_templates_dir"], "noop-molecule.yaml.j2"
    )

    # Append the noop to the normal list
    molecule_yaml_zuul_jobs = molecule_yaml_zuul_jobs + noop_jobs

    molecule_ci_config_yaml = generated_paths["ci_config_dir"] / "molecule.yaml"
    with open(molecule_ci_config_yaml, "r") as file:
        molecule_ci_jobs_info = yaml.safe_load(file)

    merged_molecule_jobs = merge_yaml_jobs_by_name(
        molecule_yaml_zuul_jobs, molecule_ci_jobs_info
    )

    with open(generated_paths["zuul_job_dir"] / "molecule.yaml", "w") as molecule_file:
        yaml.dump(merged_molecule_jobs, molecule_file)


def merge_yaml_jobs_by_name(job_list1, job_list2):
    """
    Merge YAML jobs from two lists of dictionaries based on the job name.

    Args:
        job_list1 (list): The first list of dictionaries representing
        YAML jobs.
        job_list2 (list): The second list of dictionaries representing
        YAML jobs.

    Returns:
        list: The merged list of dictionaries containing the merged YAML jobs.
    """
    for job1 in job_list1:
        for job2 in job_list2:
            if job1["job"]["name"] == job2["job"]["name"]:
                for key, val in job2["job"].items():
                    if isinstance(val, list):
                        if key not in job1["job"]:
                            job1["job"][key] = []
                        job1["job"][key] += job2["job"][key]
                    if isinstance(val, dict):
                        if key not in job1["job"]:
                            job1["job"][key] = {}
                        job1["job"][key].update(job2["job"][key])
                    if isinstance(val, str) or isinstance(val, int):
                        job1["job"][key] = job2["job"][key]

    return job_list1


if __name__ == "__main__":
    generated_paths = get_project_paths()
    regenerate_projects_zuul_jobs_yaml(generated_paths)
    regenerate_molecule_zuul_jobs_yaml(generated_paths)
