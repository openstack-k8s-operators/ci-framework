## Role: repo_setup
Please explain the role purpose.

### Privilege escalation
If apply, please explain the privilege escalation done in this role.

### Parameters
* `cifmw_repo_setup_basedir`: Installation basedirectory. Defaults to `cifmw_basedir`
which defaults to `~/ci-framework`
* `cifmw_repo_setup_promotion`: Promotion line you want to deploy. Defaults to `current-podified`
* `cifmw_repo_setup_branch`: Branch/release you want to deploy. Defaults to `zed`
* `cifmw_repo_setup_dlrn_uri`: DLRN base URI. Defaults to https://trunk.rdoproject.org/
* `cifmw_repo_setup_rdo_mirror`: Server from which to install RDO packages. Defaults to DLRN URI.
* `cifmw_repo_setup_os_release`: Operating system release. Defaults to `ansible_distribution|lower`
* `cifmw_repo_setup_src`: repo-setup repository location
* `cifmw_repo_setup_output`: Repository files output. Defaults to `{{ cifmw_repo_setup_basedir }}/artifacts/repositories`
* `cifmw_repo_setup_opts`: Additional options we may to pass to repo_setup. Defaults to `''`
