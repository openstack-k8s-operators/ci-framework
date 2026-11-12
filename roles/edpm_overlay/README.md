# edpm_overlay

Connect EDPM compute nodes to a VXLAN overlay. The role allows the tunnel UDP
port in the EDPM firewall, adds an Open vSwitch (OVS) bridge and patch port for
the transport, and can write a dataplane kustomization that connects the
compute node's external bridge to that patch port. The kustomization uses the
`os-net-config` template.

`vxlan_overlay` calls this role after setting up the transport. The role uses
privilege escalation to write the firewall configuration, install the OVS
script and unit, and manage the unit on compute nodes.

## Inputs

All inputs have the prefix `cifmw_edpm_overlay_`. There are no defaults; the
caller must supply every input even when one of the two actions is disabled.

| Input | Purpose |
| --- | --- |
| `enabled` | Prepare the local host for EDPM. Set this only on the participating compute nodes. |
| `bridge`, `peer_iface` | Transport bridge and bridge-facing end of the veth pair. |
| `tunnels` | The host's tunnel mappings, each with `name`, `vni`, `remote`, and `peer`. |
| `patch_port`, `patch_peer` | Names of the two ends of the OVS patch link: transport side and external bridge side. |
| `dstport` | UDP destination port to allow in the EDPM firewall. |
| `transport_unit`, `unit` | Transport and OVS integration systemd unit names, without `.service`. |
| `script`, `marker` | Paths for the OVS script and the marker shared with the transport. |
| `kustomize` | Write the dataplane kustomization once, independently of `enabled`. |
| `kustomize_host`, `kustomize_dir`, `kustomize_file` | Host, directory, and filename for the generated kustomization. |
| `kustomize_nodesets` | Name regex for `OpenStackDataPlaneNodeSet` resources to patch. Match only node sets whose hosts are prepared by this role. |
