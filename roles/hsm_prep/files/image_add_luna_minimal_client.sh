#!/usr/bin/env bash

# barbican_add_luna_minimal_client.sh
#
# This script adds the Linux Minimal Client for Thales Luna Network HSM
# to both the API and Worker images so that the HSM can be used as a PKCS#11
# backend for Barbican.

set -o errexit
set -o pipefail

BARBICAN_IMAGE_NAMESPACE=${BARBICAN_IMAGE_NAMESPACE:-"podified-antelope-centos9"}
BARBICAN_IMAGE_TAG=${BARBICAN_IMAGE_TAG:-"current-podified"}
BARBICAN_API_IMAGE="quay.io/$BARBICAN_IMAGE_NAMESPACE/openstack-barbican-api:$BARBICAN_IMAGE_TAG"
BARBICAN_WORKER_IMAGE="quay.io/$BARBICAN_IMAGE_NAMESPACE/openstack-barbican-worker:$BARBICAN_IMAGE_TAG"

# LUNA_LINUX_MINIMAL_CLIENT_DIR - location of the "linux-minimal" directory
# in your client media.  This could be a path to a mounted ISO or a path to
# the location where a tarball was extracted
LUNA_LINUX_MINIMAL_CLIENT_DIR=${LUNA_LINUX_MINIMAL_CLIENT_DIR:-"/media/lunaiso/linux-minimal"}

# LUNA_CLIENT_BIN - location of the binaries installed by the client
# software.
LUNA_CLIENT_BIN=${LUNA_CLIENT_BIN:-"/usr/safenet/lunaclient/bin"}

function install_client() {

  container=$(buildah from $1)

  # set required env
  buildah config --env ChrystokiConfigurationPath=/usr/local/luna $container

  # add linux-minimal client
  buildah add --chown root:root $container $LUNA_LINUX_MINIMAL_CLIENT_DIR /usr/local/luna
  buildah run --user root $container -- mkdir -p /usr/local/luna/config/certs
  buildah run --user root $container -- mkdir -p /usr/local/luna/config/token/001
  buildah run --user root $container -- touch /usr/local/luna/config/token/001/token.db
  buildah add --chown root:root $container $LUNA_CLIENT_BIN/lunacm /usr/local/bin/
  buildah add --chown root:root $container $LUNA_CLIENT_BIN/vtl /usr/local/bin/
  buildah add --chown root:root $container $LUNA_CLIENT_BIN/multitoken /usr/local/bin/
  buildah add --chown root:root $container $LUNA_CLIENT_BIN/ckdemo /usr/local/bin/

  buildah commit $container ${1}-luna
  buildah rm $container
}

install_client $BARBICAN_API_IMAGE
install_client $BARBICAN_WORKER_IMAGE
