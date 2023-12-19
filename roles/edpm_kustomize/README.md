# edpm_kustomize
Apply kustomizations to resources involved in EDPM deployment.

## Privilege escalation
None

## Parameters
* `cifmw_edpm_kustomize_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_edpm_kustomize_artifacts_dir`: (String) Artifacts directory. Defaults to `{{ cifmw_edpm_kustomize_basedir ~ '/artifacts'`.
* `cifmw_edpm_kustomize_cr_path`: (String) CRD you want to kustomize. Must be a proper YAML file. **Mandatory**.

## Examples
```YAML
- name: Kustomize resources
  vars:
    cifmw_edpm_kustomize_cr_path: "/path/to/resource.yml"
    cifmw_edpm_kustomize_content: |-
       apiVersion: kustomize.config.k8s.io/v1beta1
       kind: Kustomization
       resources:
       namespace: {{ cifmw_install_yamls_defaults.NAMESPACE }}
       patches:
       - target:
           kind: OpenStackDataPlaneNodeSet
         patch: |-
           - op: replace
             path: /spec/nodeTemplate/ansible/ansibleVars/neutron_public_interface_name
             value: "eno1"

           - op: replace
             path: /spec/nodeTemplate/ansible/ansibleVars/ctlplane_mtu
             value: "1350"

           - op: replace
             path: /spec/nodeTemplate/ansible/ansibleUser
             value: "{{ hostvars['compute-0'].ansible_user | default('zuul') }}"

           - op: replace
             path: /spec/nodeTemplate/ansible/ansibleVars/edpm_os_net_config_mappings
             value:
               net_config_data_lookup:
                 edpm-compute:
                   nic1: "{{ crc_ci_bootstrap_networks_out['compute-0'].default.iface }}"

           - op: replace
             path: /spec/nodeTemplate/ansible/ansibleUser
             value: "{{ hostvars['compute-0'].ansible_user | default('zuul') }}"
  ansible.builtin.include_role:
    name: edpm_kustomize
```
