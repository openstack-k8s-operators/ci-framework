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
* `cifmw_nfs_server_ip`: optional explicit address for the NFS listener. When
  omitted, the role resolves it from the target's IPSet reservation.
* `cifmw_nfs_clients_cidr`: optional explicit client CIDR for NFS exports. When
  omitted, the role resolves it from the target's IPSet reservation.
* `cifmw_nfs_debug`: log target interfaces, routes, selected endpoint, listener,
  and exports. Defaults to `false`.
* `cifmw_nfs_target`: inventory group or host to run NFS on. Defaults to
  `computes`.
* `nftables_path`: path to nftables files
* `nftables_conf`: path to nftables config file

When the target is the `controller` host, provide both `cifmw_nfs_server_ip` and
`cifmw_nfs_clients_cidr` to bypass the EDPM IPSet lookup. The role opens TCP
2049 through firewalld when it is active, or adds a runtime INPUT rule otherwise.
Other target groups retain the EDPM nftables behavior.

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
  hosts: >-
    {{ groups.get(cifmw_nfs_target | default('computes'),
                   [cifmw_nfs_target | default('computes')]) | first }}
  vars:
    nftables_path: /etc/nftables
    nftables_conf: /etc/sysconfig/nftables.conf
  when:
    - cifmw_edpm_deploy_nfs | default(false) | bool
  ansible.builtin.import_role:
    name: cifmw_nfs
```
