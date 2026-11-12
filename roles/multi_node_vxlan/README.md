# multi_node_vxlan

Create a persistent VXLAN Layer 2 transport between hosts. A veth pair connects
host networking to a bridge containing the VXLAN tunnels, carrying both untagged
and VLAN-tagged traffic:

```
nic2 <-> nic2-p <-> br-ovl <-> VXLAN tunnels <-> other hosts
```

The caller supplies the topology and handles IP addresses, VLAN profiles,
routing and firewall rules. This role requires NetworkManager, udev, systemd,
iproute and kernel VXLAN support to be available. It uses privilege escalation
to configure devices, write system configuration and manage the service.

## Inputs

All names below have the prefix `cifmw_multi_node_vxlan_`. There are no defaults;
every input must be supplied, including explicitly empty values where allowed.

| Input | Purpose |
| --- | --- |
| `bridge` | Transport bridge name, for example `br-ovl`. |
| `iface` | Host-facing veth name, for example `nic2`. Managed by NetworkManager. |
| `peer_iface` | Other end of the veth pair, attached to the bridge, for example `nic2-p`. |
| `mac` | Non-empty MAC address for the host-facing veth. |
| `mtu` | Overlay device MTU, accounting for underlay encapsulation overhead. |
| `dstport` | VXLAN UDP destination port. |
| `tunnels` | List of tunnel mappings, as below. May be `[]`. |
| `tunnel_prefix` | Prefix used to mark tunnel devices unmanaged in NetworkManager, for example `ovl-`. Must match the supplied tunnel names. |
| `unmanaged_interfaces` | Additional interfaces NetworkManager must leave alone. May be `[]`. The bridge, veth peer and tunnel pattern are already included. |
| `marker` | OVS handoff marker-file path, or `''` to disable handoff detection. |
| `unit` | Systemd service name without `.service`. |
| `script` | Absolute installation path for the transport script. |
| `start_commands` | Trusted shell commands appended to `start()`, or `''`. Run as root. |
| `stop_commands` | Trusted shell commands appended to `stop()`, or `''`. Run as root. |

Each tunnel requires `name`, `vni` and `remote`. The optional `peer` is a label
used only in a script comment:

```yaml
cifmw_multi_node_vxlan_tunnels:
  - name: ovl-0
    vni: 5000
    remote: 192.0.2.20
    peer: compute-0
```

## Execution

`tasks/main.yaml` runs these phases in order:

1. `configure.yaml`: validate inputs, configure NetworkManager device ownership
   and the veth udev rule, then reload configuration when files change.
2. `install.yaml`: install the transport script and systemd unit.
3. `start.yaml`: enable and start the service, restarting it if the script or
   unit changed, then apply and check the veth udev rule.

Callers can include these task files separately to insert work between phases.
Keep their order: `start.yaml` uses results registered by `install.yaml`.

The service creates devices before NetworkManager starts at boot. If the OVS
marker exists, the script leaves bridge management and port attachment to OVS;
the caller must provide that OVS integration. Stopping removes tunnels and runs
`stop_commands`, but leaves the bridge and veth pair intact.
