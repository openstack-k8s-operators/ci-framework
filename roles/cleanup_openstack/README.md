# cleanup_openstack

Cleans up OpenStack resources created by CIFMW while preserving the OpenShift cluster infrastructure for reuse. This role removes OpenStack-specific resources (CRs, API resources, storage) but keeps infrastructure operators and cluster components intact.

## Privilege escalation
None

## Parameters

### Cleanup Behavior

* `cifmw_cleanup_openstack_detach_bmh`: (Boolean) Detach BMH when cleaning flag, this is used to avoid deprovision when is not required. Default: `true`

* `cifmw_cleanup_openstack_delete_crs_direct`: (Boolean) Delete OpenStack CRs directly from cluster (not just from files). This ensures all OpenStackControlPlane, OpenStackDataPlaneDeployment, OpenStackDataPlaneNodeSet, and other CRs are removed. Default: `true`

* `cifmw_cleanup_openstack_delete_api_resources`: (Boolean) Delete OpenStack API resources (servers, networks, volumes, flavors, security groups, etc.) using the OpenStack client. This requires either an openstackclient pod in the cluster or openstackclient installed locally. Default: `true`

* `cifmw_cleanup_openstack_delete_storage`: (Boolean) Delete PVCs, secrets, ConfigMaps, and release PersistentVolumes. Default: `true`

* `cifmw_cleanup_openstack_delete_namespaces`: (Boolean) Delete OpenStack namespaces if they are empty. Use with caution as this will remove the namespace entirely. Default: `false`

* `cifmw_cleanup_openstack_force_remove_finalizers`: (Boolean) Force remove finalizers from stuck OpenStackControlPlane CRs. Use only if CRs are stuck in terminating state. Default: `false`

* `cifmw_cleanup_openstack_cloud_name`: (String) OpenStack cloud name to use for API cleanup. Default: `default`

### Path Configuration

The role includes default values for paths used by the `kustomize_deploy` and `deploy_bmh` roles. These can be overridden if needed:

* `cifmw_kustomize_deploy_basedir`: Base directory for kustomize deployment artifacts. Default: `{{ cifmw_basedir | default(ansible_user_dir ~ '/ci-framework-data') }}`

* `cifmw_kustomize_deploy_kustomizations_dest_dir`: Directory containing kustomization files. Default: `{{ cifmw_kustomize_deploy_basedir }}/artifacts/kustomize_deploy`

* `cifmw_kustomize_deploy_namespace`: OpenStack namespace. Default: `openstack`

* `cifmw_kustomize_deploy_operators_namespace`: OpenStack operators namespace. Default: `openstack-operators`

* `cifmw_deploy_bmh_basedir`: Base directory for BMH artifacts. Default: `{{ cifmw_basedir | default(ansible_user_dir ~ '/ci-framework-data') }}`

* `cifmw_deploy_bmh_dest_dir`: Directory containing BMH CRs. Default: `{{ cifmw_deploy_bmh_basedir }}/artifacts/deploy_bmh`

* `cifmw_deploy_bmh_namespace`: Namespace for BaremetalHost resources. Default: `openshift-machine-api`

**Note**: This role is self-contained and does not require the `kustomize_deploy` or `deploy_bmh` roles to be present. All necessary default values are included in this role's `defaults/main.yaml`.

## What gets cleaned up

### Always cleaned (when enabled):
- OpenStack CRs (OpenStackControlPlane, OpenStackDataPlaneDeployment, OpenStackDataPlaneNodeSet, OpenStackDataPlaneService, OpenStackClient, OpenStackVersion)
- Bare Metal Hosts (detached, not deprovisioned)
- OpenStack deployment CRs from kustomize files
- OpenStack API resources (servers, networks, volumes, flavors, security groups, etc.)
- PVCs, secrets, ConfigMaps in OpenStack namespace
- PersistentVolumes in Released state
- Certificates and Issuers (cert-manager)
- Artifacts, logs, and test directories

### Optionally cleaned:
- Namespaces (if empty)

## What is preserved

The following infrastructure components are **NOT** deleted to preserve cluster reusability:
- NMState operator (network management)
- MetalLB operator (load balancing)
- OLM (Operator Lifecycle Manager)
- OpenShift cluster operators
- Cluster-level infrastructure resources

## Usage

Basic cleanup (removes OpenStack CRs and storage, keeps OpenShift cluster):
```yaml
- name: Cleanup OpenStack
  include_role:
    name: cleanup_openstack
```

Disable API resource cleanup (if needed):
```yaml
- name: Cleanup OpenStack without API resources
  include_role:
    name: cleanup_openstack
  vars:
    cifmw_cleanup_openstack_delete_api_resources: false
```

Aggressive cleanup (removes everything including namespaces):
```yaml
- name: Aggressive cleanup
  include_role:
    name: cleanup_openstack
  vars:
    cifmw_cleanup_openstack_delete_api_resources: true
    cifmw_cleanup_openstack_delete_namespaces: true
    cifmw_cleanup_openstack_force_remove_finalizers: true
```
