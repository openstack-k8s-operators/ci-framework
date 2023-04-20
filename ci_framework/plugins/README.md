# Custom ansible plugins and modules

## action_plugins/ci_make
This wraps `community.general.make` module, mostly. It requires an additional
parameter, `output_dir`, in order to output the `make` generated command.
It also adds a new optional parameter, `dry_run`, allowing to NOT run
`community.general.make` module, but get a file with the passed parameters.

It requires a pull-request to merge in the community.general collection:
https://github.com/ansible-collections/community.general/pull/6160

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
        chdir: "~/code/github.com/ci-framework"
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

## action_plugins/discover_latest_image
Allows to discover the latest available qcow2 from a remote page. It's mainly
wrapped in the discover_latest_image role, but you may call the action
directly. Beware though, it will NOT export any fact! Please check the example
bellow for more info about its proper usage.

### options:
Any of the `ansible.builtin.uri` module is supported.

* `url`:
  * description: remote URL to the page
  * required: True
  * type: str
* `image_prefix`:
  * description: Image prefix we want to filter.
  * required: True
  * type: str

### Example:
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
    cifmw_discovered_sha256: "{{ discovered_image['data']['sha256'] }}"
    cacheable: true
```

## modules/generate_make_env
Description: Generate a structure embedding all of the environment variables
we may pass down to the Makefiles and related scripts.

### options:
* `install_yamls_path`:
  * description: Full path of the install_yamls makefile.
  * required: true
  * type: str
* `install_yamls_var`:
  * description: List of exported install_yamls variable
  * required: true
  * type: dict
* `check_var`:
  * description: Check the environment var exists in the makefile
  * required: false
  * type: bool

## modules/generate_make_tasks
Description: Generate task file per Makefile target.

### options:
* `install_yamls_path`:
  * description: Absolute path to install_yamls repository
  * required: True
  * type: str
* `output_directory`:
  * description: Absolute path to the output directory. It must exists
  * required: True
  * type: str
