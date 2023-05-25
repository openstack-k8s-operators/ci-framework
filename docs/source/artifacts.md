# Testing

Right now we are using 2 different CI systems in the CI Framework project:

- Zuul CI
- Prow CI

The goal was to unify the tests in a single CI system but since we can't have privilege escalation using Prow CI, the team has decided to use Zuul CI to execute tests under each ansible role.

## Prow CI

All the jobs are being configured through the [openshift/release](https://github.com/openshift/release/) project.

We can find two kind of configuration:

- [config](https://github.com/openshift/release/tree/master/ci-operator/config/openstack-k8s-operators/ci-framework): Right now we just have [openstack-k8s-operators-ci-framework-main.yaml](https://github.com/openshift/release/blob/master/ci-operator/config/openstack-k8s-operators/ci-framework/openstack-k8s-operators-ci-framework-main.yaml) with the images we are using, the assigned resources and the name of the tests (pre-commit, ansible-test).
    - The image used for the tests is specified under the CI Framework project in the Containerfile.ci file.
    - We can find the targets called to execute the tests under the [Makefile](https://github.com/openstack-k8s-operators/ci-framework/blob/main/Makefile).
- [jobs](https://github.com/openshift/release/tree/master/ci-operator/jobs/openstack-k8s-operators/ci-framework): Here we can find the pre-submit and post-submit files.

We can see the past and current jobs with the [openshift deck dashboard](https://prow.ci.openshift.org/).

We can check the [Prow status - openstack-k8s-operators/ci-framework](https://prow.ci.openshift.org/?repo=openstack-k8s-operators%2Fci-framework). Here we will see under the repository all the jobs involved per PR with the schedule, duration, state, logs, etc.

It can be useful also to check the [Tide status - openstack-k8s-operators/ci-framework](https://prow.ci.openshift.org/tide-history?repo=openstack-k8s-operators%2Fci-framework). In this part we can see the under this repository every commit the action triggered in Prow CI.
