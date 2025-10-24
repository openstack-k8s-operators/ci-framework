# edpm_update_host_packages

Ansible role to update RPM packages directly on EDPM compute node hosts (not in containers).

This role is particularly useful for updating host-level packages like OpenVSwitch/OVS-DPDK that run directly on the compute node OS rather than in containers.

## Privilege escalation

Yes - This role requires `become: true` to install packages and restart services on the host.

## Parameters

* `cifmw_euhp_repo_name`: (String) Repository name. Defaults to `custom-updates`.
* `cifmw_euhp_repo_baseurl`: (String) Repository base URL. **Required**.
* `cifmw_euhp_repo_enabled`: (Integer) Enable repository (0 or 1). Defaults to `1`.
* `cifmw_euhp_repo_gpgcheck`: (Integer) Enable GPG check (0 or 1). Defaults to `0`.
* `cifmw_euhp_repo_priority`: (Integer) Repository priority. Defaults to `1`.
* `cifmw_euhp_packages`: (List) Packages to update. Defaults to `['openvswitch3.3', 'openvswitch-selinux-extra-policy']`.
* `cifmw_euhp_services_to_restart`: (List) Services to restart after update. Defaults to `['openvswitch', 'ovs-vswitchd', 'ovsdb-server']`.
* `cifmw_euhp_restart_services`: (Boolean) Whether to restart services. Defaults to `true`.
* `cifmw_euhp_backup_packages`: (Boolean) Whether to backup current packages. Defaults to `true`.
* `cifmw_euhp_dnf_options`: (String) Additional DNF options. Defaults to `--best --allowerasing`.
* `cifmw_edpm_update_host_packages`: (Boolean) Enable/disable role. Defaults to `true`.

## Workflow

1. **Validate Parameters**: Ensures repository URL and package list are provided
2. **Configure Repository**: Creates `/etc/yum.repos.d/<repo-name>.repo` file
3. **Backup Packages**: Saves current package versions to `/var/lib/edpm-backups/packages/`
4. **Update Packages**: Uses DNF to update packages from custom repository
5. **Restart Services**: Restarts specified services (typically OpenVSwitch)
6. **Verify**: Checks service status and OVS connectivity

## Use Cases

### Updating OpenVSwitch on Compute Nodes

When you need to update OpenVSwitch (especially OVS-DPDK) on compute nodes:

```yaml
---
- hosts: edpm_compute
  become: true
  vars:
    cifmw_euhp_repo_baseurl: "http://example.com/ovs-updates/"
    cifmw_euhp_packages:
      - openvswitch3.3
      - openvswitch-selinux-extra-policy
  roles:
    - edpm_update_host_packages
```

### Updating Multiple Host Packages

```yaml
---
- hosts: edpm_compute
  become: true
  vars:
    cifmw_euhp_repo_baseurl: "http://example.com/updates/"
    cifmw_euhp_packages:
      - openvswitch3.3
      - openvswitch-selinux-extra-policy
      - kernel
      - kernel-modules
    cifmw_euhp_services_to_restart:
      - openvswitch
  roles:
    - edpm_update_host_packages
```

### Update Without Automatic Service Restart

```yaml
---
- hosts: edpm_compute
  become: true
  vars:
    cifmw_euhp_repo_baseurl: "http://example.com/updates/"
    cifmw_euhp_restart_services: false
  roles:
    - edpm_update_host_packages
```

## Integration with OpenStackDataPlane

This role is automatically integrated when using the complete update workflow:

```bash
# This creates an OpenStackDataPlaneService that runs this role
ansible-playbook playbooks/update_all_containers.yml \
  -e cifmw_upic_target_package=ovn24.03 \
  -e cifmw_upic_repo_baseurl=http://example.com/custom-repo/
```

The workflow will:
1. Update control plane containers
2. Update EDPM container configurations
3. Create an `update-host-packages` service that runs this role's tasks

Then deploy with:
```bash
./scripts/update_edpm_containers.sh \
  --nodeset openstack-edpm \
  --services download-cache,update-host-packages,ovn,neutron-metadata
```

## Manual Execution on Compute Nodes

For direct execution on compute nodes:

```bash
# SSH to compute node
ssh cloud-admin@compute-0

# Create repository file
sudo tee /etc/yum.repos.d/custom-updates.repo <<EOF
[custom-updates]
name=custom-updates
baseurl=http://example.com/updates/
enabled=1
gpgcheck=0
priority=1
EOF

# Update packages
sudo dnf update -y --disablerepo='*' --enablerepo=custom-updates \
  openvswitch3.3 openvswitch-selinux-extra-policy

# Restart OVS
sudo systemctl restart openvswitch

# Verify
sudo systemctl status openvswitch
sudo ovs-vsctl show
```

## Verification

After running the role, verify the updates:

```bash
# Check package versions
rpm -q openvswitch3.3 openvswitch-selinux-extra-policy

# Check service status
systemctl status openvswitch ovs-vswitchd ovsdb-server

# Verify OVS is functioning
ovs-vsctl show
ovs-vsctl list bridge

# Check logs
journalctl -u openvswitch -n 50
```

## Backup and Rollback

### Backup Location

Package versions are backed up to:
```
/var/lib/edpm-backups/packages/<timestamp>/packages.txt
```

### Rollback Procedure

```bash
# View backup
cat /var/lib/edpm-backups/packages/<timestamp>/packages.txt

# Rollback to specific version
sudo dnf downgrade openvswitch3.3-<old-version>

# Restart services
sudo systemctl restart openvswitch
```

## Troubleshooting

### Package update fails

**Error**: "No package openvswitch3.3 available"

**Solution**:
1. Verify repository is accessible:
   ```bash
   curl -I http://example.com/updates/
   ```
2. Check repository configuration:
   ```bash
   cat /etc/yum.repos.d/custom-updates.repo
   dnf repolist
   ```

### Service restart fails

**Error**: "Job for openvswitch.service failed"

**Solution**:
1. Check service logs:
   ```bash
   journalctl -u openvswitch -n 100
   ```
2. Verify OVS configuration:
   ```bash
   ovs-vsctl show
   ovs-appctl version
   ```
3. Check for port/bridge issues:
   ```bash
   ovs-vsctl list port
   ovs-vsctl list bridge
   ```

### OVS DPDK issues after update

**Error**: "DPDK not initialized"

**Solution**:
1. Verify hugepages:
   ```bash
   cat /proc/meminfo | grep Huge
   ```
2. Check DPDK configuration:
   ```bash
   ovs-vsctl get Open_vSwitch . other_config
   ```
3. Restart with proper DPDK settings:
   ```bash
   sudo systemctl restart openvswitch
   ```

## Notes

* This role updates packages on the **host OS**, not in containers
* Service restarts may cause brief network disruption
* Always test in non-production environment first
* Backups are created automatically before updates
* OVS updates may require coordination with network team
* DPDK-enabled OVS requires careful handling during updates

## Related Roles

* `update_package_in_containers` - Updates packages in containers
* `update_edpm_containers` - Updates EDPM container configurations

## See Also

* [Complete Update Workflow](../../playbooks/UPDATE_CONTAINER_PACKAGES.md)
* [EDPM Container Updates](../../playbooks/UPDATE_EDPM_CONTAINERS.md)
