# libvirt_manager

Used for checking if:
    - there's SVM/VMX virtualization, enable it if not
    - install libvirt packages and dependencies and add group and user to libvirt group if necessary,

## Privilege escalation

`become` - Required in:
    - `virsh_checks.yml`: For creating libvirt group if needed and also append user to this group if it's not there.
    - `virtualization_prerequisites.yml`: For enabling VMX/SVM module with modprobe.
    - `packages.yml`: Install all libvirt dependencies.
    - `polkit_rules.yml`: Add polkit rules under `/etc/`.

## Parameters

* `cifmw_libvirt_manager_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_libvirt_manager_enable_virtualization_module`: (Boolean) If `true` it will enable the virtualization module in case it's not already and if the hosts allow it. Defaults to `false`.
* `cifmw_libvirt_manager_user`: (String) User used for libvirt. Default: the one in the environment variable `USER`.
* `cifmw_libvirt_manager_images_url`: (String) Location basedir for the image URI. Defaults to `https://cloud.centos.org/centos/9-stream/x86_64/images`.
* `cifmw_libvirt_manager_configuration`: (Dict) Structure describing the libvirt layout (networking and VMs).
* `cifmw_libvirt_manager_crc_pool`: (String) CRC pool machine location. Defaults to `cifmw_crc_pool` which defaults to `~/.crc/machines/crc`.
* `cifmw_libvirt_manager_installyamls`: (String) install_yamls repository location. Defaults to `cifmw_installyamls_repos` which defaults to `../..`
* `cifmw_libvirt_manager_dryrun`: (Boolean) Toggle ci_make `dry_run` parameter. Defaults to `false`.
* `cifmw_libvirt_manager_compute_amount`: (Integer) State the amount of computes you want. Defaults to `1`.
* `cifmw_libvirt_manager_compute_memory`: (Integer) The amount of memory in GB per compute. Defaults to `4`.
* `cifmw_libvirt_manager_compute_disksize`: (Integer) The size of the disk in GB per compute. Defaults to `20`.
* `cifmw_libvirt_manager_compute_cpus`: (Integer) The amount of vCPUs per compute. Defaults to `1`.
* `cifmw_libvirt_manager_apply_virtproxy_patch` (Boolean) Apply patch virtproxy patch for improved libvirt stability. This is set to `true` by default.
* `cifmw_libvirt_manager_net_prefix_add` (Boolean) Adds `cifmw-` prefix to the network resources managed by this role. By default, it is set to `true`.
* `cifmw_libvirt_manager_pub_net`: (String) Network name playing the "public" interface. Defaults to `public`.
* `cifmw_libvirt_manager_vm_net_ip_set`: (Dict) Allow to extend the existing mapping for host family to IP mapping. Defaults to `{}`.

### Structure for `cifmw_libvirt_manager_configuration`

The following structure has to be passed via the configuration parameter:
```YAML
cifmw_libvirt_manager_configuration:
  vms:
    type_name:  # (string, such as "compute", "controller")
      amount: (integer, optional. Optional, defaults to 1)
      image_url: (string, URI to the base image. Optional if disk_file_name is set to "blank")
      sha256_image_name: (string, image checksum. Optional if disk_file_name is set to "blank")
      image_local_dir: (string, image destination for download. Optional if disk_file_name is set to "blank")
      disk_file_name: (string, target image name. If set to "blank", will create a blank image)
      disksize: (integer, disk size for the VM type. Optional, defaults to 40G)
      memory: (integer, RAM amount in GB. Optional, defaults to 2)
      cpus: (integer, amount of CPU. Optional, defaults to 2)
      nets: (ordered list of networks to connect to)
      target: (Hypervisor hostname you want to deploy the family on. Optional)
  networks:
    net_name: <XML definition of the network to create>
```

Specific `type_name`: `^crc.*` and `^ocp.*` are enabling specific paths in the module.

#### Example
```YAML
cifmw_libvirt_manager_networks:
  public:
    range: "192.168.100.0/24"
  osp_trunk:
    default: true
    range: "192.168.122.0/24"
    mtu: 9000
    static_ip: true

cifmw_libvirt_manager_configuration:
  vms:
    compute:
      amount: 3
      disk_file_name: blank
      nets:
        - public
        - osp_trunk
    controller:
      image_url: "{{ cifmw_discovered_image_url }}"
      sha256_image_name: "{{ cifmw_discovered_hash }}"
      image_local_dir: "{{ cifmw_basedir }}/images/"
      disk_file_name: "centos-stream-9.qcow2"
      disksize: 50
      memory: 4
      cpus: 2
      nets:
        - public
        - osp_trunk
  networks:
    public: |-
      <network>
        <name>public</name>
        <forward mode='nat'/>
        <bridge name='public' stp='on' delay='0'/>
        <ip family='ipv4'
         address='{{ cifmw_libvirt_manager_networks.public.range | ansible.utils.nthhost(1) }}'
         prefix='24'>
          <dhcp>
            <range
             start='{{ cifmw_libvirt_manager_networks.public.range | ansible.utils.nthhost(10) }}'
             end='{{ cifmw_libvirt_manager_networks.public.range | ansible.utils.nthhost(100) }}'/>
          </dhcp>
        </ip>
      </network>
    osp_trunk: |-
      <network>
        <name>osp_trunk</name>
        <forward mode='nat'/>
        <bridge name='osp_trunk' stp='on' delay='0'/>
        <mtu size='{{ cifmw_libvirt_manager_networks.osp_trunk.mtu }}'/>
        <ip
         family='ipv4'
         address='{{ cifmw_libvirt_manager_networks.osp_trunk.range | ansible.utils.nthhost(1) }}'
         prefix='24'>
        </ip>
      </network>
```

### Parameters imported from the reproducer role

The following parameters are usually set in the [reproducer](./reproducer.md) context.
The parameters listed here are therefore merely proxies to the ones set in the reproducer,
and have the same name, less the role prefix. Default values are the same as the
reproducer role.

* `cifmw_libvirt_manager_private_nic`: `{{ cifmw_reproducer_private_nic | default('eth1') }}`
* `cifmw_libvirt_manager_ctl_ip4`: `{{ cifmw_reproducer_ctl_ip4 | default('192.168.122.11') }}`
* `cifmw_libvirt_manager_ctl_gw4`: `{{ cifmw_reproducer_ctl_gw4 | default('192.168.122.1') }}`
* `cifmw_libvirt_manager_crc_ip4`: `{{ cifmw_reproducer_crc_ip4 | default('192.168.122.10') }}`
* `cifmw_libvirt_manager_crc_gw4`: `{{ cifmw_reproducer_crc_gw4 | default('192.168.122.1') }}`
* `cifmw_libvirt_manager_dns_servers`: `{{ cifmw_reproducer_dns_servers | default(['1.1.1.1', '8.8.8.8']) }}`
* `cifmw_libvirt_manager_crc_private_nic`: `{{ cifmw_reproducer_crc_private_nic | default('enp2s0') }}`

## Calling attach_network.yml from another role
You may want to include that specific tasks file from another role in order to inject some networks into
a virtual machine.

In order to do so, you have to provide specific variables:

* `vm_name`: (String) Virtual machine name. Mandatory.
* `network`: (Data structure). Mandatory.
  * `name`: (String) Network or bridge name. Mandatory.
  * `cidr`: (String) Network CIDR. Mandatory.
  * `mtu`: (Int) Network MTU. Optional (and not used in this specific case).
  * `static_ip`: (Bool) Set it to `true` to get a fixed IP.
* `cifmw_libvirt_manager_net_prefix_add`: (Bool) Toggle this to `true` if the network name needs to get the `cifmw-` prefix (advanced usage). Optional. Defaults to `true`.

### Example
```YAML
- name: Attach my network to my virtual machine
  vars:
    vm_name: my-virtual-machine
    network:
      name: my-network
      cidr: 192.168.130.0/24
      static_ip: true
  ansible.builtin.include_role:
    name: libvirt_manager
    tasks_from: attack_interface.yml
```
