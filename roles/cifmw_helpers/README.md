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

Of course, before Zuul execute the playbook, it is mandatory to call `playbooks/cifmw_collection_zuul_executor.yml`.

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
