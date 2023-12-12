# Testing

Right now we are using 3 different CI systems in the CI Framework project:

- Github workflows
- Zuul CI
- Prow CI

The goal was to unify the tests in a single CI system but since we can't have privilege escalation using Prow CI, the team has decided to use Zuul CI to execute tests under each ansible role.

## Github workflow
A series of Github workflows take place in the pull request checks:

- Spellchecking using pySpelling
- Ensure commit message has a (checked) checklist
- CodeQL (actually a scheduled run)

### Spellchecking
We're using pySpelling, a python wrapper around aspell. You can add custom words
in the `docs/dictionary/en-custom.txt` file. In order to keep it tidy and
avoid duplication, please do as follow:
```Bash
[laptop]$ sudo dnf install -y aspell-en
[laptop]$ pip install pyspelling
[laptop]$ make spelling
# Correct actual spelling issues, or add new words to
# docs/dictionary/tmp
# Then, validate again the spelling (and re-build the dictionary)
[laptop]$ make spelling
```
That way, you ensure that only unique, lower-case words are added to the list.


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
