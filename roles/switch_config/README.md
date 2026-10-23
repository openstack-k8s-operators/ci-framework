# switch_config

The switches config role performs the following tasks:

- VLAN configuration access/trunk on the switch port.
- MTU configuration on the switch port.
- LACP configuration on interface and members attach.
- IGMP Snooping configuration
- BGP configuration (Juniper only)

Supported switch platforms:

- Cisco
- Juniper
- Mellanox MLNX-OS (ONYX with JSON API is not supported due to not having access to a compatible switch)

**For Juniper switches, Ansible modules use the `netconf` capability `lock`, which is equivalent to the CLI command `configure exclusive`,
which means parallel execution is impossible.**.
We are doing a check to avoid this if the configuration database is open.
It will automatically retry 3 times every 15 minutes if it is not open (by default).
This hack might not be stable.

## Privilege escalation

None


## Parameters

* `cifmw_switch_config_task_retry_delay`: (Integer) The delay time between retries when DB is locked, defaults to `900`.
* `cifmw_switch_config_task_retries`: (Integer) Number of retries when DB is locked, defaults to `3`.
* `cifmw_switch_config_scenario_name`: (String) The scenario to use to configure the switches. Defaults to `default`.


## Inventory

This role is prepared to target `switches` based on their `ansible_network_os`. Each target host must define the variable
and it should match one of these values:

- junos
- ios
- onyx

A complete inventory that covers all the supported types follows:

```yaml
---
switches:
  hosts:
    junos-01-sw:
      ansible_user: root
      ansible_host: junos-01-sw.lab.example.com
      ansible_network_os: junos
      ansible_connection: netconf
    ios-01-sw:
      ansible_user: root
      ansible_host: ios-01-sw.lab.example.com
      ansible_network_os: ios
      ansible_connection: network_cli
      ansible_become: yes
      ansible_become_method: enable
    onyx-01-sw:
      ansible_user: root
      ansible_host: onyx-01-sw.lab.example.com
      ansible_network_os: onyx
      ansible_connection: network_cli
      ansible_become: yes
      ansible_become_method: enable
```

## Config

The role uses a common format to hold the configuration details of the switches, despite of their manufacturer.
The configuration can be passed to the role by one of these approaches:

- By passing the configuration using a dictionary named as the switch host is named in the inventory. If the
variable exists for a given switch the next approach will be ignored.
- By using the `cifmw_switch_config_scenarios` variable in conjunction with `cifmw_switch_config_scenario_name`.
This approach. This approach allows the caller to run the role multiple times with different configurations by just
toggling the `cifmw_switch_config_scenario_name`. The format of the scenario dictionary is identical to the one of
the previous approach.

Example:

```yaml
---
cifmw_switch_config_scenarios:
  default:
    junos-01-sw:
      layer3_interfaces:
        - unit: "50"
          ipv4_address: "172.29.0.254/16"
          vlan_interface: "vlan50"
        - unit: "51"
          ipv4_address: "192.168.51.254/24"
          vlan_interface: "vlan51"
      vlans:
        - start: 50
          end: 51
      interfaces:
        - description: "Inteface 0"
          iface: "ge-0/0/20"
          iface_mode: "trunk"
          native_vlan: "51"
          vlan: "50-51"
          mtu: "9192"
        - description: "Inteface 1"
          iface: "ge-0/0/21"
          iface_mode: "access"
          vlan: "50"
          mtu: "9192"
  second-scenario:
    junos-01-sw:
      layer3_interfaces:
        - unit: "50"
          ipv4_address: "172.29.0.254/16"
          vlan_interface: "vlan50"
        - unit: "51"
          ipv4_address: "192.168.51.254/24"
          vlan_interface: "vlan51"
      vlans:
        - start: 50
          end: 51
      interfaces:
        - description: "Inteface 0"
          iface: "ge-0/0/20"
          iface_mode: "trunk"
          native_vlan: "51"
          vlan: "50-51"
          mtu: "9192"
        - description: "Inteface 1"
          iface: "ge-0/0/21"
          iface_mode: "access"
          vlan: "50"
          mtu: "1500"
```

### BGP (Juniper only)

An optional `bgp` key renders `set routing-options ...` and `set protocols bgp ...`
lines. It is intended for simple fabrics such as an EVPN route-reflector. Every
field is optional; `groups` holds one or more BGP groups, and `extra_lines` is an
escape hatch for any raw Junos `set` statement not covered by the schema (for
example `set protocols evpn ...` or `set policy-options ...`).

```yaml
junos-01-sw:
  bgp:
    local_as: 65000             # set routing-options autonomous-system
    router_id: "10.0.0.1"       # set routing-options router-id
    groups:
      - name: "EVPN-RR"
        type: "internal"        # internal (default) | external
        local_address: "10.0.0.1"
        cluster: "10.0.0.1"     # presence makes the group a route-reflector
        peer_as: 65000          # for external groups
        families:               # one "family ..." statement per entry
          - "evpn signaling"
        neighbors:              # an address, or a mapping with a TCP-MD5 key
          - "10.0.0.2"
          - address: "10.0.0.3"
            authentication_key: "secret"  # must match the peer's password
    extra_lines:
      - "set protocols evpn encapsulation vxlan"
```
