# shiftstack
Role for triggering Openshift on Openstack QA automation (installation and tests).

## Parameters
* `cifmw_shiftstack_artifacts_dir`: (*string*) Directory name for the role artifacts. Defaults to `"{{ cifmw_shiftstack_basedir }}/artifacts"`.
* `cifmw_shiftstack_basedir`: (*string*) Base directory for the role artifacts and logs. Defaults to `{{ cifmw_basedir }}/tests/shiftstack` (which defaults to `~/ci-framework-data/tests/shiftstack`.
* `cifmw_shiftstack_client_pod_name`: (*string*) Pod name for the pod running the Openshift installer and tests. Defaults to `shiftstackclient`.
* `cifmw_shiftstack_client_pod_manifest`: (*string*) The file name for the shiftstackclient pod manifest. Defaults to `"{{ cifmw_shiftstack_client_pod_name }}_pod.yml"`.
* `cifmw_shiftstack_client_pod_namespace`: (*string*) The namespace where the `cifmw_shiftstack_client_pod_name` will be deployed. Defaults to `openstack`.
* `cifmw_shiftstack_client_pod_image`: (*string*) The image for the container running in the `cifmw_shiftstack_client_pod_name` pod. Defaults to `quay.io/shiftstack-qe/shiftstack-client:latest`.
* `cifmw_shiftstack_client_pvc_manifest`: (*string*) The file name for the shiftstackclient pvc manifest. Defaults to `"{{ cifmw_shiftstack_client_pod_name }}_pvc.yml"`.
* `cifmw_shiftstack_cluster_name`: (*string*) The Openshift cluster name. Defaults to `ostest`.
* `cifmw_shiftstack_installation_dir`: (*string*) Directory to place installation files. Defaults to `"{{ cifmw_shiftstack_shiftstackclient_artifacts_dir }}/installation"`.
* `cifmw_shiftstack_project_name`: (*string*) The Openstack project name. Defaults to `shiftstack`.
* `cifmw_shiftstack_qa_gerrithub_change`: (*string*) The gerrithub change to fetch from the `cifmw_shiftstack_qa_repo` repository (i.e. 'refs/changes/29/1188429/50)'. Defaults to ''.
* `cifmw_shiftstack_qa_repo`: (*string*) The repository containing the Openshift on Openstack QA automation. Defaults to `https://review.gerrithub.io/shiftstack/shiftstack-qa`.
* `cifmw_shiftstack_run_playbook`: (*string*) The playbook to be run from the `cifmw_shiftstack_qa_repo` repository. Defaults to `ocp_testing.yaml`.
* `cifmw_shiftstack_sc`: (*string*) The storage class to be used for PVC for the shiftstackclient pod. Defaults to `local-storage`.
* `cifmw_shiftstack_shiftstackclient_artifacts_dir`: (*string*) The artifacts directory path for the shiftstackclient pod. Defaults to `/home/cloud-admin/artifacts`.

## Examples
The role is imported in the test playbook, i.e. when:
```
cifmw_run_tests: true
cifmw_run_tempest: false
cifmw_run_test_role: shiftstack
cifmw_run_test_shiftstack_testconfig: 4.15_ovnkubernetes_ipi_va1.yaml
cifmw_shiftstack_qa_gerrithub_change: refs/changes/29/1188429/50 #optional

$ ansible-playbook deploy-edpm.yml --extra-vars "cifmw_run_tests=true cifmw_run_tempest=false cifmw_run_test_role=shiftstack cifmw_openshift_kubeconfig={{ ansible_user_dir }}/.kube/config cifmw_run_test_shiftstack_testconfig=4.15_ovnkubernetes_ipi_va1.yaml cifmw_shiftstack_qa_gerrithub_change=refs/changes/29/1188429/50"
```
