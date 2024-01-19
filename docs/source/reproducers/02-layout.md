# Reproduce CI layout
The CI Framework allows to reproduce the same layout we're consuming in CI.

While it's not that different from the install_yamls standard layout (one CRC,
one Compute), the CI layout introduces a third node (ansible controller), and
all of the nodes have two network interfaces.

## The playbooks
You will find `reproducer.yml` playbook at the root of the project, as well as
a specific `scenarios/reproducers` directory.

A second playbook, `reproducer-clean.yml`, allows to remove the created
resources. Please keep in mind it's destructive, and you won't be able to
recover anything after the run: virtual machines are destroyed and undefined,
and the image layers are removed.

### Extra parameter: cifmw_reproducer_repositories

This parameter allows you to pass a list of repositories you want to sync from
your local laptop onto the ansible controller machine. The form is pretty easy:
~~~{code-block} YAML
:caption: custom/repositories.yml
:linenos:
---
cifmw_reproducer_repositories:
  - src: "{{ playbook_dir }}"
    dest: "src/github.com/openstack-k8s-operators/"
  - src: "{{ cifmw_install_yamls_repo }}"
    dest: "src/github.com/openstack-k8s-operators/"
~~~

This one will ensure you have ci_framework as well as install_yamls in a
known location on the virtual machine. The dest path matches the one we usually
get in CI.

## Inventory
This feature can be launched against your own desktop or laptop, but also
against a remote hypervisor (preferred due to resources). You can therefore
create your own inventory as follows:
~~~{code-block} YAML
:caption: custom/inventory.yml
:linenos:
---
all:
  hosts:
    hypervisor:
     ansible_user: your_remote_user
     [any other ansible connection options]
~~~

## Deploy the layout
Once the layout matches your needs, you just need to run the following:
```Bash
[laptop]$ ansible-playbook -i custom/inventory.yml \
    reproducer.yml \
    -e cifmw_target_host=hypervisor \
    -e @scenarios/reproducers/networking-definition.yml \
    -e @scenarios/reproducers/3-nodes.yml \
    -e @custom/private-params.yml [-e @custom/repositories.yml]
```

### Deploy succeeds, what's next?
Once the deploy is over, you will end with ready-to-use virtual machines,
provided you passed the needed repositories to sync.

The reproducer injects proper ssh configuration in order to jump on the nodes
using their name. Usually, you'll just need to reach to the "controller":

```Bash
[laptop]$ ssh controller-0
```

You'll end on the machine, using "zuul" user. Then, you're all set to run the
framework, like we [do in the CI](https://github.com/openstack-k8s-operators/ci-framework/tree/main/ci/playbooks).

## Cleaning

In order to clean the deployed layout, you can just call the `reproducer-clean.yml`
playbook. It will clean the virtual machines:

```Bash
[laptop]$ ansible-playbook -i custom/inventory.yml reproducer-clean.yml
```
It doesn't require any environment file since it will list all of the existing
virtual machines, and clean the ones which name starts with `cifmw-`.
It will also remove the disk images - so if you did set a custom basedir in the
deployment, you would need to pass it down accordingly.

## Expected layout with the default 3-nodes.yml environment
The provided file should create the following resources on your environment:
```Bash
[hypervisor]$ virsh net-list --all
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
