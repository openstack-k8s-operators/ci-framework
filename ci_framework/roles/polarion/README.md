# polarion
Role to setup jump tool and upload XML test results to Polarion.

## Parameters
* `cifmw_polarion_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_polarion_jump_repo_dir`: (String) Jump repo directory. Defaults to `~/ci-framework-data/polarion-jump`.
* `cifmw_polarion_jump_result_dir`: (String) Test results directory. Defaults to `~/ci-framework-data/tests/tempest/`.
* `cifmw_polarion_jump_repo_url`: (String) URL of jump repository.
* `cifmw_polarion_test_id`: (String) A test-id provided by Polarion test case.
* `cifmw_polarion_update_testcases`: (Boolean) A value of True/False to update the testcase.
* `cifmw_polarion_jump_extra_vars`: (String) A list of extra_vars that are being passed to the jump script. Defaults to empty.

## Examples
```YAML
- name: Play
  hosts: localhost
  vars:
    cifmw_polarion_jump_repo_url: "https://example.com/repo.git"
    cifmw_polarion_test_id: "20230101-0001"
    cifmw_polarion_update_testcases: true
    cifmw_polarion_jump_extra_vars: >-
      "--dfg '' --jenkins_build_url='' --puddle-id='' --custom-fields build='' --remove-old-tests='' --update-existing-test-cases=''"
  roles:
    - polarion
```
