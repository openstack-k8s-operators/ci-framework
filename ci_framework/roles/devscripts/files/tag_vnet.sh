#! /usr/bin/bash
#
# Usage:
#     bash tag_vnet.sh ens1f1
#
# Options
#
#    <iface>    Name of the trunk interface
set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Invalid number of arguments"
    exit 1
fi

iface=${1}

vlans=$(nmcli -f bridge-port.vlans con show ${iface} | awk '{ print $2 }' )
master_id=$(nmcli -f connection.master con show ${iface} | awk '{ print $2 }' )
bridge_name=$(nmcli -f connection.id con show ${master_id} | awk '{ print $2 }')
vlans=${vlans/,/' '}

# Gather list of VMs
vm_names=$(virsh -c qemu:///system list --name | grep '_worker') || true
if [ -z "${vm_names}" ]; then
    vm_names=$(virsh -c qemu:///system list --name | grep '_master')
fi

for vlan_id in ${vlans}; do
    for vm in ${vm_names}; do
        vnet_iface=$(virsh -c qemu:///system domiflist ${vm} | \
                    grep ${bridge_name} | awk '{ print $1 }')
        if [ -n "${vnet_iface}" ]; then
            bridge vlan add dev ${vnet_iface} vid ${vlan_id}
        fi
    done
done

echo "Successfully attached all vlans"
