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

## Parameters imported from the reproducer role
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
