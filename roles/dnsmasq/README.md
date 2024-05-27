# dnsmasq

Create a standalone dnsmasq service and manage its configuration.

The main usage of this role is to expose a DHCP service for libvirt
networks, to properly support fixed IPv4 *and* IPv6 (the latter isn't
supported in libvirt).

## Privilege escalation

- Package installation
- Writing in protected locations `/etc/systemd/system`, `/etc/cifmw-dnsmasq.conf`, `/etc/cifmw-dnsmasq.d`

## Common Parameters

* `cifmw_dnsmasq_basedir`: (String) Configuration directory location. Defaults to `/etc/cifmw-dnsmasq.d`.
* `cifmw_dnsmasq_enable_dns`: (Bool) Toggle to enable DNS features of dnsmasq. Defaults to `false`.
* `cifmw_dnsmasq_exclude_lo`: (Bool) Toggle to disable binding on loopback interface to avoid conflicts. Defaults to `false`.
* `cifmw_dnsmasq_dns_config_file`: (String) DNS related settings configuration file path. Defaults to `{{ cifmw_dnsmasq_basedir }}/dns.conf`.
* `cifmw_dnsmasq_listener_config_file`: (String) listener related settings configuration file path. Defaults to `{{ cifmw_dnsmasq_basedir }}/listener.conf`.
* `cifmw_dnsmasq_raw_config`: (String) Raw configure options for dnsmasq. Should be passed as a (multiline) string. Defaults to `""`.

### New network parameters

* `cifmw_dnsmasq_network_name`: (String) Network name.
* `cifmw_dnsmasq_network_state`: (String) Network status. Must be either `present` or `absent`.
* `cifmw_dnsmasq_network_definition`: (Dict) Mapping representing the network definition.
* `cifmw_dnsmasq_network_definition.ranges`: (List[mapping]) List of ranges associated to the network.
* `cifmw_dnsmasq_forwarders`: (List) List of upstream DNS servers used as forwarders. Defaults to `[]`
* `cifmw_dnsmasq_interfaces`: (List) List of interfaces on which dnsmasq should be enabled. Defaults to `[]`.
* `cifmw_dnsmasq_listen_addresses`: (List) List of IP addresses on which dnsmasq should be enabled. Defaults to `[]`.
* `cifmw_dnsmasq_addresses`: (List) Specify a list of IP addresses to return for any host in the given domains. Defaults to `[]`.

#### Ranges mapping

* `label`: (String) Network label ("tag" in dnsmasq manual).
* `domain`: (String) domain name associated to the dhcp range.
* `start_v4`: (String) IPv4 starting IP.
* `start_v6`: (String) IPv6 starting IP.
* `prefix_length_v4`: (Int) IPv4 prefix length. Defaults to `24`.
* `prefix_length_v6`: (Int) IPv6 prefix length. Defaults to `64`.
* `ttl`: (String) Subnet TTL. Defaults to `1h`.
* `options`: (List) List of options associated to the network.
* `options_force`: (List) List of forced options associated to the network.

#### Examples

```YAML
    - name: Create network
      vars:
        cifmw_dnsmasq_network_name: starwars
        cifmw_dnsmasq_network_state: present
        cifmw_dnsmasq_network_listen_dns:
          - 192.168.199.9
          - ff99:abcd::9
          - ''  # empty string is supported as "no entry"
        cifmw_dnsmasq_network_definition:
          ranges:
            - label: ian
              start_v4: 192.168.254.10
              start_v6: "2345:0425:2CA1::0567:5673:23b5"
              options:
                - "3,192.168.254.1"
                - "option6:ntp-server,[1234::56]"
              options_force:
                - "vendor:PXEClient,1,0.0.0.0"
      ansible.builtin.include_role:
        name: dnsmasq
        tasks_from: manage_network.yml
```

### New host parameters

* `cifmw_dnsmasq_host_network`: (String) Existing network name.
* `cifmw_dnsmasq_host_state`: (String) Host status. Must be either `present` or `absent`.
* `cifmw_dnsmasq_host_mac`: (String) Host MAC address.
* `cifmw_dnsmasq_host_ipv6`: (String) Host IPv6. Optional if `cifmw_dnsmasq_host_ipv4` is set.
* `cifmw_dnsmasq_host_ipv4`: (String) Host IPv4. Optional if `cifmw_dnsmasq_host_ipv6` is set.
* `cifmw_dnsmasq_host_name`: (String) Host name. Optional.
