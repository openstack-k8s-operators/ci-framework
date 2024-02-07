# devscripts

This role is a wrapper around the set of scripts provided by metal3 CI team
that automates deploying of OpenShift Container Platform on baremetal like
libvirt/kvm virtual machines.

## Privilege escalation

Yes, requires privilege escalation to install dependant packages on the system. Along with performing
network configuration, repository setup and libvirt networks.

## Exposed tags

* `devscripts_prepare`: Selects tasks related to "preparing the host" and building the various
needed files.
* `devscripts_deploy`: Overlaps with the previous tag, and adds the actual deployment of devscripts
managed services.
* `devscripts_post`: Only runs the post-installation tasks.

## Parameters

* `cifmw_devscripts_artifacts_dir` (str) path to the directory to store the role artifacts.
* `cifmw_devscripts_config_overrides` (dict) key/value pairs to be used for overriding the default
  configuration. Refer [section](#supported-keys-in-cifmw_devscripts_config_overrides) for more information.
* `cifmw_devscripts_dry_run` (bool) If enabled, the workflow is evaluated.
* `cifmw_devscripts_make_target` (str) Optional, the target to be used with dev-scripts.
* `cifmw_devscripts_ocp_version` (str) The version of OpenShift to be deployed.
* `cifmw_devscripts_osp_compute_nodes` (list) A list of nodes which has key/value pairs
  containing details about OpenStack compute nodes. Refer
  [section](#supported-keys-in-cifmw_devscripts_osp_compute_nodes) for more information.
* `cifmw_devscripts_src_dir` (str) The parent folder of dev-scripts repository.
* `cifmw_devscripts_use_layers` (bool) Toggle overlay support. Specifically, this boolean will instruct the role to
  shutdown the whole OCP cluster, dump the XML, undefine the nodes, and prevents running the "post" tasks. Defaults to `false`.
* `cifmw_devscripts_remove_default_net` (bool) Remove the default virtual network. Defaults to `false`.
* `cifmw_devscripts_host_routing` (bool) Enable routing via host for OCP nodes in case of OVNKubernetes. Defaults to `false`.
* `cifmw_devscripts_enable_iscsi` (bool) Enable iSCSI services on the OCP nodes having role as `worker`. Defaults to `false`.

### Secrets management

This role calls the [manage_secrets](./manage_secrets.md) role. It allows to copy or create
the needed secrets.

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
| ovn_local_gateway_mode | `false` | Enables local gateway mode, only applicable for `OVNKubernetes`. Supported values are `true\|false`. |
| provisioning_network_profile | `Managed` | Allow the script to manage the provisioning network. Supported values are `Disabled\|Managed`. |
| manage_pro_bridge | `y` | Allow dev-scripts to manage the provisioning bridge. Supported values are `y\|n`. |
| provisioning_network | | The subnet CIDR to be used for the provisioning network. |
| pro_if | | The network interface to be attached to the provisioning bridge. |
| manage_int_bridge | `y` | Allow dev-scripts to manage the internal bridge. Supported values are `y\n`. |
| int_if | | The network interface to be attached to the internal cluster bridge. |
| manage_br_bridge | `y` | Allow dev-scripts to manage the external bridge. Supported values are `y\|n`. |
| ext_if | | The network interface to be attached to the external bridge. |
| external_subnet_v4 | | The external subnet CIDR part of IPv4 family. Includes checks before default is set. |
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

### Supported keys in cifmw_devscripts_osp_compute_nodes

| Key | Description |
| --- | ----------- |
| name | Name of the physical server. |
| bmc | Management board details Refer [section](#supported-keys-in-bmc) |
| boot_mac_addr | MAC address of physical system connected to provisioning network. |
| boot_mode | The mode to be used for booting. Choices are `legacy \| UEFI \| UEFISecureBoot`. |
| extra_spec | Key/value pairs as supported by [baremetal-operator](https://github.com/metal3-io/baremetal-operator/blob/main/docs/api.md) |

#### Supported keys in bmc

The keys supported in `cifmw_devscripts_osp_compute_nodes.bmc` are

| Key | Description |
| --- | ----------- |
| address | URL to the servers BMC. Refer notes for additional information. |
| username | Name of the BMC user encoded with base64. |
| password | Password for the above user encoded with base64. |

##### Notes

The BMC address format is `<protocol>://<fqdn_or_ip_address>[:port]/[redfish-system-id]`. Some of the examples are

* `redfish-virtualmedia://compute-bmc.foo.bar/redfish/v1/Systems/<uuid>`
* `idrac://compute-bmc.subdomain.domain`
* `idrac-virtualmedia://compute-bmc.foo.bar/redfish/v1/Systems/<uuid>`
* `redfish://compute-bmc.foo.bar/redfish/v1/Systems/<uuid>`

Additional information can be found [here](https://github.com/metal3-io/baremetal-operator/blob/main/docs/api.md#bmc)

## Examples

* Sample config for deploying a compact OpenShift platform with extra nodes, existing external network,
  separate NIC for RH-OSP networks and with OpenShift provisioning network disabled.

  ```yaml
  ---
  ...
  cifmw_use_devscripts: True

  cifmw_devscripts_ci_token: REDACTED
  cifmw_devscripts_pull_secret: |
    REDACTED

  cifmw_devscripts_src_dir: "/home/ciuser/src/dev-scripts"

  cifmw_devscripts_ocp_version: '4.13.13'
  cifmw_devscripts_crb_repo: 'https://mirror.stream.centos.org/9-stream/CRB/x86_64/os/'
  ...
  ```

* Sample config for deploying a HA OpenShift platform with additional networks, OpenShift provisioning network
  is enabled and separate RH OSP networks.

  ```YAML
  cifmw_use_devscripts: True

  cifmw_devscripts_ci_token: REDACTED
  cifmw_devscripts_pull_secret: |
    REDACTED

  cifmw_devscripts_ocp_version: '4.13.13'

  cifmw_devscripts_config_overrides:
    provisioning_network_profile: "Managed"
    provisioning_network: "172.22.0.0/16"
    num_workers: 3
    worker_memory: 16384
    worker_disk: 100
    worker_vcpu: 10
  ```

* Sample vars for a hybrid test environment (virtual OpenShift with physical servers for OpenStack compute).

  ```YAML
  cifmw_use_devscripts: True

  cifmw_devscripts_ci_token: REDACTED
  cifmw_devscripts_pull_secret: |
    REDACTED

  cifmw_devscripts_ocp_version: '4.13.13'

  cifmw_devscripts_config_overrides:
    provisioning_network_profile: "Managed"
    provisioning_network: "172.22.0.0/16"
    num_workers: 3
    worker_memory: 16384
    worker_disk: 100
    worker_vcpu: 10

  cifmw_devscripts_osp_compute_nodes:
    - name: osp-compute-0
      bmc:
        address: "idrac://osp-compute-0.bmc.foo.bar"
        username: "Zm9v"
        password: "YmFy"
      boot_mac_addr: "00:00:00:00:00:00"
      boot_mode: UEFI
    - name: osp-compute-1
      bmc:
        address: "redfish://osp-compute-1.bmc.foo.bar/redfish/v1/Systems/1"
        username: "Zm9v"
        password: "YmFy"
      boot_mac_addr: "00:00:00:00:00:01"
      boot_mode: "legacy"
  ```

## References

* [dev-scripts](https://github.com/openshift-metal3/dev-scripts)
* [Additional overrides](https://github.com/openshift-metal3/dev-scripts/blob/master/config_example.sh)
* [Baremetal-operator](https://github.com/metal3-io/baremetal-operator/blob/main/docs/api.md)
