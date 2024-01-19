# Zuul job

~~~{warning}
This feature is currently broken. The ci-framework is slightly ahead of
actual job definitions and we need to change them to provide the needed
bits again.
~~~

~~~{tip}
It is strongly advised to run this reproducer against a dedicated hypervisor
with enough resources. The current configuration will require close to 40G
of RAM and at least 24 CPUs. You can of course edit the specs,
but keep in mind *CRC* has its own needs.
[Please refer to its minimal spec](https://crc.dev/crc/getting_started/getting_started/installing/#_for_openshift_container_platform).
~~~

## How does it work (high level explanation)
It will fetch a few files from the Zuul job output, read and combine them
in order to update the layout to a matching size (especially, setting the
right amount of computes), create the virtual machines, configure them,
get the code tested in the job, and run the same playbook as the job itself.

### Content provider case
If the reproducer detects the presence of a content-provider dependency, it will
reproduce that part, using the ansible controller as the content-provider.
The reproducer will then clone all of the needed repositories, and build
the intended operators and store them in a local registry. That registry
will be accessible from the private network interface.

## How do I run that job?
### First, get the project, and get its dependencies installed
```Bash
[laptop]$ git clone https://github.com/openstack-k8s-operators/ci-framework
[laptop]$ cd ci-framework
[laptop]$ make setup_molecule
```
### Create an inventory file in order to consume your hypervisor
You can create a file in `custom/inventor.yml` for instance (ensure you ignore
that path from git tree in order to NOT inject that custom inventory).

The file should look like this:
~~~{code-block} YAML
:caption: custom/inventory.yml
:linenos:
---
all:
  hosts:
    localhost:
      ansible_connection: local
    hypervisor-1:
      ansible_user: my_remote_user
      ansible_host: hypervisor.localnet
~~~

~~~{tip}
Note the "localhost" host with the "local" connection - it will be used for some
data, avoiding the network overhead will be faster
~~~

~~~{warning}
Please ensure your hypervisor provides `sudo` for the user you intend to use,
with or without password. It must, of course, support virtualization.
~~~

### Create a custom environment file to feed your job

This file is mandatory. It will let the Framework know about your job as well as the
needed secret to deploy CRC.

~~~{code-block} YAML
:caption: custom/my-job.yml
:linenos:
cifmw_job_uri: "URI_TO_JOB_OUTPUT"
cifmw_manage_secrets_pullsecret_file: "{{ lookup('env', 'HOME') }}/pull-secret.txt"
~~~

#### cifmw_job_uri
This is the magic parameter: by setting it, you'll instruct the reproducer to switch into
"reproducer job mode". This URI is the one you can find on a Zuul job output, and usually
looks like this:

https://logserver.rdoproject.org/74/574/LONG_HASH/github-check/podified-multinode-edpm-e2e-nobuild-tagged-crc/SHORT_HASH/

Please take extra care to ensure it's NOT pointing to any sub-directory of that page, such
as "/controller" - else, it will fail to fetch the needed pieces.


### Inject your custom code
As an option, you're able to inject your custom code by leveraging the
`cifmw_reproducer_repositories` parameter as described in the
[reproducer](../roles/reproducer.md) role examples.

For instance, if you're trying to re-run a job against `nova-operators` repository,
you can override the job code in order to inject your local code and see if it
fixes the job:

~~~{code-block} YAML
:caption: custom/repo-overrides.yml
:linenos:
---
local_home_dir: "{{ lookup('env', 'HOME') }}"
local_base_dir: "{{ local_home_dir }}/src/github.com/openstack-k8s-operators"
remote_base_dir: "/home/zuul/src/github.com/openstack-k8s-operators"
cifmw_reproducer_repositories:
  - src: "{{ local_base_dir }}/nova-operator"
    dest: "{{ remote_base_dir }}/nova-operator"
~~~

Provided you have the right code branch set in your local repository, the reproducer
will then copy it 1:1 and override the Zuul content.

### Reproduce the job
Running this simple ansible-playbook command will deploy everything and run
the job:
```Bash
[laptop]$ ansible-playbook -i custom/inventory.yml \
    reproducer.yml \
    -e cifmw_target_host=hypervisor-1 \
    -e @scenarios/reproducers/3-nodes.yml \
    -e @custom/my-job.yml [-e @custom/repo-overrides.yml]
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
an easy access to the nodes: `ssh controller-0`, `ssh crc-0`, `ssh compute-0` and
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
inventory ready in the `~/ci-framework-data/artifacts/zuul_inventory.yml` file, meaning you should
be able to run:
```Bash
[controller-0]$ ansible-playbook \
    -i ~/ci-framework-data/artifacts/zuul_inventory.yml \
    SHORT_HASH_play.yml
```
You will be able to follow the live state in `~/ansible.log`:
```Bash
[controller-0]$ tail -f ~/ansible.log
```

Note that `tmux` is installed by default, and may be handy in such a case ;).

#### Zuul_inventory.yml
That file is a generated inventory, allowing ansible to know about the compute(s) and CRC nodes.

It exposes each node with the connection information (user and IP), and also created groups in
order to access, for instance, all of the computes. Those groups mimic the same behaviour we
have in Zuul.

### Ansible tags of interest
You may want to re-run some parts of the reproducer only, and avoid re-running the whole
virtual machine creation by using `--skip-tags TAG`.

In order to do so, the reproducer exposes two tags:
* bootstrap_layout
* bootstrap_repositories
* bootstrap

#### Tag: boostrap_repositories
This covers only the repositories bootstrap step of the reproducer. This is probably one
of the most useful tag when you want to iterate on a change on an already deployed layout.

Note: you **must** have an already deployed layout before running only this tag.

##### Usage
```Bash
# Reproduce first iteration of your PR that failed on Zuul
[laptop]$ ansible-playbook -i custom/inventory.yml reproducer.yml \
    -e cifmw_target_host=hypervisor-1 \
    -e @scenarios/reproducers/3-nodes.yml \
    -e @custom/my-job.yml

# Iterate with the second iteration of your PR that failed on Zuul
[laptop]$ ansible-playbook -i custom/inventory.yml reproducer.yml \
    -e cifmw_target_host=hypervisor-1 \
    -e @scenarios/reproducers/3-nodes.yml \
    -e @custom/my-job.yml \
    --tags bootstrap_repositories
```

#### Tag: bootstrap_layout
This covers everything related to "create and manage virtual machines". This is probably the
most useful tag to skip once you want to iterate on a deployed layout, since it will
ensure repositories are up-to-date, but also re-generate the needed bits to run the CI job.

Note: you **must** have an already deployed layout before skipping this tag.

##### Usage
```Bash
# Reproduce first iteration of your PR that failed on Zuul
[laptop]$ ansible-playbook -i custom/inventory.yml reproducer.yml \
    -e cifmw_target_host=hypervisor-1 \
    -e @scenarios/reproducers/3-nodes.yml \
    -e @custom/my-job.yml

# Iterate with the second iteration of your PR that failed on Zuul
[laptop]$ ansible-playbook -i custom/inventory.yml reproducer.yml \
    -e cifmw_target_host=hypervisor-1 \
    -e @scenarios/reproducers/3-nodes.yml \
    -e @custom/my-job.yml \
    --skip-tags bootstrap_layout
```

#### Tag: bootstrap
This covers everything from the creation of the virtual layout (networks and machines) to
the push of generated plays. With that, you'll only get the repositories, and some of the
zuul data, mostly.

Skip with caution, since it may end with a broken environment, where some files may miss
an update, for instance the playbook running the job in case you wanted to just update
the repository against a newer patch set.

~~~{warning}
You **must** have an already deployed layout before skipping that tag. But we strongly
recommend *against* skipping it due to the lack of data regeneration.
~~~

##### Usage
```Bash
# Reproduce first iteration of your PR that failed on Zuul
[laptop]$ ansible-playbook -i custom/inventory.yml reproducer.yml \
    -e cifmw_target_host=hypervisor-1 \
    -e @scenarios/reproducers/3-nodes.yml \
    -e @custom/my-job.yml

# Iterate with the second iteration of your PR that failed on Zuul
[laptop]$ ansible-playbook -i custom/inventory.yml reproducer.yml \
    -e cifmw_target_host=hypervisor-1 \
    -e @scenarios/reproducers/3-nodes.yml \
    -e @custom/my-job.yml \
    --skip-tags bootstrap_layout,bootstrap
```

## Cleaning the deployed job
Go in the ci-framework directory on your local computer and run:
```Bash
[laptop]$ ansible-playbook \
    -i custom/inventory.yml \
    -e cifmw_target_host=hypervisor-1 \
    reproducer-clean.yml
```

This will destroy the whole environment:
- stop the VMs
- undefine them
- remove their disk images
- clean all of the generated content on the hypervisor

~~~{warning}
This action is irreversible, therefore please be sure you save
whatever you need before running that command.
~~~

~~~{tip}
Learn more about cleanup [here](../quickstart/05_clean_infra.md)
~~~
