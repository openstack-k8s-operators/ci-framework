## Role: install_ca
It may happen we need to deploy custom CA on the host soon enough

In such case, we want to deploy it as soon as possible, since it may affect
our capabilities to access remote package repositories, among possible targets.

### Privilege escalation
- Gain write access in the standard PKI location for custom CA
- Gain access to update the CA trust ring

### Parameters
* `cifmw_install_ca_bundle_inline`: (String) Inline representation of the CA bundle we want to inject.
* `cifmw_install_ca_bundle_src`: (String) Path to the CA bundle we want to inject.
* `cifmw_install_ca_trust_dir`: (String) Directory where we put custom CA. Must be known by the update-ca-trust command. Defaults to ` /etc/pki/ca-trust/source/anchors/`.
* `cifmw_install_ca_update_cmd`: (String) Command to run in order to update the CA trust ring. Defaults to `update-ca-trust`.

### Example
```YAML
- name: Inject Red Hat downstream CA bundle
  vars:
    cifmw_install_ca_bundle_src: /etc/pki/trusted/rh.crt
  ansible.builtin.include_role:
    role: install_ca

- name: Inject custom CA from inline content
  vars:
      cifmw_install_ca_bundle_inline: |
        -----BEGIN CERTIFICATE-----
        ....
        -----END CERTIFICATE-----
  ansible.builtin.include_role:
    role: install_ca
```
