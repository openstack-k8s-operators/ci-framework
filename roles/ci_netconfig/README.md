# ci_netconfig

It creates NetConfig resources in an OCP cluster

## Parameters

- `cifmw_ci_netconfig_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
- `cifmw_ci_netconfig_manifests_dir`: (String) Directory where OCP manifests will be placed. Defaults to `"{{ cifmw_manifests | default(cifmw_ci_netconfig_basedir ~ '/artifacts/manifests')   }}"`.
- `cifmw_ci_netconfig_namespace`: (String) The namespace where OCP resources will be installed. Defaults to `openstack`.
- `cifmw_ci_netconfig_dict`: (Dict) Dictionary of Network configuration to be created in destination OCP cluster. Defaults to `{}`.

## Examples

```YAML
    - name: Configure networks
      vars:
        cifmw_ci_netconfig_list:
          ctlPlane:
            network_v4: 192.168.122.0/24
            gw_v4: 192.168.122.1
            searchDomain: ctlplane.example.com
            tools:
              netconfig:
                ranges:
                  - end: 192.168.122.120
                    start: 192.168.122.100
                  - end: 192.168.122.200
                    start: 192.168.122.150
          internalApi:
            searchDomain: internalapi.example.com
            network_v4: 172.17.0.0/24
            vlan: 20
            tools:
              netconfig:
                ranges:
                  - end: 172.17.0.250
                    start: 172.17.0.100
          external:
            searchDomain: external.example.com
            network_v4: 10.0.0.0/24
            gw_v4: 10.0.0.1
            tools:
              netconfig:
                ranges:
                  - end: 10.0.0.250
                    start: 10.0.0.100
      ansible.builtin.include_role:
        name: "ci_netconfig"
```
