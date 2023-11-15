# Prepare your environment

## Tested environment

The following operating systems were successfully tested:

- Fedora Core 38, 39 (for laptop/desktop)
- CentOS Stream 9 (for the hypervisor, laptop/desktop)
- Red Hat Enterprise Linux 9.2 (for the hypervisor, laptop/desktop)

## On your laptop/desktop

There are a few needed dependencies to install before starting consuming the framework:

```Bash
$ sudo dnf install -y git-core make
$ git clone https://github.com/openstack-k8s-operators/ci-framework ci-framework
$ cd ci-framework
$ make setup_molecule
$ source ~/test-python/bin/activate
```

## On the hypervisor

On the hypervisor, please ensure you have:

- a non-root user, with passwordless SSH access (use SSH keys)
- `sudo` configuration allowing that non-root user to run any random command, with or without password
- at least 400G of free space in /home
- an up-to-date CentOS Stream 9 or RHEL-9.2 system

Note: if you chose to require a password for `sudo`, please ensure to pass the `-K` option to any
`ansible-playbook` command running against the hypervisor.


### Virtual network consideration

For now, you have to manually destroy the `default` network provided by libvirt. This is mandatory, since
the same range is used by default for one of the deployed networks - and we can't have two virtual networks
consuming the same range.

In order to do so, please use one of those two commands:
```Bash
$ sudo virsh net-destroy default
$ virsh -c qemu:///system net-destroy default
```

Later, we may not need to do this, if we can get rid of the hard-coded subnets currently consumed in the product.
