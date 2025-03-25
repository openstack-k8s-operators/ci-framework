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
- `cifmw_set_openstack_containers`: (Bool) Run set_openstack_containers role during deployment to update openstack containers. Defaults to `false`.
- `cifmw_sushy_redfish_bmc_protocol`: (String) The RedFish BMC protocol you would like to use with Sushy Emulator, options are `redfish` or `redfish-virtualmedia`. Defaults to `redfish-virtualmedia`
- `cifmw_config_nmstate`: (Bool) toggle NMstate networking deployment. Default to false.
- `cifmw_config_multus`: (Bool) toggle Multus networking deployment. Default to false.
- `cifmw_config_bmh`: (Bool) toggle Metal3 BareMetalHost CRs deployment. Default to false.
- `cifmw_config_certmanager`: (Bool) toggle cert-manager deployment. Default to false.
- `cifmw_skip_os_net_setup`: (bool) Specifies whether os_net_setup should be executed. Default to false.
- `cifmw_ssh_keytype`: (String) Type of ssh keys that will be injected into the controller in order to connect to the rest of the nodes. Defaults to `ecdsa`.
- `cifmw_ssh_keysize`: (Integer) Size of ssh keys that will be injected into the controller in order to connect to the rest of the nodes. Defaults to 521.
- `cifmw_architecture_repo`: (String) Path of the architecture repository on the controller node.
  Defaults to `~/src/github.com/openstack-k8s-operators/architecture`
- `cifmw_architecture_scenario`: (String) The selected VA scenario to deploy.
- `cifmw_architecture_wait_condition`: (Dict) Structure defining custom wait_conditions for the automation.
- `cifmw_architecture_user_kustomize.*`: (Dict) Structures defining user provided kustomization for automation. All these variables are combined together.
- `cifmw_architecture_user_kustomize_base_dir`: (String) Path where to lock for kustomization patches.
- `cifmw_ceph_target`: (String) The Ansible inventory group where ceph is deployed. Defaults to `computes`.
- `cifmw_run_tests`: (Bool) Specifies whether tests should be executed.
  Defaults to false.
- `cifmw_run_test_role`: (String) Specifies which ci-framework role will be used to run tests. Allowed options are `test_operator`, `tempest` and `shiftstack`. Defaults to `tempest`.
- `cifmw_edpm_deploy_nfs`: (Bool) Specifies whether an nfs server should be deployed.
- `cifmw_nfs_target`: (String) The Ansible inventory group where the nfs server is deployed. Defaults to `computes`. Only has an effect if `cifmw_edpm_deploy_nfs` is set to `true`.
- `cifmw_nfs_network`: (String) The network the deployed nfs server will be accessible from. Defaults to `storage`. Only has an effect if `cifmw_edpm_deploy_nfs` is set to `true`.
- `cifmw_nfs_shares`: (List) List of the shares that will be setup in the nfs server. Only has an effect if `cifmw_edpm_deploy_nfs` is set to `true`.
- `cifmw_fips_enabled`: (Bool) Specifies whether FIPS should be enabled in the deployment. Note that not all deployment methods support this functionality. Defaults to `false`.
- `cifmw_baremetal_hosts`: (Dict) Baremetal nodes environment details. More details [here](../baremetal/01_baremetal_hosts_data.md)
- `cifmw_deploy_obs` (Bool) Specifies whether to deploy Cluster Observability operator.
- `cifmw_openshift_api_ip_address` (String) contains the OpenShift API IP address. Note: it is computed internally and should not be user defined.
- `cifmw_openshift_ingress_ip_address` (String) contains the OpenShift Ingress IP address. Note: it is computed internally and should not be user defined.
- `cifmw_nolog`: (Bool) Toggle `no_log` value for selected tasks. Defaults to `true` (hiding those logs by default).
- `cifmw_parent_scenario`: (String or List(String)) path to existing scenario/parameter file to inherit from.
- `cifmw_configure_switches`: (Bool) Specifies whether switches should be configured. Computes in `reproducer.yml` playbook. Defaults to `false`.
- `cifmw_use_ocp_overlay`: (Boolean) Specifies whether OCP nodes deployed via devscripts should use overlay images. Using overlay images speeds up the redeployment when using the reproducer role locally but in CI each job is cleaned up and redeployed. Creating the overlay image takes time so should be disabled when not used. Defaults to `true`.
- `cifmw_run_operators_compliance_scans`: (Bool) Specifies whether to run operator compliance scans. Defaults to `false`.
- `cifmw_run_compute_compliance_scans`: (Bool) Specifies whether to run compliance scans on the first compute. Defaults to `false`.
- `cifmw_run_id`: (String) CI Framework run identifier. This is used in libvirt_manager, to add some uniqueness to some types of virtual machines (anything that's not OCP, CRC nor controller).
  If not set, the Framework will generate a random string for you, and store it on the target host, in `{{ cifmw_basedir }}/artifacts/run-id`
- `cifmw_deploy_architecture_args`: (String) additional args and parameters to pass to the deploy-architecture script. Default is `''`.
- `cifmw_enable_virtual_baremetal_support`: (Bool) Toggle the deployment and configuration of virtual baremetal services. If enabled Sushy Emulator will be deployed to OCP and Libvirt will be configured on the CI-Framework Ansible controller node. Defaults to `false`
- `cifmw_openshift_setup_enable_operator_catalog_override`: (Bool) Toggles the option to deploy a custom CatalogSource and patch dependent operators to use it. Defaults to `false`

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
- `post_install_operators_kuttl_from_operator`: after installing openstack operator for kuttl test when calling them from the operator's make target
- `pre_kuttl_from_operator`: before running kuttl test when calling them from
    the operator's make target

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

## Debugging kuttl job

This example how to debug `kuttl` job on hold node was based on job, that runs
tests:

```raw
TASK [Run kuttl tests _raw_params=run-kuttl-tests.yml] *************************
included: /home/zuul/src/github.com/openstack-k8s-operators/ci-framework/ci/playbooks/kuttl/run-kuttl-tests.yml for localhost => (item=openstack)
included: /home/zuul/src/github.com/openstack-k8s-operators/ci-framework/ci/playbooks/kuttl/run-kuttl-tests.yml for localhost => (item=barbican)
included: /home/zuul/src/github.com/openstack-k8s-operators/ci-framework/ci/playbooks/kuttl/run-kuttl-tests.yml for localhost => (item=keystone)
included: /home/zuul/src/github.com/openstack-k8s-operators/ci-framework/ci/playbooks/kuttl/run-kuttl-tests.yml for localhost => (item=horizon)
```

To run the playbooks as it was done on Zuul, do:

```shell
cd src/github.com/openstack-k8s-operators/ci-framework
# make sure ansible.cfg role path contains: ~/ci-framework-data/artifacts/roles

# you can edit list of operators to be tested, by editing: ci/playbooks/kuttl/e2e-kuttl.yml
# and replace: cifmw_kuttl_tests_operator_list with list of operators to check.

cat << EOF > testvars.yaml
---
ansible_user_dir: /home/zuul
zuul:
  projects:
    github.com/openstack-k8s-operators/ci-framework:
      src_dir: src/github.com/openstack-k8s-operators/ci-framework
cifmw_internal_registry_login: false
cifmw_basedir: "{{ ansible_user_dir }}/ci-framework-data"
cifmw_openshift_setup_skip_internal_registry: true
cifmw_artifacts_basedir: "{{ ansible_user_dir }}/ci-framework-data/artifacts "
cifmw_installyamls_repos: "{{ ansible_user_dir }}/src/github.com/openstack-k8s-operators/install_yamls"
EOF

# Take the inventory.yaml file from /zuul-info directory from failing job
curl -SL https://logserver.rdoproject.org/876/rdoproject.org/876b1be532664415afb9ad158d1b031c/zuul-info/inventory.yaml > zuul-vars-tmp.yaml
yq .all.vars zuul-vars-tmp.yaml > zuul-vars.yaml

ansible-playbook -e @testvars.yaml -e @zuul-vars.yaml ci/playbooks/kuttl/e2e-kuttl.yml
```



## Rerun kuttl job on local VM

- Deploy CRC

```shell
# Run crc setup first if not executed earlier
/usr/local/bin/crc start --memory 24000 --disk-size 80 --cpus 14
```

- configure additional nodes

Based on: https://github.com/openstack-k8s-operators/install_yamls/?tab=readme-ov-file#deploy-dev-env-using-crc-edpm-nodes-with-isolated-networks

```shell
git clone https://github.com/openstack-k8s-operators/install_yamls ~/src/github.com/openstack-k8s-operators/install_yamls
cd ~/src/github.com/openstack-k8s-operators/install_yamls/devsetup

make download_tools
make crc_attach_default_interface
EDPM_TOTAL_NODES=1 make edpm_compute
```

- Prepare for kuttl:
```
pip3 install ansible-core yq
git clone https://github.com/openstack-k8s-operators/install_yamls ~/src/github.com/openstack-k8s-operators/install_yamls
git clone https://github.com/openstack-k8s-operators/ci-framework ~/src/github.com/openstack-k8s-operators/ci-framework

# Deploy compute host
cd ~/src/github.com/openstack-k8s-operators/install_yamls/devsetup
make download_tools
make crc_attach_default_interface
EDPM_TOTAL_NODES=1 make edpm_compute

sudo virsh attach-interface --domain edpm-compute-0 --type network --source default --model virtio --config --live
# attach twice even that it will fail.
sudo virsh attach-interface --domain edpm-compute-0 --type network --source default --model virtio --config --live || true
edpm_node_ip_address=$(sudo virsh net-dhcp-leases default | grep edpm-compute | awk '{print $5}' | cut -f1 -d'/')

cd ~/src/github.com/openstack-k8s-operators/ci-framework/

ansible-galaxy install -r requirements.yml
sed -i 's/localhost/controller/g' inventory.yml

mkdir -p roles/prepare-workspace/tasks/

curl -SL https://logserver.rdoproject.org/e56/rdoproject.org/e56761f5b6e147c5b0a424c47e8f0503/zuul-info/inventory.yaml > zuul-inventory.yaml
old_controller_ip=$(cat zuul-inventory.yaml | yq -e .all.hosts.controller.ansible_host | xargs)
new_controller_ip=$(ip route get 1.2.3.4 | awk '{print $7}' | head -n1)
old_controller_user=$(cat zuul-inventory.yaml | yq -e .all.hosts.controller.ansible_user | xargs)
new_controller_user=$(whoami)
old_crc_ip=$(cat zuul-inventory.yaml | yq -e .all.hosts.crc.ansible_host | xargs)
new_crc_ip=192.168.130.11
sed -i "s/$old_controller_ip/$new_controller_ip/g" zuul-inventory.yaml
sed -i "s/ansible_user: $old_controller_user/ansible_user: $new_controller_user/g" zuul-inventory.yaml
sed -i "s/$old_crc_ip/$new_crc_ip/g" zuul-inventory.yaml

for host in localhost $new_controller_ip $new_crc_ip $edpm_node_ip_address; do
    ssh-keyscan -H $host >> ~/.ssh/known_hosts
done

if ! [ -f "~/.ssh/id_ed25519" ]; then
  ssh-keygen -t ed25519 -a 200 -f ~/.ssh/id_ed25519 -N ""
fi

cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
scp -i ~/.crc/machines/crc/id_ecdsa -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ~/.ssh/id_ed25519.pub  core@192.168.130.11:~/.ssh/authorized_keys.d/controller
scp -i ~/.crc/machines/crc/id_ed25519 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ~/.ssh/id_ed25519.pub  core@192.168.130.11:~/.ssh/authorized_keys.d/controller
sshpass -p "12345678" ssh-copy-id -o StrictHostKeyChecking=no -i ~/.ssh/id_ed25519.pub "root@$edpm_node_ip_address"

# Gen zuul-vars.yaml
yq .all.vars zuul-inventory.yaml > zuul-vars.yaml

# create required files to satisfy world
executor_dir=$(dirname $(cat zuul-vars.yaml | yq -e '.zuul.executor.inventory_file' | sed 's|/inventory.yaml||g' | xargs))
executor_workdir="$executor_dir/work/logs/zuul-info"
sudo mkdir -p $executor_workdir
sudo chown $(whoami):$(whoami) $executor_workdir
ln -s $(pwd)/zuul-inventory.yaml $executor_workdir/inventory.yaml

cat << EOF > testvars.yaml
---
ansible_user_dir: /home/$(whoami)
zuul:
  projects:
    github.com/openstack-k8s-operators/ci-framework:
      src_dir: src/github.com/openstack-k8s-operators/ci-framework
cifmw_internal_registry_login: false
cifmw_basedir: "{{ ansible_user_dir }}/ci-framework-data"
cifmw_openshift_setup_skip_internal_registry: true
cifmw_artifacts_basedir: "{{ ansible_user_dir }}/ci-framework-data/artifacts "
cifmw_installyamls_repos: "{{ ansible_user_dir }}/src/github.com/openstack-k8s-operators/install_yamls"
nodepool:
  cloud: ""
## From zuul.d/kuttl_multinode.yaml
cifmw_extras:
  - '@scenarios/centos-9/kuttl_multinode.yml'
cifmw_kuttl_tests_operator_list:
  - openstack
  - barbican
  - keystone
  - horizon
commands_before_kuttl_run:
  - oc get pv
  - oc get all
commands_after_kuttl_run:
  - oc get pv
  - oc get all
EOF

sudo mkdir -p /etc/ci/env
cat << 'EOF' > gen-network-info.sh
#!/bin/bash

echo "crc_ci_bootstrap_networks_out:"

for vm in crc edpm-compute-0; do
  if [ "$vm" == "crc" ]; then
    net="crc"
  else
    net="default"
  fi
  ip=$(sudo virsh net-dhcp-leases "$net" | grep "$vm" | awk '{print $5}' | cut -f 1 -d'/')
  gw=$(sudo virsh net-dumpxml default | grep -o "address='[^']*'" | tail -n1 | cut -f2 -d'=' | xargs)
  mac=$(sudo virsh domiflist "$vm" | grep network | awk '{print $5}' | head -1)
  iface=$(ip route get 8.8.8.8 | awk '{print $5; exit}')

  if [ -z "$ip" ]; then
      ip="192.168.122.10"
  fi

  if [ -z "$gw" ]; then
      gw="192.168.122.1"
  fi
  echo "  $vm:"
  for role in default internal-api storage tenant; do
  echo "    $role:"
  echo "      connection: $net"
  echo "      gw: $gw"
  echo "      iface: $iface"
  echo "      ip: $ip"
  echo "      mac: $mac"
  echo "      mtu: '1500'"
  done
done

echo """
crc_ci_bootstrap_provider_dns:
  - $(ip route get 1.2.3.4 | awk '{print $7}')
  - 9.9.9.9
  - 1.1.1.1
"""
EOF

bash gen-network-info.sh | sudo tee /etc/ci/env/networking-info.yml

ansible-playbook -i inventory.yml -e @testvars.yaml -e @zuul-vars.yaml ci/playbooks/multinode-customizations.yml
ansible-playbook -i inventory.yml -e @testvars.yaml -e @zuul-vars.yaml ci/playbooks/e2e-prepare.yml
ansible-playbook -i inventory.yml -e @testvars.yaml -e @zuul-vars.yaml ci/playbooks/dump_zuul_data.yml
ansible-playbook -i inventory.yml -e @testvars.yaml -e @zuul-vars.yaml ci/playbooks/kuttl/run.yml
