# Update Control Flags

This document describes the granular control flags available for the container update workflow.

## Overview

The update workflow provides three independent control flags to enable/disable specific update operations:

1. **`cifmw_upic_update_control_plane_images`** - Update control plane pod/container images
2. **`cifmw_upic_update_edpm_images`** - Update EDPM compute container images (NodeSets)
3. **`cifmw_upic_update_edpm_host_packages`** - Update packages on EDPM compute node hosts

## Control Flags

### 1. Control Plane Images (`cifmw_upic_update_control_plane_images`)

**Default:** `true`

Controls whether to build and update container images for control plane services.

**What it does:**
- Builds new container images with updated packages
- Pushes images to OpenShift internal registry
- Updates OpenStackVersion CR with custom images

**When to disable:**
- You only want to update compute nodes
- Control plane is already up to date
- Testing EDPM updates in isolation

**Example:**
```bash
# Only update EDPM, skip control plane
ansible-playbook playbooks/update_all_containers.yml \
  -e cifmw_upic_target_package=ovn24.03 \
  -e cifmw_upic_repo_baseurl=http://example.com/repo/ \
  -e cifmw_upic_update_control_plane_images=false
```

### 2. EDPM Container Images (`cifmw_upic_update_edpm_images`)

**Default:** `true`

Controls whether to update EDPM NodeSets with custom container image variables.

**What it does:**
- Fetches custom images from OpenStackVersion CR
- Updates OpenStackDataPlaneNodeSets with EDPM image variables
- Maps control plane images to EDPM ansible variables

**When to disable:**
- You only want to update host packages, not containers
- NodeSets are already configured correctly
- Testing host package updates in isolation

**Example:**
```bash
# Only update host packages, skip EDPM container images
ansible-playbook playbooks/update_all_containers.yml \
  -e cifmw_upic_target_package=openvswitch3.3 \
  -e cifmw_upic_repo_baseurl=http://example.com/repo/ \
  -e cifmw_upic_update_control_plane_images=false \
  -e cifmw_upic_update_edpm_images=false
```

### 3. EDPM Host Packages (`cifmw_upic_update_edpm_host_packages`)

**Default:** `true`

Controls whether to create OpenStackDataPlaneService for updating host packages.

**What it does:**
- Creates `update-host-packages` OpenStackDataPlaneService
- Configures custom repository on compute nodes
- Updates host packages (e.g., openvswitch, kernel)
- Restarts services (e.g., openvswitch)

**When to disable:**
- You only want to update containers, not host packages
- Host packages are already up to date
- Testing container updates in isolation

**Example:**
```bash
# Only update containers, skip host packages
ansible-playbook playbooks/update_all_containers.yml \
  -e cifmw_upic_target_package=ovn24.03 \
  -e cifmw_upic_repo_baseurl=http://example.com/repo/ \
  -e cifmw_upic_update_edpm_host_packages=false
```

## Common Use Cases

### Use Case 1: Update Everything (Default)

Update control plane containers, EDPM containers, and EDPM host packages:

```bash
ansible-playbook playbooks/update_all_containers.yml \
  -e cifmw_upic_target_package=ovn24.03 \
  -e cifmw_upic_repo_baseurl=http://example.com/repo/
```

All flags default to `true`, so everything is updated.

### Use Case 2: Only Update Control Plane

Update only control plane containers, skip all EDPM updates:

```bash
ansible-playbook playbooks/update_all_containers.yml \
  -e cifmw_upic_target_package=ovn24.03 \
  -e cifmw_upic_repo_baseurl=http://example.com/repo/ \
  -e cifmw_upic_update_edpm_images=false \
  -e cifmw_upic_update_edpm_host_packages=false
```

### Use Case 3: Only Update EDPM Host Packages

Update only host packages on compute nodes (e.g., openvswitch):

```bash
ansible-playbook playbooks/update_all_containers.yml \
  -e cifmw_upic_target_package=openvswitch3.3 \
  -e cifmw_upic_repo_baseurl=http://example.com/ovs-repo/ \
  -e cifmw_upic_update_control_plane_images=false \
  -e cifmw_upic_update_edpm_images=false
```

### Use Case 4: Update Control Plane + EDPM Containers (No Host Packages)

Update containers but skip host package updates:

```bash
ansible-playbook playbooks/update_all_containers.yml \
  -e cifmw_upic_target_package=ovn24.03 \
  -e cifmw_upic_repo_baseurl=http://example.com/repo/ \
  -e cifmw_upic_update_edpm_host_packages=false
```

### Use Case 5: Only Update EDPM (Containers + Host)

Skip control plane, update only EDPM:

```bash
ansible-playbook playbooks/update_all_containers.yml \
  -e cifmw_upic_target_package=ovn24.03 \
  -e cifmw_upic_repo_baseurl=http://example.com/repo/ \
  -e cifmw_upic_update_control_plane_images=false
```

## Verification

After running the playbook, you can verify what was updated:

### Control Plane Images

```bash
# Check OpenStackVersion CR
oc get openstackversion -n openstack -o yaml | grep customContainerImages -A 20
```

### EDPM Container Images

```bash
# Check NodeSets for custom image variables
oc get openstackdataplanenodeset openstack-edpm -n openstack -o yaml | grep -A 5 "edpm_.*_image"
```

### EDPM Host Package Service

```bash
# Check if service was created
oc get openstackdataplaneservice update-host-packages -n openstack

# View service details
oc get openstackdataplaneservice update-host-packages -n openstack -o yaml
```

## Decision Matrix

| Scenario | Control Plane | EDPM Images | EDPM Host |
|----------|---------------|-------------|-----------|
| Full update (default) | ✅ | ✅ | ✅ |
| Only control plane | ✅ | ❌ | ❌ |
| Only EDPM | ❌ | ✅ | ✅ |
| Only containers (no host) | ✅ | ✅ | ❌ |
| Only host packages | ❌ | ❌ | ✅ |
| Control + EDPM containers | ✅ | ✅ | ❌ |
| Control + EDPM host | ✅ | ❌ | ✅ |
| EDPM containers + host | ❌ | ✅ | ✅ |

## Notes

- All flags default to `true` for maximum coverage
- Flags are independent - any combination is valid
- Setting all flags to `false` will skip all updates
- Use dry-run to see what would be updated: `-e cifmw_uec_dry_run=true`

## Related Documentation

- [Update Container Packages](UPDATE_CONTAINER_PACKAGES.md)
- [Update EDPM Containers](UPDATE_EDPM_CONTAINERS.md)
