# cert_manager

Ansible role to install cert-manager operator

## Privilege escalation
If apply, please explain the privilege escalation done in this role.

## Parameters
* `cifmw_cert_manager_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_cert_manager_manifests_dir`: (String) Directory in where OCP manifests will be placed. Defaults to `"{{ cifmw_manifests | default(cifmw_cert_manager_basedir ~ '/artifacts/manifests') }}"`.
* `cifmw_cert_manager_namespace`: (String) The namespace where OCP resources will be installed. Defaults to `cert-manager-operator`.
* `cifmw_cert_manager_olm_operator_group`: (Dict) The `OperatorGroup` resource to be used to install the cert-manager operator.
* `cifmw_cert_manager_olm_subscription`: (Dict) The `Subscription` resource to be used to install the cert-manager operator.
* `cifmw_cert_manager_subscription_source`: (String) The Source of `Subscription` resource to pull cert-manager operator content.
* `cifmw_cert_manager_subscription_sourcenamespace`: (String) The Source namespace of `Subscription` resource to pull cert-manager operator content.
* `cifmw_cert_manager_validate`: (Bool) Validate the cert-manager api. Default to `True`.
* `cifmw_cert_manager_version`: (String) Version of cert_manager tool. Default to `latest`.
* `cifmw_cert_manager_crds`: (List) List of cert-manager crds to cleanup.

## Examples
```YAML
---
- hosts: localhost
  vars:
    cifmw_openshift_user: "kubeadmin"
    cifmw_openshift_password: "12345678"
    cifmw_openshift_kubeconfig: "{{ ansible_user_dir }}/.crc/machines/crc/kubeconfig"
    ansible_user_dir: "{{ lookup('env', 'HOME') }}"
    cifmw_path: "{{ ansible_user_dir }}/.crc/bin:{{ ansible_user_dir }}/.crc/bin/oc:{{ ansible_user_dir }}/bin:{{ ansible_env.PATH }}"
  tasks:
    - ansible.builtin.include_role:
        name: cert_manager
```
