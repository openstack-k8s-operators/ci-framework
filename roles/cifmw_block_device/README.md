# cifmw_block_device

Creates block devices with logical volumes for Ceph OSD testing.
Supports two modes:

- **Loop mode** (default): creates a loop-backed file with LVM on top
  and a systemd unit to restore it across reboots. Useful for VMs
  that have no spare block devices.
- **Thin-pool mode**: creates thin-provisioned LVs from an existing
  VG thin pool. Useful for bare-metal hosts that already have a
  thin pool with available space.

The mode is selected by `cifmw_block_device_thin_pool`: when non-empty
the role uses thin-pool mode, otherwise loop mode.

## Privilege escalation

Requires root on the remote system to create devices and LVM objects.

## Parameters

### Common

* `cifmw_block_device_thin_pool`: VG/pool path for thin-pool mode,
  e.g. `vg/lv_thinpool`. When empty (default), loop mode is used.

### Loop mode

* `cifmw_block_device_image_file`: Name of the `dd'd` image file
  (default `/var/lib/ceph-osd.img`)
* `cifmw_block_device_size`: Size of the virtual block device (default
  `7G`)
* `cifmw_block_device_loop`: Name of the loop device (default
  `/dev/loop3`)
* `cifmw_block_vg_name`: Name of the logical volume group (default
  `ceph_vg`)
* `cifmw_block_lv_name`: Name of the logical volume (default
  `ceph_lv_data`)
* `cifmw_block_systemd_unit_file`: Name of the systemd unit which
  restores the device on system startup (default
  `/etc/systemd/system/ceph-osd-losetup.service`)

### Thin-pool mode

* `cifmw_block_device_thin_lv_size`: Size of each thin LV (default
  `50G`)
* `cifmw_block_device_thin_lv_name`: Name of the thin LV to create
  (default `ceph_osd`)

## Output

Both modes append to the `cifmw_block_device_paths` list fact.
Each role invocation adds one entry, so when called in a loop
the list accumulates all created device paths (e.g.
`["/dev/ceph_vg0/ceph_lv0", "/dev/ceph_vg1/ceph_lv1"]` or
`["/dev/vg/ceph_osd_0", "/dev/vg/ceph_osd_1"]`).

## Examples

### Loop mode (default)

The following will create a 7 GB block device on the target system
using the defaults above.
```
- import_role:
    name: cifmw_block_device
```
The `lsblk` command should then show an available block
device.
```
[root@edpm-compute-0 ~]# lsblk
NAME                   MAJ:MIN RM SIZE RO TYPE MOUNTPOINTS
loop3                    7:3    0   7G  0 loop
└─ceph_vg-ceph_lv_data 253:0    0   7G  0 lvm
vda                    252:0    0  20G  0 disk
└─vda1                 252:1    0  20G  0 part /
[root@edpm-compute-0 ~]#
```
If a Ceph spec file has the following, then an OSD will be created
which uses the virtual block device.
```
data_devices:
  paths:
  - /dev/ceph_vg/ceph_lv_data
```

### Thin-pool mode

```yaml
- include_role:
    name: cifmw_block_device
  vars:
    cifmw_block_device_thin_pool: "vg/lv_thinpool"
    cifmw_block_device_thin_lv_size: "50G"
    cifmw_block_device_thin_lv_name: "ceph_osd_0"
```
Ceph spec entry:
```yaml
data_devices:
  paths:
  - /dev/vg/ceph_osd_0
```

### Cleanup

```yaml
- import_role:
    name: cifmw_block_device
    tasks_from: cleanup
```
For thin-pool mode, pass `cifmw_block_device_thin_pool` and
`cifmw_block_device_thin_lv_name` so the correct cleanup path runs.
