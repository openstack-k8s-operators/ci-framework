# Usage guide

The Framework leverages [install_yamls](https://github.com/openstack-k8s-operators/install_yamls)
content and generate the needed bits in order to deploy EDPM on the selected infrastructure.

The Framework will also ensure we're able to reproduce the exact same run we
got in CI with a series of artifacts one may download locally, and re-run.

## Parameters

There are two levels of parameters we may provide:

* top level
* role level

### Top level parameters

The following parameters allow to set a common value for parameters that
are shared among multiple roles:

* `cifmw_basedir`: The base directory for all of the artifacts. Defaults to
`~/ci-framework-data`.
* `cifmw_crc_hostname`: Allow to set the actual CRC inventory hostname. Mostly used in the fetch_compute_facts hook.
in the multinode layout, especially for the reproducer case.
* `cifmw_edpm_deploy_baremetal`: (Bool) Toggle whether to deploy edpm on compute nodes.
provisioned with virtual baremetal vs pre-provisioned VM.
* `cifmw_installyamls_repos`: install_yamls repository location. Defaults to `../..`.
* `cifmw_manifests`: Directory where k8s related manifests will be places. Defaults to
`{{ cifmw_basedir }}/manifests`.
* `cifmw_path`: customized PATH. Defaults to `~/.crc/bin:~/.crc/bin/oc:~/bin:${PATH}`.
* `cifmw_use_libvirt`: (Bool) toggle libvirt support.
* `cifmw_use_crc`: (Bool) toggle rhol/crc usage.
* `cifmw_use_devscripts`: (Bool) toggle devscripts usage.
* `cifmw_openshift_kubeconfig`: (String) Path to the kubeconfig file if externally provided. If provided will be the kubeconfig to use and update after login.
* `cifmw_openshift_api`: (String) Path to the kubeconfig file. If provided will be the API to authenticate against.
* `cifmw_openshift_user`: (String) Login user. If provided, the user that logins.
* `cifmw_openshift_provided_token`: (String) Initial login token. If provided, that token will be used to authenticate into OpenShift.
* `cifmw_openshift_password`: (String) Login password. If provided is the password used for login in.
* `cifmw_openshift_password_file`: (String) Path to a file that contains the plain login password. If provided is the password used for login in.
* `cifmw_openshift_skip_tls_verify`: (Boolean) Skip TLS verification to login. Defaults to `false`.
* `cifmw_use_opn`: (Bool) toggle openshift provisioner node support.
* `cifmw_use_hive`: (Bool) toggle OpenShift deployment using hive operator.
* `cifmw_use_devscripts`: (Bool) toggle OpenShift deploying using devscripts role.
* `cifmw_openshift_crio_stats`: (Bool) toggle collecting cri-o stats in CRC deployment.
* `cifmw_deploy_edpm`: (Bool) toggle deploying EDPM. Default to false.
* `cifmw_config_network`: (Bool) toggle networking deployment based on CI-framework instead of install_yamls. Default to false.

#### Words of caution

If you want to output the content in another location than `~/ci-framework-data`
(namely set the `cifmw_basedir` to some other location), you will have to update
the `ansible.cfg`, updating the value of `roles_path` so that it includes
this new location.

We cannot do this change runtime unfortunately.

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

* `pre_infra`: before bootstrapping the infrastructure
* `post_infra`: after bootstrapping the infrastructure
* `pre_package_build`: before building packages against sources
* `post_package_build`: after building packages against sources
* `pre_container_build`: before building container images
* `post_container_build`: after building container images
* `pre_deploy`: before deploying EDPM
* `post_deploy`: after deploying EDPM
* `post_ctlplane_deploy`: after Control Plane deployment
* `pre_tests`: before running tests
* `post_tests`: after running tests
* `pre_admin_setup`: before admin setup
* `post_admin_setup`: before admin setup
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
[ci_framework/hooks/playbooks](https://github.com/openstack-k8s-operators/ci-framework/tree/main/ci_framework/hooks/playbooks) while
`glorious.crd` is located in some external path.

Also, the list order is important: the hook will first load the playbook,
then the CRD.

Note that you really should avoid pointing to external resources, in order to
ensure everything is available for job reproducer.

## Ansible tags

In order to allow user to run only a subset of tasks while still consuming the
entry playbook, the Framework exposes tags one may leverage with either `--tags`
or `--skip-tags`:

* `bootstrap`: Run all of the package installation tasks as well as the potential system configuration depending on the options you set.
* `packages`: Run all package installation tasks associated to the options you set.
* `bootstrap_layout`: Run the [reproducer](../reproducers/01-considerations.md) bootstrap steps only.
* `bootstrap_repositories`: Run the [reproducer](../reproducers/01-considerations.md) repositories bootstrap steps only.
* `infra`: Denotes tasks to prepare host virtualization and Openshift Container Platform when deploy-edpm.yml playbook is run.
* `build-packages`: Denotes tasks to call the role [pkg_build](../roles/pkg_build.md) when deploy-edpm.yml playbook is run.
* `build-containers`: Denotes tasks to call the role [build_containers](../roles/build_containers.md) when deploy-edpm.yml playbook is run.
* `build-operators`: Denotes tasks to call the role [operator_build](../roles/operator_build.md) when deploy-edpm.yml playbook is run.
* `control-plane`: Deploys the control-plane on OpenShift by creating `OpenStackControlPlane` CRs when deploy-edpm.yml playbook is run.
* `edpm`: Deploys the data-plane (External Data Plane Management) on RHEL nodes by creating `OpenStackDataPlane` CRs when deploy-edpm.yml playbook is run.
* `admin-setup`: Denotes tasks to call the role [os_net_setup](../roles/os_net_setup.md) when deploy-edpm.yml playbook is run.
* `run-tests`: Denotes tasks to call the role [tempest](../roles/tempest.md) when deploy-edpm.yml playbook is run.
* `logs`: Denotes tasks which generate artifacts via the role [artifacts](../roles/artifacts.md) and when collect logs when deploy-edpm.yml playbook is run.

For instance, if you want to bootstrap a hypervisor, and reuse it over and
over, you'll run the following commands:

```Bash
$ ansible-playbook deploy-edpm.yml -K --tags bootstrap,packages [-e @scenarios/centos-9/some-environment -e <...>]
$ ansible-playbook deploy-edpm.yml -K --skip-tags bootstrap,packages [-e @scenarios/centos-9/some-environment -e <...>]
```
Running the command twice, with `--tags` and `--skip-tags` as only difference,
will ensure your environment has the needed directories, packages and
configurations with the first run, while skip all of those tasks in the
following runs. That way, you will save time and resources.

If you've already deployed OpenStack but it failed
during [os_net_setup](../roles/os_net_setup.md) and you've taken steps
to correct the problem and want to test if they resolved the issue,
then use:
```Bash
ansible-playbook deploy-edpm.yml -K --tags admin-setup
```

More tags may show up according to the needs.
