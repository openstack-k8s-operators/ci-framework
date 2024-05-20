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
