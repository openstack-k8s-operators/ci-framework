# ocp_ipi
Please explain the role purpose.

## Privilege escalation
If apply, please explain the privilege escalation done in this role.

## Parameters
* `param_1`: this is an example

## Examples


```bash
ansible-playbook -i custom/host24-inventory.yml custom/ipi/run.yaml -e @custom/ipi/vars.yaml -e @custom/ipi/libvirt_manager_config.yaml
```

### Libvirt Config (~/custom/ipi/libvirt_manager_config.yaml)

```yaml
cifmw_libvirt_manager_pub_net: br-mgmt
cifmw_libvirt_manager_fixed_networks:
  - osp_trunk
  - br-mgmt
  - ocpbm
  - ocppr

cifmw_libvirt_manager_configuration:
  networks:
    br-mgmt: |-
      <network>
        <name>br-mgmt</name>
        <forward mode='open'/>
        <bridge name='br-mgmt' stp='on' delay='0'/>
        <ip
          family='ipv6'
          address='fc00:1:ffff::1'
          prefix='64'
        />
        <dns enable='no'/>
      </network>
    ocpbm: |-
      <network>
        <name>ocpbm</name>
        <forward mode='open'/>
        <bridge name='ocpbm' stp='on' delay='0'/>
        <ip
          family='ipv6'
          address='fc00:1:1::1'
          prefix='64'
        />
        <dns enable='no'/>
      </network>
    ocppr: |-
      <network>
        <name>ocppr</name>
        <forward mode='open'/>
        <bridge name='ocppr' stp='on' delay='0'/>
        <ip
          family='ipv6'
          address='fc00:1:2::1'
          prefix='64'
        />
        <dns enable='no'/>
      </network>
    osp_trunk: |-
      <network>
        <name>osp_trunk</name>
        <forward mode='open'/>
        <bridge name='osp_trunk' stp='on' delay='0'/>
        <ip
          family='ipv6'
          address='fc00:1:3::1'
          prefix='64'
        />
        <dns enable='no'/>
      </network>
  vms:
    master:
      amount: 3
      start: false
      manage: false
      disksize: 100
      memory: 16
      cpus: 8
      image_local_dir: "{{ cifmw_basedir }}/images/"
      disk_file_name: 'blank'
      nets:
        - ocppr
        - ocpbm
        - osp_trunk
```

### Variables - (~/custom/ipi/vars.yaml)

```yaml
---
# ocp_ipi
cifmw_ocp_ipi_ntp_server: _CHANGE_ME_
cifmw_ocp_ipi_ssh_pub_keys:
  - 'ssh-rsa _CHANGE_ME_'

cifmw_target_host: hypervisor-1
cifmw_ocp_ipi_dnsmasq_inventory_host: "{{ cifmw_target_host }}"
cifmw_basedir: "{{ ansible_user_dir }}/ci-framework-data"
cifmw_path: "{{ ansible_user_dir }}/bin:{{ ansible_env.PATH }}"
cifmw_manage_secrets_pullsecret_file: "_CHANGE_ME_"

cifmw_install_ca_url: "_CHANGE_ME"

# cifmw_sushy_redfish_bmc_protocol: redfish

# repo-setup related vars
_oso_release: "{{ cifmw_oso_release | default('osp18') }}"
_rhel_version: "{{ cifmw_rhel_version | default('9.4') }}"
_ceph_version: "{{ cifmw_ceph_release | default('ceph-7.0-rhel-9') }}"
_default_rhos_release_args: "{{ _ceph_version }} -r {{ _rhel_version }}"

cifmw_repo_setup_branch: "{{ _oso_release }}"
cifmw_repo_setup_dlrn_uri: "_CHANGE_ME_"
cifmw_repo_setup_os_release: "rhel"
cifmw_repo_setup_enable_rhos_release: true
cifmw_repo_setup_rhos_release_rpm: "_CHANGE_ME_"
cifmw_repo_setup_rhos_release_args: "{{ _default_rhos_release_args }}"
cifmw_repo_setup_dist_major_version: "{{ ansible_distribution_major_version }}"
cifmw_repo_setup_env:
  CURL_CA_BUNDLE: "/etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt"
cifmw_discover_latest_image_base_url: "__CHANGE_ME_"
cifmw_discover_latest_image_qcow_prefix: "rhel-guest-image-{{ _rhel_version }}-"
cifmw_discover_latest_image_images_file: "SHA256SUM"

# ci-setup
cifmw_ci_setup_yum_repos:
  - name: crb
    baseurl: "_CHANGE_ME_"
    description: Code ready builder


cifmw_root_partition_id: >-
    {{
      (cifmw_repo_setup_os_release is defined and cifmw_repo_setup_os_release == 'rhel') |
      ternary(4, 1)
    }}
```

### Playbook - (~/custom/ipi/run.yaml)

```yaml
- name: Deploy OCP using IPI
  hosts: "{{ cifmw_target_host | default('localhost') }}"
  gather_facts: true
  vars:
    _data_dir: "{{ ansible_user_dir }}/ci-framework-data"
  tasks:
    - name: Install custom CA if needed
      ansible.builtin.import_role:
        name: install_ca

    - name: CI Setup
      ansible.builtin.include_role:
        name: ci_setup

    - name: Install libvirt
      ansible.builtin.include_role:
        name: libvirt_manager

    - name: Discover latest image
      ansible.builtin.include_role:
        name: discover_latest_image

    - name: List VMs
      register: _list_vms
      community.libvirt.virt:
        command: list_vms

    - name: Build the the nat64-applaince image
      when: "'nat64-appliance' not in _list_vms.list_vms"
      ansible.builtin.include_role:
        name: nat64_appliance

    - name: Deploy the nat64 environment
      when: "'nat64-appliance' not in _list_vms.list_vms"
      ansible.builtin.include_role:
        name: nat64_appliance
        tasks_from: deploy.yml

    - name: Deploy the libvirt layout
      ansible.builtin.include_role:
        name: libvirt_manager
        tasks_from: deploy_layout.yml

    - name: Install the cifmw dnsmasq service
      vars:
        cifmw_dnsmasq_exclude_lo: true
        cifmw_dnsmasq_enable_dns: true
        cifmw_dnsmasq_interfaces:
          - br-mgmt
          - ocpbm
        cifmw_dnsmasq_raw_config: |
          no-resolv
          enable-ra
        cifmw_dnsmasq_forwarders:
          - 'fc00:abcd:abcd:fc00::2'
      ansible.builtin.include_role:
        name: dnsmasq

    - name: Set up dnsmasq for ocpbm network
      vars:
        cifmw_dnsmasq_network_name: ocpbm
        cifmw_dnsmasq_network_state: present
        cifmw_dnsmasq_network_definition:
          ranges:
            - label: ocpbm
              start_v6: fc00:1:1::1
              prefix_length_v6: 64
              domain: ocp.openstack.lab
      ansible.builtin.include_role:
        name: dnsmasq
        tasks_from: manage_network.yml

    - name: Deploy Sushy Emulator
      vars:
        cifmw_sushy_emulator_listen_ip: 'fc00:1:1::1'
        cifmw_sushy_emulator_hypervisor_target: "{{ cifmw_target_host | default('localhost') }}"
        cifmw_sushy_emulator_install_type: podman
        cifmw_sushy_emulator_hypervisor_target_connection_ip: "{{ cifmw_networking_definition.networks.ocpbm.gateway }}"
      ansible.builtin.include_role:
        name: sushy_emulator

    - name: Generate libvirt_manager_bm_info_data fact
      when: item.key is match('cifmw-')
      vars:
        _host: "{{ item.key | replace('cifmw-', '') }}"
        _uefi: >-
          {% set _type = _host | regex_replace('-[0-9]+$', '') -%}
          {{ _cifmw_libvirt_manager_layout.vms[_type].uefi | default(false) | bool }}
        _data: |
          "{{ _host }}":
            boot_mode: "{{ _uefi | ternary('UEFI', 'legacy') }}"
            uuid: "{{ item.value }}"
            connection: "{{ cifmw_sushy_redfish_bmc_protocol | default('redfish-virtualmedia') ~ '+' ~ _sushy_url }}/redfish/v1/Systems/{{ item.value }}"
            username: "{{ cifmw_redfish_username | default('admin') }}"
            password: "{{ cifmw_redfish_password | default('password') }}"
        _with_nics: >-
          {{
            _data | from_yaml |
            combine({_host: {'nics': cifmw_libvirt_manager_mac_map[_host]}},
                    recursive=true)
          }}
      ansible.builtin.set_fact:
        libvirt_manager_bm_info_data: >-
          {{
            libvirt_manager_bm_info_data | default({}) |
            combine((_with_nics | from_yaml), recursive=true) |
            combine((_oringal_cifmw_baremetal_hosts | default({}) | from_yaml), recursive=true)
          }}
      loop: "{{ cifmw_libvirt_manager_uuids | dict2items }}"

    - name: Output baremetal info file
      vars:
        _content:
          cifmw_baremetal_hosts: "{{ libvirt_manager_bm_info_data }}"
      ansible.builtin.copy:
        dest: "{{ cifmw_basedir }}/artifacts/baremetal-info.yml"
        content: "{{ _content | to_nice_yaml }}"
        mode: "0644"

    - name: Add OCP node master-0 to dnsmasq
      vars:
        cifmw_dnsmasq_host_network: ocpbm
        cifmw_dnsmasq_host_state: present
        cifmw_dnsmasq_host_mac: "{{ (cifmw_libvirt_manager_mac_map['master-0'] | selectattr('network', 'equalto', 'ocpbm') | first ).mac }}"
        cifmw_dnsmasq_host_ipv6: 'fc00:1:1::200'
        cifmw_dnsmasq_host_name: master-0.ocp.openstack.lab
      ansible.builtin.include_role:
        name: dnsmasq
        tasks_from: manage_host.yml

    - name: Add OCP node master-1 to dnsmasq
      vars:
        cifmw_dnsmasq_host_network: ocpbm
        cifmw_dnsmasq_host_state: present
        cifmw_dnsmasq_host_mac: "{{ (cifmw_libvirt_manager_mac_map['master-1'] | selectattr('network', 'equalto', 'ocpbm') | first ).mac }}"
        cifmw_dnsmasq_host_ipv6: 'fc00:1:1::201'
        cifmw_dnsmasq_host_name: master-1.ocp.openstack.lab
      ansible.builtin.include_role:
        name: dnsmasq
        tasks_from: manage_host.yml

    - name: Add OCP node master-2 to dnsmasq
      vars:
        cifmw_dnsmasq_host_network: ocpbm
        cifmw_dnsmasq_host_state: present
        cifmw_dnsmasq_host_mac: "{{ (cifmw_libvirt_manager_mac_map['master-2'] | selectattr('network', 'equalto', 'ocpbm') | first ).mac }}"
        cifmw_dnsmasq_host_ipv6: 'fc00:1:1::202'
        cifmw_dnsmasq_host_name: master-2.ocp.openstack.lab
      ansible.builtin.include_role:
        name: dnsmasq
        tasks_from: manage_host.yml

    - name: Laod baremetal-info.yml and set cifmw_ocp_ipi_hosts fact
      block:
        - name: Slurp baremetal-info.yml
          register: _baremetal_info_slurp
          delegate_to: "{{ cifmw_target_host | default('localhost') }}"
          ansible.builtin.slurp:
            path: "{{ _data_dir }}/artifacts/baremetal-info.yml"

        - name: Set _bm_info node facts
          ansible.builtin.set_fact:
            _bm_info_ocp_0: "{{ (_baremetal_info_slurp.content | b64decode | from_yaml).cifmw_baremetal_hosts['master-0'] }}"
            _bm_info_ocp_1: "{{ (_baremetal_info_slurp.content | b64decode | from_yaml).cifmw_baremetal_hosts['master-1'] }}"
            _bm_info_ocp_2: "{{ (_baremetal_info_slurp.content | b64decode | from_yaml).cifmw_baremetal_hosts['master-2'] }}"

        - name: Set cifmw_ocp_ipi_hosts fact
          ansible.builtin.set_fact:
            cifmw_ocp_ipi_hosts:
              - name: master-0
                role: master
                bmc:
                  address: "{{ _bm_info_ocp_0.connection }}"
                  username: "{{ _bm_info_ocp_0.username }}"
                  password: "{{ _bm_info_ocp_0.password }}"
                bootMACAddress: "{{ (_bm_info_ocp_0.nics | selectattr('network', 'equalto', 'ocppr') | first ).mac }}"
                rootDeviceHints:
                  deviceName: /dev/sda
              - name: master-1
                role: master
                bmc:
                  address: "{{ _bm_info_ocp_1.connection }}"
                  username: "{{ _bm_info_ocp_1.username }}"
                  password: "{{ _bm_info_ocp_1.password }}"
                bootMACAddress: "{{ (_bm_info_ocp_1.nics | selectattr('network', 'equalto', 'ocppr') | first ).mac }}"
                rootDeviceHints:
                  deviceName: /dev/sda
              - name: master-2
                role: master
                bmc:
                  address: "{{ _bm_info_ocp_2.connection }}"
                  username: "{{ _bm_info_ocp_2.username }}"
                  password: "{{ _bm_info_ocp_2.password }}"
                bootMACAddress: "{{ (_bm_info_ocp_2.nics | selectattr('network', 'equalto', 'ocppr') | first ).mac }}"
                rootDeviceHints:
                  deviceName: /dev/sda

    - name: Bootstrap OCP with IPI
      ansible.builtin.include_role:
        name: ocp_ipi
```
