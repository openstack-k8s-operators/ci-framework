# polarion
Role to setup jump tool and upload XML test results to Polarion.

## Parameters
* `cifmw_polarion_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_polarion_jump_repo_dir`: (String) Jump repo directory. Defaults to `~/ci-framework-data/polarion-jump`.
* `cifmw_polarion_jump_result_dir`: (String) Test results directory. Based on `cifmw_run_test_role` defaults to `~/ci-framework-data/tests/tempest/` or `~/ci-framework-data/tests/test_operator/`.
* `cifmw_polarion_jump_repo_url`: (String) URL of jump repository.
* `cifmw_polarion_testrun_title`: (String) A name of the test run under which the test results will be uploaded to polarion. The role appends an index number to the name to distinguish multiple test runs apart.
* `cifmw_polarion_testrun_id`: (String) A test run identification provided by Polarion test case or `create-new-test-run` if polarion should generate a random test run ID. A value other than `create-new-test-run` will force this role to upload all test results found in all directories under `cifmw_polarion_jump_repo_url` to one test run identified by the given ID. The default behavior of this role is to treat the directories in `cifmw_polarion_jump_repo_url` as separate test runs.
* `cifmw_polarion_update_testcases`: (Boolean) A value of True/False to create missing testcases (which should normally _not_ be enabled).
* `cifmw_polarion_jump_extra_vars`: (String) A list of extra_vars that are being passed to the jump script. Defaults to empty.
* `cifmw_polarion_jump_custom_fields`: (Dict) Structure listing the fields for --custom-fields argument of jump tool.
* `cifmw_polarion_use_stage`: (Bool) Flag for using the staging instance of Polarion. Default is False meaning the production instance gets updated. Don't forget to change for testing on stage instance.


## Examples
```YAML
- name: Play
  hosts: localhost
  vars:
    cifmw_polarion_jump_repo_url: "https://example.com/repo.git"
    cifmw_polarion_testrun_id: "20230101-0001"
    cifmw_polarion_use_stage: true  # uploading to the staging instance
    cifmw_polarion_jump_extra_vars: >-
      "--dfg '' --jenkins_build_url='' --puddle-id='' --custom-fields build='' --remove-old-tests='' --update-existing-test-cases=''"
  roles:
    - polarion
```

## Molecule
This role exclusively relies on the internal Polarion instance and other internal repositories.
Molecule cannot run and mimic it in an environment outside the designated network segment.
