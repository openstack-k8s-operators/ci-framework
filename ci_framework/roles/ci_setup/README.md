# ci_setup
Ensure you have the needed directories and packages for the rest of the tasks.

## Privilege escalation
- install packages

## Parameters
* `cifmw_ci_setup_basedir`: (String) Base directory for the directory tree. Default to `~/ci-framework-data`.
* `cifmw_ci_setup_packages`: (List) List of packages to install.
* `cifmw_ci_setup_openshift_client_version`: (String) Version of openshift
  client to be installed on the system. Defaults to `stable` i.e. the latest
  stable release of the client.

## Cleanup
You may call the `cleanup.yml` role in order to clear the directory tree.
