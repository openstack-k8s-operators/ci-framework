#!/bin/bash
#
# Usage:
#  bash add_bridge_port.sh <bridge-name> <iface>
#
#      <bridge-name>    Name of the bridge
#      <iface>          network device name
set -euo pipefail

BRIDGE_NAME=${1}
IFACE_NAME=${2}

CONN_NAME=$(nmcli -t -f GENERAL.CONNECTION dev show ${IFACE_NAME} | cut -d ':' -f 2)
PORT_NAME=${BRIDGE_NAME}-p0

check_port=$(nmcli con show | grep -c ${PORT_NAME}) || true

if [ ${check_port} -ne 0 ]; then
    echo "Bridge port available. Nothing to do"
    exit 0
fi

check_iface=$(nmcli dev status | grep -c ${IFACE_NAME}) || true

if [ ${check_iface} -eq 0 ]; then
    echo "Invalid device name"
    exit 1
fi

# There are interference when there is a another connection for the same interface.
dummy_con=$(nmcli -t con show | grep ${IFACE_NAME} | grep -v -e "${IFACE_NAME}$" | cut -d ':' -f 1) || true
if [ -n "${dummy_con}" ]; then
    echo "There exists a connection that could interfer"
    nmcli con delete "${dummy_con}"
fi

nohup bash -c "
    nmcli con down \"${CONN_NAME}\"
    nmcli con delete \"${CONN_NAME}\"
    nmcli con add connection.type 802-3-ethernet \
        connection.id ${PORT_NAME} \
        connection.interface-name ${IFACE_NAME} \
        connection.master ${BRIDGE_NAME} \
        connection.slave-type bridge
"

echo "${IFACE_NAME} is added as a port to ${BRIDGE_NAME} successfully."
