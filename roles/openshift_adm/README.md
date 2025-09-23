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

* `cifmw_openshift_adm_basedir` (str) Framework base directory, defaults to `cifmw_basedir` or
  `~/ci-framework-data`.
* `cifmw_openshift_user` (str) Name of the user to be used for authentication.
* `cifmw_openshift_password` (str) Password of the provided user.
* `cifmw_openshift_kubeconfig` (str) Absolute path to the kubeconfig file.
* `cifmw_openshift_adm_stable_period` (str) Minimal period for cluster stability. Defaults to `3m`.
* `cifmw_path` (str) containing information for environment.path.

## Parameters - Role

* `cifmw_openshift_adm_op` (str) The operation to be performed on the cluster.
* `cifmw_openshift_adm_dry_run` (bool) If enabled, no modifications are
  performed on the cluster.
* `cifmw_openshift_adm_retry_count` (int) The maximum number of attempts to be
  made for a command to succeed. Default is `100`.
* `cifmw_openshift_adm_context` (str) The kubeconfig context to use for cluster operations. Default is `admin`.

## Obsolete Parameters

* `cifmw_openshift_api` (str) Previously required cluster endpoint URL. Removed in favor of dynamic API server URL detection from kubeconfig context to ensure correct cluster targeting.

## Reference

* [Stop and resume cluster](https://www.redhat.com/en/blog/enabling-openshift-4-clusters-to-stop-and-resume-cluster-vms)
