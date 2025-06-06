# cifmw_nfs
This role deploys an NFS Server.

## Privilege escalation
sudo privilege is required for this role.

## Parameters
* `nftables_path`: path to nftables files
* `nftables_conf`: path to nftables config file

## Examples
```
- name: Deploy NFS server on target nodes
  become: true
  hosts: "{{ groups[cifmw_nfs_target | default('computes')][0] | default([]) }}"
  vars:
    nftables_path: /etc/nftables
    nftables_conf: /etc/sysconfig/nftables.conf
  when:
    - cifmw_edpm_deploy_nfs | default('false') | bool
  ansible.builtin.import_role:
    name: cifmw_nfs
```
