# radvd

Manage radvd (Router Advertisement Daemon) configuration.

This role provides IPv6 Router Advertisements for network interfaces, enabling
Stateless Address Autoconfiguration (SLAAC) and/or DHCPv6.

## Privilege escalation

- Package installation
- Writing in protected locations `/etc/radvd.conf`, `/etc/cifmw-radvd.d`
- Managing system service `radvd.service`

## Common Parameters

* `cifmw_radvd_basedir`: (String) Configuration fragments directory. Defaults to `/etc/cifmw-radvd.d`.
* `cifmw_radvd_networks`: (List) List of networks to configure. Defaults to `[]`.
* `cifmw_radvd_remove_package`: (Bool) Remove the radvd package during cleanup. Defaults to `false`.

## Network Configuration

Each network in `cifmw_radvd_networks` supports the following parameters:

* `name`: (String) Network/interface name. **Required**.
* `state`: (String) Network status. Must be either `present` or `absent`. Defaults to `present`.
* `prefixes`: (List[mapping]) List of IPv6 prefixes to advertise. **Required when state is present**.
* `adv_send_advert`: (Bool) Enable/disable router advertisements. Defaults to `true`.
* `adv_managed_flag`: (Bool) Managed address configuration flag (M-flag). Indicates DHCPv6 for addresses.
* `adv_other_config_flag`: (Bool) Other configuration flag (O-flag). Indicates DHCPv6 for other configuration.
* `adv_ra_solicited_unicast`: (Bool) Enable unicast router advertisements.
* `adv_link_mtu`: (Int) Advertised MTU for the link.
* `min_rtr_adv_interval`: (Int) Minimum router advertisement interval in seconds.
* `max_rtr_adv_interval`: (Int) Maximum router advertisement interval in seconds.
* `routes`: (List[mapping]) List of routes to advertise. Optional.
* `rdnss`: (List[mapping]) List of recursive DNS servers to advertise. Optional.

### Prefix mapping

* `network`: (String) IPv6 prefix (e.g., `2001:db8:1::/64`). **Required**.
* `adv_on_link`: (Bool) On-link flag. Defaults to `true`.
* `adv_autonomous`: (Bool) Autonomous address configuration flag (SLAAC). Defaults to `true`.
* `adv_router_addr`: (Bool) Include router address in prefix information.
* `adv_valid_lifetime`: (String/Int) Valid lifetime for the prefix (e.g., `86400`, `infinity`).
* `adv_preferred_lifetime`: (String/Int) Preferred lifetime for the prefix.

### Route mapping

* `network`: (String) IPv6 route prefix. **Required**.
* `adv_route_preference`: (String) Route preference (`low`, `medium`, `high`).
* `adv_route_lifetime`: (Int) Route lifetime in seconds.

### RDNSS mapping

* `servers`: (List[String]) List of IPv6 DNS server addresses. **Required**.
* `adv_rdnss_lifetime`: (Int) RDNSS lifetime in seconds.

## Examples

### Basic network with SLAAC only

```yaml
- name: Configure radvd networks
  vars:
    cifmw_radvd_networks:
      - name: testnet
        adv_managed_flag: false
        adv_other_config_flag: false
        adv_link_mtu: 1500
        min_rtr_adv_interval: 30
        max_rtr_adv_interval: 100
        prefixes:
          - network: "2001:db8:1::/64"
            adv_on_link: true
            adv_autonomous: true
            adv_router_addr: true
  ansible.builtin.include_role:
    name: radvd
```

### Network with DHCPv6 for addresses and other configuration

```yaml
- name: Configure radvd with DHCPv6
  vars:
    cifmw_radvd_networks:
      - name: provisioning
        adv_managed_flag: true
        adv_other_config_flag: true
        adv_ra_solicited_unicast: true
        adv_link_mtu: 1500
        min_rtr_adv_interval: 30
        max_rtr_adv_interval: 100
        prefixes:
          - network: "2001:db8:2::/64"
            adv_on_link: true
            adv_autonomous: false
        rdnss:
          - servers:
              - "2001:db8:2::53"
            adv_rdnss_lifetime: 300
  ansible.builtin.include_role:
    name: radvd
```

### Multiple networks

```yaml
- name: Configure multiple networks
  vars:
    cifmw_radvd_networks:
      - name: net1
        adv_managed_flag: true
        adv_other_config_flag: true
        adv_link_mtu: 1500
        min_rtr_adv_interval: 30
        max_rtr_adv_interval: 100
        prefixes:
          - network: "2001:db8:1::/64"
            adv_on_link: true
            adv_autonomous: true
      - name: net2
        adv_managed_flag: false
        adv_other_config_flag: false
        prefixes:
          - network: "2001:db8:2::/64"
            adv_on_link: true
            adv_autonomous: true
  ansible.builtin.include_role:
    name: radvd
```

### Remove a network configuration

```yaml
- name: Remove radvd configuration for a network
  vars:
    cifmw_radvd_networks:
      - name: testnet
        state: absent
  ansible.builtin.include_role:
    name: radvd
```

### Cleanup entire radvd service

```yaml
- name: Cleanup radvd
  vars:
    # Set to true to also remove the radvd package (default: false)
    cifmw_radvd_remove_package: false
  ansible.builtin.include_role:
    name: radvd
    tasks_from: cleanup.yml
```

## Understanding the flags

### Managed Flag (M-flag) - `adv_managed_flag`

When set to `true`, hosts should use DHCPv6 to obtain IPv6 addresses (stateful DHCPv6).
When set to `false`, hosts should use SLAAC (Stateless Address Autoconfiguration) based on the advertised prefix.

### Other Config Flag (O-flag) - `adv_other_config_flag`

When set to `true`, hosts should use DHCPv6 to obtain other configuration information (DNS, NTP, etc.).

### Common configurations

1. **SLAAC only**: `adv_managed_flag: false`, `adv_other_config_flag: false`, `adv_autonomous: true`
2. **SLAAC + DHCPv6 for options**: `adv_managed_flag: false`, `adv_other_config_flag: true`, `adv_autonomous: true`
3. **DHCPv6 for everything**: `adv_managed_flag: true`, `adv_other_config_flag: true`, `adv_autonomous: false`

## Notes

- The interface/bridge specified by the `name` parameter must exist before radvd can advertise on it.
- IPv6 forwarding must be enabled on the host for router advertisements to work properly.
- Multiple prefixes can be advertised on the same interface.
- The role uses the system `radvd.service` from the RPM package.
- Configuration is assembled from fragments in `/etc/cifmw-radvd.d/` into `/etc/radvd.conf`.
