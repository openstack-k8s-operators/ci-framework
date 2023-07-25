# Contribute to the CI Framework

Thank you for your interest in that project, and for taking time to contribute!

## Create a new role
Run the following command to get your new role ready:
```Bash
$ make create_new_role ROLE_NAME=my_wonderful_role
```

### Consuming install_yamls varibles
CI Framework sets a couple of facts that are useful enough to mention, the
`cifmw_install_yamls_vars`, that contains all the install_yamls variables
that should be passed to any install_yamls target, and the `cifmw_install_yamls_default`,
that contains the default values of every possible parameter of the install_yamls
Makefiles.

Here is an example, based on a common use-case, on how to use those variables
```YAML
- name: Deploy EDPM
  vars:
    make_edpm_deploy_env: "{{ cifmw_install_yamls_environment | combine({'PATH': cifmw_path }) }}"
    make_edpm_deploy_dryrun: "{{ cifmw_edpm_deploy_dryrun | bool }}"
  ansible.builtin.import_role:
    name: 'install_yamls_makes'
    tasks_from: 'make_edpm_deploy'
```

```YAML
# Fetch openstackdataplane resources from the default namespace declared in install_yamls
# Makefile. If the NAMESPACE has been overidden by cifmw_install_yamls_vars this variable
# already points to the overriden value.
- name: Get info about dataplane node
  environment:
    PATH: "{{ cifmw_path }}"
  ansible.builtin.command: |
    oc get openstackdataplane -n {{ cifmw_install_yamls_defaults['NAMESPACE'] }}
```

### Documentation
A new role must get proper documentation. Please edit the README.md located in
the role directory in order to explain its use and details the exposed parameters.

### Testing
A new role must get proper Molecule testing. Please edit the default ones, add
new scenarios if needed.

Then, you can run the following command in order to run tests locally:
```Bash
$ make run_ctx_pre_commit
$ make run_ctx_ansible_test
$ make run_ctx_molecule MOLECULE_CONFIG=.config/molecule/config_local.yml
```

This will create a container, and run tests in it (pre-commit, and molecule).

Note that `podman` as well as `buildah` are needed for this step.

One can also run:
```Bash
$ make enable-git-hooks
```

in order to configure automatic run of pre-commit tests in a local repository before
pushing changing to any branch (see .githooks/pre-push)

## Adding new script
If you want/need to add a new script (python, bash, perl, ...), please provide
proper documentation related to its use and usage. Please list the needs the
script is covering, also in the commit message.

### Testing
For random scripts, only the pre-commit target is useful from the Makefile.
If you feel you can improve the testing, please create a new target in the
Makefile, so that we can integrate it in Prow later on.
