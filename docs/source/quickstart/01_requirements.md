# System requirements

You usually want to run against a remote hypervisor in order to get a working infrastructure.

## Lightweight deployment

Such a deployment usually involves [CRC](https://crc.dev/crc/getting_started/getting_started/introducing/),
an ansible controller, and one or more compute node(s).

Minimal resources are:

- 32GB RAM
- 200G of free storage (in /home)
- 16 CPUs

### Detail

CRC instance usually needs 24G of RAM, and around 100G of disk space. The ansible controller node
can run with 2 or 4G of ram, and needs around 15G of disk space. The rest is at discretion for
the compute nodes, and would depends on your actual workload (if you intend to run tests and so on).

### Time to deploy

It of course depends on the hypervisor. Running on a dedicated, remote server, gets these kind of timings:

- Deploy from scratch the lightweight layout: ~30 minutes
- Re-deploy the lightweight layout: ~10 minutes

## Validated Architecture

The Validated Architecture involves more resources, since it requires a 3-node
[OCP](https://www.redhat.com/en/technologies/cloud-computing/openshift/container-platform) cluster,
at least three compute nodes, and the ansible controller.

Minimal requirements are:

- 64GB of RAM
- 400G of free storage (in /home)
- 24 CPUs

### Details

OCP nodes require at least 16G of RAM and 100G of disk space.

### Time to deploy

It of course depends on the hypervisor. Running on a dedicated, remote server, gets these kind of timings:

- Deploy from scratch the VA layout: ~1 hour
- Re-deploy the VA layout: ~10 minutes

# Needed packages
In order to be able to start consuming the Framework, the following packages
must be present on your system:

* git
* make
* python3-pip
* sudo

# Needed specific configurations

You must run the deployment as a **non root user**. For a remote user, it must
have appropriate SSH configuration for **password less** authentication (use the
`.ssh/authorized_keys` on the remote host).

Your user must have full `sudo` access in order to:

* install packages
* push specific configurations linked to CRC

While we try to keep the footprint low on the system, packages are needed, and
some 3rd-party software requires access, such as CRC.

The best way to achieve that access is to add the following content to a
`/etc/sudoers.d/USERNAME` file using `visudo`:
```
USERNAME          ALL=(ALL)       NOPASSWD: ALL
```
Of course, replace `USERNAME` by your user's name.

Note that you can require the password for `sudo` calls, but you'll then have to pass `-K` option to
any of the `ansible-playbook` related to the infrastructure provisioning.

## Specific access rights

Since we're using libvirt within the "system" namespace (thanks to CRC, mostly),
your user must be part of the "libvirt" group. While we manage this in one of
the roles, you may need to logout/login in order to refresh your groups.
