# sushy_emulator

This role installs, configures and tests the deployment of the Sushi Emulator service.

Sushi Emulator is a virtual Redfish BMC, this role supports both the OpenStack and Libvirt driver.

Baremetal instances must be configured prior to running this role, for the Libvirt driver, the `libvirt_manager` role can be used.

This role supports installing via a Podman pod onto the controller node or a pod in OCP or CRC.

## Privilege escalation

Required to installed required packages.

## Parameters

* `cifmw_sushy_emulator_basedir`: (String) Base directory. Defaults to `{{ ansible_user_dir ~ '/ci-framework-data' }}`
* `cifmw_sushy_emulator_container_name`: (String) Name of Podman container created. Defaults to `cifmw-sushy_emulator`
* `cifmw_sushy_emulator_driver`: (String) Select between `openstack` and `libvirt` sushy emulator driver. Defaults to `libvirt`
* `cifmw_sushy_emulator_driver_openstack_client_config_file`: (String) Path to OpenStack config file, used by OpenStack Sushi Emulator driver. Defaults to `/etc/openstack/clouds.yaml`
* `cifmw_sushy_emulator_driver_openstack_cloud`: (String) Cloud key reference in OpenStack config file. Defaults to `None`
* `cifmw_sushy_emulator_hypervisor_target` (String) Hostname of the Libvirt hypervisor to connect to.
* `cifmw_sushy_emulator_hypervisor_target_connection_ip` (String) IP Address used to connect to hypervisor, optional override for `cifmw_sushy_emulator_hypervisor_target` when specific address is required.
* `cifmw_sushy_emulator_install_type`: (String) Install type can either be `ocp` or `podman` and dictates where Sushi Emulator will be installed. Defaults to `ocp`
* `cifmw_sushy_emulator_image`: (String) Container image used when deploying Sushi Emulator container and pod. Defaults to `quay.io/metal3-io/sushy-tools:latest`
* `cifmw_sushy_emulator_libvirt_uri`: (String) Internal URI to access qemu daemon. Defaults to `qemu+ssh://{{ cifmw_sushy_emulator_libvirt_user }}@{{ cifmw_sushy_emulator_hypervisor_target_connection_ip | default(cifmw_sushy_emulator_hypervisor_target) }}/system?no_tty=1`
* `cifmw_sushy_emulator_libvirt_user`: (String) Username used by Sushi Emulator to connect to Libvirt socket. Defaults to `zuul`
* `cifmw_sushy_emulator_listen_ip`: (String) IP address Sushy Emulator listens on. Defaults to `0.0.0.0`
* `cifmw_sushy_emulator_namespace`: (String) Namespace Sushi Emulator is deployed into when using the `ocp` install method. Defaults to `sushy-emulator`
* `cifmw_sushy_emulator_parameters_file`:  (string) Path of the file which contains (v)bmc parameters. Defaults to `cifmw_sushy_emulator_basedir + parameters + baremetal-info.yml`
* `cifmw_sushy_emulator_redfish_username`: (String) Redfish username. Defaults to `{{ cifmw_redfish_username | default('admin') }}`
* `cifmw_sushy_emulator_redfish_password`: (String) Redfish password. Defaults to `{{ cifmw_redfish_password | default('password') }}`
* `cifmw_sushy_emulator_resource_directory`: (String) Path where resource files will be written. Defaults to `"{{ (ansible_user_dir, 'ci-framework-data', 'artifacts', 'sushy_emulator') | path_join }}"`
* `cifmw_sushy_emulator_sshkey_path`: (String) Path of SSH key used by sushy emulator to talk to libvirt socket. Defaults to `"{{ ansible_user_dir }}/.ssh/sushy_emulator-key"`
* `cifmw_sushy_emulator_sshkey_type`: (String) Type of SSH keypair. Defaults to `{{ cifmw_ssh_keytype | default('ecdsa') }}`.
* `cifmw_sushy_emulator_sshkey_size`: (Integer) Size of the SSH keypair. Defaults to `{{ cifmw_ssh_keysize | default(521) }}`.
* `cifmw_sushy_emulator_vm_prefix_filter`: (String) Prefix string used to filter instances created for baremetal use. Defaults to `.*`

## Examples

```yaml
- hosts: all
  vars:
    cifmw_sushy_emulator_hypervisor_target: "{{ cifmw_target_host | default('localhost') }}"
    cifmw_sushy_emulator_install_type: podman
    cifmw_sushy_emulator_hypervisor_target_connection_ip: "{{ network_bridge_info['cifmw-public'] }}"
    cifmw_sushy_emulator_vm_prefix_filter: cifmw-compute
  tasks:
    - name: Deploy and configure sushy-emulator
      ansible.builtin.import_role:
        name: 'sushy_emulator'
```
