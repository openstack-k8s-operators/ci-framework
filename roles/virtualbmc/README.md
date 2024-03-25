# virtualbmc
Deploy and manage VirtualBMC in a container.

It creates a dedicated keypair to allow SSH accesses from the container onto the
hypervisor. The keypair is shared in the container, and removed when we clean the
service.

## Privilege escalation
None

## Parameters
* `cifmw_virtualbmc_image`: (String) VirtualBMC container image. Defaults to `quay.io/metal3-io/vbmc:latest`.
* `cifmw_virtualbmc_container_name`: (String) VirtualBMC container name. Defaults to `cifmw-vbmc`.
* `cifmw_virtualbmc_listen_address`: (String) VirtualBMC listen address. Defaults to `127.0.0.1`.
* `cifmw_virtualbmc_daemon_port`: (Integer) VirtualBMC daemon listen port. Default to `50891`.
* `cifmw_virtualbmc_machine`: (String) Virtual machine to manage in VirtualBMC. Mandatory. Defaults to `null`.
* `cifmw_virtualbmc_action`: (String) VirtualBMC action. Must be either `add` or `delete`. Mandatory. Defaults to `null`.
* `cifmw_virtualbmc_sshkey_path`: (String) SSH keypair path for VirtualBMC. Defaults to `{{ ansible_user_dir }}/.ssh/vbmc-key`.
* `cifmw_virtualbmc_sshkey_type`: (String) Type of SSH keypair. Defaults to `{{ cifmw_ssh_keytype | default('ecdsa') }}`.
* `cifmw_virtualbmc_sshkey_size`: (Integer) Size of the SSH keypair. Defaults to `{{ cifmw_ssh_keysize | default(521) }}`.
* `cifmw_virtualbmc_ipmi_key_path`: (String) SSH private key location in the VBMC container. Defaults to `/root/ssh/id_rsa_virt_power`.
* `cifmw_virtualbmc_ipmi_address`: (String) IP address for Hypervisor connection. Defaults to `127.0.0.1`.
* `cifmw_virtualbmc_ipmi_password`: (String) IPMI password. Defaults to `password`.
* `cifmw_virtualbmc_ipmi_user`: (String) IPMI username. Defaults to `admin`.
* `cifmw_virtualbmc_ipmi_base_port`: (Integer) IPMI base port, used to calculate further ports for hosts. Defaults to `6240`.
* `cifmw_virtualbmc_ipmi_uri`: (String) Internal VBMC URI to access qemu daemon. Defaults to
  `qemu+ssh://{{ ansible_user_id }}@{{ cifmw_virtualbmc_ipmi_address }}/system?&keyfile={{ cifmw_virtualbmc_ipmi_key_path }}&no_verify=1&no_tty=1`.


## Examples
Refer to the molecule tests for usage examples.
