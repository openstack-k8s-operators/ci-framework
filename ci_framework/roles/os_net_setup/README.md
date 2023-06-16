## os_net_setup
This is typically an admin task before going into production,
creating network for the users.

### Privilege escalation
Not as sudo, but needs access to k8s openstack namespace and
being an openstack admin on the API.
That is provided by `openshift_login` role.

### Parameters
* `cifmw_os_net_setup_config`: See an example in ci_framework/roles/os_net_setup/defaults/main.yml
