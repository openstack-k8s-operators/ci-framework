# ci_network
Apply and manage connection in NetworkManager. This role is especially important for CI
and CI Job reproducer, since we have to prepare most of the network beforehand.

## Privilege escalation
It needs sudo access to edit Network Manager connections.

## Parameters
* `cifmw_network_generated_layout`: (Str) Path to the generated layout you want to apply. Defaults to `/etc/ci/env/network-layout.yml`.
* `cifmw_network_pre_cleanup`: (Bool) Clean existing ethernet connections before applying configuration. Defaults to `true`.
* `cifmw_network_layout`: (Dict) Network layout you want to apply.
* `cifmw_network_nm_config_file`: (Str) Path to NetworkManager configuration file. Defaults to `/etc/NetworkManager/NetworkManager.conf`.
* `cifmw_network_nm_config`: (List(dict)) List of editions to do in the NetworkManager.conf. Defaults to `[]`

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
