# Usage Guide for update_package_in_containers Role

## Overview

This role automates the process of updating RPM packages in OpenStack container images deployed on OpenShift. It replicates the functionality of the bash script but with better error handling, idempotency, and integration with Ansible workflows.

## Prerequisites

1. **OpenShift CLI (`oc`)**: Must be installed and configured
2. **Podman**: Must be installed and accessible
3. **Permissions**:
   - Create tokens in the target namespace
   - Get and patch OpenStackVersion CRs
   - Push images to the internal registry
4. **OpenStack Deployment**: A running OpenStack deployment on OpenShift with OpenStackVersion CR

## Quick Start

### 1. Basic Usage

Create a playbook with the minimum required variables:

```yaml
---
- name: Update packages in containers
  hosts: localhost
  vars:
    cifmw_upic_target_package: "ovn24.03"
    cifmw_upic_repo_baseurl: "http://example.com/repo/"
  roles:
    - update_package_in_containers
```

### 2. Run the playbook

```bash
ansible-playbook update_packages.yml
```

## Configuration Examples

### Example 1: Update OVN Package (Original Script Replication)

```yaml
---
- name: Update OVN 24.03 package
  hosts: localhost
  vars:
    cifmw_upic_target_package: "ovn24.03"
    cifmw_upic_repo_name: "rhel-9-fdp"
    cifmw_upic_repo_baseurl: "http://rhos-qe-mirror.lab.eng.tlv2.redhat.com/rhel-9/nightly/updates/FDP/latest-FDP-9-RHEL-9/compose/Server/x86_64/os/"
    cifmw_upic_namespace: "openstack"
    cifmw_upic_image_name_prefix: "ovn-updated"
  roles:
    - update_package_in_containers
```

### Example 2: Update with Custom Registry

```yaml
---
- name: Update with custom registry
  hosts: localhost
  vars:
    cifmw_upic_target_package: "neutron-ovn-metadata-agent"
    cifmw_upic_repo_baseurl: "http://custom-repo.example.com/repo/"
    cifmw_upic_image_registry: "registry.example.com"
    cifmw_upic_tls_verify: true
  roles:
    - update_package_in_containers
```

### Example 3: Multiple Package Updates

You can update multiple packages by running the role multiple times:

```yaml
---
- name: Update multiple packages
  hosts: localhost
  tasks:
    - name: Update OVN package
      ansible.builtin.include_role:
        name: update_package_in_containers
      vars:
        cifmw_upic_target_package: "ovn24.03"
        cifmw_upic_repo_baseurl: "http://repo1.example.com/"
        cifmw_upic_image_name_prefix: "ovn-updated"

    - name: Update Neutron package
      ansible.builtin.include_role:
        name: update_package_in_containers
      vars:
        cifmw_upic_target_package: "openstack-neutron"
        cifmw_upic_repo_baseurl: "http://repo2.example.com/"
        cifmw_upic_image_name_prefix: "neutron-updated"
```

## Available Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `cifmw_upic_target_package` | RPM package name to update | `ovn24.03` |
| `cifmw_upic_repo_baseurl` | Repository base URL | `http://repo.example.com/` |

### Optional Variables (with defaults)

| Variable | Default | Description |
|----------|---------|-------------|
| `cifmw_upic_namespace` | `openstack` | OpenShift namespace |
| `cifmw_upic_openstack_cr_name` | `controlplane` | OpenStackVersion CR name |
| `cifmw_upic_repo_name` | `custom-repo` | Repository name |
| `cifmw_upic_image_name_prefix` | `updated` | Prefix for new image names |
| `cifmw_upic_tls_verify` | `false` | Enable TLS verification |
| `cifmw_upic_image_registry` | `default-route-openshift-image-registry.apps.ocp.openstack.lab` | External registry URL |
| `cifmw_upic_image_registry_internal` | `image-registry.openshift-image-registry.svc:5000` | Internal registry URL |

## How It Works

The role performs the following steps:

1. **Validation**: Checks that required parameters are set and commands are available
2. **Authentication**: Creates a token and authenticates with the OpenShift registry
3. **Discovery**: Fetches all container images from the OpenStackVersion CR
4. **Processing**: For each image:
   - Creates a temporary container
   - Checks if the target package is installed
   - If found:
     - Builds a new image with updated package
     - Pushes to the registry
     - Updates the OpenStackVersion CR
   - If not found: Skips the image
5. **Summary**: Displays a summary of all updates
6. **Cleanup**: Removes temporary files and containers

## Output

The role provides detailed output:

```
TASK [update_package_in_containers : Display update summary]
ok: [localhost] => {
    "msg": [
        "==================================================",
        "Update Process Complete",
        "==================================================",
        "Summary:",
        "- Total images found: 25",
        "- Images processed: 8",
        "- Target package: ovn24.03",
        "- Repository: rhel-9-fdp"
    ]
}

TASK [update_package_in_containers : Display updated images]
ok: [localhost] => {
    "msg": [
        "quay.io/openstack/ovn-controller:latest -> default-route.../ovn-updated-ovncontroller-1729612345",
        "quay.io/openstack/ovn-northd:latest -> default-route.../ovn-updated-ovnnorthd-1729612346"
    ]
}
```

## Testing

### Run Molecule Tests

```bash
cd roles/update_package_in_containers
molecule test
```

### Dry Run (Check Mode)

To see what would be changed without actually making changes:

```bash
ansible-playbook update_packages.yml --check
```

Note: Some tasks cannot run in check mode (podman operations), but you can verify the playbook syntax.

## Troubleshooting

### Error: "oc command not found"

**Solution**: Install OpenShift CLI and ensure it's in your PATH

```bash
which oc
```

### Error: "Could not retrieve authentication token"

**Solution**: Verify you have permissions in the namespace

```bash
oc create token builder -n openstack
```

### Error: "Failed to authenticate with the registry"

**Solution**: Check the registry URL and your credentials

```bash
oc get route -n openshift-image-registry
```

### Error: "No container images found"

**Solution**: Verify the OpenStackVersion CR exists and has images defined

```bash
oc get openstackversion controlplane -n openstack -o json | jq '.status.containerImageVersionDefaults'
```

## Comparison with Original Script

| Feature | Bash Script | Ansible Role |
|---------|-------------|--------------|
| Idempotency | No | Yes |
| Error Handling | Basic | Comprehensive |
| Logging | Echo statements | Ansible logging |
| Reusability | Limited | High |
| Integration | Standalone | Part of Ansible workflow |
| Testing | Manual | Molecule tests |
| Documentation | Comments | Full role documentation |
| Parallelization | No | Possible with Ansible |

## Best Practices

1. **Test First**: Always test in a development environment before production
2. **Backup**: Take a backup of your OpenStackVersion CR before running
3. **Version Control**: Keep your playbooks in version control
4. **Logging**: Save output for audit purposes
5. **Variables**: Use variable files for different environments

## Integration with CI/CD

This role can be integrated into CI/CD pipelines:

```yaml
# Zuul job example
- job:
    name: update-ovn-packages
    run: playbooks/update-ovn-packages.yml
    vars:
      cifmw_upic_target_package: "ovn24.03"
      cifmw_upic_repo_baseurl: "{{ ovn_repo_url }}"
```

## Further Reading

- [OpenStack Operators Documentation](https://github.com/openstack-k8s-operators)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [Podman Documentation](https://docs.podman.io/)
- [OpenShift Image Registry](https://docs.openshift.com/container-platform/latest/registry/index.html)
