# multi_node_routing

Keep tunnel and management traffic on the underlay when its addresses overlap
with overlay networks. Requires IPv4 connectivity through an existing default
gateway, NetworkManager dispatcher support, Bash and iproute. Uses privilege
escalation to install the dispatcher and change routing.

The role installs a dedicated routing table pointing at the current underlay
gateway, plus rules that select it for:

- Traffic to tunnel endpoint addresses.
- Traffic from the host's underlay address to overlay ranges, protecting SSH
  replies to management clients whose addresses overlap those ranges.

Traffic sourced from overlay addresses continues to use normal routing.

## Inputs

All names below have the prefix `cifmw_multi_node_routing_`. All are required;
there are no defaults.

| Input | Purpose |
| --- | --- |
| `remotes` | List of tunnel endpoint IPv4 addresses. |
| `overlay_ranges` | List of overlay IPv4 CIDRs. |
| `iface` | Host-facing overlay interface name, for example `nic2`. |
| `bridge` | Overlay bridge name, for example `br-ovl`. |
| `route_table` | Dedicated numeric routing table ID. |
| `rule_priority` | Priority for destination rules; source rules use this value plus one. Both must precede the normal main-table lookup. |

Reserve the table and both rule priorities for this role. The dispatcher removes
stale rules at those priorities. It refuses an underlay default route on
`iface`, its VLAN subinterfaces or `bridge`.

## Execution

Run the role before activating overlay networks. It installs and immediately
runs `/etc/NetworkManager/dispatcher.d/90-cifmw-vxlan-overlay`.
NetworkManager reruns it on `up`, `dhcp4-change` and `reapply` events, refreshing
the gateway, device and source address. Missing rules are added before stale
ones are removed; failed additions prevent removal of the old rules.

After overlay profiles are active, callers can include `tasks_from: check.yaml`
to check the remote rules and presence of a default route in the dedicated
table. That entry point requires only `remotes`, `route_table` and
`rule_priority`; it does not verify the source rules.

## Testing

No Molecule scenario is included: end-to-end coverage requires overlapping
networks and NetworkManager lifecycle events. Validate with multinode CI,
including management connectivity after profile activation and reboot.
