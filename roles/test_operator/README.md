# Test operator

Execute tests via the [test-operator](https://openstack-k8s-operators.github.io/test-operator/).

## Parameters

* `cifmw_test_operator_artifacts_basedir`: (String) Directory where we will have all test_operator related files. Default value: `{{ cifmw_basedir }}/tests/test_operator` which defaults to `~/ci-framework-data/tests/test_operator`
* `cifmw_test_operator_namespace`: (String) Namespace inside which all the resources are created. Default value: `openstack`
* `cifmw_test_operator_index`: (String) Full name of container image with index that contains the test_operator. Default value: `quay.io/openstack-k8s-operators/test-operator-index:latest`
* `cifmw_test_operator_timeout`: (Integer) Timeout in seconds for the execution of the tests. Default value: `3600`
* `cifmw_test_operator_logs_image`: (String) Image that should be used to collect logs from the pods spawned by the test-operator. Default value: `quay.io/quay/busybox`
* `cifmw_test_operator_concurrency`: (Integer) Tempest concurrency value. Default value: `8`
* `cifmw_test_operator_cleanup`: (Bool) Delete all resources created by the role at the end of the testing. Default value: `false`
* `cifmw_test_operator_default_groups`: (List) List of groups in the include list to search for tests to be executed. Default value: `[ 'default' ]`
* `cifmw_test_operator_default_jobs`: (List) List of jobs in the exclude list to search for tests to be excluded. Default value: `[ 'default' ]`
* `cifmw_test_operator_dry_run`: (Boolean) Whether test-operator should run or not. Default value: `false`

* `cifmw_test_operator_tempest_registry`: (String) The registry where to pull tempest container. Default value: `quay.io`
* `cifmw_test_operator_tempest_namespace`: (String) Registry's namespace where to pull tempest container. Default value: `podified-antelope-centos9`
* `cifmw_test_operator_tempest_container`: (String) Name of the tempest container. Default value: `openstack-tempest`
* `cifmw_test_operator_tempest_image`: (String) Tempest image to be used. Default value: `{{ cifmw_test_operator_tempest_registry }}/{{ cifmw_test_operator_tempest_namespace }}/{{ cifmw_test_operator_tempest_container }}`
* `cifmw_test_operator_tempest_image_tag`: (String) Tag for the `cifmw_test_operator_tempest_image`. Default value: `current-podified`
* `cifmw_test_operator_tempest_include_list`: (String) List of tests to be executed. Setting this will not use the `list_allowed` plugin. Default value: `''`
* `cifmw_test_operator_tempest_exclude_list`: (List) List of tests to be skipped. Setting this will not use the `list_skipped` plugin. Default value: `''`
* `cifmw_test_operator_tempest_tests_include_override_scenario`: (Boolean) Whether to override the scenario `cifmw_tempest_tests_allowed` definition. Default value: `false`
* `cifmw_test_operator_tempest_tests_exclude_override_scenario`: (Boolean) Whether to override the scenario `cifmw_tempest_tests_skipped` definition. Default value: `false`

# Please refer to https://openstack-k8s-operators.github.io/test-operator/guide.html#executing-tempest-tests
* `cifmw_test_operator_tempest_config`: (Object) Definition of Tempest CRD instance that is passed to the test-operator. Default value:
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
    tempestconfRun: "{{ cifmw_tempest_tempestconf_config | default(omit) }}"
```
