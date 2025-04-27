# ci_gen_kustomize_values
Generate complete kustomization file based on multiple snippets

## Privilege escalation
None

## Parameters

```{warning}
The top level parameter `cifmw_architecture_scenario` is required in order
to select the proper VA scenario to deploy. If not provided, the role will fail
with a message.
```

* `cifmw_ci_gen_kustomize_values_basedir`: (String) Base directory.
  Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_ci_gen_kustomize_values_architecture_repo`: (String) architecture repository location.
  Defaults to `cifmw_architecture_repo` (`~/src/github.com/openstack-k8s-operators/architecture`).
* `cifmw_ci_gen_kustomize_values_src_file`: (String) Absolute path to the `values.yaml` file you want to edit.
  Defaults to `cifmw_ci_gen_kustomize_values_architecture_repo/cifmw_ci_gen_kustomize_values_architecture_examples_path/cifmw_architecture_scenario/values.yaml`
* `cifmw_ci_gen_kustomize_values_snippets_basedir`: (String) Location for the values snippets.
  Defaults to `~/ci-framework-data/artifacts/ci_k8s_snippets`.
* `cifmw_ci_gen_kustomize_values_snippets_dir_prefix`: (String) Prefix for snippet directory. Defaults to `""`.
* `cifmw_ci_gen_kustomize_values_generated_dir`: (String) Location of the generated values.yaml.
  Defaults to `~/ci-framework-data/artifacts/ci_gen_kustomize_values`.
* `cifmw_ci_gen_kustomize_values_dest_fname_prefix`: (String) Prefix for generated file name. Defaults to `""`.
* `cifmw_ci_gen_kustomize_values_dest_filename`: (String) Name of the generated output file.
  Defaults to `{{ cifmw_ci_gen_kustomize_values_dest_fname_prefix }}values.yaml`.
* `cifmw_ci_gen_kustomize_values_nameservers`: (List) List of name servers you want to inject.
  Defaults to `[]`.
* `cifmw_ci_gen_kustomize_values_userdata`: (Dict) Data structure you want to combine in the generated output.
  Defaults to `{}`.
* `cifmw_ci_gen_kustomize_values_userdata_b64`: (List) Base64 encoded list of data to combine in the generated output.
  Defaults to `[]`.
* `ci_gen_kustomize_fetch_ocp_state`: (Boolean) If true it enables generating CI templates based on the OCP state. Defaults to `true`.
* `cifmw_ci_gen_kustomize_values_storage_class_prefix`: (String) Prefix for `storageClass` in generated values.yaml files. Defaults to `"lvms-"` only if `cifmw_use_lvms` is True, otherwise it defaults to `""`. The prefix is prepended to the `cifmw_ci_gen_kustomize_values_storage_class`. It is not recommended to override this value, instead set `cifmw_use_lvms` True or False.
* `cifmw_ci_gen_kustomize_values_storage_class`: (String) Value for `storageClass` in generated values.yaml files. Defaults to `"lvms-local-storage"` only if `cifmw_use_lvms` is True, otherwise it defaults to `"local-storage"`.
* `cifmw_ci_gen_kustomize_values_remove_keys_expressions*`: (List) Remove keys matching the regular expressions from source ConfigMaps (values.yaml).
  Defaults to `["^nodes$", "^node(_[0-9]+)?$"]`. Accepts passing additional expressions by passing variables that matches `cifmw_ci_gen_kustomize_values_remove_keys_expressions.+`.

### Specific parameters for edpm-values
This configMap needs some more parameters in order to properly override the `architecture` provided one.

These parameters aren't set by default, and are mandatory for `edpm-values`.

* `cifmw_ci_gen_kustomize_values_ssh_authorizedkeys`: (String) Block of SSH authorized_keys to inject on the deployed nodes.
* `cifmw_ci_gen_kustomize_values_ssh_private_key`: (String) SSH private key to allow dataplane access on the computes.
* `cifmw_ci_gen_kustomize_values_ssh_public_key`: (String) SSH public key associated to `cifmw_ci_gen_kustomize_values_ssh_private_key`.
* `cifmw_ci_gen_kustomize_values_migration_priv_key`: (String) SSH private key dedicated for the nova-migration services.
* `cifmw_ci_gen_kustomize_values_migration_pub_key`: (String) SSH public key associated to `cifmw_ci_gen_kustomize_values_migration_priv_key`.
Note that all of the SSH keys should be in `ecdsa` format to comply with FIPS directives.

Optional parameters:

* `cifmw_ci_gen_kustomize_values_edpm_net_template_b64`: (String) The base64 content of `edpm_network_config_template`.

### Specific parameters for olm-values
This ConfigMap specifies parameters to override those in `architecture/example/common/olm/values.yaml`.

* `cifmw_ci_gen_kustomize_values_ooi_image`: (String) The URI for the image providing the OpenStack operator index. Defaults to `quay.io/openstack-k8s-operators/openstack-operator-index:latest`.
* `cifmw_ci_gen_kustomize_values_sub_channel`: (String) Specifies the channel to be used.

If the following parameter is set, it overrides the associated parameter in `architecture/example/common/olm-subscriptions/values.yaml`.

* `cifmw_ci_gen_kustomize_values_deployment_version`: (String) The version to be deployed by setting the `startingCSV` of the subscription for the OpenStack operator. Versions `v1.0.3` and `v1.0.6` are unique as they configure the subscription for all operators. The right kustomize overlay is selected by the `ci_gen_kustomize_values/tasks/olm_subscriptions_overlay.yml` file.

* `cifmw_ci_gen_kustomize_values_installplan_approval`: (String) Options are `Manual` or `Automatic`. This determines how the OpenStack operator is installed. In `Manual` mode, the install plan requires approval, which is automatically handled in the `kustomize_deploy/tasks/install_operators.yml` task file.

Access to the other parameters defined in the `olm-subscription/values.yaml` file is doable by overriding them using the `cifmw_architecture_user_kustomize_<some_string>` variable, which should set the `common.olm-values` hash. However, the last two variables should not be modified using this method, as it won't activate the additional code required for them to function correctly.

## Adding a new template

The template must have a leading comment staging its source. For example, if your template is located in
`templates/foo/edpm-values/values.yaml.j2` it must have the following header:

```YAML
---
# source: foo/edpm-values/values.yaml.j2
```

The `source` must be relative to the `templates` directory. This will help during debugging sessions, since it will show the used template
directly in `ci-framework-data/ci_k8s_snippets/TYPE/02_ci_data.yaml`.

## Examples

### Generate controlplane values.yaml for `nfv/sriov` VA

```YAML
- name: Load networking environment definition
  register: _net_env
  ansible.builtin.slurp:
    path: "/etc/ci/env/networking-environment-definition.yml"

- name: Generate controlplane without any custom user input
  vars:
    cifmw_architecture_scenario: "nfv/sriov"
    cifmw_networking_env_definition: "{{ _net_env.content | b64decode | from_yaml }}"
  ansible.builtin.import_role:
    name: ci_gen_kustomize_values
```

```YAML
- name: Load networking environment definition
  register: _net_env
  ansible.builtin.slurp:
    path: "/etc/ci/env/networking-environment-definition.yml"

- name: Generate controlplane with custom user input
  vars:
    cifmw_architecture_scenario: "nfv/sriov"
    cifmw_networking_env_definition: "{{ _net_env.content | b64decode | from_yaml }}"
    cifmw_ci_gen_kustomize_values_userdata:
      data:
        node_0:
          name: foo_bar
    cifmw_ci_gen_kustomize_values_userdata_b64:
      data:
        node_1:
          name: Zm9vX2Jhcgo=
  ansible.builtin.import_role:
    name: ci_gen_kustomize_values
```

### Generate dataplane values.yaml for `nfv/sriov` VA

```YAML
- name: Load networking environment definition
  register: _net_env
  ansible.builtin.slurp:
    path: "/etc/ci/env/networking-environment-definition.yml"

- name: Generate dataplane without any custom user input
  vars:
    cifmw_architecture_scenario: "nfv/sriov/edpm"
    cifmw_networking_env_definition: "{{ _net_env.content | b64decode | from_yaml }}"
  ansible.builtin.import_role:
    name: ci_gen_kustomize_values
```
