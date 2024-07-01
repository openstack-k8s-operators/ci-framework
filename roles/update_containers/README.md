# update_containers

Ansible role to generate custom resource file for updating
openstack services containers, Ansibleee and EDPM Baremetal Image.

## Privilege escalation
If apply, please explain the privilege escalation done in this role.

## Parameters
* `cifmw_update_containers`: The boolean value which will decide to run the 'Update the containers' role. Default to `false`.
* `cifmw_update_containers_metadata`: The metadata name of podified control plane custom resources. Default to `controlplane`.
* `cifmw_update_containers_namespace`: The namespace of the podified control plane deployment. Default to `openstack`.
* `cifmw_update_containers_base_dir`: The base directory of update_containers role. Default is "ansible_user_dir ~ '/ci-framework-data')".
* `cifmw_update_containers_dest_path`: The destination file path to create update containers CR file.
* `cifmw_update_containers_registry`: The container registry to pull containers from. Default to "quay.io".
* `cifmw_update_containers_org`: The container registry namespace to pull container from. Default to `podified-antelope-centos9`
* `cifmw_update_containers_tag`: The container tag. Default to "current-podified".
* `cifmw_update_containers_cindervolumes`: The names of the cinder volumes prefix. Default to `[]`.
* `cifmw_update_containers_manilashares`: The names of the manila shares prefix. Default to `[]`.
* `cifmw_update_containers_openstack`: Whether to generate CR for updating openstack containers. Default to `false`.
* `cifmw_update_containers_ansibleee_image_url`: Full Ansibleee Image url for updating Ansibleee Image.
* `cifmw_update_containers_edpm_image_url`: Full EDPM Image url for updating EDPM OS image.
* `cifmw_update_containers_ipa_image_url`: Full Ironic Python Agent url needed in Ironic specific podified deployment
* `cifmw_update_containers_rollback`: Rollback the container update changes. Default to `false`. It will be used with cleanup.

## Examples
### 1 - Update OpenStack container
```yaml
- hosts: all
  vars:
    cifmw_update_containers_openstack: true
    cifmw_update_containers_registry: xxxx
    cifmw_update_containers_namespace: xxxx
    cifmw_update_containers_tag: xxxx
  tasks:
    - name: Generate CR for updating openstack containers
      ansible.builtin.include_role:
        name: update_containers
```

### 2 - Update Ansibleee container image
```yaml
- hosts: all
  vars:
    cifmw_update_containers_ansibleee_image_url: quay.rdoproject.org/openstack-k8s-operators/openstack-ansibleee-runner:current-podified
  tasks:
    - name: Generate CR for updating Ansibleee container
      ansible.builtin.include_role:
        name: update_containers
```

### 3 - Update EDPM OS image
```yaml
- hosts: all
  vars:
    cifmw_update_containers_edpm_image_url: quay.rdoproject.org/openstack-k8s-operators/edpm-hardened-uefi:current-podified
  tasks:
    - name: Generate CR for updating EDPM OS container
      ansible.builtin.include_role:
        name: update_containers
```
