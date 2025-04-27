# ovirt

This role facilitates the integration of the ci-framework with oVirt, it is designed to deploy VMs on top of an oVirt infrastructure.

## Requirements

* The running Ansible host must have the `python3-ovirt-engine-sdk4` package installed.
* A working oVirt instance is required.
* A template for the created VMs must be available in the oVirt instance.

Please ensure these requirements are met before using this role.

## Parameters

* `cifmw_ovirt_artifacts_basedir`: (String) Base artifacts directory. Defaults to `~/ci-framework-data/artifacts/ovirt`.
* `cifmw_ovirt_ssh_public_key`: (String) SSH public key to pass to used as `authorized_ssh_keys`.
* `cifmw_ovirt_vm_timeout`: (Integer) A number in seconds for vm creation process to time out. Defaults to `300`.
* `cifmw_ovirt_sdk_package`: (String) Package name or URL to rpm, default to ovirt upstream rpm.
* `cifmw_ovirt_layout`: (Dictionary) Dictionary specifying the layout of oVirt virtual machines for different roles:
  * `name`: (String) Name of the VM.
  * `amount`: (Integer) Number of VM instances.
  * `memory`: (Integer) Memory allocation for the VM.
  * `cpu`: (Integer) Number of CPUs for the VM.
  * `template`: (String) Template for the VM. Defaults to "{{ cifmw_ovirt_template_rhel_guest_image }}".
  * `nets` (List): List of network profiles for the oVirt virtual machines.
    * `ovirtmgmt`: (String) Name of the network profile. ovirtmgmt is the default network.
* `cifmw_ovirt_cloud_init`: (Dictionary) Configuration for cloud-init settings on the VMs:
  * `user_name`: (String) Username for the VM. Defaults to 'root'.
  * `root_password`: (String) Root password for the VM. Defaults to '12345678'.
  * `authorized_ssh_keys`: (String) Authorized SSH keys for the VM.
* `cifmw_ovirt_engine`: (Dictionary) Details for connecting to the oVirt engine.
  It is recommended to store this sensitive information in a separate YAML file and encrypt it using Ansible Vault for security.
  * `url`: (String) URL for the oVirt engine API.
  * `fqdn`: (String) Fully Qualified Domain Name (FQDN) of the oVirt engine.
  * `username`: (String) Username for authenticating with the oVirt engine.
  * `password`: (String) Password for authenticating with the oVirt engine.
  * `insecure`: (Boolean) Whether to ignore SSL certificate validation.
* `cifmw_ovirt_cluster_name`: (String) Name of the oVirt cluster.
* `cifmw_ovirt_template_rhel_guest_image`: (String) Name of the oVirt template for RHEL guest images.

## Examples

Create a new YAML file to store the oVirt engine details, for example, `ovirt_engine_vars.yml`
(It is recommended to encrypt this file):

```YAML
---
# ovirt_engine_vars.yml
cifmw_ovirt_engine:
  url: "https://ovirt.example.com/ovirt-engine/api"
  username: "admin"
  password: "password"
  insecure: true
```

```YAML
---
- name: ovirt integration
  hosts: localhost
  var_files: ovirt_engine_vars.yml
  vars:
    cifmw_ovirt_layout:
      - name: test-vm
        amount: 1
        # GiB
        memory: 4
        cpu: 8
        template: "{{ cifmw_ovirt_template_rhel_guest_image }}"
        nets:
          - ovirtmgmt
  roles:
    - ovirt
```

## Molecule

This role depends on a pre-existing oVirt instance.
As the setup of an oVirt instance is not included in the automation, Molecule testing is not applicable for this role in the context of oVirt.
The role assumes the presence of a functioning oVirt environment for its execution.
