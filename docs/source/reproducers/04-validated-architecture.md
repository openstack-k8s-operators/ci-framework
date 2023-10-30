# Validated Architecture
## Words of warning
This feature is still under development and may change in the near future.

## Purpose
The Validated Architecture describes a deployment layout matching customer infrastructure.

## Supported environment
This has been successfully tested on the following environments:

* CentOS Stream 9 hypervisor, running CS-9 VMs
* Red Hat Enterprise Linux 9.2 hypervisor, running RHEL-9.2 VMs

Regarding hypervisor capacities, you have to get at least:

* 64G of RAM
* 130G of storage (/ must have over 80G of free space for dev-scripts, and /home must have at least 50G)
* 24 CPUs

### User on the hypervisor
The reproducer isn't supposed to run as root on the hypervisor. It is therefore strongly advised to create
a dedicated user, such as `virtuser`. Please ensure this user is at least in the following groups:

* wheel (for sudo rights)
* libvirt (if already installed)

### Subscription manager
The reproducer supports both registered and unregistered RHEL nodes.

In case you don't use subscription, you must pass some parameters:
```YAML
cifmw_repo_setup_enable_rhos_release: true
cifmw_ci_setup_yum_repos:
  - name: crb
    baseurl: https://mirror.stream.centos.org/9-stream/CRB/x86_64/os/
    description: Code ready builder
    gpgcheck: true
```

We have to get CRB repository for dev-scripts and EPEL.

## Layout content
The Layout will consist in 3 OCP nodes deployed using
[dev-scripts](https://github.com/openshift-metal3/dev-scripts), 3 computes and an ansible-controller deployed
with the [libvirt_manager](../roles/libvirt_manager.md).

Three virtual networks will also be deployed and managed during the dev-scripts run, and re-used by the
libvirt_manager stage in order to ensure connectivity.

### Private parameters the CI Framework doesn't provide
In order to deploy this layout, you will need to provide a private file containing the following information:
* cifmw_repo_setup_rhos_release_rpm
* cifmw_reproducer_internal_ca
* cifmw_discover_latest_image_base_url
* cifmw_discover_latest_image_qcow_prefix
* cifmw_discover_latest_image_images_file: "SHA256SUM"
* cifmw_devscripts_ci_token
* cifmw_devscripts_pull_secret

## Inventory file
It is recommended to run the reproducer against a remote hypervisor. In order to do so, you will need to provide a custom
inventory file, for instance located in `./custom/inventory.yml`. It is advised to mention the localhost in addition to your
remote hypervisor:

```YAML
all:
  hosts:
    localhost:
      ansible_connection: local
    hypervisor:
      ansible_user: virtuser
      ansible_host: 192.168.0.10
```

The `ansible_connection: local` will remove the network overhead when tasks are delegated to your localhost.

## Deploy the Layout
Once you provide the needed parameters in your private file (let's say you push them in ./custom/validated-architecture-1.yml),
you will have to run the following command:

```Bash
$ ansible-playbook \
    -i custom/inventory.yml \
    -e cifmw_target_host=hypervisor \
    -e @scenarios/reproducers/validated-architecture-1.yml \
    -e @custom/validated-architecture-1.yml \
    reproducer.yml
```

The deploy will take about an hour, depending on the resources available on the hypervisor and your network
connectivity/speed.

Note that the hypervisor **must** be connected to the Red Hat VPN if you expect deploying RHEL-based content,
especially in order to fetch the base image for the compute and controllers.

### Deployed content
Once the run is over, you can check for the following data:

```Bash
$ virsh list --all
 Id   Name                 State
------------------------------------
 5    ocp_master_1         running
 6    ocp_master_0         running
 7    ocp_master_2         running
 8    cifmw-compute-0      running
 9    cifmw-compute-1      running
 10   cifmw-compute-2      running
 11   cifmw-controller-0   running

$ virsh net-list --all
 Name        State    Autostart   Persistent
----------------------------------------------
 ocpbm       active   yes         yes
 ocppr       active   yes         yes
 osp_trunk   active   yes         yes
```
The `ocp_master_[0-2]` are the OCP nodes, deployed and configured by dev-scripts. The `cifmw-compute-[0-2]` and `cifmw-controller-0`
are the ones deployed and managed by libvirt_manager.

### Accesses
You can access the `cifmw-controller-0` from your laptop (provided you deployed it from there) by using `ssh controller-0`. Same goes
for the `cifmw-compute-[0-2]` nodes.

In order to access the OCP nodes, you'll need to connect to the controller-0 and, from there, jump onto the OCP nodes:
`ssh master-0 -l core -i .ssh/devscripts_key`. Same goes for `master-1` and `master-2` of course.

## Cleanup the Layout
### Remove everything
Just run the same command, but replace the `reproducer.yml` by `reproducer-clean.yml` playbook:
```Bash
$ ansible-playbook \
    -i custom/inventory.yml \
    -e cifmw_target_host=hypervisor \
    -e @scenarios/reproducers/validated-architecture-1.yml \
    -e @custom/validated-architecture-1.yml \
    reproducer-clean.yml
```

This will remove everything on the hypervisor, namely:
* OCP cluster
* All the compute nodes
* The ansible controller
* any generated content on the hypervisor (`ci-framework-data` mostly)

### I want to keep OCP, just start over on the computes and controller
We get you covered here. There are a couple of tags available in the cleanup playbook you may leverage. The easiest way to keep the OCP while removing the other nodes is:
```Bash
$ ansible-playbook \
    -i custom/inventory.yml \
    -e cifmw_target_host=hypervisor \
    -e @scenarios/reproducers/validated-architecture-1.yml \
    -e @custom/validated-architecture-1.yml \
    reproducer-clean.yml \
    --tags libvirt_layout
```

And, once this is done, you may run the following to redeploy just the needed bits:
```Bash
$ ansible-playbook \
    -i custom/inventory.yml \
    -e cifmw_target_host=hypervisor \
    -e @scenarios/reproducers/validated-architecture-1.yml \
    -e @custom/validated-architecture-1.yml \
    reproducer.yml \
    --skip-tags devscripts_layout
```
