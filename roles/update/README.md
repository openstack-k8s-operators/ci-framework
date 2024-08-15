# update
Role to run update

## Parameters
* `cifmw_update_extras`: (hash) Hold job variable that get set when running the update playbook.
* `cifmw_update_openstack_update_run_operators_updated`: (Boolean) Set if openstack_update_run make target should not modify openstack-operator csv to fake openstack services container change. Default to `True`.
* `cifmw_update_openstack_update_run_target_version`: (String) Define openstack target version to run update to.
* `cifmw_update_openstack_update_run_timeout`: (String) Define `oc wait` global timeout passed to each step of update procedure. It should be a value of a longest step of the procedure. Defaults to `600s`.
* `cifmw_update_run_dryrun`: (Boolean) Do a dry run on make openstack_update_run command. Defaults to `False`.
* `cifmw_update_ping_test`: (Boolean) Activate the ping test during update. Default to `False`.
* `cifmw_update_create_volume`: (Boolean) Attach a volume to the test OS instance when set to true.  Default to `False`
* `cifmw_update_ping_loss_second` : (Integer) Number of seconds that the ping test is allowed to fail. Default to `0`. Note that 1 packet loss is always accepted to avoid false positive.
* `cifmw_update_ping_loss_percent` : (Integer) Maximum percentage of ping loss accepted.  Default to `0`. Only relevant when `cifmw_update_ping_loss_second` is not 0.

## Examples
