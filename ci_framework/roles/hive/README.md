# hive
Hive is an operator which runs as a service on top of Kubernetes/OpenShift.
The service can be used to provision and perform initial configuration of
OpenShift clusters.

This role is wrapper around the Hive service providing the following support

* Cluster pools using OpenStack provider.
* Deployment of clusters on physical servers.

## Dependencies
* `ci_setup`
* `openshift_provisioner_node`: Required when `cifmw_hive_platform` is set to
  `baremetal`

## Parameters

### Common required parameters
* `cifmw_hive_kubeconfig`: (String) Absolute path to the kubeconfig file to be
  used for authentication with the OpenShift instance hosting the Hive
  instance.
* `cifmw_hive_namespace`: (String) Name of the openshift namespace to be used
   for creating resources like secrets, clusterimageset, clusterpool, etc.
* `cifmw_hive_platform`: (String) the name of the supported provider to be
  used for deployment. Supported values are `baremetal` | `openstack`.
* `cifmw_hive_action`: (String) the action to be performed by Hive service.
  The supported actions are `claim_cluster` | `unclaim_cluster` |
  `deploy_cluster` | `delete_cluster`.

### Common optional parameters
* `cifmw_hive_basedir`: (String) Base directory. Defaults to `cifmw_basedir`
  which defaults to `~/ci-framework-data`.
* `cifmw_hive_artifacts_dir`: (String) Path to the artifacts directory.
  Defaults to `{{ cifmw_basedir }}/artifacts/hive`.
* `cifmw_hive_dry_run`: (Boolean) It prevents execution of `oc` commands found
  in the play / role when it is enabled. It is useful for unit testing.
  Defaults to `false`.
* `cifmw_hive_oc_delete_timeout`: (String) Maximum allowed time that a resource
  can take for a delete operation. Defaults to `59m`

### OpenStack platform required parameters
* `cifmw_hive_openstack_pool_name`: (String) The name of Hive clusterpool to be
  used.
* `cifmw_hive_openstack_claim_name`: (String) The name of the claim to be used
  for the claimed OpenShift cluster.

### OpenStack platform optional parameters
* `cifmw_hive_openstack_claim_life_time`: (String) Maximum lifetime of the
  claimed OpenShift cluster. Defaults to `24h`.
* `cifmw_hive_openstack_claim_timeout`: (String) Maximum allowed time before
  failing during the claim operation. Defaults to `59m`.

### Baremetal platform required parameters
* `cifmw_hive_baremetal`: (Dict) configurations related to the baremetal test
  environment to be used for deploying OpenShift cluster.

#### Supported keys in cifmw_hive_baremetal
* `cluster_name`: (String) name of the OpenShift cluster.
* `install_config`: (String) absolute path to the install file containing
  information about the test environment. Refer to [Baremetal install config]
  (#Baremetal-install-config) example.
* `ocp_image`: (String) OpenShift release image to be used for deploying the
  environment.

## Return values
* `cifmw_openshift_kubeconfig`: (String) absolute path to the kubeconfig of the
  deployed OpenShift cluster.
* `cifmw_openshift_user`: (String) name of the user associated with the deployed
  OpenShift cluster.
* `cifmw_openshift_password`: (String) password set for
  `cifmw_openshift_username`.

## Examples
### Sample local variables file for using Hive
```YAML
cifmw_use_libvirt: true
cifmw_use_opn: true
cifmw_use_hive: true

cifmw_basedir: "{{ ansible_user_dir }}/ci-framework-data"
cifmw_installyamls_repos: "{{ ansible_user_dir }}/src/install_yamls"

cifmw_repo_setup_os_release: 'centos'
cifmw_repo_setup_dist_major_version: 9

cifmw_libvirt_manager_user: root
cifmw_libvirt_manager_skip_edpm_compute_repos: true

cifmw_opn_host: REDACTED
cifmw_opn_external_network_iface: eno3
cifmw_opn_dhcp: true
cifmw_opn_use_provisioning_network: true
cifmw_opn_prov_network_iface: eno1
cifmw_opn_bootstrap_ipv4: REDACTED

cifmw_hive_platform: baremetal
cifmw_hive_action: deploy_cluster
cifmw_hive_kubeconfig: "{{ ansible_user_dir }}/kubeconfig"
cifmw_hive_namespace: openstack

cifmw_hive_baremetal:
  cluster_name: unittest-01
  install_config: "{{ ansible_user_dir }}/install_config.yml"
  ssh_key: 'ssh-ed25519 ...REDACTED'
  ocp_image: "quay.io/openshift-release-dev/ocp-release:4.13.0-x86_64"

cifmw_operator_build_push_registry: "default-route-openshift-image-registry.unittest-01.openstack.ccitredhat.com"
cifmw_operator_build_meta_build: false

pre_infra:
  - name: Download needed tools
    inventory: "{{ cifmw_installyamls_repos }}/devsetup/hosts"
    type: playbook
    source: "{{ cifmw_installyamls_repos }}/devsetup/download_tools.yaml"
```

### Baremetal install config
```YAML
apiVersion: v1
baseDomain: mytest.openstack.local
metadata:
  name: test-01
networking:
  machineNetwork:
    - cidr: 10.8.0.0/16
  networkType: OpenShiftSDN
compute:
  - name: worker
    replicas: 3
controlPlane:
  name: master
  replicas: 3
  platform:
    baremetal: {}
platform:
  baremetal:
    apiVIPs:
      - 10.8.0.2
    ingressVIPs:
      - 10.8.0.3
    provisioningNetworkCIDR: '172.22.0.0/24'
    provisioningDHCPRange: "172.22.0.10,172.22.0.100"
    provisioningNetwork: "Managed"
    hosts:
      - name: ocp
        role: master
        bmc:
          address: 'idrac://ocp-1-mgmt.idrac.openstack.local'
          username: idrac-user
          password: idrac-pass
          disableCertificateVerification: true
        bootMACAddress: 'AA:16:3e:3a:18:00'
        rootDeviceHints:
          minSizeGigabytes: 500
        bootMode: UEFI
        networkConfig:
          interfaces:
            - name: eno1
              type: ethernet
              state: up
              ipv4:
                enabled: true
                dhcp: true
pullSecret: ''
sshKey: 'ssh-ed25519 ...'
```

## Reference
- [Hive](https://github.com/openshift/hive)
- [OpenShift-Installer](https://docs.openshift.com/container-platform/4.13/installing/installing_bare_metal_ipi/ipi-install-overview.html)
