# cifmw_backup_restore

Automate OpenStack on OpenShift backup and restore operations using OADP
(OpenShift API for Data Protection) and Velero. The role supports three
actions: **backup**, **restore**, and **cleanup**.

- **backup** — creates Galera database dumps, optionally backs up OVN NB/SB
  databases onto their PVCs, then creates Velero backups of labeled PVCs
  (via CSI snapshots) and cluster resources.
- **restore** — performs an ordered Velero restore sequence (PVCs,
  foundation, infrastructure, control plane, Galera, optional OVN file restore,
  full control plane resume, dataplane, EDPM), then Neutron–OVN verification and
  sync (**log** mode, then **repair**, matching the backup-restore user guide Step 12).
- **cleanup** — tears down dataplane and control-plane resources so the
  namespace is ready for a fresh restore.

## Privilege escalation

None. All cluster operations are performed through `oc` against the target
OpenShift cluster.

## Parameters

### Common

* `cifmw_backup_restore_action`: (String) Action to perform. Must be one of `backup`, `restore`, or `cleanup`. Defaults to `""` (role will fail if unset).
* `cifmw_backup_restore_namespace`: (String) Target OpenStack namespace. Defaults to `openstack`.
* `cifmw_backup_restore_oadp_namespace`: (String) Namespace where Velero/OADP is running. Defaults to `openshift-adp`.
* `cifmw_backup_restore_auto_ack`: (Boolean) Skip interactive pause prompts when `true`. Defaults to `false`.
* `cifmw_backup_restore_ovn_db`: (Boolean) When `true` (default), the **backup** path labels OVN NB/SB PVCs and runs `ovsdb-client` backup before the OADP PVC backup, and the **restore** path runs OVN NB/SB file restore after Galera (when timestamped files exist on the PVC) before resuming the full control plane. Set to `false` to skip both; post-EDPM `neutron-ovn-db-sync` still runs when OVN files were not backed up.
* `cifmw_backup_restore_ovn_db_ready_timeout`: (String) Timeout for `oc wait` on OVN database pods during OVN backup/restore. Defaults to `5m`.

### Backup

* `cifmw_backup_restore_galera_backup_timeout`: (String) Timeout for `oc wait` on Galera backup jobs. Defaults to `10m`.
* `cifmw_backup_restore_galera_storage_class`: (String) StorageClass for Galera backup PVCs. Empty string uses the cluster default. Defaults to `""`.
* `cifmw_backup_restore_galera_storage_request`: (String) Size of the Galera backup PVC. Defaults to `5Gi`.
* `cifmw_backup_restore_galera_transfer_storage_request`: (String) Size of the Galera transfer storage PVC. Defaults to `5Gi`.
* `cifmw_backup_restore_oadp_backup_timeout`: (String) Timeout for OADP PVC and resource backup completion. Defaults to `30m`.
* `cifmw_backup_restore_storage_location`: (String) Velero `BackupStorageLocation` name. Defaults to `velero-1`.
* `cifmw_backup_restore_backup_ttl`: (String) TTL for Velero backups. Defaults to `720h`.
* `cifmw_backup_restore_snapshot_move_data`: (Boolean) Enable Velero snapshot data mover. When `true`, cleanup also deletes labeled PVCs. Defaults to `true`.

### Restore

* `cifmw_backup_restore_backup_timestamp`: (String) Timestamp suffix that identifies the backup to restore (e.g. `20260311-081234`). **Required** when `cifmw_backup_restore_action` is `restore`.
* `cifmw_backup_restore_restore_timeout`: (Integer) Seconds to wait for each Velero Restore to reach a terminal phase. Defaults to `900`.
* `cifmw_backup_restore_infra_ready_timeout`: (String) Timeout for `oc wait` on `OpenStackControlPlaneInfrastructureReady`. Defaults to `20m`.
* `cifmw_backup_restore_ctlplane_ready_timeout`: (String) Timeout for `oc wait` on control plane `Ready` after removing the deployment-stage annotation. Defaults to `10m`.
* `cifmw_backup_restore_strict_restore`: (Boolean) Fail on Velero `PartiallyFailed` status when `true`; only warn when `false`. Defaults to `true`.
* `cifmw_backup_restore_restore_content`: (String) Content flag passed to `restore_galera` (`--content`). Defaults to `data`.
* `cifmw_backup_restore_edpm_deploy_timeout`: (String) Timeout for `oc wait` on the post-restore EDPM deployment. Defaults to `40m`.
* `cifmw_backup_restore_pin_pvcs`: (Boolean) Enable PVC-to-node pinning during restore for WaitForFirstConsumer storage classes. Defaults to `false`.
* Post-EDPM **Neutron–OVN** steps follow [user guide Step 12](https://github.com/openstack-k8s-operators/dev-docs/blob/main/backup-restore/user-guide.md#step-12-verify-and-sync-neutron-to-ovn): run `neutron-ovn-db-sync-util` in `log` mode first (`neutron-dist.conf`, `neutron.conf`, `neutron.conf.d`). **Repair** runs if `cifmw_backup_restore_ovn_db` is `false` (no OVN NB/SB file backup was taken), or if log-mode stdout/stderr contains a `WARNING` line—Neutron reports drift that way while still exiting 0. If OVN file backup/restore was enabled and log output has no `WARNING` lines, repair is skipped as redundant.

### Cleanup

* `cifmw_backup_restore_cleanup_ctlplane`: (Boolean) Delete control-plane resources during cleanup. Defaults to `true`.
* `cifmw_backup_restore_cleanup_dataplane`: (Boolean) Delete dataplane resources during cleanup. Defaults to `true`.

## Examples

### Running a backup

```YAML
- hosts: localhost
  tasks:
    - name: Backup OpenStack
      ansible.builtin.include_role:
        name: cifmw_backup_restore
      vars:
        cifmw_backup_restore_action: backup
        cifmw_backup_restore_namespace: openstack
        cifmw_backup_restore_auto_ack: true
```

### Restoring from a backup

```YAML
- hosts: localhost
  tasks:
    - name: Restore OpenStack
      ansible.builtin.include_role:
        name: cifmw_backup_restore
      vars:
        cifmw_backup_restore_action: restore
        cifmw_backup_restore_backup_timestamp: "20260311-081234"
        cifmw_backup_restore_auto_ack: true
```

### Cleaning up before a restore

```YAML
- hosts: localhost
  tasks:
    - name: Cleanup namespace
      ansible.builtin.include_role:
        name: cifmw_backup_restore
      vars:
        cifmw_backup_restore_action: cleanup
        cifmw_backup_restore_auto_ack: true
        cifmw_backup_restore_cleanup_ctlplane: true
        cifmw_backup_restore_cleanup_dataplane: true
```
