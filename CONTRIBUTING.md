# Contribute to the CI Framework

Thank you for your interest in that project, and for taking time to contribute!

## Create a new role

Run the following command to get your new role ready:

~~~Bash
[laptop]$ make new_role ROLE_NAME=my_wonderful_role
~~~

### Consuming install_yamls variables

CI Framework sets a couple of facts that are useful enough to mention, the
`cifmw_install_yamls_vars`, that contains all the install_yamls variables
that should be passed to any install_yamls target, and the `cifmw_install_yamls_default`,
that contains the default values of every possible parameter of the install_yamls
Makefiles.

Here is an example, based on a common use-case, on how to use those variables

~~~{code-block} YAML
:linenos:
---
- name: Deploy EDPM
  vars:
    make_edpm_deploy_env: "{{ cifmw_install_yamls_environment | combine({'PATH': cifmw_path }) }}"
    make_edpm_deploy_dryrun: "{{ cifmw_edpm_deploy_dryrun | bool }}"
  ansible.builtin.import_role:
    name: 'install_yamls_makes'
    tasks_from: 'make_edpm_deploy'
~~~

~~~{code-block} YAML
:linenos:
---
# Fetch openstackdataplane resources from the default namespace declared in install_yamls
# Makefile. If the NAMESPACE has been overridden by cifmw_install_yamls_vars this variable
# already points to the overridden value.
- name: Get info about dataplane node
  environment:
    PATH: "{{ cifmw_path }}"
  ansible.builtin.command: |
    oc get openstackdataplane -n {{ cifmw_install_yamls_defaults['NAMESPACE'] }}
~~~

### Documentation

A new role must get proper documentation. Please edit the README.md located in
the role directory in order to explain its use and details the exposed parameters.
Documentation must properly build and display in the CI preview job in order
for the PR to be accepted.

### Testing

A new role must get proper Molecule testing. Please edit the default ones, add
new scenarios if needed.

Then, you can run the following command in order to run tests locally:

~~~Bash
[laptop]$ make run_ctx_pre_commit
[laptop]$ make run_ctx_ansible_test
~~~

This will create a container, and run tests in it (pre-commit and ansible-test).

~~~{warning}
`podman` is needed for this step.
~~~

One can also run:

~~~Bash
[laptop]$ make enable-git-hooks
~~~

in order to configure automatic run of pre-commit tests in a local repository before
pushing changing to any branch (see .githooks/pre-push)

#### Can't get Molecule

If your role can't be tested via molecule, you can remove the "molecule" directory generated in the
role, and re-run `make role_molecule` to re-generate the the jobs and project list.

Please add a note in the role README.md for future reference.

## Adding new script

If you want/need to add a new script (python, bash, perl, ...), please provide
proper documentation related to its use and usage. Please list the needs the
script is covering, also in the commit message.

### Testing new script

For random scripts, only the pre-commit target is useful from the Makefile.
If you feel you can improve the testing, please create a new target in the
Makefile, so that we can integrate it in Prow later on.

### Help others debugging issues

If your code adds complex patterns, like consuming data sets and manipulating them in task vars,
be sure to use the `block/rescue` pattern as shown bellow. There are many other examples in the
framework code, and such pattern proves being of invaluable help whenever the run hits some
uncovered corner case.

```yaml
# Here we're creating tests in a block. You can of course put anything in such a block.
# You can also use such a block to share variables with multiple tasks.
- name: Try/catch block
  block:
    - name: Ensure all VM types have defined nets parameter
      ansible.builtin.assert:
        quiet: true
        that:
          - item.value.nets is defined
        msg: >-
          Inconsistency detected: VM type "{{ item.key }}"
          doesn't seem to have any network.
      loop: "{{ _cifmw_libvirt_manager_layout.vms | dict2items }}"
      loop_control:
        label: "{{ item.key }}"

# We caught an inconsistency, so we want to dump some data to make
# debugging easier. In this case, since the assert above is using
# the _cifmw_libvirt_manager_layout variable, we want to display it
# to ease debugging.
  rescue:
    - name: Dump built layout
      ansible.builtin.debug:
        var: _cifmw_libvirt_manager_layout

# Since "rescue" removes the errors, we have to get a proper "fail"
# to ensure we stop the whole run.
    - name: Fail for good
      ansible.builtin.fail:
        msg: >-
          Error detected, please check assertions and
          debugging output above.
```
