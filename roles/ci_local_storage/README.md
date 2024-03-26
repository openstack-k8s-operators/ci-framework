# ci_local_storage

Ansible role to create persistent volumes on Openshift cluster needed
by openstack services.

## Privilege escalation
If apply, please explain the privilege escalation done in this role.

## Parameters
* `cifmw_cls_basedir`:  (String) Base directory. Defaults to `"{{ cifmw_basedir | default(ansible_user_dir ~ '/ci-framework-data') }}"`
* `cifmw_cls_manifests_dir`: (String) Directory in where OCP manifests will be placed. Defaults to `"{{ cifmw_manifests | default(cifmw_cls_basedir ~ '/artifacts/manifests') }}/storage"`
* `cifmw_cls_storage_class`: (String) The name of the storage class. Defaults to `local-storage`.
* `cifmw_cls_storage_capacity`: (String) Storage capacity in GB. Defaults to `10Gi`.
* `cifmw_cls_local_storage_name`: (String) Name of the local storage name. Defaults to `/mnt/openstack`.
* `cifmw_cls_pv_count`: (Int) Numbers of pvs to create. Defaults to `12`.
* `cifmw_cls_storage_provisioner`: (String) Name of the storage provisioner. Defaults to `cifmw`.
* `cifmw_cls_create_ee_storage`: (Bool) Param to create ee_storage. Defaults to `false`.
* `cifmw_cls_namespace`: (String) The namespace where OCP resources will be installed. Defaults to `openstack`.
* `cifmw_cls_action`: (String) Action to perform, can be `create` or `clean`. Defaults to `create`.
* `cifmw_cls_storage_manifest`:  (Dict) The storage manifest resource to be used to initiate storage class.

## Examples
```YAML
    - hosts: localhost
      vars:
        cifmw_openshift_user: "kubeadmin"
        cifmw_openshift_password: "12345678"
        cifmw_openshift_kubeconfig: "{{ ansible_user_dir }}/.crc/machines/crc/kubeconfig"
        ansible_user_dir: "{{ lookup('env', 'HOME') }}"
        cifmw_path: "{{ ansible_user_dir }}/.crc/bin:{{ ansible_user_dir }}/.crc/bin/oc:{{ ansible_user_dir }}/bin:{{ ansible_env.PATH }}"
      tasks:
        - ansible.builtin.include_role:
            name: ci_local_storage
```
