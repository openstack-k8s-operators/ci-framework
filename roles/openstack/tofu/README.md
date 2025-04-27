# tofu
A role allowing to run tofu plan for provisioning and creation of resources as a code.

## Parameters
* `cifmw_tofu_hosts_pattern`: Ansible hosts pattern. Inventory can be provided to infrared from workspace or from parameter. '--inventory' can be used to load an external inventory to the workspace. "--ansible-args='inventory=/path/to/inventory'" can be used to use an external inventory without loading to workspace.  Refer to: https://docs.ansible.com/ansible/latest/user_guide/intro_patterns.html
* `cifmw_tofu_use_remote_project`: Do not upload local project to remote host. Only works when `ansible_host` is not equal to `localhost`
* `cifmw_tofu_binary_archive_url`: URL to the tofu binary. Every operating system and architecture has its own compiled binary. Refer to: https://www.tofu.io/downloads
* `cifmw_tofu_binary_archive_sha256_checksum`: SHA256 checksum of tofu binary. Refer to: https://www.tofu.io/downloads
* `cifmw_tofu_plan_state`: tofu infrastructure state options: present, absent.
* `cifmw_tofu_check_mode`: Flag to check tofu plan without applying it.
* `cifmw_tofu_project_path`: Path to tofu project containing `main.tf` file.
* `cifmw_tofu_plan_variables`: Dictionary of tofu variables.
* `cifmw_tofu_plan_variables_files`: List of files containing tofu variables.
* `cifmw_tofu_backend_config`: Dictionary of tofu back end configuration.
* `cifmw_tofu_backend_config_files`: List of files containing tofu back end configuration.

## Examples
```ansible-playbook playbooks/run_tofu.yml -e cifmw_tofu_plan_state=absent -e cifmw_tofu_project_path='/home/user/git/nfv-qe/ospd-17.1-vxlan-dpdk-sriov-ctlplane-dataplane-bonding-hybrid/tempest/' -vvv```
