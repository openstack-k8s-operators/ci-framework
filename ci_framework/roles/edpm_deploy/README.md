# edpm_deploy
Perform External compute deploy on the pre-provisioned node from openshift cluster.

## Privilege escalation
None

## Parameters
* `cifmw_edpm_deploy_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_edpm_deploy_manifests_dir`: (String) Directory in where install_yamls output manifests will be placed. Defaults to `"{{ cifmw_manifests | default(cifmw_edpm_deploy_basedir ~ '/artifacts/manifests') }}"`.
* `cifmw_edpm_edploy_dataplane_operator_repo`: (String) Path to Dataplane-operator repo. Defaults to `"{{ ansible_user_dir }}/src/github.com/openstack-k8s-operators/dataplane-operator"`.
* `cifmw_edpm_deploy_os_runner_img`: (String) OpenStack Runner image url. Defaults to `"quay.io/openstack-k8s-operators/openstack-ansibleee-runner:latest"`.
* `cifmw_edpm_deploy_dataplane_cr`: (String) Path to Dataplane CR. Defaults to `"config/samples/dataplane_v1beta1_openstackdataplane.yaml"`.
* `cifmw_edpm_deploy_retries`: (Integer) Number of retries for edpm deploy status. Defaults to `100`.
* `cifmw_edpm_deploy_run_validation`: (Boolean) Run validation on EDPM node. Defaults to `False`.
* `cifmw_edpm_deploy_dryrun`: (Boolean) Do a dry run on make edpm_deploy command. Defaults to `False`.
* `cifmw_edpm_deploy_timeout`: (Integer) Time, in minutes to wait for the deployment to be ready. Defaults to `40`.

## TODO
- Add support for deploying multiple compute node
- Integrate EDPM kustomize

## Resources
* [ci_framework](https://github.com/openstack-k8s-operators/install_yamls)
