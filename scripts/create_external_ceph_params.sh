#!/bin/bash
# Create tht external_ceph_params.yaml on undercloud and update ceph_conf files in osp-controller

set -e  # Exit on any error

# Parameters - only Ceph-specific values
CEPH_NODE=${1}
CEPH_MON_HOST=${2}

# Validate required parameters
if [ -z "$CEPH_NODE" ] || [ -z "$CEPH_MON_HOST" ]; then
    echo "ERROR: Missing required parameters"
    echo "Usage: $0 <ceph_node> <ceph_mon_host>"
    echo "  ceph_node: Name of the Ceph node (e.g., osp-ext-ceph-uni04delta-ipv6-0)"
    echo "  ceph_mon_host: Comma-separated list of Ceph monitor IPs (e.g., 2620:cf:cf:cccc::6a,2620:cf:cf:cccc::6b,2620:cf:cf:cccc::6c)"
    exit 1
fi

echo "Creating external Ceph parameters file..."
echo "Using Ceph node: $CEPH_NODE"
echo "Using Ceph monitor hosts: $CEPH_MON_HOST"

# Extract Ceph credentials
echo "Fetching Ceph credentials from $CEPH_NODE..."
CEPH_OUTPUT=$(ssh "$CEPH_NODE" cat /etc/ceph/ceph.conf /etc/ceph/ceph.client.openstack.keyring)

FSID=$(echo "$CEPH_OUTPUT" | awk '/fsid =/ {print $3}')
KEY=$(echo "$CEPH_OUTPUT" | awk '/key =/ {print $3}' | tr -d '"')

if [ -z "$FSID" ] || [ -z "$KEY" ]; then
    echo "ERROR: Failed to extract FSID or KEY from Ceph configuration"
    exit 1
fi

echo "Found FSID: $FSID"
echo "Found Key: $KEY"

# Create the parameter file on undercloud
echo "Creating ~/external_ceph_params.yaml on osp-undercloud-0..."
ssh osp-undercloud-0 "cat > ~/external_ceph_params.yaml" <<EOC
parameter_defaults:
  CephClusterFSID: '$FSID'
  CephClientKey: '$KEY'
  CephManilaClientKey: '$KEY'
  CephExternalMonHost: '$CEPH_MON_HOST'
EOC

echo "Successfully created ~/external_ceph_params.yaml on osp-undercloud-0"
echo ""
echo "File contents:"
ssh osp-undercloud-0 "cat ~/external_ceph_params.yaml"

# Below code copies the ceph admin keyring and conf files that are required for adoption pre-requisites

echo "Copying Ceph configuration files from $CEPH_NODE to osp-controller-0..."

echo "Creating directory on controller..."
ssh osp-controller-0 mkdir -p $HOME/ceph_client

ssh "$CEPH_NODE" sudo cat /etc/ceph/ceph.conf | ssh osp-controller-0 "cat > $HOME/ceph_client/ceph.conf"
ssh "$CEPH_NODE" sudo cat /etc/ceph/ceph.client.admin.keyring | ssh osp-controller-0 "cat > $HOME/ceph_client/ceph.client.admin.keyring"

echo " Done! Files copied to osp-controller-0:$HOME/ceph_client/"
