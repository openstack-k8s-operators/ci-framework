# idrac_configuration
Role to configure iDRAC and controlling Dell iDRAC via Redfish API.

Capable to perform the following tasks:
* Query iDRAC information.
* Set Bios Attributes.
* Set boot mode.
* Set device boot order.
* Execute a power action.

## Requirements
* iDRAC 7/8 with Firmware version 2.82.82.82 or above.
* iDRAC 9 with Firmware version 3.00.00.00 or above.

## Parameters
* `cifmw_idrac_configuration_bios_attributes`: (String) iDRAC BIOS attributes. Defaults to `False`.
* `cifmw_idrac_configuration_boot_mode`: (String) iDRAC BIOS boot mode. Defaults to `False`.
* `cifmw_idrac_configuration_boot_order`: (String) iDRAC BIOS boot order. Defaults to `False`.
* `cifmw_idrac_configuration_delete_previous_idrac_jobs`: (Boolean) Remove previously completed jobs from iDRAC job inventory. Defaults to `False`.
* `cifmw_idrac_configuration_target_hosts`: (String) Set a list of hosts to run this role against.
* `cifmw_idrac_configuration_power_action`: (String) Execute power action on iDRAC. Defaults to `False`.
* `cifmw_idrac_configuration_query`: (String) Whether to query iDRAC for info. Defaults to `False`.
* `cifmw_idrac_configuration_racreset`: (String) Performs 'GracefulRestart' on iDRAC controller. Defaults to `False`.
* `cifmw_idrac_configuration_skip_clear_pending`: (Boolean) Skips clearing pending BIOS attributes. Defaults to `False`.
* `cifmw_idrac_configuration_task_retries`: (Integer) Amount of retries attempted in supported tasks. Defaults to `30`.
* `cifmw_idrac_configuration_timeout`: (String) Timeout in seconds for URL requests to OOB (out of band) controller. Defaults to `30`.
* `cifmw_idrac_configuration_validate_ssl_certs`: (Boolean) Validate SSL certificates. Defaults to `False`.

## Examples
```YAML
- name: Set a dynamic inventory
  hosts: all
  tasks:
    - name: Split target_hosts into a list
      ansible.builtin.set_fact:
        host_list: "{{ cifmw_idrac_configuration_target_hosts.split(',') }}"

    - name: Add hosts dynamically
      ansible.builtin.add_host:
        name: "{{ item }}"
        group: idrac_target_hosts
      with_items: "{{ host_list }}"

- hosts: idrac_target_hosts
  connection: local
  vars_files:
    - idrac_hosts_vars.yml
  roles:
    - idrac_configuration
```

idrac_hosts_vars.yml:
```YAML
cifmw_idrac_configuration_target_hosts: node1-bmc.example.com,node2-bmc.example.com
cifmw_idrac_configuration_user: username
cifmw_idrac_configuration_password: password

node1-bmc.example.com:
  cifmw_idrac_configuration_boot_mode: "Bios"
  cifmw_idrac_configuration_bios_attributes:
    SysProfile: "PerfOptimized" # Set performance profile
    EnergyEfficientTurbo: "Disabled" # Disabling Intel Turbo Boost, we don't want dynamic CPU frequency
    EnergyPerformanceBias: "MaxPower" # Max power consumption
    MemFrequency: "MaxPerf" # Maximum performance for memory for best performance
    PowerSaver: "Disabled" # Disable power saver
    ProcVirtualization: "Enabled" # Enable virtualization (VT-d for Intel, AMD-V for AMD)
    LogicalProc: "Enabled" # Enable hyperthreading
    SriovGlobalEnable: "Enabled" # Enable SR-IOV
    PxeDev1EnDis: "Enabled" # Enabling PXE Device 1
    PxeDev1Interface: "NIC.Embedded.1-1-1" # Assigning physical NIC to PXE device 1
    PxeDev1Protocol: "IPv4" # Assigning PXE device 1 to IPv4
    PxeDev1VlanEnDis: "Disabled" # Disable VLAN for PXE device 1
  cifmw_idrac_configuration_boot_order:
    - "NIC.Integrated.1-1-1"
    - "NIC.Integrated.1-2-1"
```
