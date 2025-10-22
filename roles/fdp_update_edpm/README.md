# fdp_update_edpm

Unified role for updating OpenStack EDPM (Edge Data Plane Management) nodes with custom container images and host packages.

## Description

This role combines the functionality of `fdp_update_edpm_containers` and `fdp_update_edpm_host_packages` into a single, declarative role that:

1. **Updates container images** by patching OpenStackDataPlaneNodeSet CRs with new image references
2. **Updates host packages** by configuring `edpm_bootstrap_packages` and `edpm_bootstrap_repos` in the nodeset
3. **Configures registry authentication** with OpenShift service account tokens
4. **Installs CA certificates** for secure registry access
5. **Optionally creates deployments** to apply the changes to EDPM nodes

### Key Features

- **Declarative approach**: Only modifies Kubernetes CRs, doesn't execute commands directly on EDPM nodes
- **Uses native EDPM capabilities**: Leverages `edpm_bootstrap` and `edpm_podman` roles from edpm-ansible
- **Secure by default**: Installs OpenShift CA certificates instead of using insecure registries
- **Flexible**: Supports updating containers, packages, or both
- **Idempotent**: Can be run multiple times safely

## Requirements

- OpenShift cluster with OpenStack operators installed
- Access to `oc` command
- SSH access to EDPM nodes (for CA certificate installation)
- OpenStackVersion CR with custom container images
- Custom repository with updated packages (if updating host packages)

## Role Variables

### General Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `cifmw_fdp_update_edpm_enabled` | `true` | Enable/disable the role |
| `cifmw_fdp_update_edpm_namespace` | `"openstack"` | OpenShift namespace |
| `cifmw_fdp_update_edpm_nodeset_name` | `"all"` | NodeSet to update (`"all"` or specific name) |
| `cifmw_fdp_update_edpm_dry_run` | `false` | Show changes without applying |

### Container Image Updates

| Variable | Default | Description |
|----------|---------|-------------|
| `cifmw_fdp_update_edpm_containers_enabled` | `true` | Enable container image updates |
| `cifmw_fdp_update_edpm_image_registry` | `""` | External registry URL (auto-detected if empty) |
| `cifmw_fdp_update_edpm_image_variable_mapping` | See defaults | Mapping of image keys to EDPM variables |

### Host Package Updates

| Variable | Default | Description |
|----------|---------|-------------|
| `cifmw_fdp_update_edpm_packages_enabled` | `true` | Enable host package updates |
| `cifmw_fdp_update_edpm_repo_baseurl` | `""` | **REQUIRED** Repository base URL |
| `cifmw_fdp_update_edpm_repo_name` | `"custom-updates"` | Repository name |
| `cifmw_fdp_update_edpm_packages` | See defaults | List of packages to install/update |

### Registry Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `cifmw_fdp_update_edpm_configure_registry_ca` | `true` | Install OpenShift CA certificate |
| `cifmw_fdp_update_edpm_configure_insecure_registry` | `false` | Configure registry as insecure (not recommended) |
| `cifmw_fdp_update_edpm_configure_registry_auth` | `true` | Configure registry authentication |

### Deployment Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `cifmw_fdp_update_edpm_auto_deploy` | `true` | Automatically create deployment |
| `cifmw_fdp_update_edpm_deployment_per_nodeset` | `true` | Create separate deployment per nodeset |
| `cifmw_fdp_update_edpm_wait_for_deployment` | `true` | Wait for deployment to complete |
| `cifmw_fdp_update_edpm_deployment_timeout` | `3600` | Deployment timeout (seconds) |
| `cifmw_fdp_update_edpm_deployment_services` | See defaults | Services to run in deployment |

## Dependencies

None (uses native OpenStack Data Plane operators and edpm-ansible roles)

## Example Playbook

### Update both containers and packages

```yaml
- hosts: localhost
  roles:
    - role: fdp_update_edpm
      vars:
        cifmw_fdp_update_edpm_namespace: openstack
        cifmw_fdp_update_edpm_nodeset_name: openstack-edpm
        cifmw_fdp_update_edpm_repo_baseurl: "http://example.com/repos/fdp-updates"
        cifmw_fdp_update_edpm_packages:
          - openvswitch3.5
          - openvswitch-selinux-extra-policy
```

### Update only containers

```yaml
- hosts: localhost
  roles:
    - role: fdp_update_edpm
      vars:
        cifmw_fdp_update_edpm_packages_enabled: false
        cifmw_fdp_update_edpm_containers_enabled: true
```

### Update only packages

```yaml
- hosts: localhost
  roles:
    - role: fdp_update_edpm
      vars:
        cifmw_fdp_update_edpm_containers_enabled: false
        cifmw_fdp_update_edpm_packages_enabled: true
        cifmw_fdp_update_edpm_repo_baseurl: "http://example.com/repos/updates"
```

### Dry run (show changes without applying)

```yaml
- hosts: localhost
  roles:
    - role: fdp_update_edpm
      vars:
        cifmw_fdp_update_edpm_dry_run: true
```

## How It Works

1. **Fetches NodeSets**: Gets OpenStackDataPlaneNodeSet CRs from the cluster
2. **Fetches container images** (if enabled): Gets custom images from OpenStackVersion CR
3. **For each NodeSet**:
   - Patches container image variables (e.g., `edpm_ovn_controller_agent_image`)
   - Patches `edpm_bootstrap_packages` with packages to install
   - Patches `edpm_bootstrap_repos` with custom repository configuration
   - Configures registry authentication (`edpm_container_registry_logins`)
   - Installs CA certificate via SSH (if enabled)
4. **Creates deployment** (if enabled): Creates OpenStackDataPlaneDeployment CR
5. **Waits for completion** (if enabled): Monitors deployment until Ready

## Architecture: Declarative vs Imperative

This role follows the **declarative** approach of Kubernetes/OpenStack:

- ❌ **Does NOT** SSH to nodes and run `dnf install` directly
- ❌ **Does NOT** SSH to nodes and run `systemctl restart` directly
- ✅ **Does** patch NodeSet CRs with desired state
- ✅ **Does** let OpenStack Data Plane Operator apply the changes
- ✅ **Does** use native `edpm_bootstrap` role for package installation
- ✅ **Does** use native `edpm_podman` role for container management

The only exception is CA certificate installation, which uses SSH because there's no native EDPM mechanism for it yet.

## Migration from Old Roles

If you're migrating from `fdp_update_edpm_containers` or `fdp_update_edpm_host_packages`:

| Old Variable | New Variable |
|--------------|--------------|
| `cifmw_fdp_update_edpm_containers_namespace` | `cifmw_fdp_update_edpm_namespace` |
| `cifmw_fdp_update_edpm_containers_nodeset_name` | `cifmw_fdp_update_edpm_nodeset_name` |
| `cifmw_fdp_update_host_packages_repo_baseurl` | `cifmw_fdp_update_edpm_repo_baseurl` |
| `cifmw_fdp_update_host_packages_packages` | `cifmw_fdp_update_edpm_packages` |

## License

Apache 2.0

## Author Information

Red Hat OpenStack CI Framework Team
