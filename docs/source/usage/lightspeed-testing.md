# OpenStack Lightspeed deployment and functional tests

Deploy Lightspeed with the existing installer, then run its integration playbook
in an AnsibleTest Pod through the existing `test_operator` role. Keep the test
configuration in the consuming operator job's `zuul.d/jobs.yaml`.

The direct route requires the runner fixes from
[lightspeed-tests PR #17](https://github.com/openstack-k8s-operators/lightspeed-tests/pull/17)
to be merged before using the upstream default branch. Do not submit or recheck
the operator job against an upstream branch that does not contain those fixes.

## Job configuration

The core settings are:

```yaml
pre_tests_01_deploy_lightspeed_operator:
  source: install-openstack-lightspeed.yml
  type: playbook
cifmw_openstack_lightspeed_mock_enabled: true
cifmw_run_tests: true
cifmw_test_operator_fail_on_test_failure: true
cifmw_test_operator_stages:
  - name: lightspeed
    type: ansibletest
cifmw_test_operator_namespace: openstack
cifmw_test_operator_ansibletest_ansible_git_repo: https://github.com/openstack-k8s-operators/lightspeed-tests
cifmw_test_operator_ansibletest_ansible_git_branch: ""
cifmw_test_operator_ansibletest_ansible_playbook_path: playbooks/run_lightspeed_tests.yaml
cifmw_test_operator_ansibletest_ansible_inventory: |
  localhost ansible_connection=local ansible_python_interpreter=python3
cifmw_test_operator_ansibletest_ansible_var_files: |
  test_suite_path: /var/lib/ansible/ansible
  lightspeed_url: https://lightspeed-app-server.openstack-lightspeed.svc.cluster.local:8443
  lightspeed_timeout: 120
  lightspeed_token_file: /lightspeed-auth/token
  pytest_args: "-v --tb=short --color=no tests/integration"
  junit_xml_path: /var/lib/AnsibleTests/external_files/baseline.xml
cifmw_test_operator_ansibletest_extra_mounts:
  - name: lightspeed
    extraVol:
      - propagation: [AnsibleTest]
        extraVolType: Undefined
        volumes:
          - name: lightspeed-client-token
            projected:
              sources:
                - serviceAccountToken:
                    path: token
                    expirationSeconds: 3600
        mounts:
          - name: lightspeed-client-token
            mountPath: /lightspeed-auth
            readOnly: true
```

Copy the image, resources, security and result-reader settings from the consuming
job as well. It uses `openstack-ansible-tests:current-podified`, global privilege,
SELinux and storage settings for its single Lightspeed stage, and the existing
`cifmw_test_operator_log_pod_definition` override for the reader. No shared-role
extensions or preparation hook are required. KUTTL runs separately.

The deployment hook installs the catalog, OLM subscription, credential Secret
and OpenStackLightspeed resource. The opt-in mock handles model discovery and
ordinary or streamed completions. Readiness remains bounded by 120 retries at
ten-second intervals, configurable with
`cifmw_openstack_lightspeed_ready_retries`. The operator selects its default
application images when no image override is supplied by the job.

## Source and authentication

The test image clones the configured Git repository into
`/var/lib/ansible/ansible` and executes the relative playbook path above. An empty
branch setting uses the cloned repository's default branch. A nonempty setting
selects a published remote branch; arbitrary commit IDs and PR references are
not supported by the inspected image startup script.

This clone does not use the prepared Zuul checkout. `Depends-On` or adding the
tests repository to `required-projects` does not make its unmerged changes
available to the Pod's independent clone. Merge the required tests changes
first, and inspect the actual Git revision recorded by the runner. There is no
source archive, ConfigMap transport, generated stage file or bootstrap.

The test-operator disables automatic token mounting and currently uses the
`default` ServiceAccount in the test namespace. The job explicitly projects
that account's token at `/lightspeed-auth/token`; Kubernetes rotates it. The
operator creates the `lightspeed-access` `ClusterRole`, granting GET access to
`/ls-access`. The installer binds that role to the test ServiceAccount with a
namespace-specific `ClusterRoleBinding`. This also grants access to other Pods using the same
account in that namespace. Privileged execution does not supply a token.
The client token is separate from the mock provider credential; pass its path,
not its contents, to the runner.

Tests normally run in `openstack` and call the Lightspeed Service in
`openstack-lightspeed`. `cifmw_test_operator_namespace` selects the test namespace
and the ServiceAccount namespace used by the installer's access binding; it
defaults to `openstack` for standalone installation. Test access and dummy
prerequisites are grouped after the service reaches Ready.
`cifmw_openstack_lightspeed_namespace` selects the application namespace; update
the runner's `lightspeed_url` accordingly. The consuming job templates this URL.
The parent deployment supplies test-operator, its AnsibleTest API and the
existing OpenStack ConfigMap, configuration Secret and compute SSH Secret used
by the stage. Existing AnsibleTest parameters select those resource names.

## Results and failures

The runner installs Python 3.12 and locked dependencies, then runs
`tests/integration`: metrics, OKP grounding, authenticated queries and missing
authentication. It saves `baseline.xml`, `baseline.xml.log` and
`baseline.xml.runner.log` on the results PVC. It requires pytest exit code zero
and an executed JUnit case with no failure or error cases. Empty, missing,
malformed and entirely skipped reports fail.

The runner log includes its source path, Git revision and tracked changes when
Git metadata is available, input paths and setup/test failure details. It is a
diagnostic summary, not a full Ansible console transcript. Old outputs for the
report path are cleared before setup. Startup, cloning, fact gathering or
inaccessible artifact storage can fail before this log is written; inspect
Pod container logs in those cases.

The existing role waits for Pods, collects results when its wait has not timed
out, and fails the job when a Pod failed or did not complete. Its usual timeout
is 3600 seconds; this is a controller wait, not a Pod termination deadline.
The reader uses user and group ID 227 and the test Pod's SELinux level to read
the PVC. Its job override retains the reader image, mounts and scheduling settings;
review it if the upstream reader template changes.

Find reports under `controller/ci-framework-data/tests/test_operator/`, checking
the actual nested paths. Read `baseline.xml` for executed cases and failures,
its `.log` for pytest output and `.runner.log` for revision and failure context.
Generated AnsibleTest and reader manifests are under
`artifacts/test-operator-crs`. For application traffic and Pod state, inspect
must-gather, then `namespaces/openstack-lightspeed/pods/` and each Pod's logs.
The direct route does not produce the former bootstrap's `source-revision.json`,
`runner-inputs.json` or outer `runner.log`.

## Validation

For an isolated run, reuse a Ready Lightspeed deployment and installed
test-operator. Ensure the installer has granted the test account access. Copy
the consuming job's test-operator settings into a local variables file, add the
cluster's kubeconfig and storage class, and run a local play containing
`roles: [test_operator]`. No preparation playbook is needed. This creates cluster
resources; preserve reports before removing a completed run's CR and owned
resources to repeat it. Reapplying an identical completed CR does not rerun it.

Local rendering, syntax and runner fixtures do not prove cluster execution.
After the required tests fixes merge and the coordinated changes are submitted,
run combined Zuul validation. Verify default images, actual source revision,
executed application cases and published artifacts, plus deliberate failure
propagation. Inspect the non-voting deployment job's own result: a green
buildset can conceal its failure. Mock results establish the tested integration
path; real-provider credentials and model quality require separate validation.
Real OpenAI access using Jan's credentials and a separate Lightspeed results
folder are follow-up work. The current test client disables TLS verification
in this disposable setup.
