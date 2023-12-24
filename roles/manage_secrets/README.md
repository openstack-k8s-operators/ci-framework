# manage_secrets
Copy secret content such as pull-secret and ci-token to a known location with appropriate rights.

## Privilege escalation
None

## Parameters
### General parameters

* `cifmw_manage_secrets_basedir`: (String) Base directory for the directory tree. Default to `cifmw_basedir` which defaults to `~/ci-framework-data`.

### Pull-secret parameters

* `cifmw_manage_secrets_pullsecret_dest`: (String) Destination file for pull-secret.json. Defaults to `{{ cifmw_manage_secrets_basedir }}/secrets/pull_secret.json`.
* `cifmw_manage_secrets_pullsecret_file`: (String) Absolute path to the source pull-secret. Defaults to `null`.
* `cifmw_manage_secrets_pullsecret_content`: (String) Content of the source pull-secret. Defaults to `null`.

### CI Token parameters

* `cifmw_manage_secrets_citoken_dest`: (String) Destination file for ci-token. Defaults to `{{ cifmw_manage_secrets_basedir }}/secrets/ci_token`.
* `cifmw_manage_secrets_citoken_file`: (String) Absolute path to the source ci-token. Defaults to `null`.
* `cifmw_manage_secrets_citoken_content`: (String) Content of the source ci-token. Defaults to `null`.

### K8s configuration parameters

* `cifmw_manage_secrets_kube_dest`: (String) Destination directory for kube configuration files. Defaults to `~/.kube`.
* `cifmw_manage_secrets_kube_type`: (String) Type of kube configuration file. Must be either `config` or `kubeadmin-password`. Defaults to `null`.
* `cifmw_manage_secrets_kube_file`: (String) Absolute path to the source kube configuration file. Defaults to `null`.
* `cifmw_manage_secrets_kube_content:` (String) Content of the kube configuration file. Defaults to `null`.

### SSH keypair secrets

* `cifmw_manage_secrets_ssh_type`: SSH keypair algorithm, as listed by [community.crypto.openssh_keypair](https://docs.ansible.com/ansible/latest/collections/community/crypto/openssh_keypair_module.html#parameter-type). Defaults to `ecdsa`.
* `cifmw_manage_secrets_ssh_size`: SSH private key size, as listed by [community.crypto.openssh_keypair](https://docs.ansible.com/ansible/latest/collections/community/crypto/openssh_keypair_module.html#parameter-size). Defaults to `521`.
* `cifmw_manage_secrets_dataplane_ssh_name`: File name for the dataplane SSH keypair. Defaults to `ansibleee-ssh-key-id_ecdsa`.
* `cifmw_manage_secrets_dataplane_ssh_metaname`: Metadata for the dataplane ssh keypair. Defaults to `dataplane-ansible-ssh-private-key-secret`.

### OSP secrets

* `cifmw_manage_secrets_ospsecrets_manifests_dest`: (String) Destination directory for OSP secrets manifest
* `cifmw_manage_secrets_ospsecrets_list`: (List) Secrets parameter definitions. See molecule test for example.

## File versus Content
You can set either a file OR a content for the pull-secret and ci-token secrets. You can't set both.

## Examples

```YAML
- name: Initialize manage_secrets
  ansible.builtin.import_role:
    name: manage_secrets

- name: Push my local pull-secret
  vars:
    cifmw_manage_secrets_pullsecret_file: "{{ lookup('env', 'HOME') }}/pull-secret.txt"
  ansible.builtin.include_role:
    name: manage_secrets
    tasks_from: pull_secret.yml

- name: Create a ci-token with inline content
  vars:
    cifmw_manage_secrets_citoken_content: "sha256~AAABBCC123"
  ansible.builtin.include_role:
    name: manage_secrets
    tasks_from: ci_token.yml
```

In some cases, you may want to copy some content from the hypervisor to a virtual machine - this is especially
true for the kubeconfig and kubeadmin-password files. In such a case, the "easiest" way is to `slurp` the content
and pass it down:

```YAML
- name: Get kubeaconfig content
  register: _kubeconfig
  ansible.builtin.slurp:
    path: "{{ ansible_user_dir }}/ci-framework-data/artifacts/kubeconfig"

- name: Delegate block to controller-0
  delegate_to: controller-0
  remote_user: zuul
  vars:
    cifmw_manage_secrets_basedir: "/home/zuul/ci-framework-data"
  block:
    - name: Initialize manage_secrets
      ansible.builtin.import_role:
        name: manage_secrets

    - name: Inject kubeconfig
      vars:
        cifmw_manage_secrets_kube_type: "config"
        cifmw_manage_secrets_kube_content: "{{ _kubeconfig.content | b64decode }}"
      ansible.builtin.include_role:
        name: manage_secrets
        tasks_from: kube.yml
```
