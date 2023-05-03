## Role: edpm_deploy
Peform External compute deploy on the pre-provisioned node from openshift cluster.

### Privilege escalation
None

### Parameters
* `cifmw_edpm_deploy_basedir`: Base directory. Defaults to `cifmw_basedir`
which defaults to `~/ci-framework`.
* `cifmw_edpm_deploy_manifests_dir`: String) Directory in where install_yamls output manifests will be placed. Defaults to **"{{ cifmw_manifests | default(cifmw_edpm_deploy_basedir ~ '/artifacts/manifests') }}"**
* `cifmw_edpm_edploy_dataplane_operator_repo`: Path to Dataplane-operator repo. Defaults to **"{{ ansible_user_dir }}/src/github.com/openstack-k8s-operators/dataplane-operator"**
* `cifmw_edpm_deploy_os_runner_img`: OpenStack Runner image url. Defaults to **"quay.io/openstack-k8s-operators/openstack-ansibleee-runner:latest"**
* `cifmw_edpm_deploy_dataplane_cr`: Path to Dataplane CR. Defaults to **"config/samples/dataplane_v1beta1_openstackdataplane.yaml"**
* `cifmw_edpm_deploy_log_path`: Path to collect EDPM pods log. Defaults to **"{{ cifmw_edpm_deploy_basedir }}/logs/edpm/edpm_deploy.log"**
* `cifmw_edpm_deploy_run_validation`: Run validation on EDPM node. Defaults to **false**
* `cifmw_edpm_deploy_dryrun`: Do a dry run on make edpm_deploy command. Defaults to **false**

### TODO
- Add support for deploying multiple compute node
- Integrate EDPM kustomize

### Resources
* [ci_framework](https://github.com/openstack-k8s-operators/install_yamls)
