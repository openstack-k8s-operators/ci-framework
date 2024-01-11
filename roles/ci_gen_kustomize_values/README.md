# ci_gen_kustomize_values
Generate complete kustomization file based on multiple snippets

## Privilege escalation
None

## Parameters
* `cifmw_ci_gen_kustomize_values_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_ci_gen_kustomize_values_src_dir`: (String) Source directory where your snippets are located. Defaults to `{{ cifmw_ci_gen_kustomize_values_basedir }}/artifacts/ci_k8s_snippets`.
* `cifmw_ci_gen_kustomize_values_dest_dir`: (String) Destination directory of the generated file. Defaults to `{{ cifmw_ci_gen_kustomize_values_basedir }}/artifacts/ci_gen_kustomize_values/`.
* `cifmw_ci_gen_kustomize_values_dest_filename`: (String) Destination file name for generated content. Defaults to `values.yaml`.
* `cifmw_ci_gen_kustomize_values_header`: (Dict) Kustomize file header (apiVersion, kind, metadata).

## Examples
```YAML
- name: Generate Networking data
  ansible.builtin.include_role:
    name: networking_mapper

- name: Output needed snippet
  ansible.builtin.include_role:
    name: networking_mapper
    tasks_from: network_config_values.yml

- name: Generate final kustomize file
  ansible.builtin.include_role:
    name: ci_gen_kustomize_values
```
