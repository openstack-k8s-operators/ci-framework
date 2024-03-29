#! /usr/bin/bash
set -euo pipefail

if [[ $(vgdisplay cinder-volumes) ]]; then
    echo "cinder-volumes vg exists."
    exit 0
fi

disks=$(lsblk -o NAME,TYPE | awk '{ if ($2 == "disk" && $1 != "sda") print "/dev/"$1}')
disk_str=''

for disk in ${disks}; do
    pvcreate ${disk}
    disk_str="${disk_str} ${disk}"
done

vgcreate cinder-volumes ${disk_str}
