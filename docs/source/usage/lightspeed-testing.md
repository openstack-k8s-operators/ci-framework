# OpenStack Lightspeed deployment and functional tests

Use two ordered `pre_tests` hooks in the Lightspeed deployment job:

```yaml
pre_tests_01_deploy_lightspeed_operator:
  source: install-openstack-lightspeed.yml
  type: playbook
pre_tests_02_run_lightspeed_tests:
  source: run-openstack-lightspeed-tests.yml
  type: playbook
cifmw_openstack_lightspeed_mock_enabled: true
```

The job must require `openstack-k8s-operators/lightspeed-tests` so workspace
preparation supplies the tested revision on the controller. Include a
`Depends-On: <actual lightspeed-tests PR URL>` in the consuming PR description
while test-runner changes remain unmerged. The hook uses the prepared checkout;
it does not clone an unrelated `main` branch.

The deployment hook installs the catalog, OLM subscription, credential Secret,
and OpenStackLightspeed custom resource. Mock deployment is opt-in. It waits
for the mock Pod to be Ready, restarts that Pod after its code changes, and
allows up to 120 retries at ten-second intervals for application readiness.
Set `cifmw_openstack_lightspeed_ready_retries` to change that bounded wait.
Failure diagnostics include Pods, Deployments and events, followed by failure.

The test hook creates a dedicated `lightspeed-tests` ServiceAccount and grants
only GET on `/ls-access`. It obtains a short-lived client token, stores it in a
private temporary directory, and forwards the application Service to an unused
loopback port. The client token is distinct from the provider API credential.
The wrapper reads the token file in Python; token contents are not runner vars
or published artifacts. The hook cleans up the token and its tunnel on failure
as well as success. RBAC objects remain available for subsequent runs.

## Integration tests

The `baseline` run selects `tests/integration`: authenticated queries, metrics,
OKP grounding and missing-authentication rejection. Configuration unit tests
are checked separately. The hook does not alter the provider Service.

The hook invokes the Lightspeed repository's Ansible wrapper with a maximum
runtime of 1800 seconds. The wrapper uses Python 3.12 and locked dependencies,
saves pytest output, and requires pytest exit code zero and a JUnit report.
A test failure fails the wrapper, the hook and the calling job. The wrapper
does not independently validate XML contents or reject an entirely skipped
suite; inspect the reported test counts as part of CI acceptance.

## Parameters and artifacts

`cifmw_lightspeed_tests_source` defaults to
`~/src/github.com/openstack-k8s-operators/lightspeed-tests` on the controller.
Override it for a local checkout. `cifmw_openshift_kubeconfig` selects cluster
access, falling back to CRC's kubeconfig. The namespace is inherited from
`cifmw_openstack_lightspeed_namespace`, defaulting to `openstack-lightspeed`.
`cifmw_lightspeed_tests_timeout` controls individual API requests (default 120
seconds).

Artifacts default to `{{ cifmw_basedir }}/tests/lightspeed`: source revision,
port-forward output, baseline JUnit XML, pytest log and Ansible runner log.
Override `cifmw_lightspeed_tests_artifacts` for local testing. The existing
framework collector publishes its `tests` directory. Inspect the deployment
job's actual result as well as its reports when the job is non-voting.

From the operator PR's Zuul bot comment, open the buildset, then
`lightspeed-operator-deployment-crc`, then its logs. Relative to that build's
log directory, look for:

- `controller/ci-framework-data/logs/pre_tests_01_deploy_lightspeed_operator.log`:
  installation and the Ready wait.
- `controller/ci-framework-data/logs/pre_tests_02_run_lightspeed_tests.log`:
  authentication setup, API tunnel, test execution and cleanup.
- `controller/ci-framework-data/tests/lightspeed/baseline.xml`: individual test
  cases and their results.
- `controller/ci-framework-data/tests/lightspeed/baseline.xml.log`: pytest output.
- `controller/ci-framework-data/tests/lightspeed/baseline-ansible.log`: dependency
  setup, runner output and exit code, including setup failures.
- `controller/ci-framework-data/tests/lightspeed/source-revision.txt`: test checkout
  revision and working-tree changes. Use `zuul-info/inventory.yaml` to identify
  the PR revisions; Zuul's checkout HEAD may be a speculative merge commit.

Accept the run only when the deployment job itself succeeds and the integration
report contains executed passing tests. A green buildset alone can conceal a
non-voting deployment failure. KUTTL is a separate job and suite.

## Submitting the coordinated changes

The test-runner changes need a `lightspeed-tests` PR as well as the framework
and operator PRs. Before rechecking the operator PR, put both the framework PR
URL and the actual test-runner PR URL in its description, each on its own
`Depends-On:` line. A `required-projects` entry supplies a checkout; it does not
by itself select an unmerged PR. Do not submit a placeholder dependency URL.

This integration runs the existing suite on the CI controller through its
Ansible wrapper. It does not create an `AnsibleTest` resource or replace the
job's inherited test-operator stages. A future test-operator implementation
would need explicit token mounting and a way to use the prepared test revision.

CRC validates the same hooks without waiting for a complete Zuul deployment.
It does not validate workspace preparation, content-provider image selection,
cross-repository dependencies or published artifact collection. A final combined
Zuul run is required. Mock results do not establish real-provider credentials,
TLS trust or model quality. The current test client's TLS verification remains
disabled for the disposable test environment.
