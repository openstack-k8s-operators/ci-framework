# operator_deploy
Deploy only selected operator(s) on OpenShift

## Privilege escalation
None

## Parameters
* `cifmw_operator_deploy_basedir`: (String) Directory where we will have the RHOL/CRC binary and the configuration (e.g. `artifacts/.rhol_crc_pull_secret.txt`). Default to `cifmw_basedir` which defaults to `~/ci-framework`.
* `cifmw_operator_deploy_installyamls`: (String) `install_yamls` root location. Defaults to `cifmw_installyamls_repos` which defaults to `../..`.
* `cifmw_operator_deploy_list`: (List) List of the operators to deploy. It must match a proper target in install_yamls Makefile.

## Examples
### Deploy specific operator
```YAML
cifmw_operator_deploy_list:
    - name: keystone_deploy
      params:
        KEYSTONE_REPO: https://github.com/me/my-keystone
        KEYSTONE_BRANCH: feature/it-is-a-test
    - name: rabbitmq
      params:
        RABBITMQ_IMG: local.registry:5000/features/rabbitmq:my-own-tag
```
### Remove specific operator
```YAML
cifmw_operator_deploy_list:
    - name: keystone_deploy_cleanup # remove only service instance without affecting operator
    - name: rabbitmq_cleanup
```
