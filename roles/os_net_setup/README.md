# os_net_setup
This is typically an admin task before going into production,
creating network for the users.

## Privilege escalation
Not as sudo, but needs access to k8s openstack namespace and
being an openstack admin on the API.
That is provided by `openshift_login` role.

## Parameters
* `cifmw_os_net_setup_config`: See an example in roles/os_net_setup/defaults/main.yml
* `cifmw_os_net_setup_osp_calls_retries`: (Integer) Number of attempts to retry an OSP action if it fails. Defaults to `10`.
* `cifmw_os_net_setup_osp_calls_delay`: (Integer) Delay, in seconds, between failed OSP call retries. Defaults to `5`.
* `cifmw_os_net_setup_verify_tls`: (Boolean) In case of TLS enabled for OpenStack endpoint, validates against the CA. Defaults to `true`.

## Molecule
There is no molecule test for this role, since it gets tested via any end-to-end job.
