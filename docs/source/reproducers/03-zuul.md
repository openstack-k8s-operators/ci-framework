# Zuul job
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
of RAM and at least 24 CPUs. You can of course edit the specs,
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
`~/src/github.com/openstack-k8s-operators/ci-framework/SHORT_HASH_play.yml`, where SHORT_HASH
is the last hash of the `cifmw_job_uri` parameter. You should, as well, get the proper
inventory ready in the `scenarios/centos-9/zuul_inventory.yml` file, meaning you should
be able to run:
```Bash
$ ansible-playbook \
    -i scenarios/centos-9/zuul_inventory.yml \
    SHORT_HASH_play.yml
```
You will be able to follow the live state in `~/ansible.log`:
```Bash
$ tail -f ~/ansible.log
```

Note that `tmux` is installed by default, and may be handy in such a case ;).

## Cleaning the deployed job
Go in the ci-framework directory on your local computer and run:
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
