# Prepare your environment

## Tested environment

The following operating systems were successfully tested:

- Fedora Core 38, 39 (for laptop/desktop)
- CentOS Stream 9 (for the hypervisor, laptop/desktop)
- Red Hat Enterprise Linux 9.3 (for the hypervisor, laptop/desktop)

## On your laptop/desktop

There are a few needed dependencies to install before starting consuming the framework:

```Bash
[laptop]$ sudo dnf install -y git-core make
[laptop]$ git clone https://github.com/openstack-k8s-operators/ci-framework ci-framework
[laptop]$ cd ci-framework
[laptop]$ make setup_molecule
[laptop]$ source ~/test-python/bin/activate
```

## On the hypervisor

On the hypervisor, please ensure you have:

- a non-root user, with passwordless SSH access (use SSH keys)
- `sudo` configuration allowing that non-root user to run any random command, with or without password
- at least 400G of free space in /home
- an up-to-date CentOS Stream 9 or RHEL-9.3 system

Note: if you chose to require a password for `sudo`, please ensure to pass the `-K` option to any
`ansible-playbook` command running against the hypervisor.

### Virtual network consideration

For now, you have to manually destroy the `default` network provided by libvirt. This is mandatory, since
the same range is used by default for one of the deployed networks - and we can't have two virtual networks
consuming the same range.

In order to do so, please use:

```Bash
[hypervisor]$ sudo virsh net-destroy default
```

```{tip}
Later, we may not need to do this, if we can get rid of the hard-coded subnets currently consumed in the product.
```

### Multiple hypervisor

~~~{warning}
This feature isn't tested nor used by the CI Framework team.
~~~

In case you have multiple hypervisor, you may provide the following inventory

```{code-block} YAML
:caption: custom/inventory.yml
:linenos:
---
localhosts:
  hosts:
    localhost:
      ansible_connection: local

hypervisors:
  hosts:
    hypervisor-1:
      ansible_user: your_remote_user
      ansible_host: hypervisor-1.tld
      vxlan_local_ip: 10.10.1.11
      vxlan_remote_ip: 10.10.1.12
    hypervisor-2:
      ansible_user: your_remote_user
      ansible_host: hypervisor-2.tld
      vxlan_local_ip: 10.10.1.12
      vxlan_remote_ip: 10.10.1.11
```

As you can see, two custom parameters are passed via the inventory: `vxlan_remote_ip` and `vxlan_local_ip`.
Those are needed only if you're provisioning a VXLAN connection between your two hypervisors using `docs/source/files/bootstrap-vxlan.yml`.

## Bootstrap hypervisor

Since we're using non-root user with some specificities, you may want to get an automated way to provision the
hypervisor.

### Basics

The boostrap-hypervisor.yml will help you create the user, ensuring some
packages are present, as well as ensuring your user will be part of the needed group.

You can run the playbook like this:

```Bash
$ cd ci-framework
$ ansible-playbook -i custom/inventory.yml \
    -e ansible_user=root \
    -e cifmw_target_host=[hypervisor|hypervisors] \
    docs/source/files/bootstrap-hypervisor.yml
```

### VXLAN

After completing the initial bootstrap process, if you are deploying on two hypervisors, you can consume the 'bootstrap-vxlan.yml' playbook.

```Bash
$ cd ci-framework
$ ansible-playbook -i custom/inventory.yml \
  -e cifmw_target_host=hypervisors \
  docs/source/files/bootstrap-vxlan.yml
```
