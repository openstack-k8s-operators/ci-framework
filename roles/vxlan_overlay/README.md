# vxlan_overlay

Build the shared networks for a multinode CRC/EDPM job without setting up any
cloud-provider-specific networking. The controller is the hub by default. Each
spoke has one VXLAN tunnel back to the hub. The role configures NetworkManager
profiles and writes the networking information that later CRC and EDPM setup
consumes. It uses privilege escalation to configure networking and install
system files.

## Usage

Run the role in a play that targets exactly the overlay hosts. For example, a
Zuul nodeset can put the participating nodes in `overlay_hub` and
`overlay_spokes` and leave unrelated nodes out of both groups:

```yaml
- name: Build the VXLAN overlay
  hosts: overlay_hub,overlay_spokes
  gather_facts: false
  roles:
    - role: vxlan_overlay
```

By default the host list comes from `crc_ci_bootstrap_networking.instances`.
Give every participating host an IP on the untagged `default` network and
list any tagged networks it needs under that host's `networks`. Each tagged
network needs a VLAN ID in the layout. On EDPM hosts, use `config_nm: false`
on tagged network entries that EDPM should configure rather than NetworkManager.

The play's host groups select who runs the role; they do not choose the hub.
Set `cifmw_vxlan_overlay_hub` to a different participating hostname to change
it. All other participating hosts are spokes.

Allow the tunnel UDP port between hosts on the existing network. If tunnel
endpoint or SSH client addresses fall inside an overlay range, enable policy
routing only if the other tunnel endpoints are reached through the underlay
default gateway. Policy routing does not support overlapping the local
underlay subnet or reusing an underlay address as an overlay host address.

## Inputs

All inputs below have the prefix `cifmw_vxlan_overlay_`.

| Input | Default and purpose |
| --- | --- |
| `networking`, `hosts` | Network layout (`crc_ci_bootstrap_networking`) and participating hosts (the layout's `instances` keys). |
| `hub` | `controller`. Must be a participating hostname. |
| `underlay_ips`, `underlay_cidrs` | Overrides for tunnel endpoint addresses (otherwise `ansible_host`) and extra CIDRs the overlay must not overlap. Both are empty by default. |
| `dstport`, `vni_base` | UDP destination port (`4789`, valid range `1024` to `65535`) and first tunnel VNI (`5000`). |
| `mtu`, `overhead`, `min_mtu` | `mtu: 0` uses the smallest underlay MTU minus `overhead` (`54`), capped by the default network's MTU if set. The result must be at least `min_mtu` (`1280`). |
| `iface`, `peer_iface`, `bridge`, `tunnel_prefix` | Device names or prefix: `nic2`, `nic2-p`, `br-ovl`, and `ovl-`. |
| `gateway`, `firewall_zone` | The hub provides the default network's gateway and NAT by default. Overlay profiles use the `trusted` firewalld zone. |
| `policy_routing`, `route_table`, `rule_priority` | Policy routing is off by default. When enabled, reserve table `6082` and rule priorities `1082` and `1083` (the configured priority and the next one). |
| `edpm_hosts`, `edpm_kustomize` | The `computes` group by default. The role writes an EDPM dataplane kustomization by default when there are EDPM hosts. |
| `edpm_kustomize_host`, `edpm_kustomize_dir`, `edpm_kustomize_file` | Write it on `controller` under `~/ci-framework-data/artifacts/manifests/kustomizations/dataplane` as `90-kustomize-cifmw-vxlan-overlay.yaml`. |
| `edpm_kustomize_nodesets` | Name regex for dataplane node sets to patch. `.*` matches all; restrict it if any node set contains hosts outside `edpm_hosts`. |
| `unit`, `ovs_unit`, `script` | Transport unit `cifmw-vxlan-overlay`, OVS integration unit `cifmw-vxlan-overlay-ovs`, and transport script `/etc/ci/env/cifmw-vxlan-overlay.sh`. |
| `info_file` | `/etc/ci/env/networking-info.yml`. Contains `crc_ci_bootstrap_networks_out` and `crc_ci_bootstrap_provider_dns`. |
