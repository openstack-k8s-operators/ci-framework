# Use the deployed infrastructure

In the [previous step](03_deploy_infra.md), we deployed the needed infrastructure for your
tests or developments.

It's now time to see what has been deployed, and how to properly use it.

## SSH accesses

From now on, you should be able to jump on the ansible controller:

```Bash
[laptop]$ ssh controller-0
```

~~~{tip}
No user nor key is needed - everything is configured in your ~/.ssh/config for an easy access.
~~~

## Controller-0

This host is the main entry for the infrastructure. It provides, by default, a series of repositories,
tools and generated files

### Repositories

By default, you will find those three repositories:

- `~/src/github.com/openstack-k8s-operators/architecture`
- `~/src/github.com/openstack-k8s-operators/ci-framework`
- `~/src/github.com/openstack-k8s-operators/install_yamls`

~~~{tip}
If you want to either get more, or override the default clone, you can pass the following parameter:
`cifmw_reproducer_repositories`. You can know more about it [here](../roles/reproducer.md#push-repositories).
~~~

### Ansible inventory

All the hosts are known to ansible via an inventory directory, `~/reproducer-inventory/`. So you can
pass this directory to any `ansible-playbook -i ~/reproducer-inventory [...]` in order to run any module
on any hosts. The inventory also provides the correct information about remote accesses, like the
`ansible_user` and `ansible_ssh_private_key_file`.

### Other generated contents

Depending on the use-case, there may be some other generated contents. We'll list them once we hit a scenario
involving them.

## Deployed content

Let's take a look at the deployed machines, networks and so on. The referenced resources are the default
at the current time - you can get the current list of deployed resources on your hypervisor directly.
Please check the [FAQ](./99_FAQ.md#how-can-i-see-the-deployed-libvirt-resources) for more details.

### Lightweight infrastructure

This layout, involving CRC, deploys (by default):

- `crc-0` CRC instance, providing the OpenShift services.
- `controller-0` the ansible controller.
- `compute-0`.

You may, of course, get more compute if you edited the layout.

In addition to this, it also creates 2 networks in libvirt:

- `public`, mimicking a public network, with DHCP and non-fixed IPs. It's the network your nodes will use to access external resources.
- `osp_trunk`, a private network used for network isolation.
