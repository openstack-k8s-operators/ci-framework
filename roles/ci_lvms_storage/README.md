# ci_lvms_storage

The `ci_lvms_storage` role aims to be a drop in replacement
for `ci_local_storage`. It uses LVMS (Logical Volume Manager
Storage) based on the TopoLVM CSI driver to dynamically
provision local storage built from block devices on OCP
nodes.

This role requires `cifmw_lvms_disk_list` to contain a list of
paths to block devices which already exist on OCP nodes. If
the `cifmw_devscripts_config_overrides.vm_extradisks_list` list
contains `"vda vdb"`, then the `devscripts` role will create these
block devices and `cifmw_lvms_disk_list` should be set to
`['/dev/vda', '/dev/vdb']`. This role will then pass the disk list
to the `deviceSelector` list used by the `LVMCluster` CRD.

## Privilege escalation

It does not have any tasks which use become, but it does need to use
`roles/ci_lvms_storage/templates/lvms-namespace.yaml.j2` to create
create an OpenShift namespace where it then sets up a subscription
as per `roles/ci_lvms_storage/templates/subscription.yaml.j2`. It
uses the `cifmw_lvms_disk_list` list to find disks which it then wipes
clean and adds to an LVMS cluster.

## Parameters

### ci-framework parameters

* `cifmw_use_lvms`: (Boolean) Whether or not to use LVMS (default: `false`)

If the ci-framework is called and `cifmw_use_lvms` is true, then
the playbooks `06-deploy-architecture.yml` and `06-deploy-edpm.yml`
call the `ci_lvms_storage` role to create a storage class called
`lvms-local-storage` and the `ci_gen_kustomize_values` role will
set the `storageClass` to `lvms-local-storage` in the generated
values.yaml files used to build architecture CRs. The Tempest
CR file, created by the `test_operator` role, will also set its
`storageClass` value to `lvms-local-storage`.

If the ci-framework is called and `cifmw_use_lvms` is false, then the
playbooks `06-deploy-architecture.yml` and `06-deploy-edpm.yml`
call the `ci_local_storage` role to create a storage class called
`local-storage` and the `ci_gen_kustomize_values` role will set
the `storageClass` to `local-storage` in the generated values.yaml
files used to build architecture CRs. The Tempest CR file, created by
the `test_operator` role, will also set its `storageClass` value to
`local-storage`.

* `cifmw_lvms_basedir`: (String) Installation base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_lvms_manifests_dir`: (String) Directory in where OCP manifests will be placed. Defaults to `"{{ cifmw_manifests | default(cifmw_cls_basedir ~ '/artifacts/manifests') }}/lvms"`

### LVMCluster CRD Overrides

* `cifmw_lvms_disk_list`: (List) A the list of pre-created block devices on OCP nodes used as PVs of the LVMS cluster.(default `[]`)
* `cifmw_lvms_cluster_name`: (String) The `LVMCluster CRD` template override for the meta name (default `lvmcluster`)
* `cifmw_lvms_force_wipe_devices_and_destroy_all_data`: (Boolean) The `LVMCluster CRD` template override for `deviceSelector` `forceWipeDevicesAndDestroyAllData` (default `true`)
* `cifmw_lvms_fstype`: (String) The `LVMCluster CRD` template override for `deviceClasses` `fstype` (default `xfs`)
* `cifmw_lvms_thin_pool_name`: (String) The `LVMCluster CRD` template override for `thinPoolConfig` name (default `cifmw_lvms_thin_pool`)
* `cifmw_lvms_thin_pool_overprovision_ratio`: (Int) The `LVMCluster CRD` template override for `thinPoolConfig` overprovisionRatio (default `10`)
* `cifmw_lvms_thin_pool_size_percent`: (Int) The `LVMCluster CRD` template override for `thinPoolConfig` sizePercent (default `90`)
* `cifmw_lvms_storage_class`: (String) The `LVMCluster CRD` template override for the `deviceClasses` `name`. In this Ansible role it defaults to `local-storage` though the LVMS operator will prepend `lvms-` to this value, so the resultant default storage class will be `lvms-local-storage`.

### Kubernetes parameters

* `cifmw_lvms_namespace`: (String) The Kubernetes namespace where the LVMS cluster and operator pods will run (default `openshift-storage`)

### kubernetes.core.k8s_info parameters

After a Kubernetes manifest is placed in `cifmw_lvms_manifests_dir` by
the `ansible.builtin.template` module, it is applied to the cluster
with the `kubernetes.core.k8s` module. The `kubernetes.core.k8s_info`
module then polls Kubernetes for the status of the created resource
before the role goes on to apply other manifests. The polling can
be controlled with the following parameters.

* `cifmw_lvms_delay`: (Int) Ansible `delay` passed to tasks which wait for `kubernetes.core.k8s_info` (default `10`)
* `cifmw_lvms_retries`: (Int) Ansible `retries` passed to tasks which wait for `kubernetes.core.k8s_info` (default `60`)


### Optional parameters

* `ci_lvms_storage_tolerations`: (Dict) Allows to pass a set of tolerations to the lvms-operator to configure pods to eventually ignore scheduling restrictions applied to specific workers.

Here an example showing how tolerations can be configured:

```yaml
ci_lvms_storage_tolerations:
  - key: "testOperator"
    value: "true"
    effect: "NoSchedule"
  - key: "testOperator"
    value: "true"
    effect: "NoExecute"
```

## Examples

The example playbook below will create an LVMS cluster using the disks
from the `cifmw_lvms_disk_list` list. An example var for
`cifmw_devscripts_config_overrides` is also set with a matching
`vm_extradisks_list`. This parameter will result in the `devscripts`
role (not called below) creating the devices when it provisions OCP.

The playbook will use the `kubernetes.core.k8s_info` Ansible module
to ensure the LVMS operator and storage cluster are ready and then
report on their status. It will then create a test PVC and test pod
to use the PVC. The last task in the playbook will remove the test
resources as well as delete the entire LVMS cluster, operator and
namespace.

```yaml
- name: LVMS playbook
  gather_facts: false
  hosts: all
  vars:
    cifmw_openshift_kubeconfig: "~/.kube/config"
    cifmw_lvms_disk_list:
      - /dev/vda
      - /dev/vdb
    cifmw_devscripts_config_overrides:
      vm_extradisks: "true"
      vm_extradisks_list: "vdb vda"
      vm_extradisks_size: "10G"
  tasks:
    - name: Create Storage Class
      ansible.builtin.include_role:
        name: ci_lvms_storage

    - name: Report on Storage Class
      ansible.builtin.include_role:
        name: ci_lvms_storage
        tasks_from: status.yml

    - name: Test the Storage Class
      ansible.builtin.include_role:
        name: ci_lvms_storage
        tasks_from: test.yml

    - name: Clean up Storage Class
      ansible.builtin.include_role:
        name: ci_lvms_storage
        tasks_from: cleanup.yml
```

## Testing the `ci_lvms_storage` role

The `ci_lvms_storage` role is designed to be run on an OCP cluster
which has unused disks (besides the one where root is mounted). It
does not have a molecule directory however it can be tested by the
ci-framework `devscripts` integration by passing the following:

```yaml
cifmw_devscripts_config_overrides:
  vm_extradisks: "true"
  vm_extradisks_list: "vda vdb"
  vm_extradisks_size: "50G"
```
The `lsblk` command on any OCP node should show the extra block
devices. If the example playbook is then run it will use the same
parameters to create an LVMS cluster which uses `/dev/vda` and
`/dev/vdb` for backend storage.

The `tasks_from: status.yml` in the example playbook will show
the cluster status including the block devices which are used.

The `tasks_from: test.yml` in the example playbook will create
a PVC and a test POD which mounts the PVC. It will be clear from
the Ansible output if the storage class provided by this role
is functional.
