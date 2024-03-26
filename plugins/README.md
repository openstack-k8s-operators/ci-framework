# action_plugins/ci_make

> **_NOTE:_** This module is deprecated and will be removed in a future version. Please consider using the ci_script module instead.

This wraps `community.general.make` module, mostly. It requires an additional
parameter, `output_dir`, in order to output the `make` generated command.
It also adds a new optional parameter, `dry_run`, allowing to NOT run
`community.general.make` module, but get a file with the passed parameters.

Requires `community.general` collection v6.5.0 or higher.

Example:
```YAML
- hosts: localhost
  tasks:
    - name: Create artifact directory
      ansible.builtin.file:
        path: /tmp/artifacts
        state: directory
    - name: Run pre-commit tests
      ci_make:
        chdir: "~/code/github.com/ci-framework-data"
        output_dir: /tmp/artifacts
        target: pre_commit
        params:
          USE_VENV: no
```
This will output a file in /tmp/artifacts with a specific pattern:
`ci_make_INDEX_run_pre-commit_tests.sh`
The INDEX is calculated based on matching `ci_make_*` pattern in that directory.
The file can then be used as a reproducer or just debug output in order to
understand what was actually launched using `community.ansible.make` module.

# action_plugins/discover_latest_image
Allows to discover the latest available qcow2 from a remote page. It's mainly
wrapped in the discover_latest_image role, but you may call the action
directly. Beware though, it will NOT export any fact! Please check the example
bellow for more info about its proper usage.

## options:
Any of the `ansible.builtin.uri` module is supported.

* `url`:
  * description: remote URL to the page
  * required: True
  * type: str
* `image_prefix`:
  * description: Image prefix we want to filter.
  * required: True
  * type: str
* `images_file`:
  * description: Name of the file that contain the images with the corresponding hash
  * required: False
  * type: str

## Example:
```YAML
- name: Get latest CentOS 9 Stream image
  register: discovered_image
  discover_latest_image:
    url: "https://cloud.centos.org/centos/9-stream/x86_64/images/"
    image_prefix: "CentOS-Stream-GenericCloud"

- name: Export discovered image facts
  ansible.builtin.set_fact:
    cifmw_discovered_image_name: "{{ discovered_image['data']['image_name'] }}"
    cifmw_discovered_image_url: "{{ discovered_image['data']['image_url'] }}"
    cifmw_discovered_hash: "{{ discovered_image['data']['hash'] }}"
    cifmw_discovered_hash_algorithm: "{{ discovered_image['data']['hash_algorithm'] }}"
    cacheable: true
```

# modules/get_makefiles_env
Description: Retrieves a dictionary with all the environment variables
defined in the Makefiles under the given path.

## options:
* `base_path`:
  * description: The base path on where to start picking Makefiles vars.
  * required: true
  * type: str

# modules/generate_make_tasks
Description: Generate task file per Makefile target.

## options:
* `install_yamls_path`:
  * description: Absolute path to install_yamls repository
  * required: True
  * type: str
* `output_directory`:
  * description: Absolute path to the output directory. It must exist
  * required: True
  * type: str

# modules/tempest_list_allowed
Description: Generate list of tests to be executed by tempest

## options:
* `yaml_file`:
  * description: Path to a yaml file containing the tests
  * required: True
  * type: str
* `job`:
  * description: Name of the job to be used in the filter.
  * required: False
  * type: str
* `groups`:
  * description: List of groups to be used in the filter.
  * required: False
  * type: list
* `release`
  * description: Release version
  * type: str
  * default: master

# modules/tempest_list_skipped
Description: Generate list of tests to be skipped by tempest

## options:

* `yaml_file`:
  * description: Path to a yaml file containing the tests
  * required: True
  * type: str
* `jobs`:
  * description: List of the jobs to be used in the filter.
  * required: False
  * type: list
* `release`:
  * description: Release name to be used in the filter. Default is 'master'
  * required: False
  * type: str
  * default: master


## Calling generated tasks
In order to benefit of the generated role and tasks, you have to ensure ansible
knows about the role location. By default, it will be in
`{{cifmw_basedir}}/artifacts/roles/install_yamls`, and this path is already
injected in the `ansible.cfg` provided by the project.

### Task inclusion
Leveraging `ansible.builtin.include_role` and its `tasks_from` parameter, you
may call the generated task file for the desired `make` target. For instance:
```YAML
- name: Prepare storage in CRC
  vars:
    make_crc_storage_env: "{{ cifmw_edpm_prepare_common_env }}"
    make_crc_storage_dryrun: "{{ cifmw_edpm_prepare_dry_run }}"
  when: not cifmw_edpm_prepare_skip_crc_storage_creation | bool
  ansible.builtin.include_role:
    name: 'install_yamls_makes'
    tasks_from: 'make_crc_storage'
```
This block will call the `make crc_storage` command, passing some variables
that will then be transferred to the `ci_make` call.

### Available parameters
* `make_TARGET_env`: (List) Allows to pass `environment` parameter to the task.
* `make_TARGET_params`: (List) Allows to pass `make` parameters.
* `make_TARGET_dryrun`: (Boolean) Toggle `dry_run` flag of `ci_make`.
* `make_TARGET_retries`: (Integer) Number of retries for `ci_make` task.
* `make_TARGET_delay`: (Integer) Delay between retries for `ci_make` task.
* `make_TARGET_until`: (String) Early exit condition (`until`) for `ci_make` retries.

### `until` condition
When you want to leverage `retries`, it's always good to get an `until` condition.
In order to make things easier, the generated task exposes `make_TARGET_status`,
allowing an easy `make_TARGET_status is not failed` condition:
```YAML

- name: Prepare storage in CRC
  vars:
    make_crc_storage_env: "{{ cifmw_edpm_prepare_common_env }}"
    make_crc_storage_dryrun: "{{ cifmw_edpm_prepare_dry_run }}"
    make_crc_storage_retries: 10
    make_crc_storage_delay: 2
    make_crc_storage_until: "make_crc_storage_status is not failed"
  when: not cifmw_edpm_prepare_skip_crc_storage_creation | bool
  register: crc_storage_status
  ansible.builtin.include_role:
    name: 'install_yamls_makes'
    tasks_from: 'make_crc_storage'
```

# modules/approve_csr

Module that approves pending certificate requests in OpenShift platform.

## options - approve_csr

```YAML
* k8s_config
  * description: Absolute path to the kube configuration file.
    required: false
    type: str
* quiet_period
  * description: Maximum amount of time to be observed for no events.
    required: false
    type: str
    default: 3m
```

## example - approve_csr

```YAML
- name: Approve pending certificate requests in OpenShift
  hosts: hypervisor
  gather_facts: false
  vars:
    k8s_config: "/home/zuul/.kube/config"

  tasks:
    - name: Wait and approve all
      approve_csr:
        k8s_config: "{{ k8s_config }}"
```
