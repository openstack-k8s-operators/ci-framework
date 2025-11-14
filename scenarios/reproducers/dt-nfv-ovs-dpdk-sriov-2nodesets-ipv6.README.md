# dt-nfv-ovs-dpdk-sriov-2nodesets-ipv6.yml

## Overview

This reproducer is the **IPv6 variant** of `dt-nfv-ovs-dpdk-sriov-2nodesets.yml`. It configures an NFV deployment with OVS-DPDK and SR-IOV support using **IPv6 as the primary IP version** across all OpenStack networks, while maintaining dual-stack configuration on hypervisor bridges for compatibility.

## Key Features

- **IPv6 Primary**: All OpenStack networks use IPv6 addressing
- **Dual-Stack ctlplane**: Both IPv4 and IPv6 IPAM for ctlplane network
- **2 NodeSets**: Supports deployments with two different EDPM nodesets (different hardware)
- **OVS-DPDK**: High-performance DPDK-accelerated networking
- **SR-IOV**: Direct hardware access for VMs
- **OpenShift IPv6**: OCP configured with IPv6 networking

## Network Configuration

### IPv6 Network Ranges

| Network      | IPv6 Range              | VLAN | Purpose |
|--------------|-------------------------|------|---------|
| ctlplane     | 2620:cf:cf:aaaa::/64   | -    | Control plane (dual-stack) |
| internalapi  | 2620:cf:cf:bbbb::/64   | 20   | Internal API |
| storage      | 2620:cf:cf:cccc::/64   | 21   | Storage network |
| tenant       | 2620:cf:cf:eeee::/64   | 22   | Tenant/overlay network |
| storagemgmt  | 2620:cf:cf:dddd::/64   | 23   | Storage management |
| external     | 2620:cf:cf:cf02::/64   | -    | External network |

### OpenShift IPv6 Networks

| Network          | IPv6 Range               | Purpose |
|------------------|--------------------------|---------|
| provisioning     | fd00:1101::/64          | Provisioning network |
| external_subnet  | 2620:cf:cf:cf02::/64    | External access |
| service_subnet   | 2620:cf:cf:cf03::/112   | OCP services |
| cluster_subnet   | fd01::/48               | OCP pod network |

## Key Differences from IPv4 Version

### Added Configuration

1. **Primary IP Version**
   ```yaml
   cifmw_ci_gen_kustomize_values_primary_ip_version: 6
   ```

2. **IPv6 Networking Definition**
   - All networks configured with IPv6 ranges
   - VLANs preserved from original (20-23)
   - MTU settings maintained

3. **OpenShift IPv6 Configuration**
   ```yaml
   cifmw_devscripts_config_overrides:
     ip_stack: "v6"
     provisioning_network: "fd00:1101::/64"
     external_subnet_v6: "2620:cf:cf:cf02::/64"
     service_subnet_v6: "2620:cf:cf:cf03::/112"
     cluster_subnet_v6: "fd01::/48"
   ```

4. **Dual-Stack ctlplane IPAM**
   ```yaml
   ipam:
     type: whereabouts
     ipRanges:
       - range: "192.168.122.0/24"         # IPv4 (compatibility)
       - range: "2620:cf:cf:aaaa::/64"     # IPv6 (primary)
   ```

### Unchanged Configuration

- VM definitions (controller, OCP nodes)
- Libvirt network topology
- BMH configuration
- LVMS setup
- EDPM image configuration

## Usage

### In Zuul Jobs

This reproducer is used by the IPv6 variant of NFV jobs:

```yaml
- job:
    name: uni08theta-rhel9-rhoso18.0-nfv-ovs-dpdk-sriov-ipv6-trunk-patches-2nodesets
    vars:
      variable_files:
        - "{{ ci_framework_src }}/scenarios/reproducers/dt-nfv-ovs-dpdk-sriov-2nodesets-ipv6.yml"
        - ... (other variable files)
```

### Manual Deployment

```bash
# Set up your environment
cd ~/ci-framework

# Create your custom variables file
cat > my-ipv6-vars.yml <<EOF
cifmw_devscripts_ci_token: <your-token>
cifmw_devscripts_pull_secret: <your-pull-secret>
hypervisor: <your-hypervisor-fqdn>
EOF

# Deploy using this reproducer
ansible-playbook deploy-edpm.yml \
  -e @scenarios/reproducers/dt-nfv-ovs-dpdk-sriov-2nodesets-ipv6.yml \
  -e @my-ipv6-vars.yml
```

## Infrastructure Requirements

### Switch Configuration

The physical switch must support IPv6 on all VLANs:

```
# Enable IPv6 globally
ipv6 unicast-routing

# Configure VLAN IPv6 gateways
interface Vlan20  # internalapi
 ipv6 address 2620:cf:cf:bbbb::1/64
 ipv6 nd managed-config-flag
 ipv6 nd prefix 2620:cf:cf:bbbb::/64

interface Vlan21  # storage
 ipv6 address 2620:cf:cf:cccc::1/64
 ipv6 nd managed-config-flag
 ipv6 nd prefix 2620:cf:cf:cccc::/64

interface Vlan22  # tenant
 ipv6 address 2620:cf:cf:eeee::1/64
 ipv6 nd managed-config-flag
 ipv6 nd prefix 2620:cf:cf:eeee::/64

interface Vlan23  # storagemgmt
 ipv6 address 2620:cf:cf:dddd::1/64
 ipv6 nd managed-config-flag
 ipv6 nd prefix 2620:cf:cf:dddd::/64

# Enable MLD snooping (IPv6 multicast)
ipv6 mld snooping
```

### Hypervisor Requirements

- **IPv6 enabled**: `sysctl net.ipv6.conf.all.disable_ipv6=0`
- **IPv6 forwarding**: `sysctl net.ipv6.conf.all.forwarding=1`
- **Bridges with IPv6**: All bridges (ocpbm, ocppr, osp_external, osp_trunk) must have IPv6 addresses
- **Router Advertisements**: Enable RA if using SLAAC

### DNS Requirements

- DNS server with IPv6 support (AAAA records)
- Reverse DNS for IPv6 (ip6.arpa zones)
- DNS reachable at 2620:cf:cf:aaaa::1

## Topology

```
                    ┌─────────────────┐
                    │   Hypervisor    │
                    │  (dual-stack)   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
   │  OCP    │         │  OCP    │         │  OCP    │
   │ Master  │         │ Master  │         │ Master  │
   │   #1    │         │   #2    │         │   #3    │
   └─────────┘         └─────────┘         └─────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   controller-0  │
                    │ (IPv6: aaaa::9) │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
   │ Compute │         │ Compute │         │ Compute │
   │  Node   │         │  Node   │         │  Node   │
   │ (Set 1) │         │ (Set 2) │         │ (Set 2) │
   └─────────┘         └─────────┘         └─────────┘
   OVS-DPDK            OVS-DPDK            OVS-DPDK
   SR-IOV              SR-IOV              SR-IOV
```

## Verification

After deployment, verify IPv6 configuration:

```bash
# On hypervisor - check IPv6 addresses
ip -6 addr show osp_trunk
# Should show: 2620:cf:cf:aaaa::1/64 (if configured by nmstate)

# Test connectivity to controller-0
ping6 2620:cf:cf:aaaa::9

# On compute nodes - check IPv6 configuration
ssh heat-admin@<compute-node>
ip -6 addr show
# Should show IPv6 addresses on bond interfaces

# Verify OpenStack endpoints use IPv6
openstack endpoint list
# Should show IPv6 addresses like [2620:cf:cf:aaaa::X]
```

## Troubleshooting

### Common Issues

**Issue**: Computes can't reach control plane
- **Check**: DHCPv6 or SLAAC working on ctlplane
- **Verify**: `tcpdump -i osp_trunk -n icmp6`

**Issue**: Services not listening on IPv6
- **Check**: `cifmw_ci_gen_kustomize_values_primary_ip_version: 6` is set
- **Verify**: `ss -tlnp6` on controller

**Issue**: DNS resolution fails
- **Check**: AAAA records exist for all services
- **Verify**: `dig AAAA keystone.openstack.svc`

**Issue**: VLANs not working
- **Check**: Switch has IPv6 enabled on VLANs 20-23
- **Verify**: MLD snooping enabled

## Related Files

- **Original IPv4 reproducer**: `dt-nfv-ovs-dpdk-sriov-2nodesets.yml`
- **Job definition**: `zuul.d/ci-framework-rhoso-18-rhel9-trunk-nfv-jobs.yaml`
- **IPv6 UNI scenario example**: `scenarios/uni/uni04delta-ipv6/`

## References

- [IPv6 Networking in OpenStack](https://docs.openstack.org/neutron/latest/admin/config-ipv6.html)
- [OVS-DPDK Documentation](https://docs.openvswitch.org/en/latest/topics/dpdk/)
- [SR-IOV Configuration](https://docs.openstack.org/neutron/latest/admin/config-sriov.html)
- CI Framework IPv6 examples

## Author

Generated for NFV IPv6 testing scenarios.

## Version History

- **1.0** (2025-01-06): Initial IPv6 variant created based on dt-nfv-ovs-dpdk-sriov-2nodesets.yml
