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
