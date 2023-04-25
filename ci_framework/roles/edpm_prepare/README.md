## Role: edpm_prepare
Prepares the environment to deploy OpenStack control plane and compute nodes.

### Privilege escalation
This role doesn't need privilege scalation.

### Parameters
* `cifmw_edpm_prepare_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to **~/ci-framework**.
* `cifmw_edpm_prepare_dry_run`: (Boolean) Skips resources installations and waits. Defaults to false.
* `cifmw_edpm_prepare_manifests_dir`: String) Directory in where install_yamls output manifests will be placed. Defaults to **"{{ cifmw_edpm_prepare_basedir }}/artifacts/manifests"**
* `cifmw_edpm_skip_openstack_operator:`: (Boolean) Intentionally skips the deployment of the OpenStack metaoperator. Defaults to false.
* `cifmw_edpm_prepare_wait_subscription_retries`: (Integer) Number of retries, with 5 seconds delays, waiting for the OpenStack subscription to come up. Defaults to 5.
