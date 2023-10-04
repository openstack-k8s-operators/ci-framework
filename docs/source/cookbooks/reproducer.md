# Reproduce a Zuul job
## Words of warning
This feature is still fresh, and limited. For now, you can reproduce only
a job that doesn't rely on the content-provider job.

It also has to run against the latest PR content output, since you won't
have access to the actual commit hash on github.

For now, it has been tested only against
*podified-multinode-edpm-e2e-nobuild-tagged-crc* job.

## Words of advice
It is strongly advised to run this reproducer against a dedicated hypervisor
with enough resources. The current configuration will require close to 40G
of RAM and a fair amount of CPU (over 24). You can of course edit the specs,
but keep in mind *CRC* has its own needs.
 [Please refer to its minimal spec](https://crc.dev/crc/getting_started/getting_started/installing/#_for_openshift_container_platform).

## How does it work (high level explanation)
It will fetch a few files from the Zuul job output, read and combine them
in order to update the layout to a matching size (especially, setting the
right amount of computes), create the virtual machines, configure them,
get the code tested in the job, and run the same playbook as the job itself.

## How do I run that job?
### First, get the project, and get its dependencies installed
```Bash
$ git clone https://github.com/openstack-k8s-operators/ci-framework
$ cd ci-framework
$ make setup_molecule
```
### Create an inventory file in order to consume your hypervisor
You can create a file in `custom/inventor.yml` for instance (ensure you ignore
that path from git tree in order to NOT inject that custom inventory).

The file should look like this:
```YAML
all:
  hosts:
    localhost:
      ansible_connection: local
    builder1:
      ansible_user: virtuser
      ansible_host: 192.168.1.10
```
(Note the "localhost" host with the "local" connection - it will be used for some
data, avoiding the network overhead will be faster)

Please ensure your hypervisor provides `sudo` for the user you intend to use,
with or without password. It must, of course, support virtualization.

### Reproduce the job
Running this simple ansible-playbook command will deploy everything and run
the job:
```Bash
$ ansible-playbook -i custom/inventory.yml \
    reproducer.yml \
    -e cifmw_target_host=builder1 \
    -e @scenarios/reproducers/3-nodes.yml \
    -e cifmw_job_uri="URI_TO_JOB_OUTPUT" \
    -K
```
#### What does it do?!
##### reproducer.yml
This is the main playbook. It will call a series of roles ensuring libvirt and
its dependencies are present. Virtual networks and machines will be created and
properly configured. Then some more tasks will happen in order to fetch some of
the job generated output, so that the job can be properly reproduced.

##### cifmw_target_host
That parameter instructs the playbook to consume your hypervisor. If you don't set
that parameter, it will run against *localhost*. You probably don't want that.

##### @scenarios/reproducers/3-nodes.yml
That file describe a 3-nodes layout. While it's not mandatory to pass it, it will
make things easier to understand and parse. You can have a look into it, and if
you see some of the resources are a bit too high for your env, you can then duplicate
that file in the `custom` directory described earlier with your own resources.

Note that the reproducer will update the amount of computes. You therefore don't need
to change it.

##### cifmw_job_uri
This is the magic parameter: by setting it, you'll instruct the reproducer to switch into
"reproducer job mode". This URI is the one you can find on a Zuul job output, and usually
looks like this:

https://logserver.rdoproject.org/74/574/LONG_HASH/github-check/podified-multinode-edpm-e2e-nobuild-tagged-crc/SHORT_HASH/

Please take extra care to ensure it's NOT pointing to any sub-directory of that page, such
as "/controller" - else, it will fail to fetch the needed pieces.

#### Generated files
There will be a fair amount of generated files, as you may expect. As usual, most of them
are nested in the `~/ci-framework-data` directory.

On your local host (ansible controller), you will find `~/ci-framework-data/ci-reproducer`
containing a series of directories. Those directories are generated using the last
hash in the job URL. It will contain the fetched files from zuul, namely its inventory,
and the generated parameters nested in the job `ci-framework/artifacts/parameters`
directory.

On the hypervisor, you'll find the same `~/ci-framework` base directory. Inside it,
the virtual machine base image will be under the "images" directory, while the layers
will be in the "workload" one. The reproducer data, such as generated inventory and
network data, will be there as well. Those will be pushed onto the controller-0
instance.

#### Access to the virtual machines
Your local ssh configuration file will be modified by the reproducer in order to offer
an easy access to the nodes: `ssh controller-0`, `ssh core@crc-0`, `ssh compute-0` and
so on will work right out of the box.

### Specific parameters
* `cifmw_reproducer_run_job`: (Bool) Run the actual CI job. Defaults to `true`. If set
to `false` you'll end with a ready-to-use environment, just before the actual job starts.
* `cifmw_reproducer_params`: (Dict) Specific parameters you want to pass to the reproducer.
Defaults to `{}`.

You can refer to the [README](../roles/reproducer.md) nested in the role for more information.

### Running the deploy manually
The reproducer will generate a playbook mimicking the CI job itself. You can find it under
`~/src/github.com/openstack-k8s-operators/ci-framework/JOB_ID_play.yml`, where JOB_ID is
the last hash of the `cifmw_job_uri` parameter. You should, as well, get the proper
inventory ready in the `scenarios/centos-9/zuul_inventory.yml` file, meaning you should
be able to run:
```Bash
$ ansible-playbook \
    -i scenarios/centos-9/zuul_inventory.yml \
    JOB_ID_play.yml
```
You will be able to follow the live state in `~/ansible.log`:
```Bash
$ tail -f ~/ansible.log
```

Note that `tmux` is installed by default, and may be handy in such a case ;).

### Cleaning the deployed job
Just run the following to clean things up:
```Bash
$ ansible-playbook \
    -i custom/inventory.yml \
    -e cifmw_target_host=builder1 \
    reproducer-clean.yml
```
This will destroy the whole environment:
- stop the VMs
- undefine them
- remove their disk images
- clean all of the generated content on the hypervisor

Note that this action is irreversible, therefore please be sure you save
whatever you need before running that command.

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
