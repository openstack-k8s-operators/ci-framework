# Deploy local CRC VM

## Local tests

If you would like to run the molecule tests locally, you should have already
deployed VM with CRC. So far, in many places it is required to have `zuul` as a
main user. Below there would be an example how to deploy local CRC node
and a simply script, how to run example molecule test.

### Setup the CRC node

Here, we assume that you already create a VM that "fits" [CRC requirements](https://crc.dev/docs/installing/#_for_openshift_container_platform).
You should be aware, that some molecule tests would spawn few more virtual
machines on the same host (nested VMs), so it would be recommended to
deploy CRC on VM with minimum hardware:

- 8 vCPUs
- 18 GB RAM
- 100 GB disk space
- CentOS 9 stream or RHEL 9
- main user should be `zuul` (currently it is IMPORTANT)

To setup a CRC on the node, you need to have [pull-secret.txt](https://cloud.redhat.com/openshift/create/local).

You can continue deploy CRC using the [guide](https://crc.dev/docs/installing/),
or run Ansible tool described below.

#### Automated way to deploy CRC

Set required variables then run below script to setup the CRC:

```shell
# Set important variables
CRC_VM_IP=''
PULL_SECRET=''

# Install required packages
sudo dnf install -y git ansible-core

# Clone sf-infra repo
git clone https://github.com/softwarefactory-project/sf-infra
cd sf-infra

# Setup inventory file
cat << EOF > inventory.yaml
---
all:
  hosts:
    crc.dev:
      ansible_port: 22
      ansible_host: ${CRC_VM_IP}
      ansible_user: zuul
  vars:
    crc_parameters: "--memory 14336 --disk-size 80 --cpus 6"
    openshift_pull_secret: |
      ${PULL_SECRET}
EOF

# Create playbook
cat << EOF > crc-deploy.yaml
- name: Deploy CRC
  hosts: crc.dev
  tasks:
    - name: Fail when crc_version is not set or openshift_pull_secret is not set
      ansible.builtin.fail:
      when:
        - crc_version is not defined
        - openshift_pull_secret is not defined

    - name: Ensure cloud init is installed and is running
      ansible.builtin.include_role:
        name: next-gen/crc-image
        tasks_from: prepare_vm.yaml

    - name: Enable nested virt, install other kernel and configure other packages
      ansible.builtin.include_role:
        name: next-gen/crc-image
        tasks_from: configure_vm.yaml

    - name: "Run CRC {{ crc_version }} deployment"
      ansible.builtin.include_role:
        name: extra/crc

    - name: Ensure cloud init is installed and snapshot would be able to boot
      ansible.builtin.include_role:
        name: next-gen/crc-image
        tasks_from: post_vm.yaml
EOF

# Run Ansible to deploy CRC
ansible-playbook -i inventory.yaml \
    -e "modify_etcd=false" \
    -e "extracted_crc=false" \
    -e "nested_crc=true" \
    -e "crc_version=2.48.0" \
    crc-deploy.yaml

```

Helpful tip:
CRC deployment took a while, so it is good to stop the virtual machine (VM),
make a backup of the VM disk qcow2 in safe place. It would be helpful when
you want to make a CRC VM from scratch, all necessary files would be already
downloaded, so you will save time.

To start CRC after VM "shutdown", just execute:

```shell
# Set important variables
CRC_VM_IP=''

# Setup inventory file
cat << EOF > inventory.yaml
---
all:
  hosts:
    crc.dev:
      ansible_port: 22
      ansible_host: ${CRC_VM_IP}
      ansible_user: zuul
  vars:
    crc_parameters: "--memory 14336 --disk-size 80 --cpus 6"
EOF

cat << EOF > start-crc.yaml
- hosts: crc.dev
  tasks:
    - name: Start crc
      block:
        - name: Execute crc start command
          shell: |
            /usr/local/bin/crc start {{ crc_parameters }} &> ~/crc-start.log
          register: _crc_start_status
          retries: 3
          delay: 30
          until: _crc_start_status.rc != 1

        - name: Show available nodes
          shell: |
            /usr/bin/kubectl get nodes
EOF
```

#### Enable OpenShift Console

Sometimes, it is needed to check how the OpenShift is working via Web interface.
In that case, we can enable such feature in CRC nested, but executing playbook:

```shell
---
# FROM: https://github.com/softwarefactory-project/sf-infra/blob/master/roles/extra/crc/tasks/console.yaml
- name: Enable console
  hosts: crc.dev
  tasks:
    - name: Install required packages
      become: true
      ansible.builtin.package:
        name:
          - haproxy
          - policycoreutils-python-utils
        state: present

    - name: Get CRC ip address
      ansible.builtin.shell: |
        crc ip
      register: _crc_ip

    - name: Get domain
      ansible.builtin.shell: |
        oc get ingresses.config/cluster -o jsonpath={.spec.domain}
      register: _crc_domain

    # From https://crc.dev/crc/#setting-up-remote-server_gsg
    - name: Set SELinux
      become: true
      community.general.seport:
        ports: 6443
        proto: tcp
        setype: http_port_t
        state: present

    - name: Create haproxy config
      become: true
      ansible.builtin.copy:
        content: |
          global
              log /dev/log local0

          defaults
              balance roundrobin
              log global
              maxconn 100
              mode tcp
              timeout connect 5s
              timeout client 500s
              timeout server 500s

          listen apps
              bind 0.0.0.0:80
              server crcvm {{ _crc_ip.stdout }}:80 check

          listen apps_ssl
              bind 0.0.0.0:443
              server crcvm {{ _crc_ip.stdout }}:443 check

          listen api
              bind 0.0.0.0:6443
              server crcvm {{ _crc_ip.stdout }}:6443 check
        dest: /etc/haproxy/haproxy.cfg
      register: haproxy_status

    - name: Restart service
      become: true
      ansible.builtin.systemd:
        name: haproxy
        state: restarted
        enabled: true
        daemon_reload: true
      when: haproxy_status.changed

    - name: Generate local machine etc hosts template
      ansible.builtin.copy:
        content: >
          # Generate /etc/host entry.

          echo -e "Run this on your machine\n\n"

          echo "$(ip route get 1.2.3.4 | awk '{print $7}' | tr -d '\n')
          console-openshift-console.{{ _crc_domain.stdout }}
          api.crc.testing canary-openshift-ingress-canary.{{ _crc_domain.stdout }}
          default-route-openshift-image-registry.{{ _crc_domain.stdout }}
          downloads-openshift-console.{{ _crc_domain.stdout }}
          oauth-openshift.{{ _crc_domain.stdout }} {{ _crc_domain.stdout }} | sudo tee -a /etc/hosts"

          echo -e "\nNow the console is available at this address: https://console-openshift-console.apps-crc.testing/"
        dest: console-access.sh

```

Then, execute a script on the `crc` VM:

```shell
./console-access.sh
```

It should create entries in `/etc/hosts`. It is not needed on `CRC` VM, but
you need to copy it to your local (laptop) `/etc/hosts`.
Example how it should look like:

```shell
CRC_VM_IP=''
cat << EOF | sudo tee -a /etc/hosts
$CRC_VM_IP console-openshift-console.apps-crc.testing api.crc.testing canary-openshift-ingress-canary.apps-crc.testing default-route-openshift-image-registry.apps-crc.testing downloads-openshift-console.apps-crc.testing oauth-openshift.apps-crc.testing apps-crc.testing
EOF
```

After that operation, the OpenShift console should be available on this
address: [https://console-openshift-console.apps-crc.testing/](https://console-openshift-console.apps-crc.testing/)
