## update_edpm_containers

Ansible role to automatically update OpenStackDataPlaneNodeSets with custom container images from the OpenStackVersion CR.

This role automates the process of propagating custom container images (built by `update_package_in_containers` role) to EDPM (External Data Plane Management) baremetal nodes by updating their corresponding OpenStackDataPlaneNodeSet configurations.

### Privilege escalation

None - Runs as the user executing Ansible

### Parameters

* `cifmw_uec_namespace`: (String) OpenShift namespace where EDPM resources are deployed. Defaults to `openstack`.
* `cifmw_uec_nodeset_name`: (String) NodeSet name to update, or `all` for all nodesets. Defaults to `all`.
* `cifmw_uec_image_registry`: (String) Image registry URL. Auto-detected if empty.
* `cifmw_uec_dry_run`: (Boolean) Show changes without applying. Defaults to `false`.
* `cifmw_update_edpm_containers`: (Boolean) Enable/disable the role. Defaults to `true`.

### Workflow

1. **Fetch Custom Images**: Retrieves custom container images from OpenStackVersion CR's `spec.customContainerImages`
2. **Filter EDPM Images**: Identifies EDPM-relevant images based on predefined mapping
3. **Get NodeSets**: Retrieves all or specific OpenStackDataPlaneNodeSets
4. **Update NodeSets**: Patches NodeSets' `spec.nodeTemplate.ansible.ansibleVars` with corresponding EDPM image variables
5. **Display Summary**: Shows what was updated and next steps

### Image Variable Mapping

The role uses a predefined mapping to convert control plane image keys to EDPM ansible variables:

| Control Plane Image Key | EDPM Ansible Variable |
|-------------------------|----------------------|
| `ovnControllerImage` | `edpm_ovn_controller_agent_image` |
| `edpmNeutronMetadataAgentImage` | `edpm_neutron_metadata_agent_image` |
| `edpmNeutronSriovAgentImage` | `edpm_neutron_sriov_image` |
| `novaComputeImage` | `edpm_nova_compute_container_image` |
| `edpmNeutronDhcpAgentImage` | `edpm_neutron_dhcp_image` |
| `edpmNodeExporterImage` | `edpm_telemetry_node_exporter_image` |
| `edpmFrrImage` | `edpm_frr_image` |
| `edpmIscsidImage` | `edpm_iscsid_image` |
| `edpmLogrotateCrondImage` | `edpm_logrotate_crond_image` |
| `edpmMultipathdImage` | `edpm_multipathd_image` |
| `edpmOvnBgpAgentImage` | `edpm_ovn_bgp_agent_image` |

### Examples

#### Update all NodeSets

```yaml
---
- hosts: localhost
  roles:
    - role: update_edpm_containers
```

#### Update specific NodeSet

```yaml
---
- hosts: localhost
  vars:
    cifmw_uec_nodeset_name: "openstack-edpm"
  roles:
    - role: update_edpm_containers
```

#### Dry run to see what would change

```yaml
---
- hosts: localhost
  vars:
    cifmw_uec_dry_run: true
  roles:
    - role: update_edpm_containers
```

#### Use with specific namespace

```yaml
---
- hosts: localhost
  vars:
    cifmw_uec_namespace: "openstack-prod"
    cifmw_uec_nodeset_name: "prod-edpm"
  roles:
    - role: update_edpm_containers
```

### Complete Workflow Example

```bash
# Step 1: Build updated container images for control plane
ansible-playbook playbooks/update_container_packages.yml \
  -e cifmw_upic_target_package=ovn24.03 \
  -e cifmw_upic_repo_baseurl=http://example.com/custom-repo/

# Step 2: Update EDPM NodeSets with the new images
ansible-playbook playbooks/update_edpm_containers.yml

# Step 3: Deploy to EDPM nodes
./scripts/update_edpm_containers.sh \
  --nodeset openstack-edpm \
  --services ovn,neutron-metadata,neutron-sriov

# Step 4: Monitor deployment
oc get openstackdataplanedeployment -n openstack -w
```

### Integration with update_package_in_containers

This role is designed to work seamlessly with the `update_package_in_containers` role:

1. `update_package_in_containers` builds custom images and updates OpenStackVersion CR
2. `update_edpm_containers` reads those custom images and updates NodeSets
3. An OpenStackDataPlaneDeployment applies the changes to actual compute nodes

### Prerequisites

* OpenShift CLI (`oc`) must be available
* User must have permissions to:
  - Get OpenStackVersion CRs
  - Get and patch OpenStackDataPlaneNodeSets
* At least one OpenStackVersion CR with custom images must exist
* At least one OpenStackDataPlaneNodeSet must exist

### Notes

* The role only updates NodeSet configurations, it does not trigger actual deployment
* Use OpenStackDataPlaneDeployment to apply the updated configurations to compute nodes
* The role automatically filters only EDPM-relevant images from the OpenStackVersion CR
* If no EDPM images are found, the role completes without making changes
* Multiple NodeSets can be updated in a single run when `cifmw_uec_nodeset_name: all`
* The role preserves all existing ansible vars in the NodeSet
* Image variables are added or updated using JSON patch operations

### Troubleshooting

#### No custom images found

```
WARNING: No EDPM-relevant custom images found. NodeSets will not be updated.
```

**Solution**: Ensure you've run `update_container_packages.yml` first to build custom images.

#### NodeSet not found

```
ERROR: No OpenStackDataPlaneNodeSets found in namespace openstack
```

**Solution**: Verify the namespace and NodeSet name:
```bash
oc get openstackdataplanenodeset -n openstack
```

#### Patch failed

```
Error from server: openstackdataplanenodeset.dataplane.openstack.org "openstack-edpm" is invalid
```

**Solution**: Check the NodeSet structure. The role expects `spec.nodeTemplate.ansible.ansibleVars` to exist.

### Related Documentation

* [Update Container Packages Guide](../playbooks/UPDATE_CONTAINER_PACKAGES.md)
* [Update EDPM Containers Guide](../playbooks/UPDATE_EDPM_CONTAINERS.md)
* [EDPM NodeSet Custom Images Example](../openstack-edpm-nodeset-custom-images-example.yaml)
