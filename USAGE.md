# CI Framework - Usage guide
## Purpose
The purpose of this repository is to provide a unified tool for various uses,
from dev testing to CI infra.

## Workflow integration
In the end, the main entrypoint will be from within the
[install_yamls](https://github.com/openstack-k8s-operators/install_yamls)
repository, with new Makefile targets.

The Framework will then leverage install_yamls content and generate the needed
bits in order to deploy EDPM on the selected infrastructure.

The Framework will also ensure we're able to reproduce the exact same run we
got in CI with a series of artifacts one may download locally, and re-run.

## Parameters
There are two levels of parameters we may provide:
- top level
- role level

### Top level parameters
The following parameters allow to set a common value for parameters that
are shared among multiple roles:
* `cifmw_basedir`: The base directory for all of the artifacts. Defaults to
`~/ci-framework`
* `cifmw_installyamls_repos`: install_yamls repository location. Defaults to `../..`

### Role level parameters
Please refer to the README located within the various roles.

## Provided playbooks and scenarios
The provided playbooks and scenarios allow to deploy a full stack with
various options. Please refer to the provided examples and roles if you
need to know more.

## Hooks
The framework is able to leverage hooks located in various locations. Using
proper parameter name, you may run arbitrary playbook or load custom CRDs at
specific points in the standard run.

Allowed parameter names are:
* `pre_infra`: before bootstraping the infrastructure
* `post_infra`: after bootstraping the infrastructure
* `pre_package_build`: before building packages against sources
* `post_package_build`: after building packages against sources
* `pre_container_build`: before building container images
* `post_container_build`: after building container images
* `pre_deploy`: before deploying EDPM
* `post_deploy`: after deploying EDPM
* `pre_tests`: before running tests
* `post_tests`: after running tests
* `pre_reporting`: before running reporting
* `post_reporting`: after running reporting

Since steps may be skipped, we must ensure proper post/pre exists for specific
steps.

In order to provide a hook, please pass the following as an environment file:
```YAML
pre_infra:
    - name: My glorious hook name
      type: playbook
      source: foo.yml
    - name: My glorious CRD
      type: crd
      host: https://my.openshift.cluster
      username: foo
      password: bar
      wait_condition:
        type: pod
      source: /path/to/my/glorious.crd
```
In the above example, the `foo.yml` is located in
[ci_framework/hooks/playbooks](ci_framework/hooks/playbooks) while
`glorious.crd` is located in some external path.

Also, the list order is important: the hook will first load the playbook,
then the CRD.

Note that you really should avoid pointing to external resources, in order to
ensure everything is available for job reproducer.
