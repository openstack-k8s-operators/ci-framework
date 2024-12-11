#!/usr/bin/env bash

# barbican_add_luna_minimal_client.sh
#
# This script adds the Linux Minimal Client for Thales Luna Network HSM
# to both the API and Worker images so that the HSM can be used as a PKCS#11
# backend for Barbican.
set -x
set -o errexit
set -o pipefail

BARBICAN_SRC_IMAGE_REGISTRY=${BARBICAN_SRC_IMAGE_REGISTRY:-"quay.io"}
BARBICAN_SRC_IMAGE_NAMESPACE=${BARBICAN_SRC_IMAGE_NAMESPACE:-"podified-antelope-centos9"}
BARBICAN_SRC_IMAGE_TAG=${BARBICAN_SRC_IMAGE_TAG:-"current-podified"}
BARBICAN_SRC_API_IMAGE="$BARBICAN_SRC_IMAGE_REGISTRY/$BARBICAN_SRC_IMAGE_NAMESPACE/openstack-barbican-api:$BARBICAN_SRC_IMAGE_TAG"
BARBICAN_SRC_WORKER_IMAGE="$BARBICAN_SRC_IMAGE_REGISTRY/$BARBICAN_SRC_IMAGE_NAMESPACE/openstack-barbican-worker:$BARBICAN_SRC_IMAGE_TAG"

BARBICAN_DEST_IMAGE_REGISTRY=${BARBICAN_DEST_IMAGE_REGISTRY:-"quay.io"}
BARBICAN_DEST_IMAGE_NAMESPACE=${BARBICAN_DEST_IMAGE_NAMESPACE:-"podified-antelope-centos9"}
BARBICAN_DEST_IMAGE_TAG=${BARBICAN_DEST_IMAGE_TAG:-"current-podified"}
BARBICAN_DEST_API_IMAGE="$BARBICAN_DEST_IMAGE_REGISTRY/$BARBICAN_DEST_IMAGE_NAMESPACE/openstack-barbican-api:$BARBICAN_DEST_IMAGE_TAG"
BARBICAN_DEST_WORKER_IMAGE="$BARBICAN_DEST_IMAGE_REGISTRY/$BARBICAN_DEST_IMAGE_NAMESPACE/openstack-barbican-worker:$BARBICAN_DEST_IMAGE_TAG"

# LUNA_LINUX_MINIMAL_CLIENT_DIR - location of the "linux-minimal" directory
# in your client media.  This could be a path to a mounted ISO or a path to
# the location where a tarball was extracted
LUNA_LINUX_MINIMAL_CLIENT_DIR=${LUNA_LINUX_MINIMAL_CLIENT_DIR:-"/media/lunaiso/linux-minimal"}

# LUNA_CLIENT_BIN - location of the binaries installed by the client
# software.
LUNA_CLIENT_BIN=${LUNA_CLIENT_BIN:-"/usr/safenet/lunaclient/bin"}

function install_client() {

  container=$(buildah from --tls-verify=false $1)

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

  buildah commit --tls-verify=false $container $2
  podman push --tls-verify=false $2
  buildah rm $container
}

install_client $BARBICAN_SRC_API_IMAGE $BARBICAN_DEST_API_IMAGE
install_client $BARBICAN_SRC_WORKER_IMAGE $BARBICAN_DEST_WORKER_IMAGE
