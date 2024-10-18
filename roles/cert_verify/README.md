# cert_manager

Ansible role to verify cert-manager certs post deploy

## Parameters
* `cifmw_cert_verify_check_certs`: (Bool) Check endpoints cert serial. Default to `True`.
* `cifmw_cert_verify_check_endpoints`: (Bool) Check for https on public endpoints. Default to `True`.

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
        name: cert_verify
```
