#! /usr/bin/bash
set -euo pipefail

if [[ $(lvdisplay /dev/cinder_volumes_vg/cinder-volumes) ]]; then
    echo "cinder-volumes vg exists."
    exit 0
fi

disks=$(lsblk -o NAME,TYPE | awk '{ if ($2 == "disk" && $1 != "sda") print "/dev/"$1}')
disk_str=''

for disk in ${disks}; do
    pvcreate ${disk}
    disk_str="${disk_str} ${disk}"
done

vgcreate cinder_volumes_vg ${disk_str}
lvcreate -l 100%FREE -n cinder-volumes cinder_volumes_vg
