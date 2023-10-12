# ci_setup

Ensure you have the needed directories and packages for the rest of the tasks.

## Privilege escalation

- install packages

## Parameters


- `cifmw_ci_setup_basedir` (String) Base directory for the directory tree. Default to `~/ci-framework-data`.
- `cifmw_ci_setup_packages` (List) List of packages to install.
- `cifmw_ci_setup_openshift_client_version` (String) Version of openshift
  client to be installed on the system. Defaults to `stable` i.e. the latest
  stable release of the client.
- `cifmw_ci_setup_rhel_rhsm_default_repos` (List) List of repos to be enabled via Red Hat Subscription Manager.
- `cifmw_ci_setup_yum_repos` (list) List of dicts holding information on the repos to be enabled.

## Example of cifmw_ci_setup_yum_repos

```YAML
cifmw_ci_setup_yum_repos:
  - name: crb
    baseurl: https://mirror.stream.centos.org/9-stream/CRB/x86_64/os/
    description: Code ready builder
    gpgcheck: true
```

## Cleanup

You may call the `cleanup.yml` role in order to clear the directory tree.
