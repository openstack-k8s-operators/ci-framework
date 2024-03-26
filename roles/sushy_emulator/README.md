# sushy_emulator

This role installs, configures and tests the deployment of the Sushi Emulator service.

Sushi Emulator is a virtual Redfish BMC, this role supports both the OpenStack and Libvirt driver.

Baremetal instances must be configured prior to running this role, for the Libvirt driver, the `libvirt_manager` role can be used.

## Privilege escalation

Required to installed required packages.

## Parameters

* `cifmw_sushy_emulator_driver`: (String) Select between `openstack` and `libvirt` sushy emulator driver. Defaults to `libvirt`
* `cifmw_sushy_emulator_sshkey_path`: (String) Path of SSH key used by sushy emulator to talk to libvirt socket. Defaults to `"{{ ansible_user_dir }}/.ssh/id_cifw"`
* `cifmw_sushy_emulator_libvirt_user`: (String) Username used by Sushi Emulator to connect to Libvirt socket. Defaults to `zuul`
* `cifmw_sushy_emulator_listen_ip`: (String) IP Sushi Emulator service listens on. Defaults to `0.0.0.0`
* `cifmw_sushy_emulator_driver_openstack_client_config_file`: (String) Path to OpenStack config file, used by OpenStack Sushi Emulator driver. Defaults to `/etc/openstack/clouds.yaml`
* `cifmw_sushy_emulator_driver_openstack_cloud`: (String) Cloud key reference in OpenStack config file. Defaults to `None`
* `cifmw_sushy_emulator_namespace`: (String) Namespace Sushi Emulator is deployed into when using the `ocp` install method. Defaults to `sushy-emulator`
* `cifmw_sushy_emulator_redfish_username`: (String) Redfish username. Defaults to `admin`
* `cifmw_sushy_emulator_redfish_password`: (String) Redfish password. Defaults to `password`
* `cifmw_sushy_emulator_resource_directory`: (String) Path where resource files will be written. Defaults to `"{{ (ansible_user_dir, 'ci-framework-data', 'artifacts', 'sushy_emulator') | path_join }}"`
* `cifmw_sushy_emulator_image`: (String) Container image used when deploying Sushi Emulator container and pod. Defaults to `quay.io/metal3-io/sushy-tools:latest`
* `cifmw_sushy_emulator_instance_node_name_prefix`: (String) String used to find instances created for baremetal use. Defaults to `cifmw-`
* `cifmw_sushy_emulator_container_name`: (String) Name of Podman container created. Defaults to `cifmw-sushy_emulator`
* `cifmw_sushy_emulator_install_type`: (String) Install type can either be `ocp` or `podman` and dictates where Sushi Emulator will be installed. Defaults to `ocp`

## Examples

```yaml
- hosts: all
  vars:
    cifmw_baremetal_hypervisor_target: baremetal-hypervisor
  tasks:
    - name: Deploy and configure sushy-emulator
      ansible.builtin.import_role:
        name: 'sushy_emulator'
```
