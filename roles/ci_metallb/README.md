# ci_metallb

Installs metallb operator and deploys metallb with the configuration generated
from the content of the CI network definitions like `cifmw_network_layout` or
`crc_ci_bootstrap_networks_out`.

## Parameters
* `cifmw_ci_metallb_basedir`: (String) Base directory. Defaults to
`cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_ci_metallb_manifests_dir`: (String) Directory in where OCP manifests
will be placed. Defaults to `"{{ cifmw_manifests
| default(cifmw_ci_metallb_basedir ~ '/artifacts/manifests')   }}"`.
* `cifmw_ci_metallb_namespace`: (String) The namespace where OCP resources will
be installed. Defaults to `metallb-system`.
* `cifmw_ci_metallb_crc_hostname`: (String) The CRC inventory hostname.
Used to gather network information specific to those nodes, mostly the
interfaces. Defaults to `crc`.
* `cifmw_ci_metallb_olm_operator_group`: (Dict) The `OperatorGroup` resource to
be used to install the metallb operator.
* `cifmw_ci_metallb_olm_subscription`: (Dict) The `Subscription` resource to be
used to install the metallb operator.
* `cifmw_ci_metallb_subscription_source`: (String) The Source of
`Subscription` resource to pull metallb operator content.
* `cifmw_ci_metallb_subscription_sourcenamespace`: (String) The Source
namespace of `Subscription` resource to pull metallb operator content.
* `cifmw_ci_metallb_operator_config`: (Dict) The `MetalLB` resource to be used
to configure the installed metallb operator.

## Examples
```YAML
    - name: Configure the load balancer for two networks using ci_metallb
    vars:
        cifmw_network_layout:
          networks:
            osp_trunk:
              metallb:
                ranges:
                  - 192.168.122.80-192.168.122.90
            test-vlan-connection:
              metallb:
                ranges:
                  - 172.18.0.80-172.18.0.90
          controller:
            osp_trunk:
              connection: ci-private-network
              gw: 192.168.122.1
              iface: eth1
              ip: 192.168.122.11/24
              mac: fa:16:3e:45:c1:b1
              mtu: 1500
            internal-api:
              connection: ci-private-network-20
              iface: eth1.20
              ip: 172.17.0.4/24
              mac: 52:54:00:30:d2:36
              mtu: 1496
              parent_iface: eth1
              vlan: 20
          crc:
            osp_trunk:
              connection: ci-private-network
              gw: 192.168.122.1
              iface: eth2
              ip4: 192.168.122.22/24
              mtu: 1500
            test-vlan-connection:
              connection: test-network-20
              iface: "eth2.20"
              ip4: 172.17.0.5/24
              mtu: 1496
              parent_iface: "eth2"
              vlan: 20

      ansible.builtin.include_role:
        name: "ci_metallb"
```
