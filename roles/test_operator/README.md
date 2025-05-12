# Test operator

Execute tests via the [test-operator](https://openstack-k8s-operators.github.io/test-operator/).

## Parameters
* `cifmw_test_operator_artifacts_basedir`: (String) Directory where we will have all test-operator related files. Default value: `{{ cifmw_basedir }}/tests/test_operator` which defaults to `~/ci-framework-data/tests/test_operator`
* `cifmw_test_operator_namespace`: (String) Namespace inside which all the resources are created. Default value: `openstack`
* `cifmw_test_operator_controller_namespace`: (String) Namespace inside which the test-operator-controller-manager is created. Default value: `openstack-operators`
* `cifmw_test_operator_bundle`: (String) Full name of container image with bundle that contains the test-operator. Default value: `""`
* `cifmw_test_operator_version`: (String) The commit hash corresponding to the version of test-operator the user wants to use. This parameter is only used when `cifmw_test_operator_bundle` is also set.
* `cifmw_test_operator_timeout`: (Integer) Timeout in seconds for the execution of the tests. Default value: `3600`
* `cifmw_test_operator_logs_image`: (String) Image that should be used to collect logs from the pods spawned by the test-operator. Default value: `quay.io/quay/busybox`
* `cifmw_test_operator_concurrency`: (Integer) Tempest concurrency value. NOTE: This parameter is deprecated, please use `cifmw_test_operator_tempest_concurrency` instead. Default value: `8`
* `cifmw_test_operator_cleanup`: (Bool) Delete all resources created by the role at the end of the testing. Default value: `false`
* `cifmw_test_operator_tempest_cleanup`: (Bool) Run tempest cleanup after test execution (tempest run) to delete any resources created by tempest that may have been left out.
* `cifmw_test_operator_default_groups`: (List) List of groups in the include list to search for tests to be executed. Default value: `[ 'default' ]`
* `cifmw_test_operator_default_jobs`: (List) List of jobs in the exclude list to search for tests to be excluded. Default value: `[ 'default' ]`
* `cifmw_test_operator_dry_run`: (Boolean) Whether test-operator should run or not. Default value: `false`
* `cifmw_test_operator_fail_fast`: (Boolean) Whether the test results are evaluated when each test framework execution finishes or when all test frameworks are done. Default value: `false`
* `cifmw_test_operator_fail_on_test_failure`: (Boolean) Whether the role should fail on any test failure or not. Default value: `true`
* `cifmw_test_operator_controller_ip`: (String) An ip address of the controller node. Default value: `ansible_default_ipv4.address` which defaults to (`""`).
* `cifmw_test_operator_tolerations`: (Dict) `tolerations` value that is applied to all pods spawned by the test-operator and to the test-operator-controller-manager and test-operator-logs pods. Default value: `{}`
* `cifmw_test_operator_node_selector`: (Dict) `nodeSelector` value that is applied to all pods spawned by the test-operator and to the test-operator-controller-manager and test-operator-logs pods. Default value: `{}`
* `cifmw_test_operator_storage_class_prefix`: (String) Prefix for `storageClass` in generated Tempest CRD file. Defaults to `"lvms-"` only if `cifmw_use_lvms` is True, otherwise it defaults to `""`. The prefix is prepended to the `cifmw_test_operator_storage_class`. It is not recommended to override this value, instead set `cifmw_use_lvms` True or False.
* `cifmw_test_operator_storage_class`: (String) Value for `storageClass` in generated Tempest or Tobiko CRD file. Defaults to `"lvms-local-storage"` only if `cifmw_use_lvms` is True, otherwise it defaults to `"local-storage"`.
* `cifmw_test_operator_delete_logs_pod`: (Boolean) Delete tempest log pod created by the role at the end of the testing. Default value: `false`.
* `cifmw_test_operator_privileged`: (Boolean) Spawn the test pods with `allowPrivilegedEscalation: true` and default linux capabilities. This is required for certain test-operator functionalities to work properly (e.g.: `extraRPMs`, certain set of tobiko tests). Default value: `true`
* `cifmw_test_operator_selinux_level`: (String) Specify SELinux level that should be used for pods spawned with the test-operator. Note, that `cifmw_test_operator_privileged: true` must be set when this parameter has non-empty value. Default value: `s0:c478,c978`
* `cifmw_test_operator_default_registry`: (String) Default registry for all the supported test frameworks (tempest, tobiko, horizontest and ansibletest) to pull their container images. It can be overridden at test framework level.  Defaults to `quay.io`
* `cifmw_test_operator_default_namespace`: (String) Default registry's namespace for all the supported test frameworks (tempest, tobiko, horizontest and ansibletest) to pull their container images. It can be overridden at test framework level.  Defaults to `podified-antelope-centos9`
* `cifmw_test_operator_default_image_tag`: (String) Default tag for all the supported test frameworks (tempest, tobiko, horizontest and ansibletest) to pull their container images. It can be overridden at test framework level.  Defaults to `current-podified`
* `cifmw_test_operator_stages`: (List) List of dictionaries defining the stages that should be used in the test operator role. List items options are:
  * `name`: (String) The name of the stage. The name must be unique.
  * `type`: (String) The framework name you would like to call, currently the options are: tempest, ansibletest, horizontest, tobiko.
  * `test_vars_file`: (String) Path to the file used for testing, this file should contain the testing params for this stage. Only parameters specific for the controller can be used (Tempest, Ansibletest, Horizontest and Tobiko).
  * `test_vars`: (String) Testing parameters for this specific stage if a `test_vars` is used the specified parameters would override the ones in the `test_vars_file`. Only parameters specific for the controller can be used (Tempest, Ansibletest, Horizontest and Tobiko).
  > Important note! Only variables with the following structure can be used to override inside a stage: `cifmw_test_operator_[test-operator CR name]_[parameter name]`. For example, these variables cannot be overridden per stage: `cifmw_test_operator_default_registry`, `cifmw_test_operator_default_namespace`, `cifmw_test_operator_default_image_tag`.
  * `pre_test_stage_hooks`: (List) List of pre hooks to run as described [hooks README](https://github.com/openstack-k8s-operators/ci-framework/tree/main/roles/run_hook#hooks-expected-format).
  * `post_test_stage_hooks`: (List) List of post hooks to run as described [hooks README](https://github.com/openstack-k8s-operators/ci-framework/tree/main/roles/run_hook#hooks-expected-format).
 Default value:
```
cifmw_test_operator_stages:
  - name: tempest
    type: tempest
```


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
* `cifmw_test_operator_tempest_extra_configmaps_mounts`: (List) A list of configmaps that should be mounted into the tempest test pods. Default value: `[]`
* `cifmw_test_operator_tempest_extra_mounts`: (List) A list of additional volume mounts for the tempest test pods. Each item specifies a volume name, mount path, and other mount properties. Default value: `[]`
* `cifmw_test_operator_tempest_debug`: (Bool) Run Tempest in debug mode, it keeps the operator pod sleeping infinity (it must only set to `true`only for debugging purposes). Default value: `false`
* `cifmw_test_operator_tempest_resources`: (Dict) A dictionary that specifies resources (cpu, memory) for the test pods. When untouched it clears the default values set on the test-operator side. This means that the tempest test pods run with unspecified resource limits. Default value: `{requests: {}, limits: {}}`
* `cifmw_tempest_tempestconf_config`: Deprecated, please use `cifmw_test_operator_tempest_tempestconf_config` instead
* `cifmw_test_operator_tempest_tempestconf_config`: (Dict) This parameter can be used to customize the execution of the `discover-tempest-config` run. Please consult the test-operator documentation. For example, to pass a custom configuration for `tempest.conf`, use the `overrides` section:
```
cifmw_test_operator_tempest_tempestconf_config:
  overrides: |
    identity.v3_endpoint_type public
Default value: {}
```
* `cifmw_test_operator_tempest_config`: (Object) Definition of Tempest CRD instance that is passed to the test-operator (see [the test-operator documentation](https://openstack-k8s-operators.github.io/test-operator/crds.html#tempest-custom-resource)). Default value:
```
  apiVersion: test.openstack.org/v1beta1
  kind: Tempest
  metadata:
    name: "{{ cifmw_test_operator_tempest_name }}"
    namespace: "{{ cifmw_test_operator_namespace }}"
  spec:
    containerImage: "{{ cifmw_test_operator_tempest_image }}:{{ cifmw_test_operator_tempest_image_tag }}"
    storageClass: "{{ cifmw_test_operator_storage_class }}"
    tolerations: "{{ cifmw_test_operator_tolerations | default(omit) }}"
    nodeSelector: "{{ cifmw_test_operator_node_selector | default(omit) }}"
    networkAttachments: "{{ cifmw_test_operator_tempest_network_attachments }}"
    tempestRun:
      includeList: |
        {{ cifmw_test_operator_tempest_include_list | default('') }}
      excludeList: |
        {{ cifmw_test_operator_tempest_exclude_list | default('') }}
      concurrency: "{{ cifmw_test_operator_tempest_concurrency | default(8) }}"
      externalPlugin: "{{ cifmw_test_operator_tempest_external_plugin | default([]) }}"
      extraRPMs: "{{ cifmw_test_operator_tempest_extra_rpms | default([]) }}"
      extraImages: "{{ cifmw_test_operator_tempest_extra_images | default([]) }}"
    tempestconfRun: "{{ cifmw_test_operator_tempest_tempestconf_config | default(omit) }}"
    debug: "{{ cifmw_test_operator_tempest_debug }}"
```

## Tobiko specific parameters
* `cifmw_test_operator_tobiko_name`: (String) Value used in the `Tobiko.Metadata.Name` field. The value specifies the name of some resources spawned by the test-operator role. Default value: `tobiko-tests`
* `cifmw_test_operator_tobiko_registry`: (String) The registry where to pull tobiko container. Default value: `{{ cifmw_test_operator_default_registry }}`
* `cifmw_test_operator_tobiko_namespace`: (String) Registry's namespace where to pull tobiko container. Default value: `{{ cifmw_test_operator_default_namespace }}`
* `cifmw_test_operator_tobiko_cleanup`: (Boolean) Cleanup all resources created by tobiko. Default value: `false`
* `cifmw_test_operator_tobiko_container`: (String) Name of the tobiko container. Default value: `openstack-tobiko`
* `cifmw_test_operator_tobiko_image`: (String) Tobiko image to be used. Default value: `{{ cifmw_test_operator_tobiko_registry }}/{{ cifmw_test_operator_tobiko_namespace }}/{{ cifmw_test_operator_tobiko_container }}`
* `cifmw_test_operator_tobiko_image_tag`: (String) Tag for the `cifmw_test_operator_tobiko_image`. Default value: `{{ cifmw_test_operator_default_image_tag }}`
* `cifmw_test_operator_tobiko_testenv`: (String) Executed tobiko testenv. See tobiko `tox.ini` file for further details. Some allowed values: scenario, sanity, faults, neutron, octavia, py3, etc. Default value: `scenario`
* `cifmw_test_operator_tobiko_version`: (String) Tobiko version to install. It could refer to a branch (master, osp-16.2), a tag (0.6.x, 0.7.x) or an sha-1. Default value: `master`
* `cifmw_test_operator_tobiko_pytest_addopts`: (String) `PYTEST_ADDOPTS` env variable with input pytest args. Example: `-m <markers> --maxfail <max-failed-tests> --skipregex <regex>`. Defaults to `null`. In case of `null` value, `PYTEST_ADDOPTS` is not set (tobiko tests are executed without any extra pytest options).
* `cifmw_test_operator_tobiko_prevent_create`: (Boolean) Sets the value of the env variable `TOBIKO_PREVENT_CREATE` that specifies whether tobiko scenario tests create new resources or expect that those resource had been created before. Default to `null`. In case of `null` value, `TOBIKO_PREVENT_CREATE` is not set (tobiko tests create new resources).
* `cifmw_test_operator_tobiko_num_processes`: (Integer) Sets the value of the env variable `TOX_NUM_PROCESSES` that is used to run pytest with `--numprocesses $TOX_NUM_PROCESSES`. Defaults to `null`. In case of `null` value, `TOX_NUM_PROCESSES` is not set (tobiko internally uses the value `auto`, see pytest documentation about the `--numprocesses` option).
* `cifmw_test_operator_tobiko_advanced_image_url`: (String) Tobiko will download images from this URL that will be used to create advance VM instances. By default, the provided image will include all the customizations required by the tobiko tests. Defaults to `https://softwarefactory-project.io/ubuntu-minimal-customized-enp3s0`.
* `cifmw_test_operator_tobiko_kubeconfig_secret`: (String) Name of the Openshift Secret required to use Openshift Client from the Tobiko pod. Default value: `tobiko-secret`
* `cifmw_test_operator_tobiko_openstack_cmd`: (String) Openstack command is used by tobiko to cleanup resources. Default value: `oc -n openstack exec openstackclient -- openstack`
* `cifmw_test_operator_tobiko_override_conf`: (Dict) Overrides the default configuration from `cifmw_test_operator_tobiko_default_conf` that is used to generate the tobiko.conf file. Default value: empty dictionary
* `cifmw_test_operator_tobiko_ssh_keytype`: (String) Type of ssh key that tobiko will use to connect to the VM instances it creates. Defaults to `cifmw_ssh_keytype` which default to `ecdsa`.
* `cifmw_test_operator_tobiko_ssh_keysize`: (Integer) Size of ssh key that tobiko will use to connect to the VM instances it creates. Defaults to `cifmw_ssh_keysize` which defaults to 521.
* `cifmw_test_operator_tobiko_debug`: (Bool) Run Tobiko in debug mode, it keeps the operator pod sleeping infinity (it must only set to `true`only for debugging purposes). Default value: `false`
* `cifmw_test_operator_tobiko_network_attachments`: (List) List of network attachment definitions to attach to the tobiko pods spawned by test-operator. Default value: `[]`.
* `cifmw_test_operator_tobiko_workflow`: (List) Definition of a Tobiko workflow that consists of multiple steps. Each step can contain all values from Spec section of [Tobiko CR](https://openstack-k8s-operators.github.io/test-operator/crds.html#tobiko-custom-resource).
* `cifmw_test_operator_tobiko_resources`: (Dict) A dictionary that specifies resources (cpu, memory) for the test pods. When kept untouched it defaults to the resource limits specified on the test-operator side. Default value: `{}`
* `cifmw_test_operator_tobiko_extra_mounts`: (List) A list of additional volume mounts for the tobiko test pods. Each item specifies a volume name, mount path, and other mount properties. Default value: `[]`
* `cifmw_test_operator_tobiko_config`: (Dict) Definition of Tobiko CRD instance that is passed to the test-operator (see [the test-operator documentation](https://openstack-k8s-operators.github.io/test-operator/crds.html#tobiko-custom-resource)). Default value:
```
  apiVersion: test.openstack.org/v1beta1
  kind: Tobiko
  metadata:
    name: "{{ cifmw_test_operator_tobiko_name }}"
    namespace: "{{ cifmw_test_operator_namespace }}"
  spec:
    kubeconfigSecretName: "{{ cifmw_test_operator_tobiko_kubeconfig_secret }}"
    storageClass: "{{ cifmw_test_operator_storage_class }}"
    containerImage: "{{ cifmw_test_operator_tobiko_image }}:{{ cifmw_test_operator_tobiko_image_tag }}"
    testenv: "{{ cifmw_test_operator_tobiko_testenv }}"
    version: "{{ cifmw_test_operator_tobiko_version }}"
    pytestAddopts: "{{ cifmw_test_operator_tobiko_pytest_addopts if cifmw_test_operator_tobiko_pytest_addopts is not none else omit }}"
    tolerations: "{{ cifmw_test_operator_tolerations | default(omit) }}"
    nodeSelector: "{{ cifmw_test_operator_node_selector | default(omit) }}"
    networkAttachments: "{{ cifmw_test_operator_tobiko_network_attachments }}"
    debug: "{{ cifmw_test_operator_tobiko_debug }}"
    # preventCreate: preventCreate is generated by the test_operator role based on the value of cifmw_test_operator_tobiko_prevent_create
    # numProcesses: numProcesses is generated by the test_operator role based on the value of cifmw_test_operator_tobiko_num_processes
    # privateKey: privateKey is automatically generated by the test_operator role
    # publicKey: publicKey is automatically generated by the test_operator role
    # config: config is generated combining cifmw_test_operator_tobiko_default_conf and cifmw_test_operator_tobiko_override_conf
    workflow: "{{ cifmw_test_operator_tobiko_workflow }}"
```

## AnsibleTest specific parameters
* `cifmw_test_operator_ansibletest_name`: (String) Value used in the `Ansibletest.Metadata.Name` field. The value specifies the name of some resources spawned by the test-operator role. Default value: `ansibletest`
* `cifmw_test_operator_ansibletest_registry`: (String) The registry where to pull ansibletests container. Default value: `{{ cifmw_test_operator_default_registry }}`
* `cifmw_test_operator_ansibletest_namespace`: (String) Registry's namespace where to pull ansibletests container. Default value: `{{ cifmw_test_operator_default_namespace }}`
* `cifmw_test_operator_ansibletest_container`: (String) Name of the ansibletests container. Default value: `openstack-ansible-tests`
* `cifmw_test_operator_ansibletest_image`: (String) Ansibletests image to be used. Default value: `{{ cifmw_test_operator_ansibletest_registry }}/{{ cifmw_test_operator_ansibletest_namespace }}/{{ cifmw_test_operator_ansibletest_container }}`
* `cifmw_test_operator_ansibletest_image_tag`: (String) Ansibletests image to be used. Default value: `{{ cifmw_test_operator_default_image_tag }}`
* `cifmw_test_operator_ansibletest_compute_ssh_key_secret_name`: (String) The name of the k8s secret that contains an ssh key for computes. Default value: `dataplane-ansible-ssh-private-key-secret`
* `cifmw_test_operator_ansibletest_workload_ssh_key_secret_name`: (String) The name of the k8s secret that contains an ssh key for the ansible workload. Default value: `""`
* `cifmw_test_operator_ansibletest_ansible_git_repo`: (String) Git repo to clone into container. Default value: `""`
* `cifmw_test_operator_ansibletest_ansible_playbook_path`: (String) Path to ansible playbook. Default value: `""`
* `cifmw_test_operator_ansibletest_ansible_collection`: (String) Extra ansible collections to install in addition to the ones that exist in the requirements.yaml. Default value: `""`
* `cifmw_test_operator_ansibletest_ansible_var_files`: (String) interface to create ansible var files. Default value: `""`
* `cifmw_test_operator_ansibletest_ansible_extra_vars`: (String) string to pass parameters to ansible. Default value: `""`
* `cifmw_test_operator_ansibletest_ansible_inventory`: (String) string that contains the inventory file content. Default value: `""`
* `cifmw_test_operator_ansibletest_openstack_config_map`: (String) The name of the ConfigMap containing the clouds.yaml. Default value: `openstack-config`
* `cifmw_test_operator_ansibletest_openstack_config_secret`: (String) The name of the Secret containing the secure.yaml. Default value: "openstack-config-secret"
* `cifmw_test_operator_ansibletest_debug`: (Bool) Run ansible playbook with -vvvv. Default value: `false`
* `cifmw_test_operator_ansibletest_workflow`: (List) A parameter that contains a workflow definition. Default value: `[]`
* `cifmw_test_operator_ansibletest_extra_configmaps_mounts`: (List) Extra configmaps for mounting in the pod. Default value: `[]`
* `cifmw_test_operator_ansibletest_extra_mounts`: (List) A list of additional volume mounts for the ansibletest test pods. Each item specifies a volume name, mount path, and other mount properties. Default value: `[]`
* `cifmw_test_operator_ansibletest_resources`: (Dict) A dictionary that specifies resources (cpu, memory) for the test pods. When kept untouched it defaults to the resource limits specified on the test-operator side. Default value: `{}`
* `cifmw_test_operator_ansibletest_config`: Definition of AnsibleTest CRD instance that is passed to the test-operator (see [the test-operator documentation](https://openstack-k8s-operators.github.io/test-operator/crds.html)). Default value:
```
  apiVersion: test.openstack.org/v1beta1
  kind: AnsibleTest
  metadata:
    name: "{{ cifmw_test_operator_ansibletest_name }}"
    namespace: "{{ cifmw_test_operator_namespace }}"
  spec:
    containerImage: "{{ cifmw_test_operator_ansibletest_image }}:{{ cifmw_test_operator_ansibletest_image_tag }}"
    extraConfigmapsMounts: "{{ cifmw_test_operator_ansibletest_extra_configmaps_mounts }}"
    storageClass: "{{ cifmw_test_operator_storage_class }}"
    computeSSHKeySecretName: "{{ cifmw_test_operator_ansibletest_compute_ssh_key_secret_name }}"
    workloadSSHKeySecretName: "{{ cifmw_test_operator_ansibletest_workload_ssh_key_secret_name }}"
    ansibleGitRepo: "{{ cifmw_test_operator_ansibletest_ansible_git_repo }}"
    ansiblePlaybookPath: "{{ cifmw_test_operator_ansibletest_ansible_playbook_path }}"
    ansibleCollections: "{{ cifmw_test_operator_ansibletest_ansible_collection }}"
    ansibleVarFiles: "{{ cifmw_test_operator_ansibletest_ansible_var_files }}"
    ansibleExtraVars: "{{ cifmw_test_operator_ansibletest_ansible_extra_vars }}"
    ansibleInventory: "{{ cifmw_test_operator_ansibletest_ansible_inventory }}"
    openStackConfigMap: "{{ cifmw_test_operator_ansibletest_openstack_config_map }}"
    openStackConfigSecret: "{{ cifmw_test_operator_ansibletest_openstack_config_secret }}"
    workflow: "{{ cifmw_test_operator_ansibletest_workflow }}"
    debug: "{{ cifmw_test_operator_ansibletest_debug }}"
```

## Horizontest specific parameters
* `cifmw_test_operator_horizontest_name`: (String) Value used in the `Horizontest.Metadata.Name` field. The value specifies the name of some resources spawned by the test-operator role. Default value: `horizontest-tests`
* `cifmw_test_operator_horizontest_registry`: (String) The registry where to pull horizontest container. Default value: `{{ cifmw_test_operator_default_registry }}`
* `cifmw_test_operator_horizontest_namespace`: (String) Registry's namespace where to pull horizontest container. Default value: `{{ cifmw_test_operator_default_namespace }}`
* `cifmw_test_operator_horizontest_container`: (String) Name of the horizontest container. Default value: `openstack-horizontest`
* `cifmw_test_operator_horizontest_image`: (String) Horizontest image to be used. Default value: `{{ cifmw_test_operator_horizontest_registry }}/{{ cifmw_test_operator_horizontest_namespace }}/{{ cifmw_test_operator_horizontest_container }}`
* `cifmw_test_operator_horizontest_image_tag`: (String) Tag for the `cifmw_test_operator_horizontest_image`. Default value: `{{ cifmw_test_operator_default_image_tag }}`
* `cifmw_test_operator_horizontest_admin_username`: (String) OpenStack admin credentials. Default value: `admin`
* `cifmw_test_operator_horizontest_admin_password`: (String) OpenStack admin credentials. Default value: `12345678`
* `cifmw_test_operator_horizontest_dashboard_url`: (String) The URL of the Horizon dashboard. Default value: `https://horizon-openstack.apps.ocp.openstack.lab/`
* `cifmw_test_operator_horizontest_auth_url`: (String) The OpenStack authentication URL. Default value: `https://keystone-public-openstack.apps.ocp.openstack.lab`
* `cifmw_test_operator_horizontest_repo_url`: (String) The Horizon tests repository URL. Default value: `https://review.opendev.org/openstack/horizon`
* `cifmw_test_operator_horizontest_horizon_repo_branch`: (String) The branch of the Horizon repository to checkout. Default value: `master`
* `cifmw_test_operator_horizontest_image_url`: (String) The URL to download the Cirros image. Default value: `http://download.cirros-cloud.net/0.6.2/cirros-0.6.2-x86_64-disk.img`
* `cifmw_test_operator_horizontest_project_name`: (String) The name of the OpenStack project for Horizon tests. Default value: `horizontest`
* `cifmw_test_operator_horizontest_user`: (String) The username under which Horizon tests will run. Default value: `horizontest`
* `cifmw_test_operator_horizontest_password`: (String) The password for the user running the Horizon tests. Default value: `horizontest`
* `cifmw_test_operator_horizontest_flavor_name`: (String) The name of the OpenStack flavor to create for Horizon tests. Default value: `m1.tiny`
* `cifmw_test_operator_horizontest_logs_directory_name`: (String) The name of the directory to store test logs. Default value: `horizon`
* `cifmw_test_operator_horizontest_horizon_test_dir`: (String) The directory path for Horizon tests. Default value: `/var/lib/horizontest`
* `cifmw_test_operator_horizontest_resources`: (Dict) A dictionary that specifies resources (cpu, memory) for the test pods. When kept untouched it defaults to the resource limits specified on the test-operator side. Default value: `{}`
* `cifmw_test_operator_horizontest_extra_mounts`: (List) A list of additional volume mounts for the horizontest test pods. Each item specifies a volume name, mount path, and other mount properties. Default value: `[]`
* `cifmw_test_operator_horizontest_debug`: (Bool) Run HorizonTest in debug mode, it keeps the operator pod sleeping infinitely (it must only set to `true` only for debugging purposes). Default value: `false`
* `cifmw_test_operator_horizontest_extra_flag`: (String) The extra flag to modify pytest command to include/exclude tests. Default value: `not pagination`
* `cifmw_test_operator_horizontest_project_name_xpath`: (String) The xpath to select project name based on dashboard theme. Default value: `//span[@class='rcueicon rcueicon-folder-open']/ancestor::li`
* `cifmw_test_operator_horizontest_config`: (Dict) Definition of HorizonTest CR instance that is passed to the test-operator (see [the test-operator documentation](https://openstack-k8s-operators.github.io/test-operator/crds.html#horizontest-custom-resource)). Default value:
```
  apiVersion: test.openstack.org/v1beta1
  kind: HorizonTest
  metadata:
    name: "{{ cifmw_test_operator_horizontest_name }}"
    namespace: "{{ cifmw_test_operator_namespace }}"
  spec:
    containerImage: "{{ cifmw_test_operator_horizontest_image }}:{{ cifmw_test_operator_horizontest_image_tag }}"
    adminUsername: "{{ cifmw_test_operator_horizontest_admin_username }}"
    adminPassword: "{{ cifmw_test_operator_horizontest_admin_password }}"
    dashboardUrl: "{{ cifmw_test_operator_horizontest_dashboard_url }}"
    authUrl: "{{ cifmw_test_operator_horizontest_auth_url }}"
    repoUrl: "{{ cifmw_test_operator_horizontest_repo_url }}"
    horizonRepoBranch: "{{ cifmw_test_operator_horizontest_horizon_repo_branch }}"
    imageUrl: "{{ cifmw_test_operator_horizontest_image_url }}"
    projectName: "{{ cifmw_test_operator_horizontest_project_name }}"
    user: "{{ cifmw_test_operator_horizontest_user }}"
    password: "{{ cifmw_test_operator_horizontest_password }}"
    flavorName: "{{ cifmw_test_operator_horizontest_flavor_name }}"
    logsDirectoryName: "{{ cifmw_test_operator_horizontest_logs_directory_name }}"
    debug: "{{ cifmw_test_operator_horizontest_debug }}"
    extraFlag: "{{ cifmw_test_operator_horizontest_extra_flag }}"
    projectNameXpath "{{ cifmw_test_operator_horizontest_project_name_xpath }}"
    horizonTestDir: "{{ cifmw_test_operator_horizontest_horizon_test_dir }}"
```

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
