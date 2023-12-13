# ci_nmstate
Configures Ansible hosts networks by applying nmstate configurations
generated from the content of the CI network definitions like
`cifmw_network_layout` or `crc_ci_bootstrap_networks_out`.

## Privilege escalation

It needs sudo access to install nmstate packages and apply
nmstate changes as they manipulate networking.

## Parameters
* `cifmw_ci_nmstate_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_ci_nmstate_manifests_dir`: (String) Directory in where OCP manifests will be placed. Defaults to `"{{ cifmw_manifests | default(cifmw_ci_nmstate_basedir ~ '/artifacts/manifests') }}"`.
* `cifmw_ci_nmstate_configs_dir`: (String) Directory in where nmstate target states for non OCP nodes will be placed. Defaults to `"{{ cifmw_ci_nmstate_basedir ~ '/artifacts/nmstate' }}"`.
* `cifmw_ci_nmstate_namespace`: (String) The namespace where OCP resources will be installed. Defaults to `openshift-nmstate`.
* `cifmw_ci_nmstate_olm_operator_group`: (Dict) The `OperatorGroup` resource to be used to install the nmstate operator.
* `cifmw_ci_nmstate_olm_subscription`: (Dict) The `Subscription` resource to be used to install the nmstate operator.
* `cifmw_ci_nmstate_operator_config`: (Dict) The `NMState` resource to be used to configure the installed nmstate operator.
* `cifmw_ci_nmstate_nncp_config_template`: (Dict) The `NodeNetworkConfigurationPolicy` resource base used to create each OCP node NNCP resource.
* `cifmw_ci_nmstate_unmanaged_config_template`: (Dict) The base nmstate state definition used to create each non OCP node nmstate state.
* `cifmw_ci_nmstate_network_layout`: (Dict) Network layout to apply.
* `cifmw_ci_nmstate_instance_config`: (Dict) That contains the nmstate configurations to apply to each instance in case the default generated ones are not enough.

## Network configuration layout

This dict has to represent all of the networks as follow:

```YAML
cifmw_ci_nmstate_network_layout:
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
`cifmw_ci_nmstate_network_layout` can be passed directly, but if not given it will default,
by that order, to the following:
1. The content of the `cifmw_network_layout` variable.
2. The content of the `crc_ci_bootstrap_networks_out` variable.
3. The content of the `crc_ci_bootstrap_networks_out` variable loaded from `/etc/ci/env`.


## The custom instance config dict
In case the generated nmstate configuration is not enough for the given purpose it is possible
to directly pass the configuration to be applied to each instance (OCP and/or unmanaged) by placing
it in the `cifmw_ci_nmstate_instance_config` dict like this:

```YAML
cifmw_ci_nmstate_instance_config:
  <hostname-1>:
    dns:
      config:
        server:
          - 192.0.2.1
        search:
          - example.org
    routes:
      config:
        - destination: 0.0.0.0/0
          next-hop-interface: eth1
          next-hop-address: 192.0.2.1
    interfaces:
      - name: eth1
        type: ethernet
        description: Main-NIC
        state: up
        ipv4:
          enabled: true
          dhcp: false
          address:
            - ip: 192.0.2.9
              prefix-length: 24
        ipv6:
          enabled: false
  <hostname-2>:
    <rest-of-the-config>
```

## Examples
```YAML
    - name: Configure a couple of nets using ci_nmstate in two Ansible hosts
      vars:
        cifmw_ci_nmstate_network_layout:
            instance-1:
              default:
                connection: ci-private-network
                gw4: 192.168.122.1
                iface: eth1
                ip4: 192.168.122.20/24
                mtu: 1500
            instance-2:
              default:
                connection: ci-private-network
                gw4: 192.168.122.1
                iface: eth2
                ip4: 192.168.122.22/24
                mtu: 1500
              vlan-connection-20:
                connection: vlan-connection-20
                iface: eth2.20
                ip4: 172.17.0.5/24
                mtu: 1496
                parent_iface: eth2
                vlan: 20

      ansible.builtin.include_role:
        name: "ci_nmstate"
```
