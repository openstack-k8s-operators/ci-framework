# General consideration

## Top level parameters

The following parameters allow to set a common value for parameters that
are shared among multiple roles:

- `cifmw_basedir`: The base directory for all of the artifacts. Defaults to
  `~/ci-framework-data`.
- `cifmw_target_host`: (String) The target machine for ci-framework to execute its playbooks against. Defaults to `localhost`.
- `cifmw_crc_hostname`: Allow to set the actual CRC inventory hostname. Mostly used in the fetch_compute_facts hook.
  in the multinode layout, especially for the reproducer case.
- `cifmw_edpm_deploy_baremetal`: (Bool) Toggle whether to deploy edpm on compute nodes.
  provisioned with virtual baremetal vs pre-provisioned VM.
- `cifmw_installyamls_repos`: install_yamls repository location. Defaults to `../..`.
- `cifmw_manifests`: Directory where k8s related manifests will be places. Defaults to
  `{{ cifmw_basedir }}/manifests`.
- `cifmw_path`: customized PATH. Defaults to `~/.crc/bin:~/.crc/bin/oc:~/bin:${PATH}`.
- `cifmw_root_partition_id`: (Integer) Root partition ID for virtual machines. Useful for UEFI images.
- `cifmw_use_libvirt`: (Bool) toggle libvirt support.
- `cifmw_use_crc`: (Bool) toggle rhol/crc usage.
- `cifmw_use_uefi`: (Bool) toggle UEFI support in libvirt_manager provided VMs.
- `cifmw_use_lvms`: (Bool) toggle LVMS support. Defaults to `false`.
- `cifmw_openshift_kubeconfig`: (String) Path to the kubeconfig file if externally provided. If provided will be the kubeconfig to use and update after login.
- `cifmw_openshift_api`: (String) Path to the kubeconfig file. If provided will be the API to authenticate against.
- `cifmw_openshift_user`: (String) Login user. If provided, the user that logins.
- `cifmw_openshift_provided_token`: (String) Initial login token. If provided, that token will be used to authenticate into OpenShift.
- `cifmw_openshift_password`: (String) Login password. If provided is the password used for login in.
- `cifmw_openshift_password_file`: (String) Path to a file that contains the plain login password. If provided is the password used for login in.
- `cifmw_openshift_skip_tls_verify`: (Boolean) Skip TLS verification to login. Defaults to `false`.
- `cifmw_use_opn`: (Bool) toggle openshift provisioner node support.
- `cifmw_use_hive`: (Bool) toggle OpenShift deployment using hive operator.
- `cifmw_use_devscripts`: (Bool) toggle OpenShift deploying using devscripts role.
- `cifmw_openshift_crio_stats`: (Bool) toggle collecting cri-o stats in CRC deployment.
- `cifmw_deploy_edpm`: (Bool) toggle deploying EDPM. Default to false.
- `cifmw_use_vbmc`: (Bool) Toggle VirtualBMC usage. Defaults to `false`.
- `cifmw_use_sushy_emulator`: (Bool) Toggle Sushy Emulator usage. Defaults to `true`.
- `cifmw_sushy_redfish_bmc_protocol`: (String) The RedFish BMC protocol you would like to use with Sushy Emulator, options are `redfish` or `redfish-virtualmedia`. Defaults to `redfish-virtualmedia`
- `cifmw_config_nmstate`: (Bool) toggle NMstate networking deployment. Default to false.
- `cifmw_config_bmh`: (Bool) toggle Metal3 BareMetalHost CRs deployment. Default to false.
- `cifmw_config_certmanager`: (Bool) toggle cert-manager deployment. Default to false.
- `cifmw_skip_os_net_setup`: (bool) Specifies whether os_net_setup should be executed. Default to false.
- `cifmw_ssh_keytype`: (String) Type of ssh keys that will be injected into the controller in order to connect to the rest of the nodes. Defaults to `ecdsa`.
- `cifmw_ssh_keysize`: (Integer) Size of ssh keys that will be injected into the controller in order to connect to the rest of the nodes. Defaults to 521.
- `cifmw_architecture_repo`: (String) Path of the architecture repository on the controller node.
  Defaults to `~/src/github.com/openstack-k8s-operators/architecture`
- `cifmw_arch_automation_file`: (String) Name of the workflow automation file
  in the architecture repository. Defaults to `default.yaml`
- `cifmw_architecture_scenario`: (String) The selected VA scenario to deploy.
- `cifmw_architecture_wait_condition`: (Dict) Structure defining custom wait_conditions for the automation.
- `cifmw_architecture_user_kustomize.*`: (Dict) Structures defining user provided kustomization for automation. All these variables are combined together.
- `cifmw_architecture_user_kustomize_base_dir`: (String) Path where to lock for kustomization patches.
- `cifmw_ceph_target`: (String) The Ansible inventory group where ceph is deployed. Defaults to `computes`.
- `cifmw_run_tests`: (Bool) Specifies whether tests should be executed.
  Defaults to false.
- `cifmw_run_test_role`: (String) Specifies which ci-framework role will be used to run tests. Allowed options are `test_operator`, `tempest` and `shiftstack`. Defaults to `tempest`.
- `cifmw_run_tempest`: (Bool) Specifies whether tempest tests should be run.  Notice tempest tests can be executed with either `test_operator` or `tempest` roles. Defaults to true.
- `cifmw_run_tobiko`: (Bool) Specifies whether tobiko tests should be run. Notice tobiko tests can only be executed with the `test_operator` role. Defaults to false.
- `cifmw_edpm_deploy_nfs`: (Bool) Specifies whether an nfs server should be deployed.
- `cifmw_nfs_target`: (String) The Ansible inventory group where the nfs server is deployed. Defaults to `computes`. Only has an effect if `cifmw_edpm_deploy_nfs` is set to `true`.
- `cifmw_nfs_network`: (String) The network the deployed nfs server will be accessible from. Defaults to `storage`. Only has an effect if `cifmw_edpm_deploy_nfs` is set to `true`.
- `cifmw_nfs_shares`: (List) List of the shares that will be setup in the nfs server.  Only has an effect if `cifmw_edpm_deploy_nfs` is set to `true`.
- `cifmw_fips_enabled`: (Bool) Specifies whether FIPS should be enabled in the deployment. Note that not all deployment methods support this functionality. Defaults to `false`.
- `cifmw_baremetal_hosts`: (Dict) Baremetal nodes environment details. More details [here](../baremetal/01_baremetal_hosts_data.md)
- `cifmw_deploy_obs` (Bool) Specifies whether to deploy Cluster Observability operator.
- `cifmw_openshift_api_ip_address` (String) contains the OpenShift API IP address. Note: it is computed internally and should not be user defined.
- `cifmw_openshift_ingress_ip_address` (String) contains the OpenShift Ingress IP address. Note: it is computed internally and should not be user defined.
- `cifmw_nolog`: (Bool) Toggle `no_log` value for selected tasks. Defaults to `true` (hiding those logs by default).
- `cifmw_parent_scenario`: (String or List(String)) path to existing scenario/parameter file to inherit from.
- `cifmw_configure_switches`: (Bool) Specifies whether switches should be configured. Computes in `reproducer.yml` playbook. Defaults to `false`.
- `cifmw_run_operators_compliance_scans`: (Bool) Specifies whether to run operator compliance scans.  Defaults to `false`.
- `cifmw_run_compute_compliance_scans`: (Bool) Specifies whether to run compliance scans on the first compute.  Defaults to `false`.

```{admonition} Words of caution
:class: danger
If you want to output the content in another location than `~/ci-framework-data`
(namely set the `cifmw_basedir` to some other location), you will have to update
the `ansible.cfg`, updating the value of `roles_path` so that it includes
this new location.

We cannot do this change runtime unfortunately.
```

## Role level parameters

Please refer to the README located within the various roles.

## Provided playbooks and scenarios

The provided playbooks and scenarios allow to deploy a full stack with
various options. Please refer to the provided examples and roles if you
need to know more.

## Hooks

The framework is able to leverage hooks located in various locations. Using
proper parameter name, you may run arbitrary playbook or load custom CRDs at
specific points in the standard run.

Hooks may be presented in two ways:
- as a list
- as a single hook in a parameter

If you want to list multiple hooks, you have to use the following parameter names:

- `pre_infra`: before bootstrapping the infrastructure
- `post_infra`: after bootstrapping the infrastructure
- `pre_package_build`: before building packages against sources
- `post_package_build`: after building packages against sources
- `pre_container_build`: before building container images
- `post_container_build`: after building container images
- `pre_operator_build`: before building operators
- `post_operator_build`: after building operators
- `pre_deploy`: before deploying EDPM
- `post_ctlplane_deploy`: after Control Plane deployment (not architecture)
- `post_deploy`: after deploying EDPM
- `pre_admin_setup`: before admin setup
- `post_admin_setup`: before admin setup
- `pre_tests`: before running tests
- `post_tests`: after running tests

Since we're already providing hooks as list, you may want to just add one or two hooks
using your own environment file. Parameter structure is simple: `PREFIX_HOOKNAME: {hook struct}`

PREFIX must match the above parameters (`pre_infra`, `post_admin_setup` and so on).

The `{hook struct}` is the same as a listed hook, but you'll remove the `name` entry.

Since steps may be skipped, we must ensure proper post/pre exists for specific
steps.

In order to provide a hook, please pass the following as an environment file:

```{code-block} YAML
:caption: custom/my-hook.yml
:linenos:
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
[hooks/playbooks](https://github.com/openstack-k8s-operators/ci-framework/tree/main/hooks/playbooks) while
`glorious.crd` is located in some external path.

Also, the list order is important: the hook will first load the playbook,
then the CRD.

Note that you really should avoid pointing to external resources, in order to
ensure everything is available for job reproducer.

## Ansible tags

In order to allow user to run only a subset of tasks while still consuming the
entry playbook, the Framework exposes tags one may leverage with either `--tags`
or `--skip-tags`:

- `bootstrap`: Run all of the package installation tasks as well as the potential system configuration depending on the options you set.
- `packages`: Run all package installation tasks associated to the options you set.
- `bootstrap_layout`: Run the [reproducer](../reproducers/01-considerations.md) bootstrap steps only.
- `bootstrap_libvirt`: Run the [reproducer](../reproducers/01-considerations.md) libvirt bootstrap only.
- `bootstrap_repositories`: Run the [reproducer](../reproducers/01-considerations.md) repositories bootstrap steps only.
- `devscripts_layout`: Run the [reproducer](../reproducers/01-considerations.md) devscripts bootstrap only.
- `infra`: Denotes tasks to prepare host virtualization and Openshift Container Platform when deploy-edpm.yml playbook is run.
- `build-packages`: Denotes tasks to call the role [pkg_build](../roles/pkg_build.md) when deploy-edpm.yml playbook is run.
- `build-containers`: Denotes tasks to call the role [build_containers](../roles/build_containers.md) when deploy-edpm.yml playbook is run.
- `build-operators`: Denotes tasks to call the role [operator_build](../roles/operator_build.md) when deploy-edpm.yml playbook is run.
- `control-plane`: Deploys the control-plane on OpenShift by creating `OpenStackControlPlane` CRs when deploy-edpm.yml playbook is run.
- `edpm`: Deploys the data-plane (External Data Plane Management) on RHEL nodes by creating `OpenStackDataPlane` CRs when deploy-edpm.yml playbook is run.
- `admin-setup`: Denotes tasks to call the role [os_net_setup](../roles/os_net_setup.md) when deploy-edpm.yml playbook is run.
- `run-tests`: Denotes tasks to call the roles [tempest](../roles/tempest.md) and/or [tobiko](../roles/tobiko.md) when deploy-edpm.yml playbook is run.
- `logs`: Denotes tasks which generate artifacts via the role [artifacts](../roles/artifacts.md) and when collect logs when deploy-edpm.yml playbook is run.

For instance, if you want to bootstrap a hypervisor, and reuse it over and
over, you'll run the following commands:

```Bash
[controller-0]$ ansible-playbook deploy-edpm.yml \
    -K --tags bootstrap,packages \
    [-e @scenarios/centos-9/some-environment -e <...>]
$
[controller-0]$ ansible-playbook deploy-edpm.yml \
    -K --skip-tags bootstrap,packages \
    [-e @scenarios/centos-9/some-environment -e <...>]
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
[controller-0]$ ansible-playbook deploy-edpm.yml -K --tags admin-setup
```

More tags may show up according to the needs.
