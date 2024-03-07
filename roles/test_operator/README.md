# Test operator

Execute tests via the [test-operator](https://openstack-k8s-operators.github.io/test-operator/).

## Parameters

* `cifmw_test_operator_artifacts_basedir`: (String) Directory where we will have all test-operator related files. Default value: `{{ cifmw_basedir }}/tests/test_operator` which defaults to `~/ci-framework-data/tests/test_operator`
* `cifmw_test_operator_namespace`: (String) Namespace inside which all the resources are created. Default value: `openstack`
* `cifmw_test_operator_index`: (String) Full name of container image with index that contains the test-operator. Default value: `quay.io/openstack-k8s-operators/test-operator-index:latest`
* `cifmw_test_operator_timeout`: (Integer) Timeout in seconds for the execution of the tests. Default value: `3600`
* `cifmw_test_operator_logs_image`: (String) Image that should be used to collect logs from the pods spawned by the test-operator. Default value: `quay.io/quay/busybox`
* `cifmw_test_operator_concurrency`: (Integer) Tempest concurrency value. Default value: `8`
* `cifmw_test_operator_cleanup`: (Bool) Delete all resources created by the role at the end of the testing. Default value: `false`
* `cifmw_test_operator_default_groups`: (List) List of groups in the include list to search for tests to be executed. Default value: `[ 'default' ]`
* `cifmw_test_operator_default_jobs`: (List) List of jobs in the exclude list to search for tests to be excluded. Default value: `[ 'default' ]`
* `cifmw_test_operator_dry_run`: (Boolean) Whether test-operator should run or not. Default value: `false`
* `cifmw_test_operator_fail_fast`: (Boolean) Whether the test results are evaluated when each test framework execution finishes or when all test frameworks are done. Default value: `false`

## Tempest specific parameters
* `cifmw_test_operator_tempest_registry`: (String) The registry where to pull tempest container. Default value: `quay.io`
* `cifmw_test_operator_tempest_namespace`: (String) Registry's namespace where to pull tempest container. Default value: `podified-antelope-centos9`
* `cifmw_test_operator_tempest_container`: (String) Name of the tempest container. Default value: `openstack-tempest`
* `cifmw_test_operator_tempest_image`: (String) Tempest image to be used. Default value: `{{ cifmw_test_operator_tempest_registry }}/{{ cifmw_test_operator_tempest_namespace }}/{{ cifmw_test_operator_tempest_container }}`
* `cifmw_test_operator_tempest_image_tag`: (String) Tag for the `cifmw_test_operator_tempest_image`. Default value: `current-podified`
* `cifmw_test_operator_tempest_include_list`: (String) List of tests to be executed. Setting this will not use the `list_allowed` plugin. Default value: `''`
* `cifmw_test_operator_tempest_exclude_list`: (List) List of tests to be skipped. Setting this will not use the `list_skipped` plugin. Default value: `''`
* `cifmw_test_operator_tempest_external_plugin`: (List) List of dicts describing any external plugin to be installed. The dictionary contains a repository, changeRepository (optional) and changeRefspec (optional). Default value: `[]`
* `cifmw_test_operator_tempest_tests_include_override_scenario`: (Boolean) Whether to override the scenario `cifmw_tempest_tests_allowed` definition. Default value: `false`
* `cifmw_test_operator_tempest_tests_exclude_override_scenario`: (Boolean) Whether to override the scenario `cifmw_tempest_tests_skipped` definition. Default value: `false`
* `cifmw_test_operator_tempest_ssh_key_secret_name`: (String) Name of a secret that contains ssh-privatekey field with a private key. The private key is mounted to `/var/lib/tempest/.ssh/id_ecdsa`
* `cifmw_test_operator_tempest_config_overwrite`: (Dict) Dictionary where key is name of a file and value is content of the file. All files mentioned in this field are mounted to `/etc/test_operator/<filename>`
* `cifmw_test_operator_tempest_config`: (Object) Definition of Tempest CRD instance that is passed to the test-operator (see [the test-operator documentation](https://openstack-k8s-operators.github.io/test-operator/crds.html#tempest-custom-resource)). Default value:
```
  apiVersion: test.openstack.org/v1beta1
  kind: Tempest
  metadata:
    name: tempest-tests
    namespace: "{{ cifmw_test_operator_namespace }}"
  spec:
    containerImage: "{{ cifmw_test_operator_tempest_image }}:{{ cifmw_test_operator_tempest_image_tag }}"
    tempestRun:
      includeList: |
        {{ cifmw_test_operator_include_list | default('') }}
      excludeList: |
        {{ cifmw_test_operator_exclude_list | default('') }}
      concurrency: "{{ cifmw_test_operator_concurrency }}"
      externalPlugin: "{{ cifmw_test_operator_tempest_external_plugin | default([]) }}"
    tempestconfRun: "{{ cifmw_tempest_tempestconf_config | default(omit) }}"
```

## Tobiko specific parameters
* `cifmw_test_operator_tobiko_registry`: (String) The registry where to pull tobiko container. Default value: `quay.io`
* `cifmw_test_operator_tobiko_namespace`: (String) Registry's namespace where to pull tobiko container. Default value: `podified-antelope-centos9`
* `cifmw_test_operator_tobiko_container`: (String) Name of the tobiko container. Default value: `openstack-tobiko`
* `cifmw_test_operator_tobiko_image`: (String) Tobiko image to be used. Default value: `{{ cifmw_test_operator_tobiko_registry }}/{{ cifmw_test_operator_tobiko_namespace }}/{{ cifmw_test_operator_tobiko_container }}`
* `cifmw_test_operator_tobiko_image_tag`: (String) Tag for the `cifmw_test_operator_tobiko_image`. Default value: `current-podified`
* `cifmw_test_operator_tobiko_testenv`: (String) Executed tobiko testenv. See tobiko `tox.ini` file for further details. Some allowed values: scenario, sanity, faults, neutron, octavia, py3, etc. Default value: `scenario`
* `cifmw_test_operator_tobiko_version`: (String) Tobiko version to install. It could refer to a branch (master, osp-16.2), a tag (0.6.x, 0.7.x) or an sha-1. Default value: `master`
* `cifmw_test_operator_tobiko_pytest_addopts`: (String) `PYTEST_ADDOPTS` env variable with input pytest args. Example: `-m <markers> --maxfail <max-failed-tests> --skipregex <regex>`. Defaults to `null`. In case of `null` value, `PYTEST_ADDOPTS` is not set (tobiko tests are executed without any extra pytest options).
* `cifmw_test_operator_tobiko_prevent_create`: (Boolean) Sets the value of the env variable `TOBIKO_PREVENT_CREATE` that specifies whether tobiko scenario tests create new resources or expect that those resource had been created before. Default to `null`. In case of `null` value, `TOBIKO_PREVENT_CREATE` is not set (tobiko tests create new resources).
* `cifmw_test_operator_tobiko_num_processes`: (Integer) Sets the value of the env variable `TOX_NUM_PROCESSES` that is used to run pytest with `--numprocesses $TOX_NUM_PROCESSES`. Defaults to `null`. In case of `null` value, `TOX_NUM_PROCESSES` is not set (tobiko internally uses the value `auto`, see pytest documentation about the `--numprocesses` option).
* `cifmw_test_operator_tobiko_kubeconfig_secret`: (String) Name of the Openshift Secret required to use Openshift Client from the Tobiko pod. Default value: `tobiko-secret`
* `cifmw_test_operator_tobiko_override_conf`: (Dict) Overrides the default configuration from `cifmw_test_operator_tobiko_default_conf` that is used to generate the tobiko.conf file. Default value: empty dictionary
* `cifmw_test_operator_tobiko_ssh_keytype`: (String) Type of ssh key that tobiko will use to connect to the VM instances it creates. Defaults to `cifmw_ssh_keytype` which default to `ecdsa`.
* `cifmw_test_operator_tobiko_ssh_keysize`: (Integer) Size of ssh key that tobiko will use to connect to the VM instances it creates. Defaults to `cifmw_ssh_keysize` which defaults to 521.
* `cifmw_test_operator_tobiko_workflow`: (List) Definition of a Tobiko workflow that consists of multiple steps. Each step can contain all values from Spec section of [Tobiko CR](https://openstack-k8s-operators.github.io/test-operator/crds.html#tobiko-custom-resource).
* `cifmw_test_operator_tobiko_config`: (Dict) Definition of Tobiko CRD instance that is passed to the test-operator (see [the test-operator documentation](https://openstack-k8s-operators.github.io/test-operator/crds.html#tobiko-custom-resource)). Default value:
```
  apiVersion: test.openstack.org/v1beta1
  kind: Tobiko
  metadata:
    name: tobiko-tests
    namespace: "{{ cifmw_test_operator_namespace }}"
  spec:
    kubeconfigSecretName: "{{ cifmw_test_operator_tobiko_kubeconfig_secret }}"
    containerImage: "{{ cifmw_test_operator_tobiko_image }}:{{ cifmw_test_operator_tobiko_image_tag }}"
    testenv: "{{ cifmw_test_operator_tobiko_testenv }}"
    version: "{{ cifmw_test_operator_tobiko_version }}"
    pytestAddopts: "{{ cifmw_test_operator_tobiko_pytest_addopts if cifmw_test_operator_tobiko_pytest_addopts is not none else omit }}"
    # preventCreate: preventCreate is generated by the test_operator role based on the value of cifmw_test_operator_tobiko_prevent_create
    # numProcesses: numProcesses is generated by the test_operator role based on the value of cifmw_test_operator_tobiko_num_processes
    # privateKey: privateKey is automatically generated by the test_operator role
    # publicKey: publicKey is automatically generated by the test_operator role
    # config: config is generated combining cifmw_test_operator_tobiko_default_conf and cifmw_test_operator_tobiko_override_conf
    workflow: "{{ cifmw_test_operator_tobiko_workflow }}"
```
