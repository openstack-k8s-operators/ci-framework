# OpenStack Lightspeed deployment and functional tests

Deploy Lightspeed with the existing hook, then run its integration suite in an
AnsibleTest Pod through the `test_operator` role. The deployment job retains
its inherited Tempest stage:

```yaml
pre_tests_01_deploy_lightspeed_operator:
  source: install-openstack-lightspeed.yml
  type: playbook
cifmw_openstack_lightspeed_mock_enabled: true
cifmw_run_tests: true
cifmw_test_operator_fail_on_test_failure: true
cifmw_test_operator_stages:
  - name: tempest
    type: tempest
  - name: lightspeed
    type: ansibletest
    pre_test_stage_hooks:
      - name: Prepare Lightspeed tests
        source: prepare-openstack-lightspeed-tests.yml
        type: playbook
    test_vars_file: "{{ cifmw_basedir }}/artifacts/lightspeed-test-stage.yml"
```

The stage list above preserves the default Tempest stage of the Lightspeed
job's parent. If another caller defines additional stages, retain those too.
The `cifmw_setup` role runs deployment hooks before entering the test role.
The preparation hook runs immediately before the Lightspeed stage. It creates
source and authorization resources and writes stage variables; the existing
role creates the AnsibleTest, waits for its Pods and collects the results.

The deployment hook installs the catalog, OLM subscription, credential Secret
and OpenStackLightspeed resource. The opt-in mock handles model discovery and
ordinary or streamed completions. Readiness remains bounded by 120 retries at
ten-second intervals, configurable with
`cifmw_openstack_lightspeed_ready_retries`.

## Source and authentication

Require `openstack-k8s-operators/lightspeed-tests` in the job. While changes
remain unmerged, include both framework and tests PR URLs as `Depends-On:` lines
in the operator PR description. A required project alone does not select a PR.

The preparation hook packages the tracked working files of the Zuul checkout,
including tracked local edits for isolated development. Files outside the index are
excluded; add new test files to the index before a manual run. The immutable
ConfigMap contains a compressed source archive, its revision metadata and a
small bootstrap playbook. A size check leaves room below the ConfigMap limit.
The Pod checks the expected SHA256 before extracting or executing this source.

The current test image always clones a Git repository on startup. It therefore
still clones the public tests repository, but the absolute playbook path points
to the mounted bootstrap. That bootstrap runs the prepared source in a separate
writable directory. The public clone does not select the pytest revision. The
image also processes a root `requirements.yaml` if one is present in its clone;
that startup behavior and network access remain dependencies of the image.

The test-operator disables automatic token mounting and currently uses the `default`
ServiceAccount in the test namespace. The stage explicitly projects that account's token
at `/lightspeed-auth/token`; Kubernetes rotates it. A `ClusterRoleBinding` grants
that identity GET access to `/ls-access`. This also grants that permission to
other Pods using the same account in the test namespace. The client token is
separate from the mock provider credential; neither its value nor its contents
are placed in stage variables, source archives or reports.

Tests run in the existing test namespace, normally `openstack`, and call the
Lightspeed Service in `openstack-lightspeed` over the cluster network. The hook
requires the AnsibleTest CRD and the existing OpenStack ConfigMap, configuration
Secret and compute SSH Secret. It does not install test-operator or create
placeholder OpenStack resources. Those are supplied by the parent deployment.

## Results and failures

The prepared runner installs Python 3.12 and locked dependencies, then selects
`tests/integration`: metrics, OKP grounding, authenticated queries and missing
authentication. It writes `baseline.xml` and `baseline.xml.log` on the results
PVC. The bootstrap also retains `runner.log`, `runner-inputs.json` (paths only)
and `source-revision.json`. It requires the runner to succeed and the JUnit
report to contain executed tests with no failures or errors. Empty, missing,
malformed and entirely skipped reports fail the Pod.

The role checks actual Pod phases, collects completed Pods' PVC contents even
when tests failed, and fails the job when a Pod failed or did not complete.
Completion on the last polling attempt is still collected. The Lightspeed reader
Pod uses user and group ID 227 and the same SELinux level as the test Pod so it can read
the PVC. These security settings apply only to the Lightspeed stage. The role's
usual timeout is 3600 seconds; this is a controller wait, not a Pod termination
deadline. Investigate unfinished Pods if that wait expires.

The existing collector publishes under
`controller/ci-framework-data/tests/test_operator/`. Inspect the actual nested
paths for `baseline.xml`, its `.log` companion, `runner.log` and
`source-revision.json`. Compare the source revision with the Zuul workspace;
it can be a speculative merge commit. The generated AnsibleTest and reader
manifests are under `artifacts/test-operator-crs`, and preparation metadata is
under `artifacts/lightspeed-tests`. The preparation hook log is
`logs/pre_test_hooks_prepare_lightspeed_tests.log`.

## Isolated role validation

Reuse an already deployed, Ready Lightspeed instance and installed test-operator.
This avoids another complete OpenStack deployment. Supply a local prepared tests
checkout, existing OpenStack resource names and the cluster's storage class in
a variables file, for example:

```yaml
cifmw_basedir: /home/cloud-user/ci-framework-data
cifmw_openshift_kubeconfig: /home/cloud-user/.crc/machines/crc/kubeconfig
cifmw_path: "{{ ansible_env.PATH }}"
cifmw_lightspeed_tests_source: /home/cloud-user/src/lightspeed-tests
cifmw_test_operator_namespace: openstack
cifmw_test_operator_storage_class: crc-csi-hostpath-provisioner
cifmw_test_operator_stages:
  - name: lightspeed
    type: ansibletest
    test_vars_file: "{{ cifmw_basedir }}/artifacts/lightspeed-test-stage.yml"
```

First run the preparation hook with that file, then a local play containing
`roles: [test_operator]` with the same variables. These commands create cluster
resources; use them only when cluster execution is intended. The preparation
hook can be rerun safely for source packaging, but a completed AnsibleTest is
not automatically rerun by reapplying an identical resource. Preserve its
reports before removing that run's CR and owned resources for another attempt.

`cifmw_lightspeed_tests_timeout` controls API request timeouts (120 seconds).
`cifmw_openstack_lightspeed_namespace` selects the application namespace;
`cifmw_lightspeed_tests_namespace` selects the test namespace, defaulting to
`cifmw_test_operator_namespace`. The existing AnsibleTest parameters select
OpenStack ConfigMap and Secret names. The stage uses the existing
`openstack-ansible-tests:current-podified` image and inherits the role's storage
class. It enables the same privileged setting as the standalone Lightspeed
example; privilege does not supply a token.

Local syntax, source, manifest and simulated Pod checks do not establish
cluster execution. Accept the migration after a real Pod run publishes passing
integration cases and a deliberate failing run retains its reports and fails
the deployment job. A combined Zuul run must also verify image selection,
coordinated revisions and publication. Inspect the non-voting deployment job's
own result; a green buildset can conceal its failure. KUTTL is separate. Mock
results do not establish real-provider credentials, TLS trust or model quality;
the current test client disables TLS verification in this disposable setup.
