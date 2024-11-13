# install_yamls
An ansible role wrapper around [install_yamls](https://github.com/openstack-k8s-operators/install_yamls) Makefile. It dynamically creates `install_yamls_makes` role, which can be reused within [the CI Framework and other projects](https://github.com/rdo-infra/rdo-jobs/blob/39d0647cbb20abe3aaf2baad134a0e09473e1c54/playbooks/data_plane_adoption/ci_framework_install_yamls.yaml#L5-L24).

It contains a set of playbooks to deploy podified control plane.

## Parameters
* `cifmw_install_yamls_envfile`: (String) Environment file containing all the Makefile overrides. Defaults to `install_yamls`.
* `cifmw_install_yamls_out_dir`: (String) `install_yamls` output directory to store generated output. Defaults to `{{ cifmw_basedir | default(ansible_user_dir ~ '/ci-framework-data') }}/artifacts"`.
* `cifmw_install_yamls_vars`: (Dict) A dict containing Makefile overrides.
* `cifmw_install_yamls_repo`: (String) `install_yamls` repo path. Defaults to `{{ ansible_user_dir }}/src/github.com/openstack-k8s-operators/install_yamls`.
* `cifmw_install_yamls_whitelisted_vars`: (List) Allowed variables in `cifmw_install_yamls_vars` that are not part of `install_yamls` Makefiles.
* `cifmw_install_yamls_edpm_dir`: (String) Output directory for EDPM related artifacts (OUTPUT_BASEDIR). Defaults to `{{ cifmw_install_yamls_out_dir_basedir ~ '/artifacts/edpm' }}`
* `cifmw_install_yamls_checkout_openstack_ref`: (String) Enable the checkout from openstack-operator references
when cloning operator's repository using install_yamls make targets. Defaults to `"true"`

## Use case
This module uses [a custom plugin](https://github.com/openstack-k8s-operators/ci-framework/blob/main/plugins/modules/generate_make_tasks.py) created to generate the role with tasks from Makefile.
The created role directory contains multiple task files, similar to
```YAML
---
- name: Debug make_crc_storage_env
  when: make_crc_storage_env is defined
  ansible.builtin.debug:
    var: make_crc_storage_env
- name: Debug make_crc_storage_params
  when: make_crc_storage_params is defined
  ansible.builtin.debug:
    var: make_crc_storage_params
- name: Run crc_storage
  retries: "{{ make_crc_storage_retries | default(omit) }}"
  delay: "{{ make_crc_storage_delay | default(omit) }}"
  until: "{{ make_crc_storage_until | default(true) }}"
  register: "make_crc_storage_status"
  ci_script:
    output_dir: "{{ cifmw_basedir|default(ansible_user_dir ~ '/ci-framework-data') }}/artifacts"
    chdir: "/home/zuul/src/github.com/openstack-k8s-operators/install_yamls"
    script: make crc_storage
    dry_run: "{{ make_crc_storage_dryrun|default(false)|bool }}"
    extra_args: "{{ dict((make_crc_storage_env|default({})), **(make_crc_storage_params|default({}))) }}"
```

The role can be imported and tasks can be executed like this
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

Tasks are created in a form of: `make_{{ original make target }}`, corresponding to `make target` imported from [a Makefile](https://github.com/openstack-k8s-operators/install_yamls/blob/c8487df41bf9ddefa7989f9384e77ae9720ce9dd/Makefile#L418).
When task is being executed, it runs corresponding code from the Makefile.

## Override install_yamls "make" parameters and environments

### module: generate_make_tasks

1. For every makefile target we have a dedicated task file.

```YAML
    options:
      install_yamls_path:
      description:
        - Absolute path to install_yamls repository.
      required: True
      type: str
      output_directory:
      description:
        - Absolute path to the output directory. It must exists.
      required: True
      type: str
```

2. Follow below steps to find makefile target dedicated task files:

```Bash
  [laptop]$ cd ~/src/github.com/openstack-k8s-operators/ci-framework
  [laptop]$ cd ci-framework-data/artifacts/roles/install_yamls_makes/tasks
```

### Override install_yaml make parameter

User can build specific parameters using "make_TARGET_env"
and "make_TARGET_dryrun".
So, here the target could be the parameter for which user wish to override
make parameter.

Let's look at below example:-

  ```YAML
    - name: Debug make_ansibleee_cleanup_env
      when: make_ansibleee_cleanup_env is defined
      ansible.builtin.debug:
      var: make_ansibleee_cleanup_env
    - name: Debug make_ansibleee_cleanup_params
      when: make_ansibleee_cleanup_params is defined
      ansible.builtin.debug:
        var: make_ansibleee_cleanup_params
    - name: Run ansibleee_cleanup
      retries: "{{ make_ansibleee_cleanup_retries | default(omit) }}"
      delay: "{{ make_ansibleee_cleanup_delay | default(omit) }}"
      until: "{{ make_ansibleee_cleanup_until | default(true) }}"
      register: "make_ansibleee_cleanup_status"
      ci_script:
        output_dir: "{{ cifmw_basedir|default(ansible_user_dir ~ '/ci-framework-data') }}/artifacts"
        chdir: "/home/zuul/src/github.com/openstack-k8s-operators/install_yamls"
        script: "make ansibleee_cleanup"
        dry_run: "{{ make_ansibleee_cleanup_dryrun|default(false)|bool }}"
        extra_args: "{{ dict((make_ansibleee_cleanup_env|default({})), **(make_ansibleee_cleanup_params|default({}))) }}"
  ```

This is a generated task file for the "make ansibleee_cleanup". Here, a user
is able to set ansible parameter
that would then be translated into either task parameter (such as
make_ansibleee_cleanup_until,
make_ansibleee_cleanup_retries etc) or as a proper "make" parameter
(via make_ansibleee_cleanup_env)
