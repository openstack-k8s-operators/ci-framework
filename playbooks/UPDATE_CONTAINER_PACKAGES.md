# Update Container Packages Playbook

This document describes how to use the `update_container_packages.yml` playbook to update RPM packages in OpenStack container images for both control plane and data plane (EDPM) nodes.

## Overview

The playbook automates the process of:
1. Fetching container images from the OpenStackVersion CR
2. Checking which images contain the target package
3. Building new images with updated packages from a custom repository
4. Pushing updated images to the OpenShift internal registry
5. Updating the OpenStackVersion CR to use the new images
6. (Optional) Automatically updating EDPM NodeSets with the custom images

## Complete Workflow (Control Plane + EDPM)

To update both control plane and EDPM containers in one command:

```bash
# Update all containers (control plane + EDPM)
ansible-playbook playbooks/update_all_containers.yml \
  -e cifmw_upic_target_package=ovn24.03 \
  -e cifmw_upic_repo_baseurl=http://example.com/custom-repo/

# Update specific EDPM NodeSet
ansible-playbook playbooks/update_all_containers.yml \
  -e cifmw_upic_target_package=ovn24.03 \
  -e cifmw_upic_repo_baseurl=http://example.com/custom-repo/ \
  -e cifmw_uec_nodeset_name=openstack-edpm

# Dry run to see what would change
ansible-playbook playbooks/update_all_containers.yml \
  -e cifmw_upic_target_package=ovn24.03 \
  -e cifmw_upic_repo_baseurl=http://example.com/custom-repo/ \
  -e cifmw_uec_dry_run=true
```

See [Update EDPM Containers](UPDATE_EDPM_CONTAINERS.md) for more details on EDPM updates.

## Quick Start (Control Plane Only)

### Method 1: Using the Helper Script (Recommended)

The easiest way to run the update:

```bash
# Update OVN package
./scripts/update_container_packages.sh \
  --package ovn24.03 \
  --repo http://example.com/custom-repo/

# Using a predefined vars file
./scripts/update_container_packages.sh --vars ovn_update.yml

# Dry run to see what would happen
./scripts/update_container_packages.sh \
  --package ovn24.03 \
  --repo http://example.com/repo/ \
  --dry-run
```

### Method 2: Direct Ansible Playbook Execution

```bash
# Using command line variables
ansible-playbook playbooks/update_container_packages.yml \
  -e cifmw_upic_target_package=ovn24.03 \
  -e cifmw_upic_repo_baseurl=http://example.com/repo/

# Using a variables file
ansible-playbook playbooks/update_container_packages.yml \
  -e @playbooks/vars/ovn_update.yml
```

## Predefined Configurations

The following variable files are available in `playbooks/vars/`:

### 1. OVN Update (`ovn_update.yml`)

Updates OVN 24.03 package - replicates the original bash script:

```bash
ansible-playbook playbooks/update_container_packages.yml \
  -e @playbooks/vars/ovn_update.yml
```

### 2. Neutron Update (`neutron_update.yml`)

Updates Neutron packages:

```bash
ansible-playbook playbooks/update_container_packages.yml \
  -e @playbooks/vars/neutron_update.yml
```

## Custom Configuration

### Creating Your Own Variables File

Create a file in `playbooks/vars/my_update.yml`:

```yaml
---
# Target package to update
cifmw_upic_target_package: "my-package"

# Repository configuration
cifmw_upic_repo_baseurl: "http://my-repo.example.com/"
cifmw_upic_repo_name: "my-custom-repo"

# Optional: Override defaults
cifmw_upic_namespace: "openstack"
cifmw_upic_image_name_prefix: "my-update"
```

Then run:

```bash
ansible-playbook playbooks/update_container_packages.yml \
  -e @playbooks/vars/my_update.yml
```

## Available Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `cifmw_upic_target_package` | RPM package name to update | `ovn24.03` |
| `cifmw_upic_repo_baseurl` | Repository base URL | `http://repo.example.com/` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `cifmw_upic_namespace` | `openstack` | OpenShift namespace |
| `cifmw_upic_openstack_cr_name` | `controlplane` | OpenStackVersion CR name |
| `cifmw_upic_repo_name` | `custom-repo` | Repository name |
| `cifmw_upic_image_name_prefix` | `updated` | Prefix for new image names |
| `cifmw_upic_tls_verify` | `false` | Enable TLS verification |
| `cifmw_update_container_packages` | `true` | Enable/disable the playbook |

## Command Line Options

### Helper Script Options

```bash
./scripts/update_container_packages.sh [OPTIONS]

Options:
  -p, --package PACKAGE       Target package name (required)
  -r, --repo URL              Repository base URL (required)
  -v, --vars FILE             Use variables from file
  -n, --namespace NAMESPACE   OpenShift namespace (default: openstack)
  -c, --cr-name NAME          OpenStackVersion CR name (default: controlplane)
  -i, --image-prefix PREFIX   Image name prefix (default: updated)
  -d, --dry-run               Show what would be done
  -V, --verbose               Verbose output
  -h, --help                  Show help message
```

## Examples

### Example 1: Update OVN with Default Settings

```bash
./scripts/update_container_packages.sh \
  -p ovn24.03 \
  -r http://example.com/custom-repo/
```

### Example 2: Update in Different Namespace

```bash
./scripts/update_container_packages.sh \
  -p ovn24.03 \
  -r http://example.com/repo/ \
  -n openstack-prod \
  -i ovn-prod-hotfix
```

### Example 3: Dry Run

```bash
./scripts/update_container_packages.sh \
  -p ovn24.03 \
  -r http://example.com/repo/ \
  --dry-run
```

### Example 4: Using Predefined Config

```bash
# Short form - script looks in playbooks/vars/
./scripts/update_container_packages.sh -v ovn_update.yml

# Or full path
./scripts/update_container_packages.sh -v playbooks/vars/ovn_update.yml
```

### Example 5: Verbose Output

```bash
./scripts/update_container_packages.sh \
  -p ovn24.03 \
  -r http://example.com/repo/ \
  --verbose
```

## Prerequisites

1. **OpenShift CLI (`oc`)**: Must be installed and configured
2. **Podman**: Must be installed and accessible
3. **Ansible**: Version 2.15 or higher
4. **Permissions**:
   - Create tokens in the target namespace
   - Get and patch OpenStackVersion CRs
   - Push images to the internal registry

## Verification

After running the playbook, verify the updates:

### 1. Check the OpenStackVersion CR

```bash
oc get openstackversion controlplane -n openstack -o yaml | grep customContainerImages -A 20
```

### 2. Watch Pods Restarting

```bash
oc get pods -n openstack -w
```

### 3. Verify Package in Updated Container

```bash
# Get a pod name
POD=$(oc get pods -n openstack -l app=ovn-controller -o name | head -1)

# Check package version
oc exec -it $POD -n openstack -- rpm -q ovn24.03
```

## Troubleshooting

### Error: "Required variables are missing"

Make sure you provide both package name and repository URL:

```bash
./scripts/update_container_packages.sh -p ovn24.03 -r http://example.com/repo/
```

### Error: "oc command not found"

Install OpenShift CLI:

```bash
# Download from OpenShift console or
curl -O https://mirror.openshift.com/pub/openshift-v4/clients/oc/latest/linux/oc.tar.gz
tar xzf oc.tar.gz
sudo mv oc /usr/local/bin/
```

### Playbook Disabled

If you see "Early playbook stop", enable it:

```bash
ansible-playbook playbooks/update_container_packages.yml \
  -e cifmw_update_container_packages=true \
  -e cifmw_upic_target_package=ovn24.03 \
  -e cifmw_upic_repo_baseurl=http://example.com/repo/
```

## Integration with CI/CD

### Zuul Job Example

```yaml
- job:
    name: update-ovn-containers
    description: Update OVN packages in containers
    run: playbooks/update_container_packages.yml
    vars:
      cifmw_upic_target_package: "ovn24.03"
      cifmw_upic_repo_baseurl: "{{ ovn_repo_url }}"
      cifmw_upic_image_name_prefix: "ovn-ci-updated"
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    stages {
        stage('Update Containers') {
            steps {
                sh '''
                    cd ci-framework
                    ./scripts/update_container_packages.sh \
                      --package ${PACKAGE_NAME} \
                      --repo ${REPO_URL}
                '''
            }
        }
    }
}
```

## Advanced Usage

### Multiple Package Updates

Create a wrapper playbook:

```yaml
---
- name: Update multiple packages
  hosts: localhost
  tasks:
    - name: Update OVN
      ansible.builtin.include_role:
        name: update_package_in_containers
      vars:
        cifmw_upic_target_package: "ovn24.03"
        cifmw_upic_repo_baseurl: "http://repo1.example.com/"

    - name: Update Neutron
      ansible.builtin.include_role:
        name: update_package_in_containers
      vars:
        cifmw_upic_target_package: "openstack-neutron"
        cifmw_upic_repo_baseurl: "http://repo2.example.com/"
```

## Support

For issues or questions:
- Check the [role README](../roles/update_package_in_containers/README.md)
- Review the [USAGE guide](../roles/update_package_in_containers/USAGE.md)
- Open an issue in the repository
