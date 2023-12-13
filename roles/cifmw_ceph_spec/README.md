# cifmw_ceph_spec

Create an opinionated
[Ceph Service Specification](https://docs.ceph.com/en/octopus/mgr/orchestrator/#orchestrator-cli-service-spec)
for a basic N-node Ceph cluster which can run on EDPM development or
CI nodes for testing Ceph and Nova Collocation (HCI).

When the tripleo-ansible role `tripleo_cephadm` was ported to the
ci-framework as `cifmw_cephadm`, it was no longer helpful to generate
spec file using the output of Metalsmith with
[ceph_spec_bootstrap](https://docs.openstack.org/tripleo-ansible/latest/modules/modules-ceph_spec_bootstrap.html).

Because
[install_yamls](https://github.com/openstack-k8s-operators/install_yamls)
can generate an arbitrary number of EDPM nodes with an arbitrary list
of networks, it is useful to have a role which can generate a simple
spec as a function of all nodes and use whichever IPs they have which
are in the IP range the user wishes to use as a storage network.

## Privilege escalation
None

## Parameters

* `cifmw_ceph_spec_host_to_ip`: map of hostname to IP address (default `{"edpm-compute-0": "192.168.122.100"}`)
* `cifmw_ceph_spec_data_devices`: YAML multi line string describing the
  Ceph spec data devices (defaults to the path `/dev/ceph_vg/ceph_lv_data`
  which is created by the `cifmw_block_device` role)
* `cifmw_ceph_spec_path`: path of the rendered spec file (default
  `/tmp/ceph_spec.yml`)

## Examples

The `cifmw_ceph_spec_host_to_ip` parameter defaults to the following
so that it represents one EDPM node with default IP address (no
network isolation) as created by install_yamls.
```
cifmw_ceph_spec_host_to_ip:
  edpm-compute-0: 192.168.122.100
```
However if you deploy `N` EDPM nodes and use network isolation, then
the `cifmw_ceph_spec_host_to_ip` should look more like this:
```
cifmw_ceph_spec_host_to_ip:
  edpm-compute-0: 172.18.0.8
  edpm-compute-1: 172.18.0.33
  edpm-compute-2: 172.18.0.37
  ...
  edpm-compute-N: 172.18.0.N
```
If network isolation is used, then as per the
[openstack-k8s-operators networking documentation](https://github.com/openstack-k8s-operators/docs/blob/main/networking.md),
the storage network is `172.18.0.0/24`.

Assuming the networks are already provisioned on the EDPM nodes and
that a group called `edpm` exists in the inventory, the following
may be used to set `cifmw_ceph_spec_host_to_ip` to a mapping of all
EDPM node hostnames and their discovered IP addresses which are in the
storage network IP range.

```yaml
  vars:
    storage_network_range: 172.18.0.0/24
    all_addresses: ansible_all_ipv4_addresses # change if you need IPv6
  pre_tasks:
    - name: Build a dict mapping hostname to its IP which is in storage network range
      ansible.builtin.set_fact:
        host_to_ip: "{{ host_to_ip | default({}) | combine({ hostvars[item]['ansible_hostname'] :
          hostvars[item][all_addresses] | ansible.utils.ipaddr(storage_network_range) | first }) }}"
      loop: "{{ groups['edpm'] }}"
  roles:
    - role: cifmw_ceph_spec
      cifmw_ceph_spec_host_to_ip: "{{ host_to_ip }}"
      cifmw_ceph_spec_path: /tmp/ceph_spec.yml
```
After the Ansible above is run `/tmp/ceph_spec.yml` should look like
the following (the example below is frmo three EDPM nodes).

```yaml
---
addr: 172.18.0.100
hostname: edpm-compute-0
labels:
- _admin
- mgr
- mon
- osd
service_type: host
---
addr: 172.18.0.101
hostname: edpm-compute-1
labels:
- _admin
- mgr
- mon
- osd
service_type: host
---
addr: 172.18.0.102
hostname: edpm-compute-2
labels:
- _admin
- mgr
- mon
- osd
service_type: host
---
placement:
  hosts:
- edpm-compute-0
- edpm-compute-1
- edpm-compute-2
service_id: mon
service_name: mon
service_type: mon
---
placement:
  hosts:
- edpm-compute-0
- edpm-compute-1
- edpm-compute-2
service_id: mgr
service_name: mgr
service_type: mgr
---
data_devices:
  paths:
  - /dev/ceph_vg/ceph_lv_data
placement:
  hosts:
- edpm-compute-0
- edpm-compute-1
- edpm-compute-2
service_id: default_drive_group
service_name: osd.default_drive_group
service_type: osd
```

The spec file may then be passed as input to the `cifmw_cephadm` role.
