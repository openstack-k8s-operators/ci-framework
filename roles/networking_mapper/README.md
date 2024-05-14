# networking_mapper
Handles validation and mapping of the Networking Definition, the generic, CI-framework specific, way of
defining CI networks into the Networking Environment Definition, the dictionary that holds all the
networking details of a given environment.


## Parameters
* `cifmw_networking_definition`: (Dict) The Networking Definition as a dictionary.
* `cifmw_networking_mapper_ifaces_info`: (Dict) The interface information dictionary that holds low-level info for full maps.
* `cifmw_networking_mapper_assert_env_load`:(Boolean) Ensures that calling the Networking Environment Definition ends with a valid one loaded. Defaults to `true`.
* `cifmw_networking_mapper_interfaces_info_translations`: (Dict) Optional dictionary of lists that allows `cifmw_networking_mapper_ifaces_info` use different network names than the Networking Definition networks.

## Networking Definition patching
This role allows to use a base Networking Definition, given by `cifmw_networking_definition` and patch it
with other values, ie. patch it for another environment, by declaring variables prefixed that matches the
`^cifmw_networking_mapper_definition_patch.*` regex. Each of those variables, after sorting them by name,
will be combined on top of the original `cifmw_networking_definition` and that will be the Networking
Definition the networking mapper will use to generate the Networking Environment Definition.
The content of the `cifmw_networking_definition` will reflect those patches.

## Important definitions
- Networking Definition: The input to the CI-framework that defines all the networking-needed data.
- Networking Environment Definition: The output of the mapper that the CI-framework consumes to configure
  all components that depend on the environment networking.
- Partial mapping: The mapper is expected to be run in two main situations.
  - Before instances are deployed: At that point low-level information such as mac addresses, interface names or MTU may
    not be yet available, but important information such as IPs to configure, desired MTU, DNS or other data
    is available by looking at the Networking Information.
    A partial map is just that, a run of the mapper with an incomplete output that lacks of instances-specific pieces.
  - When instances are deployed: At that point, all the low-level information is available, and the mapper is able
    to create the entire output with all the details for all the involved networks and instances based on the input
    Networking Definition and the Interfaces Information dict, that contains all the details to wire up instances
    interfaces to networks.
- Interfaces Information: An input to the mapper, required for full maps, that enables that allows matching interfaces
    and mac addresses for all the instances.

## Examples
```
- name: Call the networking mapper partial map (limited instances information)
  vars:
    cifmw_networking_definition:
      networks:
          ctlplane:
            network: "192.168.122.0/24"
            gateway: "192.168.122.1"
            dns:
              - "192.168.122.253"
              - "192.168.122.254"
            search-domain: "ctlplane.example.local"
            mtu: 1500
          internal-api:
            network: "172.17.0.0/24"
            gateway: "172.17.0.1"
            vlan: 20
            mtu: 1496
          storage:
            network: "172.18.0.0/24"
            vlan: 21
            mtu: 1496
          tenant:
            network: "172.19.0.0/24"
            gateway-v4: "172.19.0.1"
            search-domain: "tenant.example.local"
            dns-v4:
              - "8.8.8.8"
              - "172.19.0.1"
            vlan: 22
            mtu: 1496
        group-templates:
          computes:
            networks:
              ctlplane:
                range: "192.168.122.10-192.168.122.14"
              internal-api:
                range: "10-14"
              tenant:
                range:
                  start: 10
                  length: 5
              storage:
                range:
                  start: 10
                  length: 5
        instances:
          crc:
            networks:
              ctlplane:
                ip: "192.168.122.10"
              storage:
                ip: "172.18.0.10"
          controller:
            networks:
              ctlplane:
                ip: "192.168.122.5"
  ansible.builtin.include_role:
    name: networking_mapper


- name: Call the networking mapper full map
  vars:
    cifmw_networking_definition:
      networks:
          ctlplane:
            network: "192.168.122.0/24"
            gateway: "192.168.122.1"
            dns:
              - "192.168.122.253"
              - "192.168.122.254"
            search-domain: "ctlplane.example.local"
            mtu: 1500
          internal-api:
            network: "172.17.0.0/24"
            gateway: "172.17.0.1"
            vlan: 20
            mtu: 1496
          storage:
            network: "172.18.0.0/24"
            vlan: 21
            mtu: 1496
          tenant:
            network: "172.19.0.0/24"
            gateway-v4: "172.19.0.1"
            search-domain: "tenant.example.local"
            dns-v4:
              - "8.8.8.8"
              - "172.19.0.1"
            vlan: 22
            mtu: 1496
        group-templates:
          computes:
            networks:
              ctlplane:
                range: "192.168.122.10-192.168.122.14"
              internal-api:
                range: "10-14"
              tenant:
                range:
                  start: 10
                  length: 5
              storage:
                range:
                  start: 10
                  length: 5
        instances:
          crc:
            networks:
              ctlplane:
                ip: "192.168.122.10"
              storage:
                ip: "172.18.0.10"
          controller:
            networks:
              ctlplane:
                ip: "192.168.122.5"
    cifmw_networking_mapper_ifaces_info:
      controller-0:
        - mac: fa:16:3e:12:4f:d1
          network: test-network
        - mac: aa:45:3e:ab:ff:e4
          network: test-network-2
      instance-0:
        - mac: fa:16:3e:c1:b2:e9
          network: test-network
      instance-1:
        - mac: fa:16:3e:3d:e5:cc
          network: test-network
        - mac: aa:45:3e:f9:00:c0
          network: test-network-2
  ansible.builtin.include_role:
    name: networking_mapper
```
