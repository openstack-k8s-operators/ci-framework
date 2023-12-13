# ci_multus
Creates additional networks in a OCP cluster using NetworkAttachmentDefinition (NAD) resources.

## Parameters
* `cifmw_ci_multus_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_ci_multus_manifests_dir`: (String) Directory in where OCP manifests will be placed. Defaults to `"{{ cifmw_manifests | default(cifmw_ci_multus_basedir ~ '/artifacts/manifests')   }}"`.
* `cifmw_ci_multus_namespace`: (String) The namespace where OCP resources will be installed. Defaults to `ci-multus`.
* `cifmw_ci_multus_ocp_hostname`: (String) The OCP inventory hostname. Used to gather network information specific to those nodes, mostly the interfaces. Defaults to `crc`.
* `cifmw_ci_multus_cniversion`: (String) The CNI specification version used when creating the resource. Defaults to `0.3.1`.
* `cifmw_ci_multus_default_nad_type`: (String) Default NAD type used when not specified by the network configuration. Defaults to `macvlan`.
* `cifmw_ci_multus_default_nad_ipam_type`: (String) Default NAD IPAM type to be used when not specified by the network configuration. Defaults to `whereabouts`.
* `cifmw_ci_multus_nad_list`: (List) List of NAD configuration to be created in destination OCP cluster. When not provided, `ci_multus` will build a list based on known cifmw variables (`cifmw_network_layout`, `crc_ci_bootstrap_networks_out`).Defaults to `[]`.
* `cifmw_ci_multus_nad_extra_list`: (List) Additional list of NAD configuration to be created in destination OCP cluster. Defaults to `[]`.

## NAD configuration layout
The user can provide a list of NAD configuration as follow:

```YAML
cifmw_ci_multus_nad_list:
  - name: storage
    iface: enps6s0.21
    type: macvlan
    ipam:
      type: whereabouts
      range: 172.18.0.0/24
      range_start: 172.18.0.30
      range_end: 172.18.0.70
  - name: bgpnet1
    iface: bgpiface
    type: interface
    ipam:
      type: whereabouts
      range: 100.65.4.0/30
      range_start: 100.65.4.1
      range_end: 100.65.4.2
```
`cifmw_ci_multus_nad_list` can be passed directly, but if not given it will default, by that order, to the following:
1. The content of the `cifmw_network_layout` variable.
2. The content of the `crc_ci_bootstrap_networks_out` variable.
3. The content of the `crc_ci_bootstrap_networks_out` variable loaded from `/etc/ci/env`.

If an additional NAD configuration needs to be configured, in addition to the content build from cifmw variables, the `cifmw_ci_multus_nad_extra_list` can be specified.

## Limitations
* Not all NetworkAttachmentDefinition types and parameters are supported by this role.
* Not all IPAM configurations are supported by this role.
* When consuming network info from CI variables, the user must provide the OCP host, using `cifmw_ci_multus_ocp_hostname` parameter, since the role doesn't perform a Node discovery on the OCP node.

## Examples
### 1 - Use of `cifmw_ci_multus_nad_list`:
```YAML
    - name: Configure additional networks using multus
      vars:
        cifmw_ci_multus_nad_list:
          - name: storage
            iface: enps6s0.21
            type: macvlan
            ipam:
              type: whereabouts
              range: 172.18.0.0/24
              range_start: 172.18.0.30
              range_end: 172.18.0.70
      ansible.builtin.include_role:
        name: "ci_multus"
```
### 2 - Content from `cifmw_network_layout`:
```YAML
    - name: Configure additional networks using multus
      vars:
        cifmw_network_layout:
          networks:
            default:
              iface: enps6s0
              mtu: 1500
              range: 192.168.122.0/24
              multus:
                range: 192.168.122.30-192.168.122.70
      ansible.builtin.include_role:
        name: "ci_multus"
```
