# hci_prepare
Prepare steps and files needed when deploying Ceph services alongside with compute nodes using `edpm_deploy` role.

## Privilege escalation
None.

## Parameters
* `cifmw_hci_prepare_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_hci_prepare_dataplane_dir`: (String) Directory in where `edpm_deploy` role will search for DataPlane kustomizations. Defaults to `"{{ cifmw_basedir }}/artifacts/manifests/kustomizations/dataplane"`.
* `cifmw_hci_prepare_dryrun`: (Boolean) Perform a dry run on a set of commands. Defaults to `False`.
* `cifmw_hci_prepare_skip_load_parameters`: Skip the initial `load_parameters` step, which load vars to gather network information. Defaults to `False`.
* `cifmw_hci_prepare_ceph_secret_path`: "/tmp/k8s_ceph_secret.yml"
* `cifmw_hci_prepare_enable_storage_mgmt`: (Boolean) Creates a kustomization file to include `storage-mgmt` network in DataPlane deployment. Defaults to `True`.
* `cifmw_hci_prepare_storage_mgmt_mtu`: (Int) Storage-Management network MTU. Defaults to `1500`.
* `cifmw_hci_prepare_storage_mgmt_vlan`: (Int) Storage-Management network VLAn. Defaults to `23`.

## Examples
### 1 - How to deploy HCI using hci_prepare and edpm_deploy
```yaml
- hosts: localhost
  tasks:
    - name: Prepare for HCI deploy phase 1
      ansible.builtin.import_role:
        name: hci_prepare
        tasks_from: phase1.yml

    - name: Deploy EDPM using edpm_deploy role
      ansible.builtin.import_role:
        name: edpm_deploy

    - name: Deploy Ceph on edpm nodes
      ansible.builtin.import_playbook: ceph.yml

    - name: Prepare for HCI deploy phase 2
      ansible.builtin.import_role:
        name: hci_prepare
        tasks_from: phase2.yml

    - name: Continue HCI deployment using edpm_deploy role
      ansible.builtin.import_role:
        name: edpm_deploy
```
