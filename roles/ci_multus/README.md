# ci_multus

Creates additional networks in a OCP cluster using NetworkAttachmentDefinition
(NAD) resources.

## Parameters

* `cifmw_ci_multus_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_ci_multus_manifests_dir`: (String) Directory in where OCP manifests will be placed. Defaults to `"{{ cifmw_manifests | default(cifmw_ci_multus_basedir ~ '/artifacts/manifests')   }}"`.
* `cifmw_ci_multus_namespace`: (String) The namespace where OCP resources will be installed. Defaults to `openstack`.
* `cifmw_ci_multus_ocp_hostname`: (String) The OCP inventory hostname. Used to gather network information specific to those nodes, mostly the interfaces. Defaults to `crc`.
* `cifmw_ci_multus_cniversion`: (String) The CNI specification version used when creating the resource. Defaults to `0.3.1`.
* `cifmw_ci_multus_default_nad_type`: (String) Default NAD type used when not specified by the network configuration. Defaults to `macvlan`. You can select the type of each NAD by "multus_type"
* `cifmw_ci_multus_default_bridge_attach`: (String) Set place to attach the bridge when NAD type is bridge. Defaults to `interface`. You can select the place to attach it by "multus_attach".
* `cifmw_ci_multus_default_nad_ipam_type`: (String) Default NAD IPAM type to be used when not specified by the network configuration. Defaults to `whereabouts`.
* `cifmw_ci_multus_default_nad_ipam_type_ip_version``: (String) Default IP version to use in IPAM config. Defaults to `v4`.
* `cifmw_ci_multus_dryrun`: (Bool) When enabled, tasks that require an OCP environment are skipped. Defaults to `false`.
* `cifmw_ci_multus_allow_list`: (List) Adding network names to this list allows you to define what networks will be rendered into the NAD manifest. Defaults to `[]`.
* `cifmw_ci_multus_deny_list`: (List) Adding network names to this list allows you to define what networks should be skipped from being rendered into the NAD manifest. Defaults to `[]`.

By default the `ci_multus` role reads the `cifmw_networking_env_definition` variable to generate NetworkAttachmentDefinition manifests for networks who have the Multus tool defined.

In addition to that, you can also pass any number of "patch" variables using `cifmw_ci_multus_net_info_patch` that allow you to extend the config used to render the NetworkAttachmentDefinition manifests.
For a working example, please see `cifmw_ci_multus_net_info_patch_1` in molecule/local/molecule.yml

## cifmw_ci_multus_net_info_patch example

```YAML
cifmw_ci_multus_net_info_patch_1:
  patchnetwork:
    gw_v4: 192.168.122.1
    network_name: patchnetwork
    network_v4: 192.168.122.0/24
    interface_name: eth2
    tools:
      multus:
        ipv4_ranges:
          - start: 192.168.122.30
            end: 192.168.122.70
        type: bridge
        attach: linux-bridge
```

## Limitations

* Not all NetworkAttachmentDefinition types and parameters are supported by this role.
* Not all IPAM configurations are supported by this role.
* When consuming network info from CI variables, the user must provide the OCP host, using `cifmw_ci_multus_ocp_hostname` parameter, since the role doesn't perform a Node discovery on the OCP node.

## Examples

### 1 - Default use case consuming cifmw_networking_env_definition

```YAML
    - name: Configure additional networks using multus
      ansible.builtin.include_role:
        name: "ci_multus"
```

### 2 - Using patch:

```YAML
    - name: Configure additional networks using multus
      vars:
        cifmw_ci_multus_net_info_patch_1:
          patchnetwork:
            gw_v4: 192.168.122.1
            network_name: patchnetwork
            network_v4: 192.168.122.0/24
            interface_name: eth2
            tools:
              multus:
                ipv4_ranges:
                  - start: 192.168.122.30
                    end: 192.168.122.70
              type: macvlan
      ansible.builtin.include_role:
        name: "ci_multus"
```

### 2 - Using allow and deny list:

```YAML
    - name: Configure additional networks using multus
      vars:
        cifmw_ci_multus_allow_list:
          - default
          - awesomenet
          - maybenet
        cifmw_ci_multus_deny_list:
          - maybenet
      ansible.builtin.include_role:
        name: "ci_multus"
```
