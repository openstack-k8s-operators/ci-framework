# openshift_provisioner_node
This role performs all the necessary tasks required to run the OpenShift
installer. The designated host is prepared to run the installation program and
hosts the bootstrap VM that deploys the controller/s of a new OpenShift
Container Platform cluster.

Bootstrap VM is used in the process of deploying an OpenShift Container
platform cluster.

## Prerequisites
* `libvirt_manager` role

## Privilege escalation
`become`: Is required to install packages, configure services and networking.

## Parameters
* `cifmw_opn_host`: (String) IPv4 address of the machine that would be hosting
  the bootstrap VM.
* `cifmw_opn_external_bridge_name`: (String) Name of the external bridge to be
  created for attaching with the bootstrap VM. It is associated to the
  baremetal network. Defaults to `baremetal`.
* `cifmw_opn_external_network_iface`: (String) Name of the iface to be attached
  to the external bridge.
* `cifmw_opn_use_provisioning_network`: (Boolean) If enabled, the necessary
  steps to configure the provisioning network is executed. Defaults to `false`.
* `cifmw_opn_prov_bridge_name`: (String) Name of the provisioning bridge to be
  created for attaching with the bootstrap VM. It is associated to the
  provisioning network. Defaults to `provisioning`.
* `cifmw_opn_prov_network_iface`: (String) Name of the iface to be attached to
  the provisioning bridge.
* `cifmw_opn_user`: (String) Name of the user to be passed to openshift
  installer. Defaults to `kni`.
* `cifmw_opn_dry_run`: (Boolean) Set this variable to `true` for unit testing
  the role. It is mainly for development purpose.

## Examples

### Use a separate network for deployment of OCP cluster.
```YAML
cifmw_use_libvirt_manager: true

cifmw_use_opn: true
cifmw_opn_host: 192.168.20.10
cifmw_opn_external_network_iface: eth0
cifmw_opn_prov_network_iface: eth1
```

### Use a virtual media for OCP cluster deployment
```YAML
cifmw_use_libvirt_manager: true

cifmw_use_opn: true
cifmw_opn_host: 192.168.20.10
cifmw_opn_external_network_iface: eno3
```

### Use provisioning network with internal DHCP
```YAML
cifmw_use_libvirt_manager: true

cifmw_use_opn: true
cifmw_opn_host: 192.168.20.10
cifmw_opn_external_network_iface: eno1
cifmw_opn_prov_network_iface: eno2
```

### Inventory file
```YAML
all:
  hosts:
    localhost:
      ansible_connection: local
  children:
    virthosts:
      hosts:
        foo.bar:
```

## Reference
[OpenShift-Installer](https://docs.openshift.com/container-platform/4.13/installing/installing_bare_metal_ipi/ipi-install-overview.html)
