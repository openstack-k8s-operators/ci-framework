# ci_gen_kustomize_values
Generate complete kustomization file based on multiple snippets

## Privilege escalation
None

## Parameters
* `cifmw_ci_gen_kustomize_values_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_ci_gen_kustomize_values_architecure_repo`: (String) architecture repository location. Defaults to `~/src/github.com/openstack-k8s-operators/architecture`.
* `cifmw_ci_gen_kustomize_values_dt_src_file`: (String) Relative path for the `values.yaml` file you want to edit. Path must be relative to `cifmw_ci_gen_kustomize_values_architecure_repo`. Mandatory parameter. Defaults to `null`.
* `cifmw_ci_gen_kustomize_values_snippets_dir`: (String) Location for the values snippets. Defaults to `~/ci-framework-data/artifacts/ci_k8s_snippets`.
* `cifmw_ci_gen_kustomize_values_generated_dir`: (String) Location of the generated values.yaml. Defaults to `~/ci-framework-data/artifacts/ci_gen_kustomize_values`.
* `cifmw_ci_gen_kustomize_values_dest_filename`: (String) Name of the generated output file. Defaults to `values.yaml`.
* `cifmw_ci_gen_kustomize_values_nameservers`: (List) List of name servers you want to inject. Defaults to `[]`.
* `cifmw_ci_gen_kustomize_values_userdata`: (Dict) Data structure you want to combine in the generated output. Defaults to `{}`.

### Specific parameters for edpm-values
This configMap needs some more parameters in order to properly override the `architecture` provided one. Those parameters aren't set by default, and are mandatory for `edpm-values`.

* `cifmw_ci_gen_kustomize_values_ssh_authorizedkeys`: (String) Block of SSH authorized_keys to inject on the deployed nodes.
* `cifmw_ci_gen_kustomize_values_ssh_private_key`: (String) SSH private key to allow dataplane access on the computes.
* `cifmw_ci_gen_kustomize_values_ssh_public_key`: (String) SSH public key associated to `cifmw_ci_gen_kustomize_values_ssh_private_key`.
* `cifmw_ci_gen_kustomize_values_migration_priv_key`: (String) SSH private key dedicated for the nova-migration services.
* `cifmw_ci_gen_kustomize_values_migration_pub_key`: (String) SSH public key associated to `cifmw_ci_gen_kustomize_values_migration_priv_key`.

Note that all of the SSH keys should be in `ecdsa` format to comply with FIPS directives.
