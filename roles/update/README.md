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
* `cifmw_update_control_plane_check`: (Boolean) Activate a continuous control plane testing. Default to `False`
* `cifmw_update_ctl_plane_max_cons_fail`: (Integer) For continuous control plane testing, maximum number of consecutive failures allowed. Default to 2.
* `cifmw_update_ctl_plane_max_fail`: (Integer) For continuous control plane testing, maximum number of failures allowed. Default to 3.
* `cifmw_update_ctl_plane_max_tries`: (Integer) For continuous control plane testing, number of retries allowed to stop and destroy the last vm created. Each retry is 5 seconds apart. Default to 84, so 7 minutes.
* `cifmw_update_openstackclient_pod_timeout`: (Integer) Maximum number of seconds to wait for the openstackclient Pod to be available during control plane testing, as it is being restarted during update.  Default to `10` seconds.
* `cifmw_update_reboot_test`: (Boolean) Activate the reboot test after update. Default to `False`.
* `cifmw_update_ansible_ssh_private_key_file`: (String) Define the path to the private key file used for the compute nodes.
* `cifmw_update_wait_retries_reboot`: (Integer) Number of retries to wait for a compute node reboot. One retry is done every five seconds. Default to 60, so five minutes.
* `cifmw_update_resources_monitoring_interval`: (Integer) Interval, in seconds, between two resources monitor during update. Default to 10 seconds.

## Examples
