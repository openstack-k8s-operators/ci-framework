# hosted_cluster

Deploys an optional KubeVirt hosted control plane cluster on the initial
OpenShift (OCP) cluster, which becomes a *management cluster*, then deploys
the RHOSO control plane **inside** that hosted cluster. Deployment then
proceeds to the RHOSO data plane as normal.

This follows the Red Hat Tech Preview procedure for deploying RHOSO on
OpenShift Virtualization hosted control plane clusters: the management
cluster hosts the hosted control plane (etcd, API server, ...) as pods, and
the hosted cluster's worker nodes are KubeVirt VMs running on the management
cluster. RHOSO network isolation is achieved with isolated network
attachments and MetalLB rather than a shared L2 domain.

## Limitations

This is a Technology Preview feature. The hosted control plane cluster has
no Metal3 operator, so **only pre-provisioned data plane nodes are
supported** -- the `OpenStackDataPlaneNodeSet` CR must end up with
`spec.preProvisioned: true`. Which EDPM path `cifmw_deploy_hosted_cluster`
is combined with matters:

* **Classic EDPM flow** (`cifmw_architecture_scenario` not set --
  `roles/cifmw_setup/tasks/deploy_edpm.yml` runs directly): the default,
  `cifmw_edpm_deploy_baremetal: false`, already does the right thing.
  `libvirt_manager` boots EDPM compute VMs from a pre-built OS image (no
  Metal3/Ironic/BareMetalHost involved) and `edpm_deploy` applies the
  NodeSet with `preProvisioned: true` hardcoded. Do **not** set
  `cifmw_edpm_deploy_baremetal: true` -- that path provisions virtual
  `BareMetalHost`s through Metal3/Ironic, which this hosted cluster cannot
  run.
* **Architecture-scenario flow** (`cifmw_architecture_scenario` is set):
  EDPM nodes come from that scenario's `stages`, defined in the external
  `architecture` repo, not from `cifmw_edpm_deploy_baremetal`. Pick a
  scenario that renders pre-provisioned/VM-based nodes
  (`cifmw_edpm_deploy_pre_provisioned: true`, the default where that
  variable is consulted). Baremetal-oriented scenarios such as `bmo01`
  unconditionally set `bmhLabelSelector` for Metal3 and are **not**
  compatible with this role. Nothing in ci-framework enforces this choice
  today -- verify the scenario you pick before enabling
  `cifmw_deploy_hosted_cluster`.

## Prerequisites

* A management OCP cluster able to run OpenShift Virtualization (bare metal
  or nested virtualization), with `cifmw_networking_env_definition` loaded
  (see the `networking_mapper` role).
* `cifmw_hosted_cluster_kubeapi_address_pool` set to a MetalLB address range
  on the management cluster's primary network for exposing the hosted
  cluster's KubeAPI. This cannot be derived from
  `cifmw_networking_env_definition`, which only models the RHOSO isolated
  networks.
* Etcd and KubeVirt VM root-volume storage: either set
  `cifmw_hosted_cluster_etcd_storage_class` /
  `cifmw_hosted_cluster_root_volume_storage_class`, or leave them empty to
  have the role install `ci_lvms_storage` against the management cluster's
  nodes (requires `cifmw_hosted_cluster_lvms_disk_list` -- **not** the
  global `cifmw_lvms_disk_list`, which `cifmw_use_lvms` separately applies
  to the hosted cluster's own KubeVirt worker nodes after the cluster switch;
  those two node types rarely have the same free block devices).
* `cifmw_networking_env_definition.networks.<name>.tools.metallb` must be
  populated for each network in `cifmw_hosted_cluster_networks` -- this is
  the standard `networking_mapper` output used across ci-framework.
* `cifmw_hosted_cluster_management_interface` must name a real, otherwise
  unused NIC on the management cluster nodes selected by
  `cifmw_hosted_cluster_management_node_selector` (e.g. `enp6s0`) -- a
  `NodeNetworkConfigurationPolicy` bridges it for the hosted worker VMs'
  isolated networks. Required; there is no
  `cifmw_networking_env_definition.instances`-based discovery, since a
  management cluster installed by something other than ci-framework (e.g.
  dev-scripts) has no matching `instances` entry to resolve one from.
* The automation SSH keypair at `cifmw_hosted_cluster_ssh_private_key` /
  `_ssh_public_key` (`~/.ssh/id_cifw` by default -- the keypair
  `deploy_architecture.yml` already injects into provisioned nodes, since
  this role runs on controller-0, not the hypervisor) must be usable to
  reach the hosted worker VMs once they boot -- it is passed to
  `hcp create cluster kubevirt --ssh-key` for the `core` user.
* `cifmw_hosted_cluster_cnv_hyperconverged` sets
  `spec.workloadSources.enableCommonBootImageImport: false` -- the default
  OpenShift Virtualization golden-image `DataImportCron`s (CentOS/Fedora/RHEL
  boot sources) land on the same node-local LVMS storage pool used for
  etcd/root-volume PVCs, and can be large enough to starve them out on small
  management clusters. Only re-enable this if something else on the
  management cluster needs those boot sources.

## What this role does

1. Installs OpenShift Virtualization, the multicluster engine (MCE, with the
   `hypershift` and `hypershift-local-hosting` components -- not
   `central-infrastructure-management`, which is Agent-provider-only),
   MetalLB and the NMState Operator on the management cluster.
2. Allows wildcard routes on the management cluster's default ingress
   controller, creates the hosted cluster's control plane namespace, and
   exposes the hosted cluster's KubeAPI through a dedicated MetalLB address
   pool. Mirroring the upstream documented architecture for this feature, a
   `NodeNetworkConfigurationPolicy` bridges
   `cifmw_hosted_cluster_management_interface` on the management nodes --
   without a VLAN tag for ctlplane and with VLAN tags (per
   `cifmw_networking_definition`) for internalapi/storage/tenant -- into one
   Linux bridge per network, and
   `ci_multus` exposes each bridge as its own `NetworkAttachmentDefinition`
   with `whereabouts` IPAM. KubeVirt assigns and configures each worker VM
   interface automatically at boot from these NADs; no in-guest nmstate/VLAN
   configuration happens or is possible, since HyperShift -- not ci-framework
   -- generates the worker VMs' ignition. A separate `datacentre` NAD on the
   ctlplane-backed provider trunk gives each VM a dedicated, unnumbered NIC
   for the OVN gateway pod.
3. Creates the hosted cluster with `hcp create cluster kubevirt`, attaching
   the four isolated-network NADs and the datacentre NAD via
   `--additional-network`, the
   automation SSH key via `--ssh-key`, and (when
   `cifmw_hosted_cluster_map_infra_storage_class` is true, the default)
   the management cluster's resolved root-volume storage class into the
   guest cluster under the same name via `--infra-storage-class-mapping`
   -- `hcp create cluster kubevirt` only provisions worker VMs with a root
   volume, so this is what gives the guest cluster a working storage class
   without a second, real LVMS install. Waits for it to become available,
   saves its kubeconfig, and waits for its KubeVirt worker nodes to become
   `Ready`.
4. Enables global IP forwarding on the hosted cluster's network, the one
   setting genuinely specific to a KubeVirt hosted control plane that the
   generic RHOSO flow does not configure.
5. Discovers each hosted worker's real interface names: reads the
   deterministic MAC and IP HyperShift/KubeVirt/whereabouts assigned to each
   isolated-network NIC from its `VirtualMachineInstance`, adds the node to
   the runtime inventory over SSH (via its ctlplane address -- the Node's own
   `InternalIP` sits on the management cluster's internal pod network and is
   not reachable from outside it), gathers its facts, and feeds both into a
   `cifmw.general.ci_net_map` run scoped to a dedicated
   `cifmw_hosted_cluster_worker_group` group-template (one standalone
   interface per network, unlike the VLAN-on-trunk `ocp_workers`/`computes`
   group-templates, with its own non-overlapping IP range so it can never
   collide with the management cluster's own node addressing). The result is
   merged into the same global `cifmw_networking_env_definition` used
   everywhere else. The unnumbered datacentre NIC is discovered separately
   and persisted as `cifmw_hosted_cluster_datacentre_interface` for the
   generated guest NAD and OVN NIC mapping.
6. Points `cifmw_openshift_kubeconfig` at the hosted cluster, mirroring
   the override pattern used by the `hive` role, so every later
   `cifmw_setup` phase (`deploy_architecture.yml`, `deploy_edpm.yml`)
   transparently deploys RHOSO onto the hosted cluster instead of the
   management cluster. This is also why MetalLB pools for the isolated
   networks, storage classes and the OpenStack operator are **not** installed
   by this role: the existing `deploy_architecture.yml` / `kustomize_deploy`
   flow already does all of that, generically, against whatever cluster
   `cifmw_openshift_kubeconfig` points to -- now including the hosted
   workers' real interface names resolved in step 5. When
   `cifmw_hosted_cluster_map_infra_storage_class` is true (the default), the
   generic storage-class-selection steps in `deploy_architecture.yml` /
   `deploy_edpm.yml` (and the storage-class-prefix defaults in
   `ci_gen_kustomize_values` / `test_operator`) skip the `cifmw_use_lvms`
   LVMS branch for the guest cluster, since it already received a working
   storage class for free in step 3 -- a KubeVirt worker VM has no secondary
   data disk for a second, real LVMS install to use, and `ci_lvms_storage`
   would otherwise time out waiting for an `LVMCluster` that cannot become
   ready. This is a plain `cifmw_deploy_hosted_cluster` /
   `cifmw_hosted_cluster_map_infra_storage_class`
   check inline at each of those call sites, not an override of
   `cifmw_use_lvms` itself -- `cifmw_use_lvms` can safely stay `true` for
   the management cluster/global scenario setting.

`roles/cifmw_setup/tasks/deploy_architecture.yml` additionally scales
`openstack-baremetal` to zero replicas when `cifmw_deploy_hosted_cluster` is
enabled, since `install_operators.yml` has no per-scenario override hook for
the OpenStack init CR it generates.

## Parameters

| Variable | Default | Purpose |
|---|---|---|
| `cifmw_deploy_hosted_cluster` | `false` | Enables this role in `cifmw_setup` infra. |
| `cifmw_hosted_cluster_name` | `hcp-0` | HostedCluster name. |
| `cifmw_hosted_cluster_namespace` | `clusters` | HostedCluster and kubeconfig namespace. |
| `cifmw_hosted_cluster_hosted_namespace` | `clusters-<name>` | Control plane namespace HyperShift manages; where service-pod NADs are attached. |
| `cifmw_hosted_cluster_networks` | `[ctlplane, internalapi, storage, tenant]` | Numbered isolated networks attached to the hosted cluster. A separate unnumbered datacentre NIC is always attached for the OVN gateway. |
| `cifmw_hosted_cluster_management_interface` | `""` | **Required.** Physical NIC on the management cluster nodes bridged (via `NodeNetworkConfigurationPolicy`) into one Linux bridge per isolated network -- without a VLAN tag for ctlplane and with VLAN tags for internalapi/storage/tenant. No `cifmw_networking_env_definition.instances`-based discovery, since a dev-scripts-installed management cluster has no matching entry. |
| `cifmw_hosted_cluster_management_node_selector` | `{node-role.kubernetes.io/master: ""}` | Node selector for the isolated-networks `NodeNetworkConfigurationPolicy`. |
| `cifmw_hosted_cluster_nmstate_channel` | `stable` | NMState Operator subscription channel. |
| `cifmw_hosted_cluster_worker_group` | `hosted_cluster_workers` | networking_mapper group-template / inventory group name for the hosted worker nodes. |
| `cifmw_hosted_cluster_worker_net_range_start` / `_length` | `200` / `10` | IP range reserved for hosted workers within each isolated network, kept clear of the `ocps`/`ocp_workers`/`computes` ranges. |
| `cifmw_hosted_cluster_ssh_user` | `core` | SSH user on the hosted worker VMs. |
| `cifmw_hosted_cluster_ssh_public_key` / `_ssh_private_key` | `~/.ssh/id_cifw{.pub,}` | Automation keypair passed to `hcp create cluster kubevirt --ssh-key` and used to gather facts from the hosted workers. |
| `cifmw_hosted_cluster_worker_count` | `3` | NodePool replicas (KubeVirt VM workers). |
| `cifmw_hosted_cluster_worker_cores` | `16` | vCPUs per worker VM. |
| `cifmw_hosted_cluster_worker_memory` | `32Gi` | Memory per worker VM. |
| `cifmw_hosted_cluster_root_volume_size` | `85` | GiB per worker root volume. |
| `cifmw_hosted_cluster_root_volume_storage_class` | empty | Existing RWO storage class for worker root volumes; empty installs `ci_lvms_storage`. |
| `cifmw_hosted_cluster_etcd_storage_class` | empty | Existing RWO storage class for hosted etcd; empty installs `ci_lvms_storage`. |
| `cifmw_hosted_cluster_lvms_disk_list` | `[]` | Block devices on the **management cluster's** OCP nodes for `ci_lvms_storage`, used only when the two storage class variables above are empty. Separate from the global `cifmw_lvms_disk_list`. |
| `cifmw_hosted_cluster_map_infra_storage_class` | `true` | Maps the management cluster's resolved root-volume storage class into the guest cluster under the same name via `hcp create cluster kubevirt --infra-storage-class-mapping`, and makes the generic storage-class-selection steps in `deploy_architecture.yml` / `deploy_edpm.yml` / `ci_gen_kustomize_values` / `test_operator` skip the `cifmw_use_lvms` LVMS branch for the guest cluster -- the guest's KubeVirt worker VMs have no secondary data disk for a second, real LVMS install to use. Set `false` to restore the old behavior. |
| `cifmw_hosted_cluster_release_image` | empty | Hosted cluster release image; empty resolves to the management cluster's own version. |
| `cifmw_hosted_cluster_cnv_channel` | `stable` | OpenShift Virtualization subscription channel. |
| `cifmw_hosted_cluster_mce_channel` | `stable-2.17` | MCE subscription channel. No generic "stable" meta-channel exists -- verify this matches your OpenShift release against the MCE Support Matrix on access.redhat.com; `stable-2.17` is current for OpenShift 4.20-4.22. |
| `cifmw_hosted_cluster_metallb_channel` | `stable` | MetalLB subscription channel. |
| `cifmw_hosted_cluster_kubeapi_address_pool` | `[]` | **Required.** MetalLB address range for the hosted cluster's KubeAPI, e.g. `["192.168.100.50-192.168.100.60"]`. |
| `cifmw_hosted_cluster_kubeapi_interface` | `br-ex` | Management cluster interface the KubeAPI VIP is announced on. |
| `cifmw_hosted_cluster_artifacts_dir` | `{{ cifmw_basedir }}/artifacts/hosted_cluster` | Manifest, CLI, and kubeconfig directory. |
| `cifmw_hosted_cluster_wait_retries` | `120` | Poll attempts for cluster resources. |
| `cifmw_hosted_cluster_wait_delay` | `10` | Seconds between polls. |
| `cifmw_hosted_cluster_render_only` | `false` | Render manifests without a cluster, for Molecule. |
| `cifmw_hosted_cluster_cli_validate_certs` | `false` | Validate TLS when downloading the `hcp` CLI from the management cluster's `apps.*` route. Defaults to `false` because that route normally sits behind a self-signed ingress certificate. |

## Enable the role

```yaml
cifmw_deploy_hosted_cluster: true
cifmw_hosted_cluster_kubeapi_address_pool:
  - 192.168.100.50-192.168.100.60
# Block devices on the management cluster's OCP nodes (for HCP etcd and
# KubeVirt worker root volumes). The hosted cluster's own RHOSO storage
# class is configured separately, via the existing cifmw_use_lvms /
# cifmw_lvms_disk_list applied by deploy_architecture.yml.
cifmw_hosted_cluster_lvms_disk_list:
  - /dev/vdb
# cifmw_edpm_deploy_baremetal already defaults to false -- shown here only
# as a reminder not to flip it to true. See "Limitations" for the
# architecture-scenario equivalent (cifmw_edpm_deploy_pre_provisioned).
cifmw_edpm_deploy_baremetal: false
```

The hosted kubeconfig is saved at
`{{ cifmw_hosted_cluster_artifacts_dir }}/kubeconfig-{{ cifmw_hosted_cluster_name }}`.

## Iterating / cleanup

`cleanup-hosted-cluster.yml` (repo root) tears down just the hosted
control plane -- the `HostedCluster`, its `clusters-<name>` control plane
namespace (and the trunk NAD it owns), and the KubeAPI MetalLB pool/
advertisement -- without touching the management cluster or the operators
(OpenShift Virtualization, MCE, MetalLB) and storage class this role
installed on it. This makes it cheap to iterate: run it, then re-run your
normal deploy to recreate the hosted cluster from scratch.

```
ansible-playbook cleanup-hosted-cluster.yml -i inventory.yml \
  -e cifmw_target_host=localhost \
  -e cifmw_openshift_kubeconfig=<path to the MANAGEMENT cluster kubeconfig> \
  -e @custom/hosted.yml --flush-cache
```

`cifmw_openshift_kubeconfig` **must** point at the management cluster.
`retarget.yml` sets it as a cacheable fact pointing at the hosted cluster
during a normal deploy, so a stale fact-cache entry from a prior run would
otherwise make the cleanup silently no-op against the wrong cluster --
`cleanup.yml` asserts the `HostedCluster` is actually found first and
fails loudly instead if it isn't, telling you to pass
`cifmw_openshift_kubeconfig` explicitly or re-run with `--flush-cache`.

## Molecule

The Molecule scenario renders and inspects the management cluster operator
manifests (HyperConverged, MultiClusterEngine, MetalLB) and the hosted
cluster KubeAPI MetalLB manifests. A complete deployment requires a live
OpenShift cluster with OpenShift Virtualization support.
