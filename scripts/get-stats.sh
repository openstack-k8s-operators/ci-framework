#!/bin/bash

# Copyright Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

## Shell Opts ----------------------------------------------------------------
set -o pipefail
set -x

DURATION_TIME=${DURATION_TIME:-10}

NODE_NAMES=$(/usr/local/bin/oc get node -o name -l node-role.kubernetes.io/worker)
if [ -z "$NODE_NAMES" ]; then
    echo "Unable to determine node name with 'oc' command."
    exit 1
fi

for node in $NODE_NAMES; do
    /usr/local/bin/oc debug "${node}" -T -- chroot /host /usr/bin/bash -c "crictl stats -a -s ${DURATION_TIME} |  (sed -u 1q; sort -k 2 -h -r)"
done
