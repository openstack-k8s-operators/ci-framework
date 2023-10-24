# Validated Architecture
## Words of warning
This feature is still under development and may change in the near future.

## Purpose
The Validated Architecture describes a deployment layout matching customer infrastructure.

On the "hardware" part, it consist in a 3-node OCP service, and at least 3 compute nodes.

## Supported environment
This has been successfully tested on the following environments:

* CentOS Stream 9 hypervisor, running CS-9 VMs
* Red Hat Enterprise Linux 9.2 hypervisor, running RHEL-9.2 VMs

Regarding hypervisor capacities, you have to get at least:

* 64G of RAM
* 130G of storage (/ must have over 80G of free space for dev-scripts, and /home must have at least 50G)
* 24 CPUs

## Deploy the layout
(doc will be updated on due time once all the pieces are in the repository)
