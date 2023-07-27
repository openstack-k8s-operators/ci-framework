# cifmw_block_device

Creates a virtual block device with logical volumes. Useful for
deploying Ceph on a virtual machine which does not have any
block devices except for root. Creates a systemd unit so the
virtual block device comes back online during reboot.

The target system must have 7 GB of available disk space at minimum.

This role will recreate the block device on each run. Thus, if there
is data on the block device from the previous run it will delete it.
The assumption is that the block device exists for testing and that
rebuilding the environment quickly is more important preserving any
test data.

## Privilege escalation

Requires root on the remote system to create loop back device and
systemd unit.

## Parameters

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

## Examples

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
The following will stop and disable the systemd unit file which starts
the virtual block device, remove the logical volume, volume group, and
physical volume, and delete the loopback device and its backing file.
```
- import_role:
    name: cifmw_block_device
    tasks_from: cleanup
```
