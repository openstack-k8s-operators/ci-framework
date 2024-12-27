# shiftstack
Role for triggering Openshift on Openstack QA automation (installation and tests).

## Parameters
* `cifmw_shiftstack_ansible_command_logs_dir`: (*string*) Directory name for the ansible command module output. Defaults to `"{{ cifmw_shiftstack_basedir }}/ansible_command_logs"`.
* `cifmw_shiftstack_artifacts_dir`: (*string*) Directory name for the role artifacts. Defaults to `"{{ cifmw_shiftstack_basedir }}/artifacts"`.
* `cifmw_shiftstack_basedir`: (*string*) Base directory for the role artifacts and logs. Defaults to `{{ cifmw_basedir }}/tests/shiftstack` (which defaults to `~/ci-framework-data/tests/shiftstack`.
* `cifmw_shiftstack_client_incluster_secret_manifest`: (*string*) The manifest file for creating the secret that will hold the RHOSO kubeconfig. Defaults to `{{ cifmw_shiftstack_client_pod_name }}_incluster_secret.yml`.
* `cifmw_shiftstack_client_incluster_secret_name:`: (*string*) The secret name that will hold the RHOSO kubeconfig. Defaults to `incluster-kubeconfig`.
* `cifmw_shiftstack_client_pod_name`: (*string*) Pod name for the pod running the Openshift installer and tests. Defaults to `shiftstackclient`.
* `cifmw_shiftstack_client_pod_manifest`: (*string*) The file name for the shiftstackclient pod manifest. Defaults to `"{{ cifmw_shiftstack_client_pod_name }}_pod.yml"`.
* `cifmw_shiftstack_client_pod_namespace`: (*string*) The namespace where the `cifmw_shiftstack_client_pod_name` will be deployed. Defaults to `openstack`.
* `cifmw_shiftstack_client_pod_image`: (*string*) The image for the container running in the `cifmw_shiftstack_client_pod_name` pod. Defaults to `quay.io/shiftstack-qe/shiftstack-client:latest`.
* `cifmw_shiftstack_client_pvc_manifest`: (*string*) The file name for the shiftstackclient pvc manifest. Defaults to `"{{ cifmw_shiftstack_client_pod_name }}_pvc.yml"`.
* `cifmw_shiftstack_cluster_name`: (*string*) The Openshift cluster name. Defaults to `ostest`.
* `cifmw_shiftstack_hypervisor`: (*string*) The hypervisor where RHOSO is deployed. Defaults to `"{{ hostvars[hostvars['controller-0']['cifmw_hypervisor_host'] | default ('')]['ansible_host'] | default('') }}"`.
* `cifmw_shiftstack_exclude_artifacts_regex`: (*string*) Regex that will be passed on `oc rsync` command as `--exclude` param, so the role does not gather the artifacts matching it.
* `cifmw_shiftstack_installation_dir`: (*string*) Directory to place installation files. Defaults to `"{{ cifmw_shiftstack_shiftstackclient_artifacts_dir }}/installation"`.
* `cifmw_shiftstack_manifests_dir`: (*string*) Directory name for the role generated Openshift manifests. Defaults to `"{{ cifmw_shiftstack_basedir }}/manifests"`.
* `cifmw_shiftstack_project_name`: (*string*) The Openstack project name. Defaults to `shiftstack`.
* `cifmw_shiftstack_proxy`: (*string*) The proxy url that should be used to reach the underlying OCP. Defaults to omit.
* `cifmw_shiftstack_qa_gerrithub_change`: (*string*) The gerrithub change to fetch from the `cifmw_shiftstack_qa_repo` repository (i.e. 'refs/changes/29/1188429/50)'. Defaults to ''.
* `cifmw_shiftstack_qa_repo`: (*string*) The repository containing the Openshift on Openstack QA automation. Defaults to `https://review.gerrithub.io/shiftstack/shiftstack-qa`.
* `cifmw_shiftstack_run_playbook`: (*string*) The playbook to be run from the `cifmw_shiftstack_qa_repo` repository. Defaults to `ocp_testing.yaml`.
* `cifmw_shiftstack_sc`: (*string*) The storage class to be used for PVC for the shiftstackclient pod. Defaults to `local-storage`.
* `cifmw_shiftstack_shiftstackclient_artifacts_dir`: (*string*) The artifacts directory path for the shiftstackclient pod. Defaults to `/home/cloud-admin/artifacts`.
* `cifmw_shiftstack_shiftstackclient_incluster_kubeconfig_dir`: (*string*) The directory path in shiftstackclient pod the will hold the RHOSO kubeconfig. Defaults to `/home/cloud-admin/incluster-kubeconfig`.

## Examples
The role is imported in the test playbook, i.e. when:
```
cifmw_run_tests: true
cifmw_run_tempest: false
cifmw_run_test_role: shiftstack
cifmw_run_test_shiftstack_testconfig:
  - 4.17_ovnkubernetes_ipi.yaml
  - 4.17_ovnkubernetes_upi.yaml
cifmw_shiftstack_qa_gerrithub_change: refs/changes/29/1188429/50 #optional

$ ansible-playbook deploy-edpm.yml -e 'cifmw_run_tests=true cifmw_run_tempest=false cifmw_run_test_role=shiftstack cifmw_openshift_kubeconfig={{ ansible_user_dir }}/.kube/config cifmw_shiftstack_qa_gerrithub_change=refs/changes/29/1188429/50' -e 'cifmw_run_test_shiftstack_testconfig=["4.17_ovnkubernetes_ipi.yaml","4.17_ovnkubernetes_upi.yaml"]'
```
