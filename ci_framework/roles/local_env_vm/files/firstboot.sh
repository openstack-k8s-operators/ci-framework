#!/usr/bin/env bash
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
set -xeuo

/usr/bin/growpart /dev/vda 1
/usr/sbin/xfs_growfs /
/usr/bin/systemctl disable --now cloud-init
/usr/sbin/useradd -m -d /home/zuul -G libvirt zuul
echo 'zuul ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/zuul
/usr/bin/cp /root/pull-secret /home/zuul/
/usr/bin/cp -a /root/.ssh /home/zuul/
/usr/bin/chown -R zuul: /home/zuul/.ssh /home/zuul/pull-secret
sudo -u zuul git config --global pull.rebase true
sudo -u zuul ssh-keygen -t ed25519 -b 512 -f /home/zuul/.ssh/id_ed25519 -N ''
cat /home/zuul/.ssh/id_ed25519.pub | sudo -u zuul tee -a /home/zuul/.ssh/authorized_keys
sudo -u zuul mkdir /home/zuul/src
