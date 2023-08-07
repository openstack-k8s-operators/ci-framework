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
            kind: OpenStackDataPlane
          patch: |-
            - op: replace
              path: /spec/roles/edpm-compute/nodeTemplate/ansibleVars/edpm_network_config_template
              value: "{{ cifmw_edpm_deploy_extra_vars.DATAPLANE_NETWORK_CONFIG_TEMPLATE }}"

            - op: replace
              path: /spec/roles/edpm-compute/nodeTemplate/ansibleVars/neutron_public_interface_name
              value: "{{ crc_ci_bootstrap_networks_out.compute.default.iface }}"

            - op: replace
              path: /spec/roles/edpm-compute/nodeTemplate/ansibleVars/ctlplane_mtu
              value: "{{ crc_ci_bootstrap_networks_out.compute.default.mtu }}"

            - op: replace
              path: /spec/roles/edpm-compute/nodeTemplate/ansibleVars/edpm_os_net_config_mappings
              value:
                net_config_data_lookup:
                  edpm-compute:
                    nic1: "{{ crc_ci_bootstrap_networks_out.compute.default.iface }}"

            - op: replace
              path: /spec/roles/edpm-compute/nodeTemplate/ansibleUser
              value: "{{ hostvars.compute.ansible_user | default('zuul') }}"
  ansible.builtin.include_role:
    name: edpm_kustomize
```
