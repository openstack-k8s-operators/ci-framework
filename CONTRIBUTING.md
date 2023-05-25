# Contribute to the CI Framework

Thank you for your interest in that project, and for taking time to contribute!

## Create a new role
Run the following command to get your new role ready:
```Bash
$ ansible-galaxy role init --role-skeleton _skeleton_role_ --init-path ci_framework/roles ROLENAME
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
