# ci_network

Apply and manage connection in NetworkManager. This role is especially important for CI
and CI Job reproducer, since we have to prepare most of the network beforehand.

## Privilege escalation

It needs sudo access to edit Network Manager connections.

## Parameters

* `cifmw_network_generated_layout`: (Str) Path to the generated layout you want to apply. Defaults to `/etc/ci/env/network-layout.yml`.
* `cifmw_network_pre_cleanup`: (Bool) Clean existing ethernet connections before applying configuration. Defaults to `true`.
* `cifmw_network_layout`: (Dict) Network layout you want to apply.
* `cifmw_network_nm_config`: (List(dict)) List of editions to do in the NetworkManager.conf. Defaults to `[]`
* `cifmw_network_nm_config_dir`: (Str) Path to NetworkManager configuration directory. Defaults to `/etc/NetworkManager`.
* `cifmw_network_nm_config_file`: (Str) Path to NetworkManager configuration file. Defaults to `cifmw_network_nm_config_dir ~ NetworkManager.conf`.
* `cifmw_network_nm_config_dnsmasq_file`: (Str) Path to NetworkManager dnsmasq enabling file. Defaults to `cifmw_network_nm_config_dir ~ /conf.d/00-use-dnsmasq.conf`.

### Deprecated parameters
* `cifmw_network_dnsmasq_config`: (Dict) dnsmasq configuration to be applied on the KVM host.
* `cifmw_network_dnsmasq_leases_file`: (Str) Path to the dnsmasq DHCP static leases file. Defaults to `cifmw_network_nm_config_dir ~ /dnsmasq.d/98-cifmw-static-leases.conf`.
* `cifmw_network_dnsmasq_forwarders_file`: (Str) Path to the dnsmasq forwarders file. Defaults to `cifmw_network_nm_config_dir ~ /dnsmasq.d/99-cifmw-dns-forwarders.conf`.
* `cifmw_network_dnsmasq_config_file`: (Str) Path to the dnsmasq config file. Defaults to `cifmw_network_nm_config_dir ~ /dnsmasq.d/97-cifmw-local-domain.conf`.
* `cifmw_network_dnsmasq_static_leases_time`: (Str) dnsmasq static leases default lifetime. Defaults to `infinite`.

## NetworkManager configuration layout

The list must be as follow:

```YAML
cifmw_network_nm_config:
  - state: present|absent  # Optional. Defaults to present
    section:  # Mandatory. Section name in the ini file
    option:  # Mandatory. Option name in the ini file
    value:  # Mandatory. Value of the option
```

## Network configuration layout

This dict has to represent all of the networks as follow:

```YAML
cifmw_network_layout:
  <hostname>:
    <network-name>:
      iface:  # Mandatory. Interface name on the host.
      mac:  # Optional. MAC address of the interface.
      mtu:  # Optional. Defaults to 1500.
      connection:  # Optional. Connection name. Defaults to "network-name" key value.
      ip4:  # Mandatory. IPv4 address.
      dns4:  # Optional. IPv4 DNS servers list.
      gw4:  # Optional. IPv4 gateway for that network.
      ip6:  # Optional. IPv6 address.
      gw6:  # Optional. IPv6 gateway.
      dns6:  # Optional. IPV6 DNS servers list.
```

## Bootstrap CI

It will also look for a specific parameter from the CI Bootstrap steps: `crc_ci_bootstrap_networks_out`.
If it finds it, it will consume it instead of `cifmw_network_layout`.

## DNS configuration

WARNING: deprecated feature!

The configuration is represented by

```YAML
cifmw_network_dnsmasq_config:
  listen_addresses:   # Optional. list, IP address for the daemon to listen on. Default: 127.0.0.1
  interfaces:         # Optional. list, names of network interfaces to listen on.
  domains:            # Optional. list, local domains to be configured
  addresses:          # Optional. list, of dictionaries
    - fqdn:           # str, Fully Qualified Domain Name
      address:        # str, a valid IP address
  forwarders:
    - 8.8.8.8         # Optional. list, of DNS forwarders to be applied.
```


## DHCP configuration

WARNING: deprecated feature!

To enable dnsmasq configuration is represented by

```YAML
cifmw_network_dnsmasq_config:
  dhcp:
    network:      # Optional. str. Network subnet.
    gateway:      # Optional. str. Network gateway.
    dns:          # Optional. list/string. Network DNS servers.
    domain:       # Optional. str. DHCP network domain.
    range:        # Optional. IP range to give leases.
      start:      # str. Start of the DHCP range (included)
      end:        # str. End of the range (included)
      lease_time: # Optional. str. Range lease time. Defaults to 12h.
```
