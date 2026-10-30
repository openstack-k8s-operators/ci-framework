# rally
Role to setup and run Rally benchmarking tests against an OpenStack deployment.

Rally is run inside the `quay.io/airshipit/xrally-openstack` container via podman.
OpenStack credentials are discovered automatically from the Kubernetes KeystoneAPI resource,
or can be supplied directly via `cifmw_rally_os_*` variables.

## Prerequisites
- `oc` CLI available and pointing to the target OpenStack cluster (used for credential and CA discovery).
- `cifmw_openstack_namespace` must be set to the OpenStack namespace (typically `openstack`).

### Manila prerequisites

If running Manila benchmarks, the `dhss_true` share type must exist before Rally runs.
Use `manila_create_default_resources.yml` with `share_type_name` and `extra_specs` overrides:

```yaml
pre_tests_80_manila_share_type:
  type: playbook
  source: manila_create_default_resources.yml
  extra_vars:
    share_type_name: dhss_true
    extra_specs: {}
```

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
* `cifmw_rally_task_file`: (String) Absolute path to a custom Rally task YAML on the host.
  Mutually exclusive with `cifmw_rally_openstack_tests`. Default: `""`
* `cifmw_rally_task_extra_args`: (String) Extra arguments passed verbatim to `rally task start`. Default: `""`
* `cifmw_rally_dns_servers`: (List) DNS servers used inside the Rally container. Default: `["192.168.122.10"]`
* `cifmw_rally_os_auth_url`: (String) OpenStack auth URL. Auto-discovered from KeystoneAPI if unset.
* `cifmw_rally_os_username`: (String) OpenStack username. Default: `admin`
* `cifmw_rally_os_password`: (String) OpenStack password. Auto-discovered from Kubernetes secret if unset.
* `cifmw_rally_os_project_name`: (String) OpenStack project. Default: `admin`
* `cifmw_rally_os_user_domain_name`: (String) User domain. Default: `Default`
* `cifmw_rally_os_project_domain_name`: (String) Project domain. Default: `Default`
* `cifmw_rally_os_region_name`: (String) OpenStack region. Default: `regionOne`
* `cifmw_rally_runs`: (List) List of run definitions for sequential multi-run mode.
  When empty (default), the role runs once using the top-level `cifmw_rally_*` variables.
  When non-empty, the role loops over the list; each entry may override any `cifmw_rally_*`
  variable for that run and **must** include a `name` key used to namespace artifacts.
  Default: `[]`

## Standalone usage (single run)

```yaml
- hosts: hypervisor
  roles:
    - role: rally
      vars:
        cifmw_rally_openstack_tests: "cinder"
        cifmw_rally_concurrency: 2
        cifmw_rally_fail_on_task_failure: false
```

## Usage via hook (multiple runs)

Add a `post_tests_*` hook in your job vars and define `cifmw_rally_runs`:

```yaml
post_tests_90_rally_run:
  type: playbook
  source: rally_run.yaml
cifmw_rally_runs:
  - name: cinder
    cifmw_rally_openstack_tests: "cinder"
    cifmw_rally_concurrency: 1
  - name: nova
    cifmw_rally_openstack_tests: "nova"
    cifmw_rally_concurrency: 2
    cifmw_rally_fail_on_task_failure: false
```

Each run stores its artifacts under `cifmw_rally_artifacts_basedir/<name>/`.

## Custom task files

To use a custom Rally task file, set `cifmw_rally_task_file` to the absolute path of the
YAML on the hypervisor host (pre-stage it via an earlier hook if needed).

### Glance image preparation

For custom Glance workloads, run `rally_glance_prerequisites.yaml` on the same
host as `rally_run.yaml`. It installs `qemu-img`, creates 100 MiB dummy QCOW2
and raw disks, and caches a checksum-verified CirrOS 0.6.2 boot image. Existing
images are validated and reused; invalid files are reported and left untouched.
Image preparation errors are rescued with a warning so this hook does not
prevent Rally execution. Scenarios that require unavailable or invalid images
may fail, while other workloads can still run.
Image preparation does not depend on whether a CirrOS image already exists
in Glance: image-creation scenarios need a local file to upload themselves.

Order the hooks before Rally execution, for example:

```yaml
post_tests_70_rally_prerequisites:
  type: playbook
  source: rally_prerequisites.yaml
post_tests_80_rally_glance_prerequisites:
  type: playbook
  source: rally_glance_prerequisites.yaml
post_tests_90_rally_run:
  type: playbook
  source: rally_run.yaml
```

The Glance hook honors `cifmw_rally_artifacts_basedir`. In multi-run mode it
prepares entries named `glance` and skips other runs. In single-run mode
(`cifmw_rally_runs` unset or empty), it prepares the base artifacts directory.
The common prerequisites hook shown above currently expects `cifmw_rally_runs`
and handles named runs; configure those shared cloud prerequisites separately
when using single-run mode.

Images are placed under each selected run's `tasks/images/`, which the role's
existing tasks volume makes available inside the container. Update the custom
workload to use these paths for `image_location` and `contexts.images.image_url`:

- `/var/lib/rally/tasks/images/dummy_image.qcow2` for QCOW2 API tests.
- `/var/lib/rally/tasks/images/dummy_image.raw` for raw API tests.
- `/var/lib/rally/tasks/images/cirros.qcow2` for `create_image_and_boot_instances`.

An empty dummy disk cannot boot an OS. Keep the boot scenario's Rally-managed
network context and `boot_server_kwargs.auto_assign_nic: true` when temporary
tenants have no suitable shared network. Set `sla.failure_rate.max: 0` for each
workload so CI detects failures. These settings belong in the custom task YAML;
the preparation hook does not rewrite workloads or change bundled tests.

The hook does not change Rally's test-failure policy. To continue to later
component runs even if a Glance run fails, set
`cifmw_rally_fail_on_task_failure: false` in that run's `cifmw_rally_runs` entry.
Rally still records the scenario failures in its logs and reports.
