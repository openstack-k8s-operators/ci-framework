# masquerade_external
A role to configure masquerading of traffic going out the default interface,
based on the source address.

This is handy when libvirt networks need to have routing to different libvirt
networks on the host enabled. In `nat` mode libvirt inserts firewall rules that
prevent this. Instead of using `nat` mode for libvirt networks, the `routed` or
`open` mode can be used instead, and this role can set up the masquerading
rules so that the VMs on these networks can still reach external networks.

Example rules inserted by this role:
```bash
Chain POSTROUTING (policy ACCEPT 118 packets, 13329 bytes)
 pkts bytes target     prot opt in     out     source               destination
    0     0 CIFMW-PRT  all  --  any    any     anywhere             anywhere

Chain CIFMW-PRT (1 references)
 pkts bytes target     prot opt in     out     source               destination
    0     0 MASQUERADE  all  --  any    eth0    172.17.0.0/24        anywhere
    0     0 MASQUERADE  all  --  any    eth0    172.16.0.0/24        anywhere
```

## Privilege escalation
Requires privileged escalation to manipulate iptables firewall.

## Parameters
* `cifmw_masquerade_external_source_ranges`: (List) List of source IP or ip networks in CIDR format. Defaults to: `[]`
* `cifmw_masquerade_external_post_routing_chain_name`: (String) Name of the iptables chain
* `cifmw_masquerade_external_out_interface`: (String) Device name for the outgoing interface. Defaults to: `{{ hostvars[inventory_hostname].ansible_default_ipv4.interface }}`

## Examples

### Add masquerading rules for sources `172.16.0.0/24` and `172.17.0.0/24`
```yaml
- name: Include the role with var
  vars:
    cifmw_masquerade_external_source_ranges:
      - '172.16.0.0/24'
      - '172.17.0.0/24'
  ansible.builtin.include_role:
    name: masquerade_external
```

### Cleanup masquerading rules and chain
```yaml
- name: Include the role with var
  ansible.builtin.include_role:
    name: masquerade_external
    tasks_from: cleanup.yml
```
