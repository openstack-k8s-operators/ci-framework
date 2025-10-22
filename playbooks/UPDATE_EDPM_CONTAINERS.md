# Update EDPM Container Packages Guide

This document describes how to update container images on EDPM (External Data Plane Management) baremetal nodes.

## Overview

EDPM containers are configured through the OpenStackDataPlaneNodeSet's `ansibleVars` section. To update containers with custom-built images (e.g., with updated packages), you need to:

1. Build updated container images (using the control plane update process)
2. Update the OpenStackDataPlaneNodeSet with custom image references
3. Deploy the updated configuration

## Step 1: Build Updated Container Images

First, build the updated images for the EDPM services you want to update. Use the control plane update playbook:

```bash
ansible-playbook playbooks/update_container_packages.yml \
  -e cifmw_upic_target_package=ovn24.03 \
  -e cifmw_upic_repo_baseurl=http://example.com/custom-repo/
```

This will create updated images in the OpenShift internal registry with names like:
- `updated-ovnControllerImage-1234567890`
- `updated-edpmNeutronMetadataAgentImage-1234567890`
- `updated-novaComputeImage-1234567890`

## Step 2: Update OpenStackDataPlaneNodeSet

Add custom image variables to your NodeSet's `ansibleVars` section:

### Common EDPM Image Variables

Add these to `spec.nodeTemplate.ansible.ansibleVars`:

```yaml
# OVN Controller
edpm_ovn_controller_agent_image: "default-route-openshift-image-registry.apps.ocp.openstack.lab/openstack/updated-ovnControllerImage-1234567890"

# Neutron Metadata Agent
edpm_neutron_metadata_agent_image: "default-route-openshift-image-registry.apps.ocp.openstack.lab/openstack/updated-edpmNeutronMetadataAgentImage-1234567890"

# Neutron SR-IOV Agent
edpm_neutron_sriov_image: "default-route-openshift-image-registry.apps.ocp.openstack.lab/openstack/updated-edpmNeutronSriovAgentImage-1234567890"

# Nova Compute
edpm_nova_compute_container_image: "default-route-openshift-image-registry.apps.ocp.openstack.lab/openstack/updated-novaComputeImage-1234567890"

# Libvirt
edpm_libvirt_image: "default-route-openshift-image-registry.apps.ocp.openstack.lab/openstack/updated-novaLibvirtImage-1234567890"

# Telemetry Node Exporter (if updating)
edpm_telemetry_node_exporter_image: "default-route-openshift-image-registry.apps.ocp.openstack.lab/openstack/updated-edpmNodeExporterImage-1234567890"
```

### Example: Your NodeSet with Custom Images

Based on your configuration, here's how to add custom images:

```yaml
apiVersion: dataplane.openstack.org/v1beta1
kind: OpenStackDataPlaneNodeSet
metadata:
  name: openstack-edpm
  namespace: openstack
spec:
  # ... existing baremetalSetTemplate, env, networkAttachments ...

  nodeTemplate:
    ansible:
      ansiblePort: 22
      ansibleUser: cloud-admin
      ansibleVars:
        # ===== CUSTOM IMAGES =====
        # Add these variables to use updated containers
        edpm_ovn_controller_agent_image: "default-route-openshift-image-registry.apps.ocp.openstack.lab/openstack/updated-ovnControllerImage-1234567890"
        edpm_neutron_metadata_agent_image: "default-route-openshift-image-registry.apps.ocp.openstack.lab/openstack/updated-edpmNeutronMetadataAgentImage-1234567890"
        edpm_neutron_sriov_image: "default-route-openshift-image-registry.apps.ocp.openstack.lab/openstack/updated-edpmNeutronSriovAgentImage-1234567890"
        edpm_nova_compute_container_image: "default-route-openshift-image-registry.apps.ocp.openstack.lab/openstack/updated-novaComputeImage-1234567890"

        # ===== EXISTING VARIABLES =====
        dns_search_domains: []
        edpm_bootstrap_command: |-
          # ... your existing bootstrap command ...
        # ... rest of your existing ansibleVars ...
```

## Step 3: Apply the Updated NodeSet

```bash
oc apply -f openstack-edpm-nodeset.yaml
```

## Step 4: Create a Deployment to Update the Nodes

Create a deployment that targets only the services you want to update:

### Option A: Update Specific Services

```bash
oc apply -f - <<EOF
apiVersion: dataplane.openstack.org/v1beta1
kind: OpenStackDataPlaneDeployment
metadata:
  name: edpm-update-containers
  namespace: openstack
spec:
  nodeSets:
    - openstack-edpm
  servicesOverride:
    - download-cache
    - ovn
    - neutron-metadata
    - neutron-sriov
    - nova-custom-ovsdpdksriov
EOF
```

### Option B: Update All Services

```bash
oc apply -f - <<EOF
apiVersion: dataplane.openstack.org/v1beta1
kind: OpenStackDataPlaneDeployment
metadata:
  name: edpm-update-all
  namespace: openstack
spec:
  nodeSets:
    - openstack-edpm
EOF
```

## Step 5: Monitor the Deployment

```bash
# Watch deployment progress
oc get openstackdataplanedeployment -n openstack -w

# Check detailed status
oc describe openstackdataplanedeployment edpm-update-containers -n openstack

# View Ansible job logs
oc logs -n openstack -l app=openstackansibleee --tail=100 -f
```

## Complete Image Variable Reference

Here's a comprehensive list of EDPM image variables you can override:

| Service | Variable Name | Description |
|---------|--------------|-------------|
| OVN Controller | `edpm_ovn_controller_agent_image` | OVN controller for compute nodes |
| Neutron Metadata | `edpm_neutron_metadata_agent_image` | Neutron metadata agent |
| Neutron SR-IOV | `edpm_neutron_sriov_image` | SR-IOV agent for network acceleration |
| Neutron DHCP | `edpm_neutron_dhcp_image` | DHCP agent (if using) |
| Nova Compute | `edpm_nova_compute_container_image` | Nova compute service |
| Libvirt | `edpm_libvirt_image` | Libvirt daemon |
| Node Exporter | `edpm_telemetry_node_exporter_image` | Prometheus node exporter |
| FRR | `edpm_frr_image` | FRRouting daemon (if using) |
| Iscsid | `edpm_iscsid_image` | iSCSI daemon (if using) |
| Logrotate | `edpm_logrotate_crond_image` | Log rotation service |
| Multipathd | `edpm_multipathd_image` | Multipath daemon (if using) |

## Verification

After deployment completes, verify the updated containers on the compute node:

```bash
# SSH to the compute node
ssh cloud-admin@compute-0

# Check running containers
sudo podman ps

# Verify specific container image
sudo podman inspect edpm_ovn_controller | grep Image

# Check package version in container
sudo podman exec edpm_ovn_controller rpm -q ovn24.03

# Check systemd service status
sudo systemctl status edpm_ovn_controller
```

## Rollback

To rollback to original images, remove the custom image variables from the NodeSet and redeploy:

```bash
# Edit the NodeSet to remove custom image variables
oc edit openstackdataplanenodeset openstack-edpm -n openstack

# Create rollback deployment
oc apply -f - <<EOF
apiVersion: dataplane.openstack.org/v1beta1
kind: OpenStackDataPlaneDeployment
metadata:
  name: edpm-rollback-containers
  namespace: openstack
spec:
  nodeSets:
    - openstack-edpm
  servicesOverride:
    - ovn
    - neutron-metadata
    - neutron-sriov
    - nova-custom-ovsdpdksriov
EOF
```

## Troubleshooting

### Container fails to pull image

```bash
# Check registry connectivity from compute node
ssh cloud-admin@compute-0
curl -k https://default-route-openshift-image-registry.apps.ocp.openstack.lab/v2/

# Check podman authentication
sudo cat /run/containers/0/auth.json
```

### Service fails to start

```bash
# Check service logs
ssh cloud-admin@compute-0
sudo journalctl -u edpm_ovn_controller -n 100

# Check podman logs
sudo podman logs edpm_ovn_controller
```

### Deployment stuck

```bash
# Check Ansible job pods
oc get pods -n openstack -l app=openstackansibleee

# Get job logs
oc logs -n openstack <ansible-pod-name>
```

## Integration with update_container_packages.yml

You can combine both control plane and data plane updates:

```bash
# 1. Update control plane containers
ansible-playbook playbooks/update_container_packages.yml \
  -e cifmw_upic_target_package=ovn24.03 \
  -e cifmw_upic_repo_baseurl=http://example.com/custom-repo/

# 2. Note the image names from the output

# 3. Create a variables file for EDPM update
cat > edpm_custom_images.yaml <<EOF
edpm_ovn_controller_agent_image: "default-route-openshift-image-registry.apps.ocp.openstack.lab/openstack/updated-ovnControllerImage-1234567890"
edpm_neutron_metadata_agent_image: "default-route-openshift-image-registry.apps.ocp.openstack.lab/openstack/updated-edpmNeutronMetadataAgentImage-1234567890"
EOF

# 4. Update NodeSet
# (Manually edit or use a patch)

# 5. Deploy to EDPM nodes
oc apply -f edpm-deployment-update.yaml
```

## Best Practices

1. **Test in staging first**: Always test image updates in a non-production environment
2. **One service at a time**: Update one service type at a time for easier troubleshooting
3. **Backup configurations**: Keep backup of working NodeSet configurations
4. **Monitor workloads**: Ensure no VMs are impacted during updates
5. **Use specific tags**: Always use specific image tags, never `:latest`
6. **Document changes**: Keep track of which images were updated and why
7. **Rolling updates**: For multiple compute nodes, update them one at a time

## Notes

- EDPM containers run as systemd services managed by podman
- Container images are pulled during the deployment process
- Each service has its own systemd unit (e.g., `edpm_ovn_controller.service`)
- Containers persist across reboots unless explicitly removed
- Image updates require a new deployment to take effect
