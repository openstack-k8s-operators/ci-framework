## Role: repo_setup
Please explain the role purpose.

### Privilege escalation
If apply, please explain the privilege escalation done in this role.

### Parameters
* `cifmw_repo_setup_basedir`: Installation basedirectory. Defaults to `cifwm_basedir`
which defaults to `~/ci-framework`
* `cifmw_repo_setup_promotion`: Promotion line you want to deploy. Defaults to `current-podified`
* `cifmw_repo_setup_branch`: Branch/release you want to deploy. Defaults to `zed`
* `cifwm_repo_setup_dlrn_uri`: DLRN base URI. Defaults to https://trunk.rdoproject.org/
* `cifmw_repo_setup_os_release`: Operatinf system release. Defaults to `ansible_distribution|lower`
