#!/bin/bash
set -eu

test "$*" = "build-parallel base,edpm/edpm-bootc"
test "$STREAM" = master
test "$REGISTRY/$NAMESPACE" = localhost/openstack
test "$TAG" = test-s2i
test "$GIT_REVISION" = 0123456789abcdef0123456789abcdef01234567
test "$SOURCE_CACHE" = false
test -z "$BUILD_FLAGS"
grep -qx 'EDPM_BASE_IMAGE=quay.io/centos-bootc/centos-bootc:stream10' "$BUILD_FLAGS_FILE"
grep -qx 'FIPS=1' "$BUILD_FLAGS_FILE"
grep -qx 'USER_PACKAGES=extra-package another-package' "$BUILD_FLAGS_FILE"
touch "$BUILD_LOGS_DIR/s2i-build-passed"
