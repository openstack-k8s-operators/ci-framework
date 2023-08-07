# Reproduce CI layout
The CI Framework allows to reproduce the same layout we're consuming in CI.

While it's not that different from the install_yamls standard layout (one CRC,
one Compute), the CI layout introduces a third node (ansible controller), and
all of the nodes have two network interfaces.

## Tested environment
This reproducer has been successfully tested on a CentOS Stream 9 hypervisor
running latest CRC qcow2, and latest CentOS Stream 9 qcow2 images.

It *may* work on RHEL based hypervisor and VMs, provided you give the correct
information for the [discover_latest_image](../roles/discover_latest_image.md)
role/plugin, or download beforehand the images and consume them from within the
configuration, but it **wasn't tested** (yet).

## The playbooks
You will find `reproducer.yml` playbook at the root of the project, as well as
a specific `scenarios/reproducers` directory.

A second playbook, `reproducer-clean.yml`, allows to remove the created
resources. Please keep in mind it's destructive, and you won't be able to
recover anything after the run: virtual machines are destroyed and undefined,
and the image layers are removed.

## Prerequisites
### CRC
The CRC VM has to be properly set up prior running the reproducer play. You
may get to that leveraging wither the rhol_crc role from the CI Framework, or
manually by calling `crc setup && crc start -p pull-secret`.

Once the CRC VM is properly started, you can then stop it and undefine it as
follow:
```Bash
$ virsh -c qemu:///system destroy crc
$ virsh -c qemu:///system undefine crc
```

Since most of the ranges are hard-coded for now, please ensure no network is
pre-existing:
```Bash
$ virsh -c qemu:///system net-list --all
$ virsh -c qemu:///system net-destroy <NETWORK>
$ virsh -c qemu:///system net-undefine <NETWORK>
```

You then have to ensure you have the following content on the target hypervisor:
- ~/.crc/machine/crc/crc.qcow2
- ~/.crc/machine/crc/id_*
- ~/.crc/machine/crc/kubeconfig

### Ssh authorized_keys
On the target hypervisor, you have to ensure the ~/.ssh/authorized_keys has all
of the needed public keys. It will then be copied in the various virtual machines
the reproducer will create.

## Needed parameters
While we provide the "simple" layout, consuming three nodes, you may want
to provide your own layout, maybe with more compute, or some other kind of
node.

In any cases, the following data are the bare minimal:

- `cifmw_path`: you can take the same value as in the provided file, or extend it as needed
- `cifmw_libvirt_manager_configuration`: this dict is mandatory in order to create the layout.

In the `cifmw_libvirt_manager_configuration`, there are also some conventions
and mandatory content/information.

In the `vms` section, please ensure you have at least "controller" and "crc".
Those names are fixed and used later as static reference.

In the `networks` section, you can define your own custom networks. Usually,
you can take the same values we provide in the existing layout.

Note that, if you just want to get more compute, you can play with the `amount`
value. It will then create `compute-[0..n]` virtual machines.

### Extra parameter: cifmw_reproducer_repositories

This parameter allows you to pass a list of repositories you want to sync from
your local laptop onto the ansible controller machine. The form is pretty easy:
```YAML
cifmw_reproducer_repositories:
  - src: "{{ playbook_dir }}"
    dest: "src/github.com/openstack-k8s-operators/"
  - src: "{{ cifmw_install_yamls_repo }}"
    dest: "src/github.com/openstack-k8s-operators/"
```
This one will ensure you have ci_framework as well as install_yamls in a
known location on the virtual machine. The dest path matches the one we usually
get in CI.

## Inventory
This feature can be launched against your own desktop or laptop, but also
against a remote hypervisor (preferred due to resources). You can therefore
create your own inventory as follow:
```YAML
---
# inventory_hypervisor.yml
all:
  hosts:
    hypervisor:
     ansible_user: your_remote_user
     [any other ansible connection options]
```

## Usage
Once the layout matches your needs, you just need to run the following:
```Bash
$ ansible-playbook -K -i inventory_hypervisor.yml \
    reproducer.yml \
    -e cifmw_target_host=hypervisor \
    -e @scenarios/reproducers/3-nodes.yml
```
Note: the `-K` option instructs ansible to request `sudo` password. This is
needed in case you don't have the `NOPASSWD` option in the sudoers. Of course,
if you're using root as the remote user, you won't need that option either.

### Deploy succeeds, what's next?
Once the deploy is over, you will end with ready-to-use virtual machines,
provided you passed the needed repositories to sync.

The reproducers injects proper ssh configuration in order to jump on the nodes
using their name. Usually, you'll just need to reach to the "controller":
```Bash
$ ssh controller-0
```
You'll end on the machine, using "zuul" user. Then, you're all set to run the
framework, like we [do in the CI](https://github.com/openstack-k8s-operators/ci-framework/tree/main/ci/playbooks).

## Cleaning
In order to clean the deployed layout, you can just call the `reproducer-clean.yml`
playbook. It will clean the virtual machines:
```Bash
$ ansible-playbook -i inventory_hypervisor.yml reproducer-clean.yml
```
It doesn't require any environment file since it will list all of the existing
virtual machines, and clean the ones which name starts with `cifmw-`.
It will also remove the disk images - so if you did set a custom basedir in the
deployment, you would need to pass it down accordingly.

## Expected layout with the default 3-nodes.yml environment
The provided file should create the following resources on your environment:
```Bash
$ virsh net-list --all
 Name            State    Autostart   Persistent
--------------------------------------------------
 cifmw-default   active   no          yes
 cifmw-public    active   no          yes

$ virsh list --all
 Id   Name                 State
------------------------------------
 4    cifmw-compute-0      running
 5    cifmw-controller-0   running
 6    cifmw-crc-0          running
```
The "Id" value may change.
