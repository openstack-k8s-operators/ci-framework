# cifmw_helpers

That role was created to replace nested Ansible (Ansible that execute
ansible or ansible-playbook binary using command/shell module) execution in
this project.

## Helper for Zuul executor cifmw general collection

The Zuul executor does not have `ci-framework` collection installed.
It means, that when we want to drop nested Ansible execution, it would raise
an errors (example):

    ERROR! couldn't resolve module/action 'cifmw.general.discover_latest_image'

To avoid such error, we will be using basic Ansible behaviour which is create
a symbolic link to our modules to Ansible workspace before edited playbook is
executed.

Example, how to apply the workaround in Zuul CI job definition.

Before applying fix:

```yaml
# .zuul.yml

- job:
    name: cifmw-adoption-base
    (...)
    roles:
      - zuul: github.com/openstack-k8s-operators/ci-framework
    pre-run:
      - ci/playbooks/multinode-customizations.yml
      - ci/playbooks/e2e-prepare.yml
      - ci/playbooks/dump_zuul_data.yml
    post-run:
      - ci/playbooks/e2e-collect-logs.yml
      - ci/playbooks/collect-logs.yml
      - ci/playbooks/multinode-autohold.yml
    (...)
```

After:

```yaml
- job:
    name: cifmw-adoption-base
    (...)
    roles:
      - zuul: github.com/openstack-k8s-operators/ci-framework
    pre-run:
      - playbooks/cifmw_collection_zuul_executor.yml # here we added our play
      - ci/playbooks/multinode-customizations.yml
      - ci/playbooks/e2e-prepare.yml
      - ci/playbooks/dump_zuul_data.yml
    post-run:
      - ci/playbooks/e2e-collect-logs.yml
      - ci/playbooks/collect-logs.yml
      - ci/playbooks/multinode-autohold.yml
    (...)
```

The example playbook - `playbooks/cifmw_collection_zuul_executor.yml` can look like:

```yaml
---
- name: Make cifmw modules to be available
  hosts: all
  tasks:
    - name: Make a symlink to local .ansible collection dir
      ansible.builtin.include_role:
        name: cifmw_helpers
        tasks_from: symlink_cifmw_collection.yml
```

After doing a symbolic link of modules dir to Ansible working dir in `$HOME` dir,
we should not have `ERROR! couldn't resolve module/action` error anymore.

## Helper for calling nested Ansible

In many places in the project, there is nested Ansible execution done.
It means, that the Ansible is running `ansible` or `ansible-playbook`
inside the `shell` or `command` module. Sometimes, nested Ansible execution
is done 5 times (Ansible calls Ansible calls Ansible etc.)
That is later difficult to debug. More, logs are not printed directly, but they
are going to special dir, where after job finish, we can read. That's not
what we should have in the CI or during local tests.

### Example nested Ansible replacement

Example code, with nested Ansible execution:

```yaml
- name: Run log collection
  ansible.builtin.command:
    chdir: "{{ ansible_user_dir }}/src/github.com/openstack-k8s-operators/ci-framework"
    cmd: >-
      ansible-playbook playbooks/99-logs.yml
      -e @scenarios/centos-9/base.yml
```

Or another example, which does not execute `ansible-playbook`, but `ansible`
and directly call the role:

```yaml
- name: Run run_logs tasks from cifmw_setup
  ansible.builtin.command: >
    ansible localhost
    -m include_role
    -a "name=cifmw_setup tasks_from=run_logs.yml"
    -e "@scenarios/centos-9/base.yml"
  args:
    chdir: "{{ ansible_user_dir }}/src/github.com/openstack-k8s-operators/ci-framework"
```

That code, can be replaced by:

```yaml
- name: Read base centos-9 scenarios
  vars:
    provided_file: >
      {{ ansible_user_dir }}/src/github.com/openstack-k8s-operators/
      ci-framework/scenarios/centos-9/base.yml
  ansible.builtin.include_role:
    name: cifmw_helpers
    tasks_from: var_file.yml

- name: Run log collection
  ansible.builtin.include_role:
    name: cifmw_setup
    tasks_from: run_logs.yml
  tags:
    - logs
```

#### Read var file and set as fact

Example task execution:

```yaml
- name: Read base centos-9 scenarios
  vars:
    provided_file: >
      {{ ansible_user_dir }}/src/github.com/openstack-k8s-operators/
      ci-framework/scenarios/centos-9/base.yml
  ansible.builtin.include_role:
    name: cifmw_helpers
    tasks_from: var_file.yml
```

Of course, before Zuul execute the playbook, it is mandatory to call `playbooks/cifmw_collection_zuul_executor.yml`.

#### Read directory and parse all files and then set as fact

For setting all files in the directory as fact, use `var_dir.yml` tasks.
Example:

```yaml
- name: Read all centos-9 scenarios dir files and set as fact
  vars:
    provided_dir: >
      {{ ansible_user_dir }}/src/github.com/openstack-k8s-operators/
      ci-framework/scenarios/centos-9/
  ansible.builtin.include_role:
    name: cifmw_helpers
    tasks_from: var_dir.yml
```

#### Set as fact various variables

In some places in our workflow, we can have a list that contains
various variables like files: "@some_file.yml" or dictionaries like "some: var".
To parse them and set as a fact, use `various_vars.yml` task file.

```yaml
- name: Example
  hosts: localhost
  tasks:
    - name: Test various vars
      vars:
        various_vars:
          - "@scenarios/centos-9/base.yml"
          - test: ok
      ansible.builtin.include_role:
        name: cifmw_helpers
        tasks_from: various_vars.yml

    - name: Print parsed variables
      ansible.builtin.debug:
        msg: |
          "Value for file is: {{ cifmw_repo_setup_os_release }}"
          "Value for dict is: {{ test }}"
```

#### Parse inventory file and add it to inventory

Sometimes, the VMs on which action would be done are not available when the
main Ansible playbook is executed. In that case, to parse the new inventory file
use `inventory_file.yml` task, then you would be able to use delegation to
execute tasks on new host.

```yaml
- name: Test parsing additional inventory file
  hosts: localhost
  tasks:
    - name: Read inventory file and add it using add_host module
      vars:
        include_inventory_file: vms-inventory.yml
      ansible.builtin.include_role:
        name: cifmw_helpers
        tasks_from: inventory_file.yml
```

#### Parse string of arguments and convert to list of variables or list of files

In some playbook, when nested Ansible is executed via shell/command module,
there is a string which contains arguments to parse by the ansible-playbook
binary. If nested Ansible can be removed, it would be required to parse
such variables. Below example how nested Ansible execution looks like,
and how it could be replaced.

NOTE: `test.yaml` is executed on `host-1`.

Example:
- all files are on same host which execute ansible-playbook

```yaml
- name: Nested Ansible execution
  hosts: localhost
  tasks:
    - name: Run ansible-playbook
      vars:
        cmd_args: "-e@somefile.yml -e @/tmp/someotherfile.yml -e myvar=test"
      ansible.builtin.command: |
        ansible-playbook "{{ cmd_args }}" test.yaml
```

To:

```yaml
- name: Playbook that does not use nested Ansible - same host
  hosts: localhost
  vars:
    cifmw_cmd_args: "-e@somefile.yml -e @/tmp/someotherfile.yml -e myvar=test"
  tasks:
    # NOTE: The task returns fact: cifmw_cmd_args_vars and cifmw_cmd_args_files
    - name: Read inventory file and add it using add_host module
      ansible.builtin.include_role:
        name: cifmw_helpers
        tasks_from: parse_ansible_args_string.yml

    - name: Parse only variables from cifmw_cmd_args_vars
      when: cifmw_cmd_args_vars is defined and cifmw_cmd_args_vars | length > 0
      vars:
        various_vars: "{{ cifmw_cmd_args_vars }}"
      ansible.builtin.include_role:
        name: cifmw_helpers
        tasks_from: various_vars.yml

    - name: Read var files from cifmw_cmd_args
      when: cifmw_cmd_args_files is defined and cifmw_cmd_args_files | length > 0
      ansible.builtin.include_vars:
        file: "{{ files_item }}"
      loop: "{{ cifmw_cmd_args_files }}"
      loop_control:
        loop_var: files_item
```

- files are located in remote host - controller

In alternative version, variables are available on remote host. That requires
to fetch the files first to host which is executing the Ansible - include_vars
reads only files that are on the host where ansible-playbook was executed.
Example:

```yaml
- name: Nested Ansible execution
  hosts: controller
  tasks:
    - name: Run ansible-playbook
      vars:
        cmd_args: "-e@somefile.yml -e @/tmp/someotherfile.yml -e myvar=test"
      ansible.builtin.command: |
        ansible-playbook "{{ cmd_args }}" test.yaml
```

To:

```yaml
- name: Playbook that does not use nested Ansible - different host
  hosts: controller
  vars:
    cifmw_cmd_args: "-e@somefile.yml -e @/tmp/someotherfile.yml -e myvar=test"
  tasks:
    # NOTE: The task returns fact: cifmw_cmd_args_vars and cifmw_cmd_args_files
    - name: Read inventory file and add it using add_host module
      ansible.builtin.include_role:
        name: cifmw_helpers
        tasks_from: parse_ansible_args_string.yml

    - name: Parse only variables from cifmw_cmd_args_vars
      when: cifmw_cmd_args_vars is defined and cifmw_cmd_args_vars | length > 0
      vars:
        various_vars: "{{ cifmw_cmd_args_vars }}"
      ansible.builtin.include_role:
        name: cifmw_helpers
        tasks_from: various_vars.yml

    - name: Fetch cifmw_cmd_args_files to executing host
      when: cifmw_cmd_args_files is defined and cifmw_cmd_args_files | length > 0
      ansible.builtin.fetch:
        src: "{{ files_item }}"
        dest: "{{ files_item }}"
        flat: true
      loop: "{{ cifmw_cmd_args_files }}"
      loop_control:
        loop_var: files_item

    - name: Read fetched var files from cmd_args
      when: cifmw_cmd_args_files is defined and cifmw_cmd_args_files | length > 0
      ansible.builtin.include_vars:
        file: "{{ files_item }}"
      loop: "{{ cifmw_cmd_args_files }}"
      loop_control:
        loop_var: files_item
```
