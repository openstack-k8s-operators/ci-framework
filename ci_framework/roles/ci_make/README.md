## Role: ci_make
Wrap community.general.make module and provides ordered playbook for each
call.

### Parameters
* `cifmw_ci_make_outputdir`: Output directory for the generated playbooks. Defaults
to "{{ ansible_user_dir }}/ci_output"
* `chdir`: community.general.make `chdir` (mandatory)
* `file`: community.general.make `file` (optional)
* `jobs`: community.general.make `jobs` (optional)
* `make`: community.general.make `make` (optional)
* `params`: community.general.make `params` (optional)
* `target`: community.general.make `target` (optional)
