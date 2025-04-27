# nat64_appliance

`main.yml`: Tasks to build a NAT64 + DNS64 appliance VM image, uses `diskimage-builder`.
`deploy.yml`: Tasks to deploy networks and appliance VM on a libvirt hypervisor.
`cleanup.yml`: Tasks to destroy and undefine the VM and networks on a libvirt hypervisor, and delete the built image.

## Parameters

* `cifmw_nat64_appliance_basedir`: (String) Base directory. Defaults to `{{ cifmw_basedir }}` which defaults to `~/ci-framework-data`.
* `cifmw_nat64_appliance_workdir`: (String) Working directory. Defaults to `{{ cifmw_nat64_appliance_basedir }}/nat64_appliance`.
* `cifmw_nat64_appliance_venv_dir`: (String) Python virtual environment directory. Defaults to `{{ cifmw_nat64_appliance_workdir }}/venv`.
* `cifmw_nat64_libvirt_uri`: (String) The libvirt URI for the hypervisor to deploy on. Defaults to `qemu:///system`.
* `cifmw_nat64_firewall_zone`: (String) The value for the firewalld `zone` attribute on the libvirt networks. Defaults to `libvirt`.
* `cifmw_nat64_network_ipv4_name`: (String) Name of the nat64 IPv4 libvirt network. Defaults to: `nat64-net-v4`.
* `cifmw_nat64_network_ipv4_bridge_name`: (String) Bridge name for the nat64 IPv4 libvirt network. Defaults to: `br-64v4`.
* `cifmw_nat64_network_ipv4_address`: (String) IP address for the nat64 IPv4 libvirt network. Defaults to: `172.31.255.1`.
* `cifmw_nat64_network_ipv4_prefix`: (Integer) IP prefix length for the nat64 IPv4 libvirt network. Defaults to: `24`.
* `cifmw_nat64_network_ipv6_name`: (String) Name of the nat64 IPv6 libvirt network. Defaults to: `nat64-net-v6`.
* `cifmw_nat64_network_ipv6_bridge_name`: (String) The bridge name for the nat64 IPv6 libvirt network. Defaults to: `br-64v6`.
* `cifmw_nat64_network_ipv6_address`: (String) IP address for the nat64 IPv6 libvirt network. Defaults to: `fc00:abcd:abcd:fc00::1`.
* `cifmw_nat64_network_ipv6_prefix`: (Integer) IP prefix length for the nat64 IPv6 libvirt network. Defaults to: `64`.
* `cifmw_nat64_appliance_name`: (String) Name and hostname for the nat64 appliance VM. Defaults to: `nat64-appliance`.
* `cifmw_nat64_appliance_ipv4_address`: (String) IPv4 address for the nat64 appliance VM. Defaults to: `172.31.255.2`.
* `cifmw_nat64_appliance_ipv6_address`: (String) IPv6 address for the nat64 appliance VM. Defaults to: `fc00:abcd:abcd:fc00::2`.
* `cifmw_nat64_appliance_memory`: (Integer) Memory in GiB for the nat64 appliance VM. Defaults to: `2`.
* `cifmw_nat64_appliance_cpus`: (Integer) Virtual CPUs for the nat64 appliance VM. Defaults to: `2`.
* `cifmw_nat64_appliance_ssh_pub_keys`: (List) List of SSH public key for the nat64 appliance VM. Defaults to: `[]`.
* `cifmw_nat64_ipv6_prefix`: (String) IPv6 prefix for nat64. Defaults to: `fc00:abcd:abcd:fc00::/64`.
* `cifmw_nat64_ipv6_tayga_address`: (String) Tayga IPv6 address. Defaults to: `fc00:abcd:abcd:fc00::3`.

## Building the image

Include the `nat64_appliance` role in a playbook. For example:

```
- name: Build nat64-appliance
  hosts: "{{ cifmw_target_host | default('localhost') }}"
  roles:
    - nat64_appliance
```

The built image will be in: `{{ cifmw_nat64_appliance_workdir }}/nat64-appliance.qcow2`

## Using the nat64-appliance

- [With Libvirt](#with-libvirt){#toc-with-libvirt}
- [With Openstack cloud](#with-openstack-cloud){#toc-with-openstack-cloud}

### With Libvirt

```
- name: "Build nat64 appliance image"
  ansible.builtin.include_role:
    name: nat64_appliance
- name: "Deploy the nat64 appliance and networks"
  ansible.builtin.include_role:
    name: nat64_appliance
    tasks_from: deploy.yml
```

To cleanup the libvirt nat64 deployment:
```
- name: "Build nat64 appliance image"
  ansible.builtin.include_role:
    name: nat64_appliance
    tasks_from: cleanup.yml
```


### With Openstack cloud

The nat64-appliance can be combined with standard openstack constructs
such as networks and routers to provide NAT64 for one or more IPv6
tenant networks.

The following is an example topology, where the `private`
network and the `private-router` is the typical IPv4 openstack tenant
network setup with `provider` as the external gateway network.
`nat64-network` is the openstack IPv6 tenant network attaching to the
`nat64-appliance` openstack instance. The `nat64-appliance` instance is
also connected to the `private` network (IPv4) for IPv4 connectivity. An
openstack router attached to the `nat64-network` IPv6 network
(`nat64-router`), this router is configured with a default route using
the `nat64-appliance`'s IPv6 address as the `next-hop`.

With this topology in place, users can create individual IPv6 networks
and attach to the `nat64-router` openstack router to get external
network access via the NAT64 gateway. Like the `my-ipv6-network` in the
example.

> \[!NOTE\] The `nat64-appliance`'s IPv6 address must be configured as
> the DNS server since this is providing the DNS64 service.


#### Create (upload) the image to the openstack cloud

``` bash
openstack image create --disk-format qcow2 --file nat64-appliance.qcow2 nat64-appliance
```

#### Create private IPv6 network in openstack cloud

``` bash
openstack network create nat64-network
openstack subnet create nat64-subnet \
  --network nat64-network \
  --ip-version 6 \
  --no-dhcp \
  --subnet-range fc00:abcd:abcd:fc00::/64 \
  --gateway fc00:abcd:abcd:fc00::1
```

#### Create security group

``` bash
openstack security group create sg_nat64 --description "Security group for NAT64 router appliance"
openstack security group rule create --protocol icmp sg_nat64

openstack security group rule create sg_nat64 --protocol tcp --dst-port 22:22 --ethertype IPv4
```

#### Create ports for NAT64 instance

``` bash
openstack port create nat64-appliance-ipv4 \
  --network private \
  --security-group sg_nat64
openstack port create nat64-appliance-ipv6 \
  --network nat64-network \
  --disable-port-security \
  --fixed-ip subnet=nat64-subnet,ip-address=fc00:abcd:abcd:fc00::2
openstack port create nat64-appliance-ipv6-tayga \
  --description "NAT64 Tayga TAP interface IP address allocation. (Port is not bound/attached to instance)" \
  --network nat64-network \
  --disable-port-security \
  --fixed-ip subnet=nat64-subnet,ip-address=fc00:abcd:abcd:fc00::3
```

#### Create router in the openstack cloud

``` bash
openstack router create nat64-router
```

#### Attach nat64-subnet to the router in the openstack cloud

``` bash
openstack router add subnet nat64-router nat64-subnet
```

#### Set up nat64-router default route via nat64-appliance instance

``` bash
openstack router add route nat64-router \
  --route destination="::/0",gateway="$(openstack port show nat64-appliance-ipv6 -f json -c fixed_ips | jq -r .fixed_ips[0].ip_address)"
```

#### Create instance in openstack cloud

##### Create instance user_data file

``` bash
cat << EOF > nat64_user_data.txt
#cloud-config
write_files:
  - path: /etc/nat64/config-data
    owner: root:root
    content: |
      NAT64_IPV6_PREFIX=$(openstack subnet show nat64-subnet -c cidr -f value)
      NAT64_HOST_IPV6=$(openstack port show nat64-appliance-ipv6 -f json -c fixed_ips | jq -r .fixed_ips[0].ip_address)/64
      NAT64_TAYGA_IPV6=$(openstack port show nat64-appliance-ipv6-tayga -f json -c fixed_ips | jq -r .fixed_ips[0].ip_address)
EOF
```

> \[!NOTE\] Optional user_data configurations, and their default
> values. - `NAT64_TAYGA_IPV6_PREFIX=fc00:abcd:abcd:fcff::/96` -
> `NAT64_TAYGA_DYNAMIC_POOL=192.168.255.0/24` -
> `NAT64_TAYGA_IPV4=192.168.255.1`

##### Create the nat64-appliance instance

``` bash
openstack server create \
  --flavor m1.small \
  --image nat64-appliance \
  --port nat64-appliance-ipv4 \
  --port nat64-appliance-ipv6 \
  --key-name default \
  --user-data nat64_user_data.txt \
  nat64-appliance

# (Optional) Add a floating IP - for troubleshooting or using the instance as a jump host.
openstack server add floating ip \
  --fixed-ip-address $(openstack port show nat64-appliance-ipv4 -f json -c fixed_ips | jq -r .fixed_ips[0].ip_address) \
  nat64-appliance \
  192.168.254.161
```

#### Additional IPv6 networks with external access via nat64-appliance

With the nat64-appliance and openstack router (nat64-router) up and
running, additional IPv6 networks can be created in the openstack cloud.
Attach these networks to the nat64-router to get external access. For
example:

``` bash
openstack network create my-ipv6-network
openstack subnet create my-ipv6-subnet \
  --network my-ipv6-network \
  --ip-version 6 \
  --no-dhcp \
  --subnet-range fc00:abcd:aaaa:fc00::/64 \
  --dns-nameserver "$(openstack port show nat64-appliance-ipv6 -f json -c fixed_ips | jq -r .fixed_ips[0].ip_address)"
openstack router add subnet nat64-router my-ipv6-subnet
openstack server create test-ipv6-only \
  --image Fedora-Cloud-Base-39 \
  --network my-ipv6-network \
  --key-name default \
  --flavor m1.small \
  --config-drive True
```

Create a jump host to SSH to the test-ipv6-only instance:

``` bash
$ openstack server create my-ipv6-network-jump-host \
  --network private \
  --network my-ipv6-network \
  --image Fedora-Cloud-Base-39 \
  --key-name default \
  --flavor m1.small
$ openstack server show my-ipv6-network-jump-host -c addresses
+-----------+------------------------------------------------------------------+
| Field     | Value                                                            |
+-----------+------------------------------------------------------------------+
| addresses | my-ipv6-network=fc00:abcd:aaaa:fc00::38; private=192.168.253.139 |
+-----------+------------------------------------------------------------------+
$ openstack floating ip create provider
+---------------------+-----------------+
| Field               | Value           |
+---------------------+-----------------+
| floating_ip_address | 192.168.254.164 |
+---------------------+-----------------+
$ openstack server add floating ip my-ipv6-network-jump-host --fixed-ip-address 192.168.253.139 192.168.254.164
$ openstack server show test-ipv6-only -c addresses
+-----------+------------------------------------------+
| Field     | Value                                    |
+-----------+------------------------------------------+
| addresses | my-ipv6-network=fc00:abcd:aaaa:fc00::2b8 |
+-----------+------------------------------------------+
$ ssh -J fedora@192.168.254.164 fedora@fc00:abcd:aaaa:fc00::2b8
[fedora@test-ipv6-only ~]$ ip addr show eth0
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1442 qdisc fq_codel state UP group default qlen 1000
    link/ether fa:16:3e:8a:c1:af brd ff:ff:ff:ff:ff:ff
    altname enp0s3
    altname ens3
    inet6 fc00:abcd:aaaa:fc00::2b8/64 scope global noprefixroute
       valid_lft forever preferred_lft forever
    inet6 fe80::f816:3eff:fe8a:c1af/64 scope link noprefixroute
       valid_lft forever preferred_lft forever
[fedora@test-ipv6-only ~]$ ping sunet.se
PING sunet.se(fc00:abcd:abcd:fcff::259c:c033 (fc00:abcd:abcd:fcff::259c:c033)) 56 data bytes
64 bytes from fc00:abcd:abcd:fcff::259c:c033 (fc00:abcd:abcd:fcff::259c:c033): icmp_seq=1 ttl=53 time=4.91 ms
```
