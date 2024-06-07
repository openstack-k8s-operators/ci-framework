# update
Role to run update

## Parameters
* ``cifmw_update_extras`: (hash) Hold job variable that get set when running the update playbook.
* ``cifmw_update_openstack_update_run_operators_updated`: (Boolean) Set if openstack_update_run make target should not modify openstack-operator csv to fake openstack services container change. Default to `True`.
* ``cifmw_update_openstack_update_run_target_version`: (String) Define openstack target version to run update to.
* `cifmw_update_run_dryrun`: (Boolean) Do a dry run on make openstack_update_run command. Defaults to `False`.
