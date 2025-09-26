# Test operator

Execute tests via the [test-operator](https://openstack-k8s-operators.github.io/test-operator/).

<!-- START VARIABLES -->

_This section is automatically generated from `defaults/main.yml`. Do not edit manually._


## Generic Parameters

| Parameter | Default Value |
|-----------|---------------|
| `cifmw_test_operator_stages` | `[{name: tempest, type: tempest}]` |
| `cifmw_test_operator_fail_on_test_failure` | `true ...` |
| `cifmw_test_operator_artifacts_basedir` | `'{{ cifmw_basedir | default(ansible_user_dir ~ ''/ci-framework-data'') }}/tests/test_operator'` |
| `cifmw_test_operator_namespace` | `openstack ...` |
| `cifmw_test_operator_controller_namespace` | `openstack-operators ...` |
| `cifmw_test_operator_bundle` | `''` |
| `cifmw_test_operator_timeout` | `3600 ...` |
| `cifmw_test_operator_logs_image` | `quay.io/quay/busybox ...` |
| `cifmw_test_operator_cleanup` | `false ...` |
| `cifmw_test_operator_clean_last_run` | `false ...` |
| `cifmw_test_operator_dry_run` | `false ...` |
| `cifmw_test_operator_default_groups` | `[default]` |
| `cifmw_test_operator_default_jobs` | `[default]` |
| `cifmw_test_operator_fail_fast` | `false ...` |
| `cifmw_test_operator_storage_class_prefix` | `'{{ ''lvms-'' if cifmw_use_lvms | default(false) | bool  else '''' }}'` |
| `cifmw_test_operator_storage_class` | `'{{ cifmw_test_operator_storage_class_prefix }}local-storage'` |
| `cifmw_test_operator_delete_logs_pod` | `false ...` |
| `cifmw_test_operator_privileged` | `true ...` |
| `cifmw_test_operator_selinux_level` | `s0:c478,c978 ...` |
| `cifmw_test_operator_crs_path` | `'{{ cifmw_basedir | default(ansible_user_dir ~ ''/ci-framework-data'') }}/artifacts/test-operator-crs'` |
| `cifmw_test_operator_log_pod_definition` | `(see `defaults/main.yml`)` |
| `cifmw_test_operator_default_registry` | `quay.io ...` |
| `cifmw_test_operator_default_namespace` | `podified-antelope-centos9 ...` |
| `cifmw_test_operator_default_image_tag` | `current-podified ...` |


## Tempest Parameters

| Parameter | Default Value |
|-----------|---------------|
| `cifmw_test_operator_tempest_name` | `tempest-tests ...` |
| `cifmw_test_operator_tempest_concurrency` | `8 ...` |
| `cifmw_test_operator_tempest_registry` | `'{{ cifmw_test_operator_default_registry }}'` |
| `cifmw_test_operator_tempest_namespace` | `'{{ cifmw_test_operator_default_namespace }}'` |
| `cifmw_test_operator_tempest_container` | `openstack-tempest-all ...` |
| `cifmw_test_operator_tempest_image` | `'{{ stage_vars_dict.cifmw_test_operator_tempest_registry }}/{{ stage_vars_dict.cifmw_test_operator_tempest_namespace }}/{{   stage_vars_dict.cifmw_test_operator_tempest_container }}'` |
| `cifmw_test_operator_tempest_image_tag` | `'{{ cifmw_test_operator_default_image_tag }}'` |
| `cifmw_test_operator_tempest_network_attachments` | `[]` |
| `cifmw_test_operator_tempest_tests_include_override_scenario` | `false ...` |
| `cifmw_test_operator_tempest_tests_exclude_override_scenario` | `false ...` |
| `cifmw_test_operator_tempest_workflow` | `[]` |
| `cifmw_test_operator_tempest_cleanup` | `false ...` |
| `cifmw_test_operator_tempest_rerun_failed_tests` | `false ...` |
| `cifmw_test_operator_tempest_rerun_override_status` | `false ...` |
| `cifmw_test_operator_tempest_tempestconf_config` | `'{{ cifmw_tempest_tempestconf_config }}'` |
| `cifmw_test_operator_tempest_resources` | `{requests: {}, limits: {}}` |
| `cifmw_tempest_tempestconf_config_defaults` | `(see `defaults/main.yml`)` |
| `cifmw_test_operator_tempest_debug` | `false ...` |
| `cifmw_test_operator_tempest_config` | `(see `defaults/main.yml`)` |


## Tobiko Parameters

| Parameter | Default Value |
|-----------|---------------|
| `cifmw_test_operator_tobiko_name` | `tobiko-tests ...` |
| `cifmw_test_operator_tobiko_registry` | `'{{ cifmw_test_operator_default_registry }}'` |
| `cifmw_test_operator_tobiko_namespace` | `'{{ cifmw_test_operator_default_namespace }}'` |
| `cifmw_test_operator_tobiko_container` | `openstack-tobiko ...` |
| `cifmw_test_operator_tobiko_image` | `'{{ stage_vars_dict.cifmw_test_operator_tobiko_registry }}/{{ stage_vars_dict.cifmw_test_operator_tobiko_namespace }}/{{ stage_vars_dict.cifmw_test_operator_tobiko_container   }}'` |
| `cifmw_test_operator_tobiko_image_tag` | `'{{ cifmw_test_operator_default_image_tag }}'` |
| `cifmw_test_operator_tobiko_testenv` | `scenario ...` |
| `cifmw_test_operator_tobiko_version` | `master ...` |
| `cifmw_test_operator_tobiko_pytest_addopts` | `null ...` |
| `cifmw_test_operator_tobiko_prevent_create` | `null ...` |
| `cifmw_test_operator_tobiko_num_processes` | `null ...` |
| `cifmw_test_operator_tobiko_advanced_image_url` | `https://softwarefactory-project.io/ubuntu-minimal-customized-enp3s0 ...` |
| `cifmw_test_operator_tobiko_override_conf` | `{}` |
| `cifmw_test_operator_tobiko_kubeconfig_secret` | `tobiko-secret ...` |
| `cifmw_test_operator_tobiko_openstack_cmd` | `oc -n openstack exec openstackclient -- openstack ...` |
| `cifmw_test_operator_tobiko_cleanup` | `false ...` |
| `cifmw_test_operator_tobiko_ssh_keytype` | `'{{ cifmw_ssh_keytype | default(''ecdsa'') }}'` |
| `cifmw_test_operator_tobiko_ssh_keysize` | `'{{ cifmw_ssh_keysize | default(521) }}'` |
| `cifmw_test_operator_tobiko_debug` | `false ...` |
| `cifmw_test_operator_tobiko_network_attachments` | `[]` |
| `cifmw_test_operator_tobiko_workflow` | `[]` |
| `cifmw_test_operator_tobiko_config` | `(see `defaults/main.yml`)` |


## AnsibleTest Parameters

| Parameter | Default Value |
|-----------|---------------|
| `cifmw_test_operator_ansibletest_name` | `ansibletest ...` |
| `cifmw_test_operator_ansibletest_registry` | `'{{ cifmw_test_operator_default_registry }}'` |
| `cifmw_test_operator_ansibletest_namespace` | `'{{ cifmw_test_operator_default_namespace }}'` |
| `cifmw_test_operator_ansibletest_container` | `openstack-ansible-tests ...` |
| `cifmw_test_operator_ansibletest_image` | `'{{ stage_vars_dict.cifmw_test_operator_ansibletest_registry }}/{{ stage_vars_dict.cifmw_test_operator_ansibletest_namespace   }}/{{ stage_vars_dict.cifmw_test_operator_ansibletest_container }}'` |
| `cifmw_test_operator_ansibletest_image_tag` | `'{{ cifmw_test_operator_default_image_tag }}'` |
| `cifmw_test_operator_ansibletest_compute_ssh_key_secret_name` | `dataplane-ansible-ssh-private-key-secret ...` |
| `cifmw_test_operator_ansibletest_workload_ssh_key_secret_name` | `''` |
| `cifmw_test_operator_ansibletest_ansible_git_repo` | `''` |
| `cifmw_test_operator_ansibletest_ansible_playbook_path` | `''` |
| `cifmw_test_operator_ansibletest_ansible_collection` | `''` |
| `cifmw_test_operator_ansibletest_ansible_var_files` | `''` |
| `cifmw_test_operator_ansibletest_ansible_extra_vars` | `''` |
| `cifmw_test_operator_ansibletest_ansible_inventory` | `''` |
| `cifmw_test_operator_ansibletest_openstack_config_map` | `openstack-config ...` |
| `cifmw_test_operator_ansibletest_openstack_config_secret` | `openstack-config-secret ...` |
| `cifmw_test_operator_ansibletest_debug` | `false ...` |
| `cifmw_test_operator_ansibletest_workflow` | `[]` |
| `cifmw_test_operator_ansibletest_extra_configmaps_mounts` | `[]` |
| `cifmw_test_operator_ansibletest_config` | `(see `defaults/main.yml`)` |


## HorizonTest Parameters

| Parameter | Default Value |
|-----------|---------------|
| `cifmw_test_operator_horizontest_name` | `horizontest-tests ...` |
| `cifmw_test_operator_horizontest_registry` | `'{{ cifmw_test_operator_default_registry }}'` |
| `cifmw_test_operator_horizontest_namespace` | `'{{ cifmw_test_operator_default_namespace }}'` |
| `cifmw_test_operator_horizontest_container` | `openstack-horizontest ...` |
| `cifmw_test_operator_horizontest_image` | `'{{ stage_vars_dict.cifmw_test_operator_horizontest_registry }}/{{ stage_vars_dict.cifmw_test_operator_horizontest_namespace   }}/{{ stage_vars_dict.cifmw_test_operator_horizontest_container }}'` |
| `cifmw_test_operator_horizontest_image_tag` | `'{{ cifmw_test_operator_default_image_tag }}'` |
| `cifmw_test_operator_horizontest_admin_username` | `admin ...` |
| `cifmw_test_operator_horizontest_admin_password` | `'12345678'` |
| `cifmw_test_operator_horizontest_dashboard_url` | `https://horizon-openstack.apps.ocp.openstack.lab/ ...` |
| `cifmw_test_operator_horizontest_auth_url` | `https://keystone-public-openstack.apps.ocp.openstack.lab ...` |
| `cifmw_test_operator_horizontest_repo_url` | `https://review.opendev.org/openstack/horizon ...` |
| `cifmw_test_operator_horizontest_horizon_repo_branch` | `master ...` |
| `cifmw_test_operator_horizontest_image_url` | `http://download.cirros-cloud.net/0.6.2/cirros-0.6.2-x86_64-disk.img ...` |
| `cifmw_test_operator_horizontest_project_name` | `horizontest ...` |
| `cifmw_test_operator_horizontest_user` | `horizontest ...` |
| `cifmw_test_operator_horizontest_password` | `horizontest ...` |
| `cifmw_test_operator_horizontest_flavor_name` | `m1.tiny ...` |
| `cifmw_test_operator_horizontest_logs_directory_name` | `horizon ...` |
| `cifmw_test_operator_horizontest_debug` | `false ...` |
| `cifmw_test_operator_horizontest_horizon_test_dir` | `/var/lib/horizontest ...` |
| `cifmw_test_operator_horizontest_extra_flag` | `not pagination ...` |
| `cifmw_test_operator_horizontest_project_name_xpath` | `//span[@class='rcueicon rcueicon-folder-open']/ancestor::li ...` |
| `cifmw_test_operator_horizontest_config` | `(see `defaults/main.yml`)` |


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

<!-- BEGIN TEST OPERATOR PARAMS -->

## Test Operator Parameters

### Generic Variables

| Parameter | Default Value |
|-----------|---------------|
| `cifmw_test_operator_stages` | `[{name: tempest, type: tempest}]` |
| `cifmw_test_operator_fail_on_test_failure` | `true ...` |
| `cifmw_test_operator_artifacts_basedir` | `'{{ cifmw_basedir | default(ansible_user_dir ~ ''/ci-framework-data'') }}/tests/test_operator'` |
| `cifmw_test_operator_namespace` | `openstack ...` |
| `cifmw_test_operator_controller_namespace` | `openstack-operators ...` |
| `cifmw_test_operator_bundle` | `''` |
| `cifmw_test_operator_timeout` | `3600 ...` |
| `cifmw_test_operator_logs_image` | `quay.io/quay/busybox ...` |
| `cifmw_test_operator_cleanup` | `false ...` |
| `cifmw_test_operator_clean_last_run` | `false ...` |
| `cifmw_test_operator_dry_run` | `false ...` |
| `cifmw_test_operator_default_groups` | `[default]` |
| `cifmw_test_operator_default_jobs` | `[default]` |
| `cifmw_test_operator_fail_fast` | `false ...` |
| `cifmw_test_operator_storage_class_prefix` | `'{{ ''lvms-'' if cifmw_use_lvms | default(false) | bool  else '''' }}'` |
| `cifmw_test_operator_storage_class` | `'{{ cifmw_test_operator_storage_class_prefix }}local-storage'` |
| `cifmw_test_operator_delete_logs_pod` | `false ...` |
| `cifmw_test_operator_privileged` | `true ...` |
| `cifmw_test_operator_selinux_level` | `s0:c478,c978 ...` |
| `cifmw_test_operator_crs_path` | `'{{ cifmw_basedir | default(ansible_user_dir ~ ''/ci-framework-data'') }}/artifacts/test-operator-crs'` |
| `cifmw_test_operator_log_pod_definition` | `(see [defaults/main.yml](defaults/main.yml))` |
| `cifmw_test_operator_default_registry` | `quay.io ...` |
| `cifmw_test_operator_default_namespace` | `podified-antelope-centos9 ...` |
| `cifmw_test_operator_default_image_tag` | `current-podified ...` |

### Tempest Variables

| Parameter | Default Value |
|-----------|---------------|
| `cifmw_test_operator_tempest_name` | `tempest-tests ...` |
| `cifmw_test_operator_tempest_concurrency` | `8 ...` |
| `cifmw_test_operator_tempest_registry` | `'{{ cifmw_test_operator_default_registry }}'` |
| `cifmw_test_operator_tempest_namespace` | `'{{ cifmw_test_operator_default_namespace }}'` |
| `cifmw_test_operator_tempest_container` | `openstack-tempest-all ...` |
| `cifmw_test_operator_tempest_image` | `'{{ stage_vars_dict.cifmw_test_operator_tempest_registry }}/{{ stage_vars_dict.cifmw_test_operator_tempest_namespace }}/{{ stage_vars_dict.cifmw_test_operator_tempest_container }}'` |
| `cifmw_test_operator_tempest_image_tag` | `'{{ cifmw_test_operator_default_image_tag }}'` |
| `cifmw_test_operator_tempest_network_attachments` | `[]` |
| `cifmw_test_operator_tempest_tests_include_override_scenario` | `false ...` |
| `cifmw_test_operator_tempest_tests_exclude_override_scenario` | `false ...` |
| `cifmw_test_operator_tempest_workflow` | `[]` |
| `cifmw_test_operator_tempest_cleanup` | `false ...` |
| `cifmw_test_operator_tempest_rerun_failed_tests` | `false ...` |
| `cifmw_test_operator_tempest_rerun_override_status` | `false ...` |
| `cifmw_test_operator_tempest_tempestconf_config` | `'{{ cifmw_tempest_tempestconf_config }}'` |
| `cifmw_test_operator_tempest_resources` | `{requests: {}, limits: {}}` |
| `cifmw_tempest_tempestconf_config_defaults` | `(see [defaults/main.yml](defaults/main.yml))` |
| `cifmw_test_operator_tempest_debug` | `false ...` |
| `cifmw_test_operator_tempest_config` | `(see [defaults/main.yml](defaults/main.yml))` |

### Tobiko Variables

| Parameter | Default Value |
|-----------|---------------|
| `cifmw_test_operator_tobiko_name` | `tobiko-tests ...` |
| `cifmw_test_operator_tobiko_registry` | `'{{ cifmw_test_operator_default_registry }}'` |
| `cifmw_test_operator_tobiko_namespace` | `'{{ cifmw_test_operator_default_namespace }}'` |
| `cifmw_test_operator_tobiko_container` | `openstack-tobiko ...` |
| `cifmw_test_operator_tobiko_image` | `'{{ stage_vars_dict.cifmw_test_operator_tobiko_registry }}/{{ stage_vars_dict.cifmw_test_operator_tobiko_namespace }}/{{ stage_vars_dict.cifmw_test_operator_tobiko_container }}'` |
| `cifmw_test_operator_tobiko_image_tag` | `'{{ cifmw_test_operator_default_image_tag }}'` |
| `cifmw_test_operator_tobiko_testenv` | `scenario ...` |
| `cifmw_test_operator_tobiko_version` | `master ...` |
| `cifmw_test_operator_tobiko_pytest_addopts` | `null ...` |
| `cifmw_test_operator_tobiko_prevent_create` | `null ...` |
| `cifmw_test_operator_tobiko_num_processes` | `null ...` |
| `cifmw_test_operator_tobiko_advanced_image_url` | `https://softwarefactory-project.io/ubuntu-minimal-customized-enp3s0 ...` |
| `cifmw_test_operator_tobiko_override_conf` | `{}` |
| `cifmw_test_operator_tobiko_kubeconfig_secret` | `tobiko-secret ...` |
| `cifmw_test_operator_tobiko_openstack_cmd` | `oc -n openstack exec openstackclient -- openstack ...` |
| `cifmw_test_operator_tobiko_cleanup` | `false ...` |
| `cifmw_test_operator_tobiko_ssh_keytype` | `'{{ cifmw_ssh_keytype | default(''ecdsa'') }}'` |
| `cifmw_test_operator_tobiko_ssh_keysize` | `'{{ cifmw_ssh_keysize | default(521) }}'` |
| `cifmw_test_operator_tobiko_debug` | `false ...` |
| `cifmw_test_operator_tobiko_network_attachments` | `[]` |
| `cifmw_test_operator_tobiko_workflow` | `[]` |
| `cifmw_test_operator_tobiko_config` | `(see [defaults/main.yml](defaults/main.yml))` |

### AnsibleTest Variables

| Parameter | Default Value |
|-----------|---------------|
| `cifmw_test_operator_ansibletest_name` | `ansibletest ...` |
| `cifmw_test_operator_ansibletest_registry` | `'{{ cifmw_test_operator_default_registry }}'` |
| `cifmw_test_operator_ansibletest_namespace` | `'{{ cifmw_test_operator_default_namespace }}'` |
| `cifmw_test_operator_ansibletest_container` | `openstack-ansible-tests ...` |
| `cifmw_test_operator_ansibletest_image` | `'{{ stage_vars_dict.cifmw_test_operator_ansibletest_registry }}/{{ stage_vars_dict.cifmw_test_operator_ansibletest_namespace }}/{{ stage_vars_dict.cifmw_test_operator_ansibletest_container }}'` |
| `cifmw_test_operator_ansibletest_image_tag` | `'{{ cifmw_test_operator_default_image_tag }}'` |
| `cifmw_test_operator_ansibletest_compute_ssh_key_secret_name` | `dataplane-ansible-ssh-private-key-secret ...` |
| `cifmw_test_operator_ansibletest_workload_ssh_key_secret_name` | `''` |
| `cifmw_test_operator_ansibletest_ansible_git_repo` | `''` |
| `cifmw_test_operator_ansibletest_ansible_playbook_path` | `''` |
| `cifmw_test_operator_ansibletest_ansible_collection` | `''` |
| `cifmw_test_operator_ansibletest_ansible_var_files` | `''` |
| `cifmw_test_operator_ansibletest_ansible_extra_vars` | `''` |
| `cifmw_test_operator_ansibletest_ansible_inventory` | `''` |
| `cifmw_test_operator_ansibletest_openstack_config_map` | `openstack-config ...` |
| `cifmw_test_operator_ansibletest_openstack_config_secret` | `openstack-config-secret ...` |
| `cifmw_test_operator_ansibletest_debug` | `false ...` |
| `cifmw_test_operator_ansibletest_workflow` | `[]` |
| `cifmw_test_operator_ansibletest_extra_configmaps_mounts` | `[]` |
| `cifmw_test_operator_ansibletest_config` | `(see [defaults/main.yml](defaults/main.yml))` |

### HorizonTest Variables

| Parameter | Default Value |
|-----------|---------------|
| `cifmw_test_operator_horizontest_name` | `horizontest-tests ...` |
| `cifmw_test_operator_horizontest_registry` | `'{{ cifmw_test_operator_default_registry }}'` |
| `cifmw_test_operator_horizontest_namespace` | `'{{ cifmw_test_operator_default_namespace }}'` |
| `cifmw_test_operator_horizontest_container` | `openstack-horizontest ...` |
| `cifmw_test_operator_horizontest_image` | `'{{ stage_vars_dict.cifmw_test_operator_horizontest_registry }}/{{ stage_vars_dict.cifmw_test_operator_horizontest_namespace }}/{{ stage_vars_dict.cifmw_test_operator_horizontest_container }}'` |
| `cifmw_test_operator_horizontest_image_tag` | `'{{ cifmw_test_operator_default_image_tag }}'` |
| `cifmw_test_operator_horizontest_admin_username` | `admin ...` |
| `cifmw_test_operator_horizontest_admin_password` | `'12345678'` |
| `cifmw_test_operator_horizontest_dashboard_url` | `https://horizon-openstack.apps.ocp.openstack.lab/ ...` |
| `cifmw_test_operator_horizontest_auth_url` | `https://keystone-public-openstack.apps.ocp.openstack.lab ...` |
| `cifmw_test_operator_horizontest_repo_url` | `https://review.opendev.org/openstack/horizon ...` |
| `cifmw_test_operator_horizontest_horizon_repo_branch` | `master ...` |
| `cifmw_test_operator_horizontest_image_url` | `http://download.cirros-cloud.net/0.6.2/cirros-0.6.2-x86_64-disk.img ...` |
| `cifmw_test_operator_horizontest_project_name` | `horizontest ...` |
| `cifmw_test_operator_horizontest_user` | `horizontest ...` |
| `cifmw_test_operator_horizontest_password` | `horizontest ...` |
| `cifmw_test_operator_horizontest_flavor_name` | `m1.tiny ...` |
| `cifmw_test_operator_horizontest_logs_directory_name` | `horizon ...` |
| `cifmw_test_operator_horizontest_debug` | `false ...` |
| `cifmw_test_operator_horizontest_horizon_test_dir` | `/var/lib/horizontest ...` |
| `cifmw_test_operator_horizontest_extra_flag` | `not pagination ...` |
| `cifmw_test_operator_horizontest_project_name_xpath` | `//span[@class='rcueicon rcueicon-folder-open']/ancestor::li ...` |
| `cifmw_test_operator_horizontest_config` | `(see [defaults/main.yml](defaults/main.yml))` |

<!-- END TEST OPERATOR PARAMS -->


