# openshift_adm

This role performs OpenShift cluster operations like wait for a stable
environment, shutdown and force regeneration of cluster certificate. The main
purpose of this role is perform administrative actions on the OpenShift
cluster.

## Privilege escalation

No privilege escalation is required on the executing host. However, it
requires administrator level privileges for the deployed OpenShift.

## General Parameters

This role requires the following parameters to be configured.

* `cifmw_openshift_api` (str) Cluster endpoint to be used for communication.
* `cifmw_openshift_user` (str) Name of the user to be used for authentication.
* `cifmw_openshift_password` (str) Password of the provided user.
* `cifmw_openshift_kubeconfig` (str) Absolute path to the kubeconfig file.
* `cifmw_base_dir` (str) Absolute path to the base directory
* `cifmw_path` (str) containing information for environment.path.

## Parameters - Role

* `cifmw_openshift_adm_op` (str) The operation to be performed on the cluster.
* `cifmw_openshift_adm_dry_run` (bool) If enabled, no modifications are
  performed on the cluster.
* `cifmw_openshift_adm_login_retry_count` (int) The maximum number of attempts
  to be made for a OpenShift login success. Default is `10`.
* `cifmw_openshift_adm_api_retry_count` (int) The maximum number of attempts to
  be made for confirming API response. Default is `100`.
* `cifmw_openshift_adm_node_retry_count` (int) The maximum number of attempts
  to be made for gathering the list of nodes. Default is `60`.

## Reference

* [Stop and resume cluster](https://www.redhat.com/en/blog/enabling-openshift-4-clusters-to-stop-and-resume-cluster-vms)
