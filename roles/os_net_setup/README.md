# os_net_setup

This is typically an admin task before going into production,
creating network resources for the users.

## Privilege escalation

Not as sudo, but needs access to k8s openstack namespace and
being an openstack admin on the API.
That is provided by `openshift_login` role.

## Parameters

* `cifmw_os_net_setup_config`: (list) It contains the definitions for networks and their associated subnets.
    See an example in roles/os_net_setup/defaults/main.yml
* `cifmw_os_net_subnetpool_config`: (list) It contains the definitions for subnet pools.
    See an example in roles/os_net_setup/defaults/main.yml
* `cifmw_os_net_setup_dry_run`: (bool) Disable the generation of the commands.
* `cifmw_os_net_setup_namespace`: (str) Namespace in which to access the OSP cloud. Defaults to `openstack`.

## Molecule

There is no molecule test for this role, since it gets tested via any end-to-end job.
