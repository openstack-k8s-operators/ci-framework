# rally
Role to setup and run Rally benchmarking tests against an OpenStack deployment.

Rally is run inside the `quay.io/airshipit/xrally-openstack` container via podman.
OpenStack credentials are discovered automatically from the Kubernetes KeystoneAPI resource,
or can be supplied directly via `cifmw_rally_os_*` variables.

## Prerequisites
- `oc` CLI available and pointing to the target OpenStack cluster (used for credential and CA discovery).
- `cifmw_openstack_namespace` must be set to the OpenStack namespace (typically `openstack`).

## Privilege escalation
become - Required to install podman and fix artifact directory ownership after the container run.

## Parameters

* `cifmw_rally_artifacts_basedir`: (String) Directory where all Rally artifacts are stored.
  Default: `{{ cifmw_basedir }}/tests/rally`
* `cifmw_rally_registry`: (String) Container registry. Default: `quay.io`
* `cifmw_rally_namespace`: (String) Registry namespace. Default: `airshipit`
* `cifmw_rally_container`: (String) Container image name. Default: `xrally-openstack`
* `cifmw_rally_image`: (String) Full image reference. Composed from registry/namespace/container.
* `cifmw_rally_image_tag`: (String) Container image tag. Default: `3.0.0`
* `cifmw_rally_dry_run`: (Boolean) Skip actual container execution. Default: `false`
* `cifmw_rally_remove_container`: (Boolean) Remove container after run. Default: `true`
* `cifmw_rally_fail_on_task_failure`: (Boolean) Fail the play if Rally exits non-zero. Default: `true`
* `cifmw_rally_deployment_name`: (String) Rally deployment name. Default: `cifmw`
* `cifmw_rally_concurrency`: (Integer) Concurrency passed to the Rally task via `--task-args`. Default: `1`
* `cifmw_rally_task_file`: (String) Filename of the Rally task YAML inside the tasks directory.
  Must exist in the role's `files/` directory or be pre-staged in `cifmw_rally_artifacts_basedir/tasks/`
  via a pre-test hook. Default: `default-task.yaml`
* `cifmw_rally_task_extra_args`: (String) Extra arguments passed verbatim to `rally task start`. Default: `""`
* `cifmw_rally_dns_servers`: (List) DNS servers used inside the Rally container. Default: `["192.168.122.10"]`
* `cifmw_rally_os_auth_url`: (String) OpenStack auth URL. Auto-discovered from KeystoneAPI if unset.
* `cifmw_rally_os_username`: (String) OpenStack username. Default: `admin`
* `cifmw_rally_os_password`: (String) OpenStack password. Auto-discovered from Kubernetes secret if unset.
* `cifmw_rally_os_project_name`: (String) OpenStack project. Default: `admin`
* `cifmw_rally_os_user_domain_name`: (String) User domain. Default: `Default`
* `cifmw_rally_os_project_domain_name`: (String) Project domain. Default: `Default`
* `cifmw_rally_os_region_name`: (String) OpenStack region. Default: `regionOne`

## Standalone usage

```yaml
- hosts: hypervisor
  roles:
    - role: rally
      vars:
        cifmw_rally_concurrency: 2
        cifmw_rally_task_file: my-benchmark.yaml
        cifmw_rally_fail_on_task_failure: false
```

Set `cifmw_run_test_role: rally` in a scenario `05-tests.yaml` to invoke this role
from the cifmw_setup workflow without using the test_operator.

## Usage as a test_operator stage

Add a `rally` stage to `cifmw_test_operator_stages` in your scenario's `05-tests.yaml`:

```yaml
cifmw_run_tests: true
cifmw_run_test_role: test_operator
cifmw_test_operator_stages:
  - name: tempest
    type: tempest
  - name: rally
    type: rally
    test_vars:
      cifmw_test_operator_rally_concurrency: 2
      cifmw_test_operator_rally_fail_on_task_failure: false
```

## Custom task files

To use a custom Rally task file, either:

1. Add it to the role's `files/` directory and set `cifmw_rally_task_file` to its filename.
2. Pre-stage it in `cifmw_rally_artifacts_basedir/tasks/` via a `pre_test_stage_hooks` hook
   and set `cifmw_rally_task_file` to the filename.
