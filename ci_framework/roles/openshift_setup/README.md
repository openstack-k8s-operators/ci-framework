# openshift_setup
Prepares the target OpenShift cluster to be used by further steps:
- Project/Namespace creation

## Privilege escalation
No privilege escalation needed.

## Parameters
* `cifmw_openshift_setup_dry_run`: (Boolean) Skips resources creation. Defaults to `false`.
* `cifmw_openshift_setup_create_namespaces`: (Strings) Namespaces to create beforehand. Defaults to `[]`.
* `cifmw_openshift_setup_skip_internal_registry_login`: (Boolean) Skips login to Internal Openshift registry. Defaults to `false`.
