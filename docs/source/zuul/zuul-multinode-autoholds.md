# Autoholds resources retention mechanism


## Why is it needed?

Zuul uses nodepool to manage the life-cycle of the instances required to run a job, also known as the nodeset. Zuul only manages the default network for initial access, all other networks required for our complex testing are managed via the CI-Framework, external to Zuul.

The ci-framework uses a special set of [playbooks](https://review.rdoproject.org/r/plugins/gitiles/config.git/+/refs/heads/master/playbooks/crc/) to create network resources around the nodepool deployed instances. Those resources are cleaned up on each run, no matter how the run finishes, leading to an environment that may be useless from a debugging perspective.

The autohold retention mechanism checks with Zuul to see if the run has an autohold request and, in that case, skips the cleanup process so the network resources remains.

For the skipped network resources, a script managed by the infrastructure team cleans the resources periodically.

## Where is the code?

The code that handles skipping the cleanup in the framework [repo](https://github.com/openstack-k8s-operators/ci-framework/blob/main/ci/playbooks/multinode-autohold.yml).


## How does it work?

Basically the [code](https://github.com/openstack-k8s-operators/ci-framework/blob/main/ci/playbooks/multinode-autohold.yml) checks against the Zuul API to see if there is an autohold request created for the run based on the information stored in the `zuul` Ansible variable.

The code uses the `krb_request` role that uses kerberos underneath if needed and if a kerberos token is present. If the Zuul API is not secured the method will not use any kind of authentication.

Some Zuul instances are not configured to use the executor as an API so, for those cases, the `zuul_autohold_endpoint` needs to be set to point to the autohold URL of the Zuul instance. If the variable is not present the URL is auto-generated assuming the API is reachable through the executor.

This check is only done if the job failed, if the job passed the autohold will not retain the instances so we follow the same approach with the network resources of cleaning them up before finishing the job.
