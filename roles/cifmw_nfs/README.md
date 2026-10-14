# cifmw_nfs
This role deploys an NFS Server.

## Privilege escalation
sudo privilege is required for this role.

## Parameters
* `cifmw_nfs_shares`: list of share names. Each one is created under `/data/<name>`
  and exported.
* `cifmw_nfs_share_ownership`: optional mapping, keyed by share name, that
  overrides the ownership of the created share directory. Each entry may set any
  of `owner`, `group` and `mode`. When `owner` or `group` is not set, that
  attribute is left untouched, so the directory keeps the ownership of the user
  that runs the role. When `mode` is not set, it falls back to
  `cifmw_nfs_share_default_mode`.
* `cifmw_nfs_share_default_mode`: mode applied to shares without a `mode`
  override (default: `0755`).
* `nftables_path`: path to nftables files
* `nftables_conf`: path to nftables config file

### Per-share ownership example
```yaml
cifmw_nfs_shares:
  - glance
  - cinder
cifmw_nfs_share_ownership:
  # Full override: glance runs as uid/gid 42415.
  glance:
    owner: "42415"
    group: "42415"
    mode: "0770"
  # Partial override: only the mode changes.
  cinder:
    mode: "0750"
# Any share not listed uses 0755, without overriding uid/gid.
```

## Examples
```
- name: Deploy NFS server on target nodes
  become: true
  hosts: "{{ groups[cifmw_nfs_target | default('computes')][0] | default([]) }}"
  vars:
    nftables_path: /etc/nftables
    nftables_conf: /etc/sysconfig/nftables.conf
  when:
    - cifmw_edpm_deploy_nfs | default(false) | bool
  ansible.builtin.import_role:
    name: cifmw_nfs
```
