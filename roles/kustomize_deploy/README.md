# kustomize_deploy

Ansible role designed to deploy architecture-based scenarios using the kustomize tool.

## Parameters

```{warning}
The top level parameter `cifmw_architecture_scenario` is required in order
to select the proper architecture-based scenario to deploy. If not provided, the role will fail
with a message.
```

### default resources

- `cifmw_kustomize_deploy_basedir`: _(string)_ Base directory for the
  ci-framework artifacts. Defaults to `~/ci-framework-data/`
- `cifmw_kustomize_deploy_architecture_repo_url`: _(string)_ URL of The
  "architecture" repository, where the architecture-based scenarios are defined.
  Defaults to `https://github.com/openstack-k8s-operators/architecture`
- `cifmw_kustomize_deploy_architecture_repo_dest_dir`: _(string)_ Directory
  where the architecture repo is cloned on the controller node.
  Defaults to `~/src/github.com/openstack-k8s-operators/architecture`
- `cifmw_kustomize_deploy_architecture_repo_version`: _(string)_ Default branch
  of the architecture repo to clone. Takes its value from group_vars
  cifmw_architecture_repo_version_pin, defaults to `HEAD` if not defined.
- `cifmw_kustomize_deploy_architecture_examples_common_path`: _(string)_
  Relative path of the common CRs in the architecture repo. Defaults to
  `/examples/common`
- `cifmw_kustomize_deploy_architecture_examples_path`: _(string)_ Relative
  path of the architecture-based scenario list in the operator repo. Defaults to `/examples/va`
- `cifmw_kustomize_deploy_kustomizations_dest_dir`: _(string)_ Path for the
  generated CR files. Defaults to
  `cifmw_kustomize_deploy_destfiles_basedir + /artifacts/kustomize_deploy`
- `cifmw_kustomize_deploy_generate_crs_only`: _(boolean)_ The generated CRs
  aren't applied (dry-run). Defaults to `false`
- `cifmw_kustomize_deploy_keep_generated_crs`: _(boolean)_ Keep the generated
  CRs in the destination folder. Defaults to `true`

### operators resources

- `cifmw_kustomize_deploy_olm_source_files`: _(string)_ Path of the source
  kustomization files for OLM resources. Defaults to
  `cifmw_kustomize_deploy_architecture_repo_dest_dir + /examples/common/olm`
- `cifmw_kustomize_deploy_olm_dest_file`: _(string)_ Path of the generated CR
  file for OLM resources. Defaults to
  `cifmw_kustomize_deploy_kustomizations_dest_dir + olm.yml`
- `cifmw_kustomize_deploy_metallb_source_files`: _(string)_ Path of the source
  kustomization files for MetalLB resources. Defaults to
  `cifmw_kustomize_deploy_architecture_repo_dest_dir + /examples/common/metallb/`
- `cifmw_kustomize_deploy_metallb_dest_file`: _(string)_ Path of the generated
  CR file for MetalLB resources. Defaults to
  `cifmw_kustomize_deploy_kustomizations_dest_dir + metallb.yml`
- `cifmw_kustomize_deploy_nmstate_source_files`: _(string)_ Path of the source
  kustomization files for NMstate resources. Defaults to
  `cifmw_kustomize_deploy_architecture_repo_dest_dir + /examples/common/nmstate`
- `cifmw_kustomize_deploy_nmstate_dest_file`: _(string)_ Path of the generated
  CR file for NMstate resources. Defaults to
  `cifmw_kustomize_deploy_kustomizations_dest_dir + nmstate.yml`

### controlplane resources

- `cifmw_kustomize_deploy_nncp_source_files`: _(string)_ Path of the NNCP
  kustomize source files.
  Defaults to `cifmw_kustomize_deploy_cp_source_files + /nncp/`
- `cifmw_kustomize_deploy_nncp_values_dest_file`: _(string)_ Path of the
  generated CR file for the NNCP resources deploy. Defaults to
  `cifmw_kustomize_deploy_nncp_source_files + values.yaml`
- `cifmw_kustomize_deploy_nncp_dest_file`: _(string)_ Path of the generated CR
  file for NNCP resources. Defaults to
  `cifmw_kustomize_deploy_kustomizations_dest_dir + nncp.yaml`
- `cifmw_kustomize_deploy_cp_source_files`: _(string)_ Path of the
  control-plane kustomize source files. Defaults to
  `cifmw_kustomize_deploy_architecture_repo_dest_dir + /examples/va/hci/control-plane`
- `cifmw_kustomize_deploy_nncp_values_src_file`: _(string)_ Path of the
  `values.yaml` file for the NNCP customization. Defaults to
  `~/ci-framework-data/artifacts/ci_gen_kustomize_values/network-values/values.yaml`
- `cifmw_kustomize_deploy_cp_dest_file`: _(string)_ Path of the generated CR
  file for OSP control-plane resources. Defaults to
  `cifmw_kustomize_deploy_kustomizations_dest_dir + control-plane.yaml`

### dataplane resources

- `cifmw_kustomize_deploy_dp_source_files`: _(string)_ Path of the
  dataplane kustomize source files. Defaults to
  `cifmw_kustomize_deploy_architecture_repo_dest_dir +`
  `cifmw_kustomize_deploy_architecture_examples_path +`
  `cifmw_architecture_scenario`
- `cifmw_kustomize_deploy_dp_values_src_file`: _(string)_ Path of the
  generated `values.yaml` for dataplane resources. Defaults to
  `~/ci-framework-data/artifacts/ci_gen_kustomize_values/edpm-values/values.yaml`
- `cifmw_kustomize_deploy_dp_values_dest_file`: _(string)_ Path of the
  `values.yaml` file for dataplane resources. Defaults to
  `cifmw_kustomize_deploy_dp_source_files + values.yaml`
- `cifmw_kustomize_deploy_dp_dest_file`: _(string)_ Path of the generated
  CR file for the DataPlane resources deploy. Defaults to
  `cifmw_kustomize_deploy_kustomizations_dest_dir + dataplane.yaml`

### osp-secrets randomization

- `cifmw_kustomize_deploy_osp_secrets_env_path`: _(string)_ Relative path
  (within the architecture repo) to the `osp-secrets.env` file whose default
  hardcoded values are replaced with random ones before `kustomize build`.
  Defaults to `lib/control-plane/base/osp-secrets.env`.

- `cifmw_kustomize_deploy_osp_secrets_special_keys`: _(dict)_ Keys that
  require a specific value format rather than a plain alphanumeric password.
  Each entry maps a key name to its generation parameters:
  - `type: "base64"` — generates `length` random bytes, then base64-encodes.
  - `type: "hex"` — generates `length` random bytes as a hex string
    (output is `length * 2` hex characters).

  Default:

  ```yaml
  cifmw_kustomize_deploy_osp_secrets_special_keys:
    HeatAuthEncryptionKey:
      type: "hex"
      length: 16
  ```

- `cifmw_kustomize_deploy_osp_secrets_skip_keys`: _(list)_ Keys to leave
  unchanged (their original value from the architecture repo is preserved).
  Use this for keys that are managed by a separate mechanism.
  Default: `[BarbicanSimpleCryptoKEK]`.

- `cifmw_kustomize_deploy_osp_secrets_cache_path`: _(string)_ Path to a
  local file where generated secrets are cached between runs. On subsequent
  runs the cached values are reused rather than regenerated.
  Default: `{{ cifmw_kustomize_deploy_basedir }}/artifacts/osp-secrets-generated.env`.

The randomization runs automatically after the architecture repo is cloned
and before any kustomize build. For each key the task uses a three-tier
resolution order:

1. **Live cluster** — if the `osp-secret` K8s Secret already exists in the
   target namespace, its values take priority (preserves secrets across
   redeploys).
2. **Local cache** — if a previous run cached the generated secrets on disk,
   those values are reused.
3. **Generate** — a new random value is produced (respecting the special-keys
   format rules). Keys in the skip list are never touched.

If the `.env` file does not exist in the architecture checkout (e.g. it was
removed upstream), the task is silently skipped. If the cluster is
unreachable the task falls through to the cache/generation layers without
failing.

## Automation specificities

### Timeouts

Some tasks uses timeouts when applying or waiting for resources. Those timeouts can be controlled by:

* `cifmw_kustomize_deploy_delay`: (Int) Ansible `delay` passed to tasks that waits for a resource to reach a target state (default `10`)
* `cifmw_kustomize_deploy_retries_subscription`: (Int) Ansible `retries` passed to tasks that wait for the Subscription (default `90`)
* `cifmw_kustomize_deploy_retries_install_plan`: (Int) Ansible `retries` passed to tasks that wait for the InstallPlan (default `60`)

### Task tagging

Tags are dynamically associated to each stage of the automated deployment.
This allows to discard specific stages by passing the following parameter
to `ansible-playbook`:
```Bash
$ ansible-playbook deploy-edpm.yml \
  -e @scenarios/reproducers/va-hci.yml \
  -e @scenarios/reproducers/networking-definition.yml \
  --skip-tags deploy_architecture_stage_0
```
This would skip the first stage described in the automation file.

### Break point

You can also stop the automated deploy by setting `cifmw_deploy_architecture_stopper`
parameter to a specific value.

Break point names are built using the stage ID, and the code currently supports
three different stopper:

- Before calling `kustomize build`: `pre_kustomize_stage_ID`
- Before applying the CR: `post_kustomize_stage_ID`
- After applying the CR (and after the validation): `post_apply_stage_ID`

#### Example

```Bash
$ ansible-playbook deploy-edpm.yml [...] \
  -e cifmw_deploy_architecture_stopper=post_kustomize_stage_3
```

## Examples

```yaml
- name: Call kustomize_deploy role
  vars:
    cifmw_kustomize_deploy_nncp_values_src_file: /tmp/values.yml
    cifmw_architecture_scenario: hci
  ansible.builtin.include_role:
    name: "kustomize_deploy"
```
