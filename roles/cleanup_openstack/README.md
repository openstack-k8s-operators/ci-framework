# cleanup_openstack

Cleans up OpenStack resources created by CIFMW while preserving the OpenShift cluster infrastructure for reuse. This role removes OpenStack-specific resources (CRs, API resources, storage) but keeps infrastructure operators and cluster components intact.

## Privilege escalation

May require privilege escalation for:
- Removing artifacts and logs from protected directories
- Installing openstackclient locally (if needed)

## Parameters

### Cleanup Behavior

* `cifmw_cleanup_openstack_dry_run`: (Boolean) When true, only reports what would be deleted without making changes. Useful for verification before actual cleanup. Default: `false`

* `cifmw_cleanup_openstack_detach_bmh`: (Boolean) Detach BareMetalHost resources to prevent deprovisioning. This allows reuse of physical hardware. Default: `true`

* `cifmw_cleanup_openstack_delete_crs_direct`: (Boolean) Delete OpenStack CRs directly from cluster (not just from files). This ensures all OpenStackControlPlane, OpenStackDataPlaneDeployment, OpenStackDataPlaneNodeSet, and other CRs are removed. Default: `true`

* `cifmw_cleanup_openstack_delete_api_resources`: (Boolean) Delete OpenStack API resources (servers, networks, volumes, flavors, security groups, etc.) using the OpenStack client. This requires either an openstackclient pod in the cluster or openstackclient installed locally. Default: `true`

* `cifmw_cleanup_openstack_delete_storage`: (Boolean) Delete PVCs, secrets, ConfigMaps, and release PersistentVolumes. Default: `true`

* `cifmw_cleanup_openstack_delete_namespaces`: (Boolean) Delete OpenStack namespaces if they are empty. Use with caution as this will remove the namespace entirely. Default: `false`

* `cifmw_cleanup_openstack_force_remove_finalizers`: (Boolean) Force remove finalizers from stuck OpenStackControlPlane CRs. Use only if CRs are stuck in terminating state. Default: `false`

* `cifmw_cleanup_openstack_cloud_name`: (String) OpenStack cloud name to use for API cleanup. Default: `default`

* `cifmw_cleanup_openstack_keep_generated_crs`: (Boolean) Keep generated CR YAML files after deletion (for debugging). Default: `false`

### Path Configuration

The role includes default values for paths used by the `kustomize_deploy` and `deploy_bmh` roles. These can be overridden if needed:

* `cifmw_kustomize_deploy_basedir`: Base directory for kustomize deployment artifacts. Default: `{{ cifmw_basedir | default(ansible_user_dir ~ '/ci-framework-data') }}`

* `cifmw_kustomize_deploy_kustomizations_dest_dir`: Directory containing kustomization files. Default: `{{ cifmw_kustomize_deploy_basedir }}/artifacts/kustomize_deploy`

* `cifmw_kustomize_deploy_namespace`: OpenStack namespace. Default: `openstack`

* `cifmw_kustomize_deploy_operators_namespace`: OpenStack operators namespace. Default: `openstack-operators`

* `cifmw_deploy_bmh_basedir`: Base directory for BMH artifacts. Default: `{{ cifmw_basedir | default(ansible_user_dir ~ '/ci-framework-data') }}`

* `cifmw_deploy_bmh_dest_dir`: Directory containing BMH CRs. Default: `{{ cifmw_deploy_bmh_basedir }}/artifacts/deploy_bmh`

* `cifmw_deploy_bmh_namespace`: Namespace for BaremetalHost resources. Default: `openshift-machine-api`

### OpenShift Cluster Access

* `cifmw_openshift_kubeconfig`: (String) Path to kubeconfig file. Optional - will be inherited from `openshift_login` role if available, falls back to `KUBECONFIG` environment variable, or defaults to `~/.kube/config`.

* `cifmw_openshift_token`: (String) OpenShift API token. Optional.

* `cifmw_openshift_context`: (String) OpenShift context to use. Optional.

### Architecture Variables (Optional)

These are only needed if you deployed using architecture-based automation. If not provided, cleanup will skip architecture-specific tasks:

* `cifmw_architecture_repo`: (String) Path to architecture repository. Optional.

* `cifmw_architecture_scenario`: (String) Scenario name used during deployment. Optional.

* `cifmw_architecture_automation_file`: (String) Direct path to automation YAML file. Optional - overrides repo+scenario.

**Note**: This role is self-contained and does not require the `kustomize_deploy`, `deploy_bmh`, or `openshift_login` roles to be present. All necessary default values are included in this role's `defaults/main.yaml`. Architecture variables are optional and only needed for architecture-based deployments.

## What gets cleaned up

### Always cleaned (when enabled):
- OpenStack CRs (OpenStackControlPlane, OpenStackDataPlaneDeployment, OpenStackDataPlaneNodeSet, OpenStackDataPlaneService, OpenStackClient, OpenStackVersion)
- Bare Metal Hosts (detached, not deprovisioned)
- OpenStack deployment CRs from kustomize files
- OpenStack API resources (servers, networks, volumes, flavors, security groups, load balancers, Swift containers, etc.)
- PVCs, secrets, ConfigMaps in OpenStack namespace
- PersistentVolumes in Released state
- Certificates and Issuers (cert-manager)
- Artifacts, logs, and test directories

### Optionally cleaned:
- Namespaces (if empty and explicitly enabled)

## What is preserved

The following infrastructure components are **NOT** deleted to preserve cluster reusability:
- NMState operator (network management)
- MetalLB operator (load balancing)
- OLM (Operator Lifecycle Manager)
- cert-manager operator
- OpenShift cluster operators
- Cluster-level infrastructure resources

## Usage

### Basic cleanup
Removes OpenStack CRs and storage, keeps OpenShift cluster:

```yaml
- name: Cleanup OpenStack
  include_role:
    name: cleanup_openstack
```

### Dry-run mode
Preview what would be deleted without making changes:

```yaml
- name: Preview cleanup
  include_role:
    name: cleanup_openstack
  vars:
    cifmw_cleanup_openstack_dry_run: true
```

### Selective cleanup using tags

```bash
# Only detach BMH
ansible-playbook cleanup-openstack-for-reuse.yml --tags cleanup_bmh

# Only clean CRs from cluster
ansible-playbook cleanup-openstack-for-reuse.yml --tags cleanup_crs_direct

# Clean CRs and storage
ansible-playbook cleanup-openstack-for-reuse.yml --tags cleanup_crs_direct,cleanup_storage

# Skip OpenStack API cleanup
ansible-playbook cleanup-openstack-for-reuse.yml --skip-tags cleanup_api
```

Available tags:
- `cleanup_bmh` - Detach BareMetalHosts
- `cleanup_crs` - Delete CRs from files
- `cleanup_crs_direct` - Delete CRs directly from cluster
- `cleanup_api` - Clean OpenStack API resources
- `cleanup_storage` - Clean storage resources (PVCs, secrets, PVs)
- `cleanup_namespaces` - Delete empty namespaces
- `cleanup_artifacts` - Remove artifacts and logs

### Disable specific cleanup operations

```yaml
- name: Cleanup without API resources
  include_role:
    name: cleanup_openstack
  vars:
    cifmw_cleanup_openstack_delete_api_resources: false
```

### Aggressive cleanup
Removes everything including namespaces:

```yaml
- name: Aggressive cleanup
  include_role:
    name: cleanup_openstack
  vars:
    cifmw_cleanup_openstack_delete_api_resources: true
    cifmw_cleanup_openstack_delete_namespaces: true
    cifmw_cleanup_openstack_force_remove_finalizers: true
```

### With custom kubeconfig

```yaml
- name: Cleanup with custom kubeconfig
  include_role:
    name: cleanup_openstack
  vars:
    cifmw_openshift_kubeconfig: /path/to/kubeconfig
```

## Cleanup Summary

The role provides a detailed summary at the end showing:
- Execution mode (dry-run or actual)
- Duration in seconds
- Number of CRs deleted
- API resources cleanup status
- Storage cleanup status
- BMH detachment count
- Namespaces deleted (if any)
- Errors encountered (if any)

## Error Handling

The role is designed to be fault-tolerant:
- Failed operations don't stop the cleanup process
- Missing resources are skipped gracefully
- Kubernetes API failures are handled with retries
- Comprehensive error reporting in final summary

## Integration

This role integrates seamlessly with:
- **openshift_login**: Inherits kubeconfig and authentication
- **kustomize_deploy**: Uses deployment paths and namespaces
- **deploy_bmh**: Handles BaremetalHost cleanup
- **test_operator**: Cleans up test resources
- **architecture scenarios**: Automatically detects and processes architecture-based deployments

## Examples

### Example 1: CI job cleanup for infrastructure reuse
```bash
ansible-playbook -i inventory.yml cleanup-openstack-for-reuse.yml
```

### Example 2: Troubleshooting - dry-run first
```bash
# Preview cleanup
ansible-playbook cleanup-openstack-for-reuse.yml -e cifmw_cleanup_openstack_dry_run=true

# If preview looks good, execute
ansible-playbook cleanup-openstack-for-reuse.yml
```

### Example 3: Clean only specific components
```bash
# Only clean storage and CRs, preserve API resources
ansible-playbook cleanup-openstack-for-reuse.yml \
  --tags cleanup_storage,cleanup_crs_direct
```

### Example 4: Architecture-based deployment cleanup
```yaml
- name: Cleanup architecture deployment
  include_role:
    name: cleanup_openstack
  vars:
    cifmw_architecture_repo: /path/to/architecture
    cifmw_architecture_scenario: hci
```

## Verification

After cleanup, verify the cluster state:
- OpenStack CRs should be gone: `oc get openstackcontrolplane -n openstack`
- Infrastructure operators should remain: `oc get pods -n openshift-operators`
- PVCs should be cleaned: `oc get pvc -n openstack`

See also: `playbooks/cleanup/verify-cleanup.yaml` in ci-framework-jobs repository.
