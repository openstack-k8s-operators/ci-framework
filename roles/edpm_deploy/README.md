# edpm_deploy
Perform External compute deploy on the pre-provisioned node from openshift cluster.

## Privilege escalation
None

## Parameters
* `cifmw_edpm_deploy_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_edpm_deploy_manifests_dir`: (String) Directory in where install_yamls output manifests will be placed. Defaults to `"{{ cifmw_manifests | default(cifmw_edpm_deploy_basedir ~ '/artifacts/manifests') }}"`.
* `cifmw_edpm_deploy_os_runner_img`: (String) OpenStack Runner image url. Defaults to `"quay.io/openstack-k8s-operators/openstack-ansibleee-runner:latest"`.
* `cifmw_edpm_deploy_dataplanenodeset_cr`: (String) Path to OpenStackDataPlaneNodeSet CR. Defaults to `"config/samples/dataplane_v1beta1_openstackdataplanenodeset.yaml"`.
* `cifmw_edpm_deploy_retries`: (Integer) Number of retries for edpm deploy status. Defaults to `100`.
* `cifmw_edpm_deploy_run_validation`: (Boolean) Run validation on EDPM node. Defaults to `False`.
* `cifmw_edpm_deploy_dryrun`: (Boolean) Do a dry run on make edpm_deploy command. Defaults to `False`.
* `cifmw_edpm_deploy_timeout`: (Integer) Time, in minutes to wait for the deployment to be ready. Defaults to `40`.
* `cifmw_edpm_deploy_nova_compute_extra_config`: (String) Oslo config snippet defining extra configuration for the nova-compute services. Defaults to an empty string.
* `cifmw_edpm_deploy_nova_compute_extra_configs`: (Dict) Per-NodeSet nova-compute configuration. Defaults to `{}`, preserving the common configuration path. See the example and validation rules below.
* `cifmw_edpm_deploy_step2_kind`: (String) Define the resources that should be applied only in a second step during the EDPM deployment. Defaults to `"OpenStackDataPlaneDeployment"`.

## Per-Nodeset nova extra configuration

`cifmw_edpm_deploy_nova_compute_extra_configs` allows different groups of
compute hosts to run with different `nova.conf` options, which is needed for
example to give each compute a different `[compute] cpu_dedicated_set` when
testing CPU pinning and live migration with the whitebox tempest plugin:

```yaml
cifmw_edpm_deploy_nova_compute_extra_configs:
  openstack-edpm-0:
    hosts:
      - compute-0
    nova_compute_extra_config: |
      [compute]
      cpu_dedicated_set = 0,1,4,5
      cpu_shared_set = 2,3,6,7
  openstack-edpm-1:
    hosts:
      - compute-1
    nova_compute_extra_config: |
      [compute]
      cpu_dedicated_set = 2,3,6,7
      cpu_shared_set = 0,1,4,5
```

The map keys become the final NodeSet names. Each entry contains a `hosts`
list and a `nova_compute_extra_config` string. Hostnames are the rendered
nodes' `hostName` values, which the multinode CI hook sets from inventory
aliases such as `compute-0`.

This path splits exactly one rendered, pre-provisioned NodeSet and its
deployment after kustomization. Every compute must be listed exactly once
across non-empty groups; a mismatched assignment fails before applying
dataplane resources. Any number of groups can be declared, and a group can
contain multiple hosts. The
`OpenStackDataPlaneDeployment` references every generated NodeSet, and the
role waits for each of them to become `SetupReady`.

Each group gets a `nova-<NodeSet name>` service and a
`nova-extra-config-<NodeSet name>` ConfigMap referenced through the service's
`dataSources`. The service type remains `nova`, preserving dependency matching
and the `/var/lib/openstack/nova/25-nova-extra.conf` path on each host.

When the mapping is non-empty, `cifmw_edpm_deploy_nova_compute_extra_config`
is ignored. Because each entry replaces the nova service of its NodeSet, the snippet of
an entry must be complete: options that the job previously set through
`cifmw_edpm_deploy_nova_compute_extra_config` for every compute, such as the
`[libvirt]` CPU model used to allow live migration between computes from the
node pool, have to be repeated in every entry.

## TODO
- Add support for deploying multiple compute node
- Integrate EDPM kustomize

## Resources
* [install_yamls](https://github.com/openstack-k8s-operators/install_yamls)
