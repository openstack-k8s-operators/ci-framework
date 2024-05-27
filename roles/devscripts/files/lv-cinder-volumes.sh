#! /usr/bin/bash
set -euo pipefail

_disks=${OSP_CINDER_VOL_DISKS:-''}

if [[ $(vgdisplay cinder-volumes) ]]; then
    echo "cinder-volumes vg exists."
    exit 0
fi

disk_str=''
for disk in ${_disks}; do
    pvcreate ${disk}
    disk_str="${disk_str} ${disk}"
done

vgcreate cinder-volumes ${disk_str}
