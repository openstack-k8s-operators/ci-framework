# shiftstack
Role for triggering Openshift on Openstack QA automation (installation and tests).

## Parameters
* `cifmw_shiftstack_artifacts_dir`: (*string*) Directory name for the role artifacts. Defaults to `artifacts`.
* `cifmw_shiftstack_basedir`: (*string*) Base directory for the role artifacts and logs. Defaults to `{{ cifmw_basedir }}/tests/shiftstack` (which defaults to `~/ci-framework-data/tests/shiftstack`.
* `cifmw_shiftstack_client_pod_name`: (*string*) Pod name for the pod running the Openshift installer and tests. Defaults to `shiftstackclient`.
* `cifmw_shiftstack_client_pod_namespace`: (*string*) The namespace where the `cifmw_shiftstack_client_pod_name` will be deployed. Defaults to `openstack`.
* `cifmw_shiftstack_client_pod_image`: (*string*) The image for the container running in the `cifmw_shiftstack_client_pod_name` pod. Defaults to `quay.io/shiftstack-qe/shiftstack-client:latest`.
* `cifmw_shiftstack_qa_repo`: (*string*) The repository containing the Openshift on Openstack QA automation. Defaults to `https://review.gerrithub.io/shiftstack/shiftstack-qa`.
* `cifmw_shiftstack_run_playbook`: (*string*) The playbook to be run from the `cifmw_shiftstack_qa_repo` repository. Defaults to `ocp_testing.yaml`.

## Examples
The role is imported in the test playbook, i.e. when:
```
cifmw_run_tests: true
cifmw_run_tempest: false
cifmw_run_test_role: shiftstack
cifmw_run_test_shiftstack_testconfig: 4.15_ovnkubernetes_ipi_va1.yaml

$ ansible-playbook deploy-edpm.yml --extra-vars "cifmw_run_tests=true cifmw_run_tempest=false cifmw_run_test_role=shiftstack cifmw_openshift_kubeconfig={{ ansible_user_dir }}/.kube/config cifmw_run_test_shiftstack_testconfig=4.15_ovnkubernetes_ipi_va1.yaml"
```
