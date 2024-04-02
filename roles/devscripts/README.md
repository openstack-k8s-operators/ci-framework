# devscripts

This role is a wrapper around the set of scripts provided by metal3 CI team
that automates deploying of OpenShift Container Platform on baremetal like
libvirt/kvm virtual machines.

## Privilege escalation

Yes, requires privilege escalation to install dependant packages on the system.
Along with performing network configuration, repository setup and libvirt
networks.

## Exposed tags

* `devscripts_prepare`: Selects tasks related to "preparing the host" and
  building the various needed files.
* `devscripts_deploy`: Overlaps with the previous tag, and adds the actual
  deployment of devscripts managed services.
* `devscripts_post`: Only runs the post-installation tasks.

## Parameters

* `cifmw_devscripts_artifacts_dir` (str) path to the directory to store the
  role artifacts.
* `cifmw_devscripts_config_overrides` (dict) key/value pairs to be used for
  overriding the default configuration. Refer
  [section](#supported-keys-in-cifmw_devscripts_config_overrides) for more
  information.
* `cifmw_devscripts_dry_run` (bool) If enabled, the workflow is evaluated.
* `cifmw_devscripts_src_dir` (str) The parent folder of dev-scripts repository.
* `cifmw_devscripts_remove_libvirt_net_default` (bool) Remove the default
  virtual network. Defaults to `false`.
* `cifmw_devscripts_enable_ocp_nodes_host_routing` (bool) Enable routing via
  host for OCP nodes in case of OVNKubernetes. Defaults to `false`.
* `cifmw_devscripts_enable_iscsi_on_ocp_nodes` (bool) Enable iSCSI services on
  the OpenShift nodes having role as `worker`. Defaults to `false`.
* `cifmw_devscripts_enable_multipath_on_ocp_nodes` (bool) Enable multipath
  services on the OpenShift nodes. Defaults to `false`.
* `cifmw_devscripts_create_logical_volume` (bool) Create a logical volume with
  the name cinder-volumes on all OCP nodes. Defaults to `false`.
* `cifmw_devscripts_host_bm_net_ip_addr` (str) The IP address of the host to be
  assigned. Must be from the specified external network.
* `cifmw_devscripts_use_static_ip_addr` (bool) Use static IP addresses for the
  OCP nodes. Defaults to `false`
* `cifmw_devscripts_external_net` (dict) Key/value pair containing information
  about the network infrastructure.
  Refer [section](#supported-keys-in-cifmw_devscripts_external_net).
* `cifmw_libvirt_manager_configuration_overrides` (dict) key/value pairs to be
  used to override cifmw_libvirt_manager_configuration.

### Secrets management

This role calls the [manage_secrets](./manage_secrets.md) role. It allows to
copy or create the needed secrets.

#### pull-secret

You **must** provide either `cifmw_manage_secrets_pullsecret_file` OR
`cifmw_manage_secrets_pullsecret_content`.

If you provide neither, or both, it will fail.

#### CI Token

You **must** provide either `cifmw_manage_secrets_citoken_file` OR
`cifmw_manage_secrets_citoken_content`.

If you provide neither, or both, it will fail.

### Supported keys in cifmw_devscripts_config_overrides

| Key | Default Value | Description |
| --- | ------------- | ----------- |
| working_dir | `/home/dev-scripts` | Path to the directory to store script artifacts. |
| openshift_version | | The version of OpenShift to be deployed. |
| openshift_release_type | | Type of OpenShift release. Supported values are `nightly\|ga\|okd` |

#### General settings

| Key | Default Value | Description |
| --- | ------------- | ----------- |
| cluster_name | `ocp` | Name for the ocp cluster. |
| base_domain | `openstack.lab` | Base domain to be used for the cluster. |
| ssh_pub_key | | SSH public key to enable access to the nodes part of OCP cluster. |
| ntp_servers | `clock.corp.redhat.com` | NTP servers to be configured in the cluster. |

#### OpenShift networking

| Key | Default Value | Description |
| --- | ------------- | ----------- |
| ip_stack | `v4` | IP stack for the cluster. Supported values are `v4\|v6\|v6v4`. |
| network_type | `OVNKubernetes` | Sets the network type for the OpenShift cluster. Supported values are `OpenShiftSDN\|OVNKubernetes`. |
| provisioning_network_profile | `Managed` | Allow the script to manage the provisioning network. Supported values are `Disabled\|Managed`. |
| manage_pro_bridge | `y` | Allow dev-scripts to manage the provisioning bridge. Supported values are `y\|n`. |
| provisioning_network | | The subnet CIDR to be used for the provisioning network. |
| pro_if | | The network interface to be attached to the provisioning bridge. |
| manage_int_bridge | `y` | Allow dev-scripts to manage the internal bridge. Supported values are `y\n`. |
| int_if | | The network interface to be attached to the internal cluster bridge. |
| manage_br_bridge | `y` | Allow dev-scripts to manage the external bridge. Supported values are `y\|n`. |
| ext_if | | The network interface to be attached to the external bridge. |
| external_subnet_v4 | `192.168.111.0/24` | The external subnet CIDR part of IPv4 family. |
| external_subnet_v6 | | The external subnet CIDR belonging to IPv6 family required when IP stack is other than `v4`. |
| cluster_subnet_v4 | `192.168.16.0/20` | The cluster network cidr for the OpenShift cluster. |
| cluster_subnet_v6 | | The cluster network cidr belonging to IPv6 family. Required when IP stack is other than `v4`. |
| service_subnet_v4 | `172.30.0.0/16` | The service network cidr for the OpenShift cluster. |
| service_subnet_v6 | | The service network cidr from the IPv6 family. Required when IP stack is other than `v4`. |
| network_config_folder | | Absolute path to the folder containing custom network configuration to be applied for the nodes participating in the cluster. |
| bond_primary_interface | | The primary bond interface to be configured. Used when bond interface configuration is enabled. |

#### Virtual Machine

| Key | Default Value | Description |
| --- | ------------- | ----------- |
| num_masters | `3` | The number of VMs that would have OpenShift controller role. |
| master_memory | `32768` | The amount of memory to be set for each controller node. |
| master_disk | `100` | The disk size to be set for each controller node. |
| master_vcpu | `10` | The number of vCPUs to be configured for each controller node. |
| num_workers | `0` | The number of VMs that would have OpenShift worker role. |
| worker_memory_mb | | The amount of memory to be set for each worker node. |
| worker_disk | | The disk size to be set for each worker node. |
| worker_vcpu | | The number of vCPUs to be configured for each worker node. |
| num_extra_workers | | The number of additional VMs to be created that would act as OpenStack computes. |
| extra_worker_memory_mb | |  The amount of memory to be set for the extra nodes. |
| extra_worker_disk | | The disk size to be set for each extra nodes. |
| extra_worker_vcpu | | The number of vCPUs to be configured for each extra nodes. |

### Support keys in cifmw_devscripts_external_net

| Key | Description |
| --- | ----------- |
| gw | IP address of the external network gateway. |
| dns | IP address of the external DNS service. |

## Examples

* Sample config for deploying a compact OpenShift platform with extra nodes, existing external network,
  separate NIC for RH-OSP networks and with OpenShift provisioning network disabled.

  ```yaml
  ---
  ...
  cifmw_use_libvirt: true
  cifmw_libvirt_manager_configuration:
    vms:
      ocp:
        amount: 3
        admin_user: core
        image_local_dir: "/home/dev-scripts/pool"
        disk_file_name: "ocp_master"
        disksize: "105"
        xml_paths:
          - /home/dev-scripts/ocp_master_0.xml
          - /home/dev-scripts/ocp_master_1.xml
          - /home/dev-scripts/ocp_master_2.xml

  cifmw_manage_secrets_citoken_file: "{{ lookup('env', 'HOME')/ci_token }}"
  cifmw_manage_secrets_pullsecret_file: "{{ lookup('env', 'HOME')/pull_secret }}"

  cifmw_use_devscripts: true
  cifmw_devscripts_config_overrides:
    provisioning_network_profile: "Disabled"
    num_extra_workers: 2
    extra_worker_memory_mb: 16384
    extra_worker_disk: 50
    worker_vcpu: 8
  ...
  ```

* Sample config for deploying a HA OpenShift platform with additional networks, OpenShift provisioning network
  is enabled and separate RH OSP networks.

  ```YAML
  cifmw_use_libvirt: true
  cifmw_libvirt_manager_configuration:
    networks:
      osp_trunk: |
        <network>
          <name>osp_trunk</name>
          <forward mode='nat'/>
          <bridge name='osp_trunk' stp='on' delay='0'/>
          <ip family='ipv4' address='192.168.122.1' prefix='24'> </ip>
        </network>
    vms:
      ocp:
        amount: 3
        admin_user: core
        image_local_dir: "/home/dev-scripts/pool"
        disk_file_name: "ocp_master"
        disksize: "105"
        xml_paths:
          - /home/dev-scripts/ocp_master_0.xml
          - /home/dev-scripts/ocp_master_1.xml
          - /home/dev-scripts/ocp_master_2.xml
        nets:
          - osp_trunk

  cifmw_use_devscripts: true

  cifmw_manage_secrets_citoken_content: REDACTED
  cifmw_manage_secrets_pullsecret_content: |
    REDACTED

  cifmw_devscripts_config_overrides:
    openshift_version: "4.16.0"
    num_workers: 3
    worker_memory: 16384
    worker_disk: 100
    worker_vcpu: 10
  ```

* Sample custom variable file for customizing the deployment with add-on configurations.

  ```YAML
  cifmw_use_libvirt: true
  cifmw_libvirt_manager_configuration:
    networks:
      osp_trunk: |
        <network>
          <name>osp_trunk</name>
          <forward mode='nat'/>
          <bridge name='osp_trunk' stp='on' delay='0'/>
          <ip family='ipv4' address='192.168.122.1' prefix='24'> </ip>
        </network>
    vms:
      ocp:
        amount: 3
        admin_user: core
        image_local_dir: "/home/dev-scripts/pool"
        disk_file_name: "ocp_master"
        disksize: "105"
        xml_paths:
          - /home/dev-scripts/ocp_master_0.xml
          - /home/dev-scripts/ocp_master_1.xml
          - /home/dev-scripts/ocp_master_2.xml
        nets:
          - osp_trunk

  cifmw_manage_secrets_citoken_content: REDACTED
  cifmw_manage_secrets_pullsecret_content: |
    REDACTED
  cifmw_use_devscripts: true
  cifmw_devscripts_enable_ocp_nodes_host_routing: true
  cifmw_devscripts_enable_iscsi_on_ocp_nodes: true
  cifmw_devscripts_enable_multipath_on_ocp_nodes: true
  cifmw_devscripts_create_logical_volume: true
  cifmw_devscripts_config_overrides:
    openshift_version: "4.16.0"
    vm_extradisks: "true"
    vm_extradisks_list: "vdb vdc vdd"
    vm_extradisks_size: "10G"
  ```

## References

* [dev-scripts](https://github.com/openshift-metal3/dev-scripts)
* [Additional overrides](https://github.com/openshift-metal3/dev-scripts/blob/master/config_example.sh)
