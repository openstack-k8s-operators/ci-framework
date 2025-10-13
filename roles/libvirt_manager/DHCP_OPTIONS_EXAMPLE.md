# DHCP Options Support in libvirt_manager

This document explains how to add DHCP options to VM groups in the libvirt_manager role.

## Overview

The libvirt_manager role now supports assigning DHCP options to groups of VMs based on their type. This is useful for scenarios like PXE booting where you need to provide specific boot parameters to certain VM types.

## How It Works

1. **VM Type Tagging**: Each VM is automatically tagged with its type (e.g., `compute`, `controller`, `baremetal_instance`)
2. **DHCP Options**: You can specify DHCP options in the VM type definition
3. **dnsmasq Configuration**: The role automatically generates dnsmasq configuration that applies these options to all VMs of that type

## Configuration Example

### Basic Example

Here's how to add DHCP options for PXE booting to baremetal instances:

```yaml
cifmw_libvirt_manager_configuration:
  vms:
    baremetal_instance:
      amount: 3
      disk_file_name: "blank"
      disksize: 50
      memory: 8
      cpus: 4
      bootmenu_enable: "yes"
      nets:
        - public
        - provisioning
      dhcp_options:
        - "60,HTTPClient"                                   # Vendor class identifier
        - "67,http://192.168.122.1:8081/boot.ipxe"          # Boot filename (iPXE script)
```

### Advanced Example with Multiple VM Types

```yaml
cifmw_libvirt_manager_configuration:
  vms:
    controller:
      amount: 1
      image_url: "{{ cifmw_discovered_image_url }}"
      sha256_image_name: "{{ cifmw_discovered_hash }}"
      disk_file_name: "centos-stream-9.qcow2"
      disksize: 50
      memory: 4
      cpus: 2
      nets:
        - public
        - osp_trunk
      # No DHCP options for controllers - they'll use defaults

    compute:
      amount: 3
      disk_file_name: blank
      disksize: 40
      memory: 8
      cpus: 4
      nets:
        - public
        - osp_trunk
      dhcp_options:
        - "60,HTTPClient"
        - "67,http://192.168.122.1:8081/boot-artifacts/compute-boot.ipxe"

    baremetal_instance:
      amount: 2
      disk_file_name: "blank"
      disksize: 50
      memory: 8
      cpus: 4
      bootmenu_enable: "yes"
      nets:
        - public
      dhcp_options:
        - "60,HTTPClient"
        - "67,http://192.168.122.1:8081/boot-artifacts/agent.x86_64.ipxe"
```

## Common DHCP Options

Here are some commonly used DHCP options for PXE/network booting:

| Option | Name | Purpose | Example |
|--------|------|---------|---------|
| 60 | vendor-class-identifier | Identifies the vendor/client type | `60,HTTPClient` |
| 67 | bootfile-name | Path to boot file | `67,http://server/boot.ipxe` |
| 66 | tftp-server-name | TFTP server address | `66,192.168.1.10` |
| 150 | tftp-server-address | TFTP server IP (Cisco) | `150,192.168.1.10` |
| 210 | path-prefix | Path prefix for boot files | `210,/tftpboot/` |


## Technical Details

### Under the Hood

1. **Tag Assignment**: When VMs are created, each is assigned a tag matching its type in the dnsmasq DHCP host entry:
   ```
   set:baremetal_instance,52:54:00:xx:xx:xx,192.168.122.10,hostname
   ```

2. **DHCP Options Configuration**: A configuration file is generated at `/etc/cifmw-dnsmasq.d/vm-types-dhcp-options.conf`:
   ```
   # Options for baremetal_instance VMs
   dhcp-option=tag:baremetal_instance,60,HTTPClient
   dhcp-option=tag:baremetal_instance,67,http://192.168.122.1:8081/boot.ipxe
   ```

3. **dnsmasq Processing**: When a VM with the `baremetal_instance` tag requests DHCP, it receives both the standard network options AND the VM-type-specific options.

### Files Modified

- `roles/libvirt_manager/tasks/reserve_dnsmasq_ips.yml`: Adds VM type tags to DHCP entries
- `roles/libvirt_manager/tasks/create_dhcp_options.yml`: New file that generates DHCP options configuration
- `roles/libvirt_manager/tasks/generate_networking_data.yml`: Includes the new task
- `roles/dnsmasq/tasks/manage_host.yml`: Updated to support tags in DHCP entries

## Troubleshooting

### Verify DHCP Options Are Applied

1. Check the generated configuration:
   ```bash
   cat /etc/cifmw-dnsmasq.d/vm-types-dhcp-options.conf
   ```

2. Check DHCP host entries:
   ```bash
   ls -la /etc/cifmw-dnsmasq.d/dhcp-hosts.d/
   cat /etc/cifmw-dnsmasq.d/dhcp-hosts.d/public_*
   ```

3. Verify dnsmasq configuration is valid:
   ```bash
   dnsmasq -C /etc/cifmw-dnsmasq.conf --test
   ```

4. Monitor DHCP requests:
   ```bash
   journalctl -u cifmw-dnsmasq -f
   ```

### Common Issues

**Issue**: DHCP options not being sent to VMs
- **Solution**: Ensure dnsmasq service is restarted after making changes
- **Check**: Verify the VM type tag matches between the DHCP host entry and the options configuration

**Issue**: VMs not PXE booting correctly
- **Solution**: Verify the boot file URL is accessible from the VM's network
- **Check**: Ensure option 67 contains the full URL including protocol (http://)

## References

- [dnsmasq manual](http://www.thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html)
- [DHCP Options RFC](https://www.iana.org/assignments/bootp-dhcp-parameters/bootp-dhcp-parameters.xhtml)
- [iPXE documentation](https://ipxe.org/howto/dhcpd)
