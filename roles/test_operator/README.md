# Test operator

Execute tests via the [test-operator](https://openstack-k8s-operators.github.io/test-operator/).

<!-- START VARIABLES -->
### Generic Params

* `cifmw_test_operator_stages`: (Default: [Refer to `roles/test_operator/defaults/main.yml`])
* `cifmw_test_operator_fail_on_test_failure`: (Default: `True`) — Whether the role should fail on any test failure or not
* `cifmw_test_operator_temp_var`: (Default: `test`)
* `cifmw_test_operator_artifacts_basedir`: (Default: [Refer to `roles/test_operator/defaults/main.yml`]) — Directory where we will have all test-operator related files
* `cifmw_test_operator_namespace`: (Default: `openstack`) — Namespace inside which all the resources are created
* `cifmw_test_operator_controller_namespace`: (Default: `openstack-operators`) — Namespace inside which the test-operator-controller-manager is created
* `cifmw_test_operator_bundle`: (Default: ``) — Full name of container image with bundle that contains the test-operator
* `cifmw_test_operator_timeout`: (Default: `3600`)
* `cifmw_test_operator_logs_image`: (Default: `quay.io/quay/busybox`) — Image that should be used to collect logs from the pods spawned by the test-operator
* `cifmw_test_operator_cleanup`: (Default: `False`) — Delete all resources created by the role at the end of the testing
* `cifmw_test_operator_clean_last_run`: (Default: `False`) — Delete all resources created by the previous run at the beginning of the role
* `cifmw_test_operator_dry_run`: (Default: `False`) — Whether test-operator should run or not
* `cifmw_test_operator_default_groups`: (Default: [Refer to `roles/test_operator/defaults/main.yml`]) — List of groups in the include list to search for tests to be executed
* `cifmw_test_operator_default_jobs`: (Default: [Refer to `roles/test_operator/defaults/main.yml`]) — List of jobs in the exclude list to search for tests to be excluded
* `cifmw_test_operator_fail_fast`: (Default: `False`) — Whether the test results are evaluated when each test framework execution finishes or when all test frameworks are done
* `cifmw_test_operator_storage_class_prefix`: (Default: [Refer to `roles/test_operator/defaults/main.yml`]) — Prefix for `storageClass` in generated Tempest CRD file. Defaults to `"lvms-"` only if `cifmw_use_lvms` is True, otherwise it defaults to `""`. The prefix is prepended to the `cifmw_test_operator_storage_class`. It is not recommended to override this value, instead set `cifmw_use_lvms` True or False.
* `cifmw_test_operator_storage_class`: (String) Value for `storageClass` in generated Tempest or Tobiko CRD file. Defaults to `"lvms-local-storage"` only if `cifmw_use_lvms` is True, otherwise it defaults to `"local-storage"`.
* `cifmw_test_operator_delete_logs_pod`: (Boolean) Delete tempest log pod created by the role at the end of the testing
* `cifmw_test_operator_storage_class`: (Default: `{{ cifmw_test_operator_storage_class_prefix }}local-storage`)
* `cifmw_test_operator_delete_logs_pod`: (Default: `False`)
* `cifmw_test_operator_privileged`: (Default: `True`) — Spawn the test pods with `allowPrivilegedEscalation: true` and default linux capabilities. This is required for certain test-operator functionalities to work properly (e.g.: `extraRPMs`, certain set of tobiko tests)
* `cifmw_test_operator_selinux_level`: (Default: `s0:c478,c978`) — Specify SELinux level that should be used for pods spawned with the test-operator. Note, that `cifmw_test_operator_privileged: true` must be set when this parameter has non-empty value
* `cifmw_test_operator_crs_path`: (Default: [Refer to `roles/test_operator/defaults/main.yml`])
* `cifmw_test_operator_log_pod_definition`: (Default: [Refer to `roles/test_operator/defaults/main.yml`]) — The CR definition template for creating the test log pod
* `cifmw_test_operator_default_registry`: (Default: `quay.io`) — Default registry for all the supported test frameworks (tempest, tobiko, horizontest and ansibletest) to pull their container images. It can be overridden at test framework level.  Defaults to `quay.io`
* `cifmw_test_operator_default_namespace`: (String) Default registry's namespace for all the supported test frameworks (tempest, tobiko, horizontest and ansibletest) to pull their container images. It can be overridden at test framework level.  Defaults to `podified-antelope-centos9`
* `cifmw_test_operator_default_image_tag`: (String) Default tag for all the supported test frameworks (tempest, tobiko, horizontest and ansibletest) to pull their container images. It can be overridden at test framework level.  Defaults to `current-podified`
* `cifmw_test_operator_stages`: (List) List of dictionaries defining the stages that should be used in the test operator role. List items options are:
  * `name`: (String) The name of the stage. The name must be unique.
  * `type`: (String) The framework name you would like to call, currently the options are: tempest, ansibletest, horizontest, tobiko.
  * `test_vars_file`: (String) Path to the file used for testing, this file should contain the testing params for this stage. Only parameters specific for the controller can be used (Tempest, Ansibletest, Horizontest and Tobiko).
  * `test_vars`: (String) Testing parameters for this specific stage if a `test_vars` is used the specified parameters would override the ones in the `test_vars_file`. Only parameters specific for the controller can be used (Tempest, Ansibletest, Horizontest and Tobiko).
  > Important note! Generally only the variables with the following structure can be used to override inside a stage: `cifmw_test_operator_[test-operator CR name]_[parameter name]`. For example, these variables cannot be overridden per stage: `cifmw_test_operator_default_registry`, `cifmw_test_operator_default_namespace`, `cifmw_test_operator_default_image_tag`. One exception is `cifmw_test_operator_namespace`, which allows running the testing frameworks in multiple namespaces.
  * `pre_test_stage_hooks`: (List) List of pre hooks to run as described [hooks README](https://github.com/openstack-k8s-operators/ci-framework/tree/main/roles/run_hook#hooks-expected-format).
  * `post_test_stage_hooks`: (List) List of post hooks to run as described [hooks README](https://github.com/openstack-k8s-operators/ci-framework/tree/main/roles/run_hook#hooks-expected-format)
* `cifmw_test_operator_default_namespace`: (Default: `podified-antelope-centos9`)
* `cifmw_test_operator_default_image_tag`: (Default: `current-podified`)

### Tempest

<<<<<<< HEAD
## Tempest specific parameters
* `cifmw_test_operator_tempest_name`: (String) Value used in the `Tempest.Metadata.Name` field. The value specifies the name of some resources spawned by the test-operator role. Default value: `tempest-tests`
* `cifmw_test_operator_tempest_registry`: (String) The registry where to pull tempest container. Default value: `{{ cifmw_test_operator_default_registry }}`
* `cifmw_test_operator_tempest_namespace`: (String) Registry's namespace where to pull tempest container. Default value: `{{ cifmw_test_operator_default_namespace }}`
* `cifmw_test_operator_tempest_container`: (String) Name of the tempest container. Default value: `openstack-tempest`
* `cifmw_test_operator_tempest_image`: (String) Tempest image to be used. Default value: `{{ cifmw_test_operator_tempest_registry }}/{{ cifmw_test_operator_tempest_namespace }}/{{ cifmw_test_operator_tempest_container }}`
* `cifmw_test_operator_tempest_image_tag`: (String) Tag for the `cifmw_test_operator_tempest_image`. Default value: `{{ cifmw_test_operator_default_image_tag }}`
* `cifmw_test_operator_tempest_concurrency`: (Integer) The number of worker processes running tests concurrently. Default value: `8`
* `cifmw_test_operator_tempest_include_list`: (String) List of tests to be executed. Setting this will not use the `list_allowed` plugin. Default value: `''`
* `cifmw_test_operator_tempest_exclude_list`: (String) List of tests to be skipped. Setting this will not use the `list_skipped` plugin. Default value: `''`
* `cifmw_test_operator_tempest_expected_failures_list`: (String) List of tests for which failures will be ignored. Default value: `''`
* `cifmw_test_operator_tempest_external_plugin`: (List) List of dicts describing any external plugin to be installed. The dictionary contains a repository, changeRepository (optional) and changeRefspec (optional). Default value: `[]`
* `cifmw_test_operator_tempest_tests_include_override_scenario`: (Boolean) Whether to override the scenario `cifmw_test_operator_tempest_include_list` definition. Default value: `false`
* `cifmw_test_operator_tempest_tests_exclude_override_scenario`: (Boolean) Whether to override the scenario `cifmw_test_operator_tempest_exclude_list` definition. Default value: `false`
* `cifmw_test_operator_tempest_parallel`: (Boolean) Enable parallel execution of steps in workflow. Default value: `false`
* `cifmw_test_operator_tempest_ssh_key_secret_name`: (String) Name of a secret that contains ssh-privatekey field with a private key. The private key is mounted to `/var/lib/tempest/.ssh/id_ecdsa`
* `cifmw_test_operator_tempest_config_overwrite`: (Dict) Dictionary where key is name of a file and value is content of the file. All files mentioned in this field are mounted to `/etc/test_operator/<filename>`
* `cifmw_test_operator_tempest_workflow`: (List) Definition of a Tempest workflow that consists of multiple steps. Each step can contain all values from Spec section of [Tempest CR](https://openstack-k8s-operators.github.io/test-operator/crds.html#tempest-custom-resource).
* `cifmw_test_operator_tempest_extra_images`: (List) A list of images that should be uploaded to OpenStack before the tests are executed. The value is passed to extraImages parameter in the [Tempest CR](https://openstack-k8s-operators.github.io/test-operator/crds.html#tempest-custom-resource). Default value: `[]`
* `cifmw_test_operator_tempest_network_attachments`: (List) List of network attachment definitions to attach to the tempest pods spawned by test-operator. Default value: `[]`.
* `cifmw_test_operator_tempest_extra_rpms`: (List) . A list of URLs that point to RPMs that should be installed before the execution of tempest. Note that this parameter has no effect when `cifmw_test_operator_tempest_external_plugin` is used. Default value: `[]`
* `cifmw_test_operator_tempest_extra_configmaps_mounts`: WARNING: This parameter will be deprecated! Please use `cifmw_test_operator_tempest_extra_mounts` parameter instead. (List) A list of configmaps that should be mounted into the tempest test pods. Default value: `[]`
* `cifmw_test_operator_tempest_extra_mounts`: (List) A list of additional volume mounts for the tempest test pods. Each item specifies a volume name, mount path, and other mount properties. Default value: `[]`
* `cifmw_test_operator_tempest_debug`: (Bool) Run Tempest in debug mode, it keeps the operator pod sleeping infinity (it must only set to `true`only for debugging purposes). Default value: `false`
* `cifmw_test_operator_tempest_rerun_failed_tests`: (Bool) Activate tempest re-run feature. When activated, tempest will perform another run of the tests that failed during the first execution. Default value: `false`
* `cifmw_test_operator_tempest_rerun_override_status`: (Bool) Allow override of exit status with the tempest re-run feature. When activated, the original return value of the tempest run will be overridden with a result of the tempest run on the set of failed tests. Default value: `false`
* `cifmw_test_operator_tempest_timing_data_url`: (String) An URL pointing to an archive that contains the saved timing data. This data is used to optimize the test order and reduce Tempest execution time. Default value: `''`
* `cifmw_test_operator_tempest_resources`: (Dict) A dictionary that specifies resources (cpu, memory) for the test pods. When untouched it clears the default values set on the test-operator side. This means that the tempest test pods run with unspecified resource limits. Default value: `{requests: {}, limits: {}}`
* `cifmw_tempest_tempestconf_config`: Deprecated, please use `cifmw_test_operator_tempest_tempestconf_config` instead
* `cifmw_test_operator_tempest_tempestconf_config`: (Dict) This parameter can be used to customize the execution of the `discover-tempest-config` run. Please consult the test-operator documentation. For example, to pass a custom configuration for `tempest.conf`, use the `overrides` section:
=======
* `cifmw_test_operator_tempest_name`: (Default: `tempest-tests`) — Value used in the `Tempest.Metadata.Name` field. The value specifies the name of some resources spawned by the test-operator role
* `cifmw_test_operator_tempest_test`: (Default: `{{ cifmw_test_operator_tolerations | default(omit) }}`)
* `cifmw_test_operator_tempest_concurrency`: (Default: `8`) — The number of worker processes running tests concurrently
* `cifmw_test_operator_tempest_registry`: (Default: `{{ cifmw_test_operator_default_registry }}`) — The registry where to pull tempest container
* `cifmw_test_operator_tempest_namespace`: (Default: `{{ cifmw_test_operator_default_namespace }}`) — Registry's namespace where to pull tempest container
* `cifmw_test_operator_tempest_container`: (Default: `openstack-tempest-all`) — Name of the tempest container
* `cifmw_test_operator_tempest_image`: (Default: [Refer to `roles/test_operator/defaults/main.yml`]) — Tempest image to be used
* `cifmw_test_operator_tempest_image_tag`: (Default: `{{ cifmw_test_operator_default_image_tag }}`) — Tag for the `cifmw_test_operator_tempest_image`
* `cifmw_test_operator_tempest_network_attachments`: (Default: [Refer to `roles/test_operator/defaults/main.yml`]) — List of network attachment definitions to attach to the tempest pods spawned by test-operator
* `cifmw_test_operator_tempest_tests_include_override_scenario`: (Default: `False`) — Whether to override the scenario `cifmw_test_operator_tempest_include_list` definition
* `cifmw_test_operator_tempest_tests_exclude_override_scenario`: (Default: `False`) — Whether to override the scenario `cifmw_test_operator_tempest_exclude_list` definition
* `cifmw_test_operator_tempest_workflow`: (Default: [Refer to `roles/test_operator/defaults/main.yml`])
* `cifmw_test_operator_tempest_cleanup`: (Default: `False`) — Run tempest cleanup after test execution (tempest run) to delete any resources created by tempest that may have been left out.
* `cifmw_test_operator_crs_path`: (String) The path into which the tests CRs file will be created in
* `cifmw_test_operator_tempest_rerun_failed_tests`: (Default: `False`) — Activate tempest re-run feature. When activated, tempest will perform another run of the tests that failed during the first execution
* `cifmw_test_operator_tempest_rerun_override_status`: (Default: `False`) — Allow override of exit status with the tempest re-run feature. When activated, the original return value of the tempest run will be overridden with a result of the tempest run on the set of failed tests
* `cifmw_test_operator_tempest_tempestconf_config`: (Default: `{{ cifmw_tempest_tempestconf_config }}`) — This parameter can be used to customize the execution of the `discover-tempest-config` run. Please consult the test-operator documentation. For example, to pass a custom configuration for `tempest.conf`, use the `overrides` section:
>>>>>>> 0daf6d11 (Testing my script to update the README.md file to sync variables of tesat-operator role from defaults/main.yml)
```
cifmw_test_operator_tempest_tempestconf_config:
  overrides: |
    identity.v3_endpoint_type public
* `cifmw_test_operator_tempest_resources`: (Default: [Refer to `roles/test_operator/defaults/main.yml`]) — A dictionary that specifies resources (cpu, memory) for the test pods. When untouched it clears the default values set on the test-operator side. This means that the tempest test pods run with unspecified resource limits
* `cifmw_tempest_tempestconf_config_defaults`: (Default: [Refer to `roles/test_operator/defaults/main.yml`])
* `cifmw_test_operator_tempest_debug`: (Default: `False`) — Run Tempest in debug mode, it keeps the operator pod sleeping infinity (it must only set to `true`only for debugging purposes)
* `cifmw_test_operator_tempest_temp_var`: (Default: [Refer to `roles/test_operator/defaults/main.yml`])
* `cifmw_test_operator_tempest_config`: (Default: [Refer to `roles/test_operator/defaults/main.yml`]) — Definition of Tempest CRD instance that is passed to the test-operator (see [the test-operator documentation](https://openstack-k8s-operators.github.io/test-operator/crds.html#tempest-custom-resource))

### Tobiko

* `cifmw_test_operator_tobiko_name`: (Default: `tobiko-tests`) — Value used in the `Tobiko.Metadata.Name` field. The value specifies the name of some resources spawned by the test-operator role
* `cifmw_test_operator_tobiko_registry`: (Default: `{{ cifmw_test_operator_default_registry }}`) — The registry where to pull tobiko container
* `cifmw_test_operator_tobiko_namespace`: (Default: `{{ cifmw_test_operator_default_namespace }}`) — Registry's namespace where to pull tobiko container
* `cifmw_test_operator_tobiko_container`: (Default: `openstack-tobiko`) — Name of the tobiko container
* `cifmw_test_operator_tobiko_image`: (Default: [Refer to `roles/test_operator/defaults/main.yml`]) — Tobiko image to be used
* `cifmw_test_operator_tobiko_image_tag`: (Default: `{{ cifmw_test_operator_default_image_tag }}`) — Tag for the `cifmw_test_operator_tobiko_image`
* `cifmw_test_operator_tobiko_testenv`: (Default: `scenario`) — Executed tobiko testenv. See tobiko `tox.ini` file for further details. Some allowed values: scenario, sanity, faults, neutron, octavia, py3, etc
* `cifmw_test_operator_tobiko_version`: (Default: `master`) — Tobiko version to install. It could refer to a branch (master, osp-16.2), a tag (0.6.x, 0.7.x) or an sha-1
* `cifmw_test_operator_tobiko_pytest_addopts`: (Default: `None`) — `PYTEST_ADDOPTS` env variable with input pytest args. Example: `-m <markers> --maxfail <max-failed-tests> --skipregex <regex>`. Defaults to `null`. In case of `null` value, `PYTEST_ADDOPTS` is not set (tobiko tests are executed without any extra pytest options).
* `cifmw_test_operator_tobiko_prevent_create`: (Boolean) Sets the value of the env variable `TOBIKO_PREVENT_CREATE` that specifies whether tobiko scenario tests create new resources or expect that those resource had been created before. Default to `null`. In case of `null` value, `TOBIKO_PREVENT_CREATE` is not set (tobiko tests create new resources).
* `cifmw_test_operator_tobiko_num_processes`: (Integer) Sets the value of the env variable `TOX_NUM_PROCESSES` that is used to run pytest with `--numprocesses $TOX_NUM_PROCESSES`. Defaults to `null`. In case of `null` value, `TOX_NUM_PROCESSES` is not set (tobiko internally uses the value `auto`, see pytest documentation about the `--numprocesses` option).
* `cifmw_test_operator_tobiko_advanced_image_url`: (String) Tobiko will download images from this URL that will be used to create advance VM instances. By default, the provided image will include all the customizations required by the tobiko tests. Defaults to `https://softwarefactory-project.io/ubuntu-minimal-customized-enp3s0`.
* `cifmw_test_operator_tobiko_kubeconfig_secret`: (String) Name of the Openshift Secret required to use Openshift Client from the Tobiko pod
* `cifmw_test_operator_tobiko_prevent_create`: (Default: `None`)
* `cifmw_test_operator_tobiko_num_processes`: (Default: `None`)
* `cifmw_test_operator_tobiko_advanced_image_url`: (Default: [Refer to `roles/test_operator/defaults/main.yml`])
* `cifmw_test_operator_tobiko_override_conf`: (Default: [Refer to `roles/test_operator/defaults/main.yml`]) — Overrides the default configuration from `cifmw_test_operator_tobiko_default_conf` that is used to generate the tobiko.conf file
* `cifmw_test_operator_tobiko_kubeconfig_secret`: (Default: `tobiko-secret`)
* `cifmw_test_operator_tobiko_openstack_cmd`: (Default: `oc -n openstack exec openstackclient -- openstack`) — Openstack command is used by tobiko to cleanup resources
* `cifmw_test_operator_tobiko_cleanup`: (Default: `False`) — Cleanup all resources created by tobiko
* `cifmw_test_operator_tobiko_ssh_keytype`: (Default: `{{ cifmw_ssh_keytype | default('ecdsa') }}`) — Type of ssh key that tobiko will use to connect to the VM instances it creates. Defaults to `cifmw_ssh_keytype` which default to `ecdsa`.
* `cifmw_test_operator_tobiko_ssh_keysize`: (Integer) Size of ssh key that tobiko will use to connect to the VM instances it creates. Defaults to `cifmw_ssh_keysize` which defaults to 521.
* `cifmw_test_operator_tobiko_debug`: (Bool) Run Tobiko in debug mode, it keeps the operator pod sleeping infinity (it must only set to `true`only for debugging purposes)
* `cifmw_test_operator_tobiko_ssh_keysize`: (Default: `{{ cifmw_ssh_keysize | default(521) }}`)
* `cifmw_test_operator_tobiko_debug`: (Default: `False`)
* `cifmw_test_operator_tobiko_network_attachments`: (Default: [Refer to `roles/test_operator/defaults/main.yml`]) — List of network attachment definitions to attach to the tobiko pods spawned by test-operator
* `cifmw_test_operator_tobiko_workflow`: (Default: [Refer to `roles/test_operator/defaults/main.yml`]) — Definition of a Tobiko workflow that consists of multiple steps. Each step can contain all values from Spec section of [Tobiko CR](https://openstack-k8s-operators.github.io/test-operator/crds.html#tobiko-custom-resource).
* `cifmw_test_operator_tobiko_resources`: (Dict) A dictionary that specifies resources (cpu, memory) for the test pods. When kept untouched it defaults to the resource limits specified on the test-operator side
* `cifmw_test_operator_tobiko_config`: (Default: [Refer to `roles/test_operator/defaults/main.yml`]) — Definition of Tobiko CRD instance that is passed to the test-operator (see [the test-operator documentation](https://openstack-k8s-operators.github.io/test-operator/crds.html#tobiko-custom-resource))

### AnsibleTest

* `cifmw_test_operator_ansibletest_name`: (Default: `ansibletest`) — Value used in the `Ansibletest.Metadata.Name` field. The value specifies the name of some resources spawned by the test-operator role
* `cifmw_test_operator_ansibletest_registry`: (Default: `{{ cifmw_test_operator_default_registry }}`) — The registry where to pull ansibletests container
* `cifmw_test_operator_ansibletest_namespace`: (Default: `{{ cifmw_test_operator_default_namespace }}`) — Registry's namespace where to pull ansibletests container
* `cifmw_test_operator_ansibletest_container`: (Default: `openstack-ansible-tests`) — Name of the ansibletests container
* `cifmw_test_operator_ansibletest_image`: (Default: [Refer to `roles/test_operator/defaults/main.yml`]) — Ansibletests image to be used
* `cifmw_test_operator_ansibletest_image_tag`: (Default: `{{ cifmw_test_operator_default_image_tag }}`) — Ansibletests image to be used
* `cifmw_test_operator_ansibletest_compute_ssh_key_secret_name`: (Default: `dataplane-ansible-ssh-private-key-secret`) — The name of the k8s secret that contains an ssh key for computes
* `cifmw_test_operator_ansibletest_workload_ssh_key_secret_name`: (Default: ``) — The name of the k8s secret that contains an ssh key for the ansible workload
* `cifmw_test_operator_ansibletest_ansible_git_repo`: (Default: ``) — Git repo to clone into container
* `cifmw_test_operator_ansibletest_ansible_playbook_path`: (Default: ``) — Path to ansible playbook
* `cifmw_test_operator_ansibletest_ansible_collection`: (Default: ``) — Extra ansible collections to install in addition to the ones that exist in the requirements.yaml
* `cifmw_test_operator_ansibletest_ansible_var_files`: (Default: ``) — interface to create ansible var files
* `cifmw_test_operator_ansibletest_ansible_extra_vars`: (Default: ``) — string to pass parameters to ansible
* `cifmw_test_operator_ansibletest_ansible_inventory`: (Default: ``) — string that contains the inventory file content
* `cifmw_test_operator_ansibletest_openstack_config_map`: (Default: `openstack-config`) — The name of the ConfigMap containing the clouds.yaml
* `cifmw_test_operator_ansibletest_openstack_config_secret`: (Default: `openstack-config-secret`) — The name of the Secret containing the secure.yaml
* `cifmw_test_operator_ansibletest_debug`: (Default: `False`) — Run ansible playbook with -vvvv
* `cifmw_test_operator_ansibletest_workflow`: (Default: [Refer to `roles/test_operator/defaults/main.yml`]) — A parameter that contains a workflow definition
* `cifmw_test_operator_ansibletest_extra_configmaps_mounts`: (Default: [Refer to `roles/test_operator/defaults/main.yml`])
* `cifmw_test_operator_ansibletest_config`: (Default: [Refer to `roles/test_operator/defaults/main.yml`])

### HorizonTest

* `cifmw_test_operator_horizontest_name`: (Default: `horizontest-tests`)
* `cifmw_test_operator_horizontest_registry`: (Default: `{{ cifmw_test_operator_default_registry }}`) — The registry where to pull horizontest container
* `cifmw_test_operator_horizontest_namespace`: (Default: `{{ cifmw_test_operator_default_namespace }}`) — Registry's namespace where to pull horizontest container
* `cifmw_test_operator_horizontest_container`: (Default: `openstack-horizontest`) — Name of the horizontest container
* `cifmw_test_operator_horizontest_image`: (Default: [Refer to `roles/test_operator/defaults/main.yml`]) — Horizontest image to be used
* `cifmw_test_operator_horizontest_image_tag`: (Default: `{{ cifmw_test_operator_default_image_tag }}`) — Tag for the `cifmw_test_operator_horizontest_image`
* `cifmw_test_operator_horizontest_admin_username`: (Default: `admin`) — OpenStack admin credentials
* `cifmw_test_operator_horizontest_admin_password`: (Default: `12345678`) — OpenStack admin credentials
* `cifmw_test_operator_horizontest_dashboard_url`: (Default: `https://horizon-openstack.apps.ocp.openstack.lab/`) — The URL of the Horizon dashboard
* `cifmw_test_operator_horizontest_auth_url`: (Default: `https://keystone-public-openstack.apps.ocp.openstack.lab`) — The OpenStack authentication URL
* `cifmw_test_operator_horizontest_repo_url`: (Default: `https://review.opendev.org/openstack/horizon`) — The Horizon tests repository URL
* `cifmw_test_operator_horizontest_horizon_repo_branch`: (Default: `master`) — The branch of the Horizon repository to checkout
* `cifmw_test_operator_horizontest_image_url`: (Default: [Refer to `roles/test_operator/defaults/main.yml`]) — The URL to download the Cirros image
* `cifmw_test_operator_horizontest_project_name`: (Default: `horizontest`) — The name of the OpenStack project for Horizon tests
* `cifmw_test_operator_horizontest_user`: (Default: `horizontest`) — The username under which Horizon tests will run
* `cifmw_test_operator_horizontest_password`: (Default: `horizontest`) — The password for the user running the Horizon tests
* `cifmw_test_operator_horizontest_flavor_name`: (Default: `m1.tiny`) — The name of the OpenStack flavor to create for Horizon tests
* `cifmw_test_operator_horizontest_logs_directory_name`: (Default: `horizon`) — The name of the directory to store test logs
* `cifmw_test_operator_horizontest_debug`: (Default: `False`) — Run HorizonTest in debug mode, it keeps the operator pod sleeping infinitely (it must only set to `true` only for debugging purposes)
* `cifmw_test_operator_horizontest_horizon_test_dir`: (Default: `/var/lib/horizontest`) — The directory path for Horizon tests
* `cifmw_test_operator_horizontest_extra_flag`: (Default: `not pagination`) — The extra flag to modify pytest command to include/exclude tests
* `cifmw_test_operator_horizontest_project_name_xpath`: (Default: `//span[@class='rcueicon rcueicon-folder-open']/ancestor::li`) — The xpath to select project name based on dashboard theme
* `cifmw_test_operator_horizontest_config`: (Default: [Refer to `roles/test_operator/defaults/main.yml`]) — Definition of HorizonTest CR instance that is passed to the test-operator (see [the test-operator documentation](https://openstack-k8s-operators.github.io/test-operator/crds.html#horizontest-custom-resource))
<!-- END VARIABLES -->

## Examples

### Execute the `test-operator` role multiple times within a single job

If you want to run the `test-operator` role twice within a single job, make sure
that for the second run, you specify a value for the `cifmw_test_operator_*_name`
other than the default one (e.g., `tempest-tests`, `tobiko-tests`, ...):

```
cifmw_test_operator_tempest_name: "post-update-tempest-tests"
```

### Use test operator stages
Test operator stages are meant to allow setting the order of stages,running stages
of the same controller multiple times and using different hooks,vars and names for stages.
```
cifmw_test_operator_stages:
  - name: basic-functionallity
    type: tempest
    test_vars:
      cifmw_test_operator_tempest_name: 'basic-functionality-tests'
  - name: ansibletest
    type: ansibletest
  - name: advanced-tests
    type: tempest
    test_vars:
      cifmw_test_operator_tempest_name: 'advanced-tests'
  - name: tobiko
    type: tobiko
    test_vars_file: /path/to/tobiko/override/test/file
```