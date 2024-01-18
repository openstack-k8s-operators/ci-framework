# kustomize_deploy

Ansible role designed to deploy VA scenarios using the kustomize tool.

## Parameters

```{warning}
The top level parameter `cifmw_architecture_va_scenario` is required in order
to select the proper VA scenario to deploy. If not provided, the role will fail
with a message.
```

- `cifmw_kustomize_deploy_destfiles_basedir`: Base directory for the ci-framework artifacts.
  Defaults to `~/ci-framework-data/`
- `cifmw_kustomize_deploy_architecture_repo_url`: URL of the "architecture" repository, where the VA scenarios are defined.
  Defaults to `https://github.com/openstack-k8s-operators/architecture`
- `cifmw_kustomize_deploy_architecture_repo_dest_dir`: Directory where the architecture repo is cloned on the controller node.
  Defaults to `~/src/github.com/openstack-k8s-operators/architecture`
- `cifmw_kustomize_deploy_architecture_repo_version`: Default branch of the architecture repo to clone.Defaults to `HEAD`
- `cifmw_kustomize_deploy_kustomizations_dest_dir`: Path for the generated CR files.
  Defaults to `cifmw_kustomize_deploy_destfiles_basedir + /artifacts/kustomize_deploy`
- `cifmw_kustomize_deploy_olm_dest_file`: Path of the generated CR file for OLM resources.
  Defaults to `cifmw_kustomize_deploy_kustomizations_dest_dir + olm.yml`
- `cifmw_kustomize_deploy_olm_source_files`: Path of the source kustomization files for OLM resources.
  Defaults to `cifmw_kustomize_deploy_architecture_repo_dest_dir + /examples/common/olm`
- `cifmw_kustomize_deploy_metallb_dest_file`: Path of the generated CR file for MetalLB resources.
  Defaults to `cifmw_kustomize_deploy_kustomizations_dest_dir + metallb.yml`
- `cifmw_kustomize_deploy_metallb_source_files`: Path of the source kustomization files for MetalLB resources.
  Defaults to `cifmw_kustomize_deploy_architecture_repo_dest_dir + /examples/common/metallb/`
- `cifmw_kustomize_deploy_nmstate_dest_file`: Path of the generated CR file for NMstate resources.
  Defaults to `cifmw_kustomize_deploy_kustomizations_dest_dir + nmstate.yml`
- `cifmw_kustomize_deploy_nmstate_source_files`: Path of the source kustomization files for NMstate resources.
  Defaults to `cifmw_kustomize_deploy_architecture_repo_dest_dir + /examples/common/nmstate`
- `cifmw_kustomize_deploy_cp_values_src_file`: Path of the `values.yaml` file for the control-plane customization.
  Defaults to `~/ci-framework-data/artifacts/ci_gen_kustomize_values/values.yaml`
- `cifmw_kustomize_deploy_cp_source_files`: Path of the control-plane kustomize source files.
  Defaults to `cifmw_kustomize_deploy_architecture_repo_dest_dir + /examples/va/hci/`
- `cifmw_kustomize_deploy_cp_values_dest_file`: Path of the generated CR file for the control-plane deploy.
  Defaults to `cifmw_kustomize_deploy_cp_source_files + values.yml`
- `cifmw_kustomize_deploy_cp_dest_file`: Path of the generated CR file for OSP control-plane resources.
  Defaults to `cifmw_kustomize_deploy_kustomizations_dest_dir + control-plane.yml`
- `cifmw_kustomize_deploy_architecture_examples_common_path`: Relative path of the common CRs in the architecture repo.
  Defaults to `/examples/common`
- `cifmw_kustomize_deploy_architecture_examples_va_path`: Relative path of the VA scenario list in the operator repo.
  Defaults to `/examples/va`

## Examples

```yaml
- name: Call kustomize_deploy role
  vars:
    cifmw_kustomize_deploy_cp_values_src_file: /tmp/values.yml
    cifmw_architecture_va_scenario: hci
  ansible.builtin.include_role:
    name: "kustomize_deploy"
```

## TODO

- Implement all the steps
