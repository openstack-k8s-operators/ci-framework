# edpm_prepare
Prepares the environment to deploy OpenStack control plane and compute nodes.

## Privilege escalation
This role doesn't need privilege escalation.

## Parameters
* `cifmw_edpm_prepare_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_edpm_prepare_dry_run`: (Boolean) Skips resources installations and waits. Defaults to false.
* `cifmw_edpm_prepare_manifests_dir`: (String) Directory in where install_yamls output manifests will be placed. Defaults to `"{{ cifmw_edpm_prepare_basedir }}/artifacts/manifests"`
* `cifmw_edpm_prepare_skip_crc_storage_creation`: (Boolean) Intentionally skips the deployment of the CRC storage related resources. Defaults to `False`.
* `cifmw_edpm_prepare_oc_retries`: (Integer) Number of retries, with 5 seconds delays, waiting for the OpenStack subscription to come up. Defaults to `5`.
* `cifmw_edpm_prepare_oc_retries`: (Integer) Number of attempts to retry an oc command if it fails. Defaults to `10`.
* `cifmw_edpm_prepare_oc_delay`: (Integer) Delay, in seconds, between failed oc call retries. Defaults to `30`.
* `cifmw_edpm_prepare_update_os_containers`: (Boolean) Updates the openstack services containers env variable. Defaults to `false`.
* `cifmw_edpm_prepare_timeout`: (Integer) Time, in minutes to wait for the deployment to be ready. Defaults to `30`.
* `cifmw_edpm_prepare_verify_tls`: (Boolean) In case of TLS enabled for OpenStack endpoint, validates against the CA. Defaults to `true`.
* `cifmw_edpm_prepare_skip_patch_ansible_runner`: (Boolean) Intentionally skips setting ansible runner image to `latest` from quay.io. Defaults to `False`.
* `cifmw_edpm_prepare_kustomizations`: (List) Kustomizations to apply on top of the controlplane CRs. Defaults to `[]`.
* `cifmw_edpm_prepare_wait_controplane_status_change_sec`: (Integer) Time, in seconds, to wait before checking
openstack control plane deployment status. Useful when using the role to only update the control plane resource, scenario where it may be in a `ready` status. Defaults to `30`.
