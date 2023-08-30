# edpm_deploy_baremetal
This Ansible role deploys compute nodes with BMAAS, installs the OpenStack operator and services,
and provision the compute nodes for further deployment by toggling the deploy:true flag in the openstackdataplane CR,
and waits for the necessary components to be available.

## Privilege escalation
This role doesn't need privilege escalation.

## Parameters
* `cifmw_edpm_deploy_baremetal_manifests_dir`: (string) The directory path where the manifests will be stored. Default: `{{ cifmw_manifests | default(cifmw_edpm_deploy_baremetal_basedir ~ '/artifacts/manifests') }}`
* `cifmw_edpm_deploy_baremetal_dry_run`: (boolean) Whether to perform a dry run of the deployment. Default: `false`
* `cifmw_install_yamls_defaults`: (dictionary) Default values for installation. Default: `{'NAMESPACE': 'openstack'}`
* `cifmw_edpm_deploy_baremetal_wait_provisionserver_retries`: (integer) Number of retries when waiting for the Provision Server pod. Default: `60`
* `cifmw_edpm_deploy_baremetal_wait_provisionserver_timeout_mins`: (integer) Timeout for waiting for the Provision Server deployment. Default: `20`
* `cifmw_edpm_deploy_baremetal_wait_bmh_timeout_mins`: (integer) Timeout for waiting for the bare metal nodes. Default: `20`
* `cifmw_edpm_deploy_baremetal_wait_dataplane_timeout_mins`: (integer) Timeout for waiting for the OpenStackDataPlane. Default: `30`
* `cifmw_edpm_deploy_baremetal_update_os_containers`: (Boolean) Update the uefi image. Default: `false`
* `cifmw_edpm_deploy_baremetal_repo_setup_override`: (Boolean) Override the repo-setup service in OpenStackDataPlane with repo-setup-downstream. Default: `false`

## Examples
### 1 - Perform edpm baremetal deployment
```yaml
- hosts: all
  tasks:
    - name: Perform edpm baremetal deployment
      ansible.builtin.include_role:
        name: edpm_deploy_baremetal
```
