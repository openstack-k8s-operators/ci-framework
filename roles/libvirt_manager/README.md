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
* `cifmw_libvirt_manager_fixed_networks`: (List) Network names you don't want to prefix with `cifmw-`. It will be concatenated with cifmw_libvirt_manager_fixed_networks_defaults. Defaults to`[]`.
* `cifmw_libvirt_manager_reproducer_key_type`: (String) Type of ssh key that will be injected into the controller VMs. Defaults to `cifmw_ssh_keytype` which default to `ecdsa`.
* `cifmw_libvirt_manager_reproducer_key_size`: (Integer) Size of the ecdsa ssh keys that will be injected into the controller VMs. Defaults to `cifmw_ssh_keysize` which default to 521.
* `cifmw_libvirt_manager_spineleaf_setup`: (Boolean) Whether the VMs deployed are connected to a spine/leaf virtual infrastructure or not. When set to `true`, the interfaces of the instances from a certain type of VM are not connected to the same networks, but they can be defined per VM using the `spineleafnets` list (except for the `controller`). Defaults to `false`.
* `cifmw_libvirt_manager_network_interface_types`: (Dict) By default, interfaces attached to VMs are created with `--type bridge`, but with this parameter, those interfaces can be configured with any other types. Defaults to empty dictionary.
* `cifmw_libvirt_manager_configuration_patch(.)*`: (Dict) Structure describing the patch to combine on top of `cifmw_libvirt_manager_configuration`.
* `cifmw_libvirt_manager_enable_sushy_emulator`: (Boolean) Toggle the installation of sushy-emulator (Virtual RedFish BMC). Defaults to: `false`

### Structure for `cifmw_libvirt_manager_configuration`

The following structure has to be passed via the configuration parameter:

```YAML
cifmw_libvirt_manager_configuration:
  vms:
    type_name:  # (string, such as "compute", "controller")
      amount: (integer, optional. Optional, defaults to 1, allowed [0-9]+)
      image_url: (string, URI to the base image. Optional if disk_file_name is set to "blank")
      sha256_image_name: (string, image checksum. Optional if disk_file_name is set to "blank")
      image_local_dir: (string, image destination for download. Optional if disk_file_name is set to "blank")
      disk_file_name: (string, target image name. If set to "blank", will create a blank image)
      disksize: (integer, disk size for the VM type. Optional, defaults to 40G)
      memory: (integer, RAM amount in GB. Optional, defaults to 2)
      cpus: (integer, amount of CPU. Optional, defaults to 2)
      nets: (ordered list of networks to connect to)
      extra_disks_num: (integer, optional. Number of extra disks to be configured.)
      extra_disks_size: (string, optional. Storage capacity to be allocated. Example 1G, 512M)
      password: (string, optional, defaults to fooBar. Root password for console access)
      target: (Hypervisor hostname you want to deploy the family on. Optional)
      uefi: (boolean, toggle UEFI boot. Optional, defaults to false)
  networks:
    net_name: <XML definition of the network to create>
```

Specific `type_name`: `^crc.*` and `^ocp.*` are enabling specific paths in the module.

#### Example

```YAML
_networks:
  public:
    range: "192.168.100.0/24"
  osp_trunk:
    default: true
    range: "192.168.122.0/24"
    mtu: 9000

cifmw_libvirt_manager_configuration:
  vms:
    compute:
      amount: 3
      disk_file_name: blank
      nets:
        - public
        - osp_trunk
      extra_disks_num: 5
      extra_disks_size: '1G'
    controller:
      image_url: "{{ cifmw_discovered_image_url }}"
      sha256_image_name: "{{ cifmw_discovered_hash }}"
      image_local_dir: "{{ cifmw_basedir }}/images/"
      disk_file_name: "centos-stream-9.qcow2"
      disksize: 50
      memory: 4
      cpus: 2
      ip_address:
        address: "192.168.111.9/24"
        gw: "192.168.111.1"
        dns: "192.168.111.1"
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
         address='{{ _networks.public.range | ansible.utils.nthhost(1) }}'
         prefix='24'>
          <dhcp>
            <range
             start='{{ _networks.public.range | ansible.utils.nthhost(10) }}'
             end='{{ _networks.public.range | ansible.utils.nthhost(100) }}'/>
          </dhcp>
        </ip>
      </network>
    osp_trunk: |-
      <network>
        <name>osp_trunk</name>
        <forward mode='nat'/>
        <bridge name='osp_trunk' stp='on' delay='0'/>
        <mtu size='{{ _networks.osp_trunk.mtu }}'/>
        <ip
         family='ipv4'
         address='{{ _networks.osp_trunk.range | ansible.utils.nthhost(1) }}'
         prefix='24'>
        </ip>
      </network>
```

### Parameters imported from the reproducer role

The following parameters are usually set in the [reproducer](./reproducer.md) context.
The parameters listed here are therefore merely proxies to the ones set in the reproducer,
and have the same name, less the role prefix. Default values are the same as the
reproducer role.

* `cifmw_libvirt_manager_dns_servers`: `{{ cifmw_reproducer_dns_servers | default(['1.1.1.1', '8.8.8.8']) }}`

## Calling attach_network.yml from another role

You may want to include that specific tasks file from another role in order to inject some networks into
a virtual machine.

In order to do so, you have to provide specific variables:

* `vm_name`: (String) Virtual machine name. Mandatory.
* `network`: (Data structure). Mandatory.
  * `name`: (String) Network or bridge name. Mandatory.
  * `cidr`: (String) Network CIDR. Mandatory.
* `cifmw_libvirt_manager_net_prefix_add`: (Bool) Toggle this to `true` if the network name needs to get the `cifmw-` prefix (advanced usage). Optional. Defaults to `true`.

## Layout patching
This role allows to use a base layout, given by `cifmw_libvirt_manager_configuration` and patch it
with other values, ie. patch it for another environment, by declaring variables prefixed that matches the
`^cifmw_libvirt_manager_configuration_patch.*` regex. Each of those variables, after sorting them by name,
will be combined on top of the original `cifmw_libvirt_manager_configuration` and that will be the final
layout used by the role.

### Example of a task

```YAML
- name: Attach my network to my virtual machine
  vars:
    vm_name: my-virtual-machine
    network:
      name: my-network
      cidr: 192.168.130.0/24
  ansible.builtin.include_role:
    name: libvirt_manager
    tasks_from: attack_interface.yml
```
