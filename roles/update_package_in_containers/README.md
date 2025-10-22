# update_package_in_containers

Ansible role to update specific RPM packages in OpenStack container images by rebuilding them with custom repositories.

This role automates the process of:
1. Fetching container images from OpenStackVersion CR
2. Checking if target package exists in each image
3. Building new images with updated packages from custom repository
4. Pushing updated images to OpenShift internal registry
5. Patching OpenStackVersion CR to use the new images

## Privilege escalation
None - Runs as the user executing Ansible

## Parameters

* `cifmw_upic_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_upic_namespace`: (String) OpenShift namespace where OpenStack is deployed. Defaults to `openstack`.
* `cifmw_upic_openstack_cr_name`: (String) Name of the OpenStackVersion CR. Defaults to `controlplane`.
* `cifmw_upic_target_package`: (String) Name of the RPM package to update (e.g., `ovn24.03`). **Required**.
* `cifmw_upic_repo_name`: (String) Repository name. Defaults to `custom-repo`.
* `cifmw_upic_repo_baseurl`: (String) Repository base URL. **Required**.
* `cifmw_upic_repo_enabled`: (Integer) Enable repository (0 or 1). Defaults to `1`.
* `cifmw_upic_repo_gpgcheck`: (Integer) Enable GPG check (0 or 1). Defaults to `0`.
* `cifmw_upic_repo_priority`: (Integer) Repository priority. Defaults to `0`.
* `cifmw_upic_repo_sslverify`: (Integer) Enable SSL verification (0 or 1). Defaults to `0`.
* `cifmw_upic_image_registry`: (String) External OpenShift image registry URL. Auto-detected from cluster if not specified. Leave empty for auto-detection.
* `cifmw_upic_image_registry_internal`: (String) Internal OpenShift image registry URL. Defaults to `image-registry.openshift-image-registry.svc:5000`.
* `cifmw_upic_image_name_prefix`: (String) Prefix for new image names. Defaults to `updated`.
* `cifmw_upic_tls_verify`: (Boolean) Enable TLS verification for podman operations. Defaults to `false`.
* `cifmw_upic_temp_dir`: (String) Temporary directory for build context. Auto-generated if not specified.
* `cifmw_upic_update_dnf_args`: (String) Additional arguments for dnf update command. Defaults to `--disablerepo='*' --enablerepo={{ cifmw_upic_repo_name }}`.

## Examples

### Update OVN package in all containers
```yaml
---
- hosts: localhost
  vars:
    cifmw_upic_target_package: "ovn24.03"
    cifmw_upic_repo_name: "custom-repo"
    cifmw_upic_repo_baseurl: "http://example.com/custom-repo/"
    cifmw_upic_namespace: "openstack"
  roles:
    - role: "update_package_in_containers"
```

### Update with custom registry and image prefix
```yaml
---
- hosts: localhost
  vars:
    cifmw_upic_target_package: "ovn24.03"
    cifmw_upic_repo_baseurl: "http://custom-repo.example.com/repo/"
    cifmw_upic_image_registry: "registry.example.com"
    cifmw_upic_image_name_prefix: "ovn-hotfix"
    cifmw_upic_tls_verify: true
  roles:
    - role: "update_package_in_containers"
```

### Update with specific DNF arguments
```yaml
---
- hosts: localhost
  vars:
    cifmw_upic_target_package: "neutron-ovn-metadata-agent"
    cifmw_upic_repo_baseurl: "http://custom-repo.example.com/repo/"
    cifmw_upic_update_dnf_args: "--disablerepo='*' --enablerepo={{ cifmw_upic_repo_name }} --nobest"
  roles:
    - role: "update_package_in_containers"
```

## How it works

1. **Registry Setup**:
   - Enables the default route for OpenShift image registry
   - Adds the registry to insecure registries list (if TLS verification is disabled)
   - Auto-detects the registry hostname or uses the configured value
2. **Authentication**: Obtains a token from OpenShift and authenticates with the internal registry
3. **Image Discovery**: Queries the OpenStackVersion CR for all container images
4. **Package Check**: For each image, creates a temporary container to check if the target package is installed
5. **Image Build**: If the package exists, builds a new image with the updated package from the custom repository
6. **Registry Push**: Pushes the new image to the OpenShift internal registry
7. **CR Update**: Patches the OpenStackVersion CR's `spec.customContainerImages` field with the new image reference
8. **Summary**: Provides a summary of all updated images

## Requirements

* OpenShift CLI (`oc`) must be available
* Podman must be installed and accessible
* User must have permissions to:
  - Create tokens in the target namespace
  - Get and patch OpenStackVersion CRs
  - Push images to the internal registry
  - Patch image registry configuration (`configs.imageregistry.operator.openshift.io/cluster`)
  - Patch cluster image configuration (`image.config.openshift.io/cluster`)

## Notes

* The role uses podman to build and push images
* Each updated image gets a unique tag with timestamp: `<prefix>-<image-key>-<timestamp>`
* Only images containing the target package will be updated
* The role cleans up temporary containers automatically
* All build contexts are created in a temporary directory that is cleaned up after execution
* The role automatically configures the OpenShift image registry for external access:
  - Enables the default route if not already enabled
  - Adds the registry to insecure registries list when TLS verification is disabled
  - Auto-detects the registry hostname from the route
