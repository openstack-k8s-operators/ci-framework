# reproducer

Role to deploy close to CI layout on a hypervisor. Supports both libvirt/KVM
virtual machine deployments (via dev-scripts) and agent-based bare metal
Single Node OpenShift (SNO) deployments on physical hardware managed through
iDRAC Redfish APIs.

## Privilege escalation

Bare metal deployment requires privilege escalation for `/etc/hosts`
management and running the ISO HTTP server via podman.

## Exposed tags

* `bootstrap`: All reproducer bootstrap tasks.
* `bootstrap_layout`: Layout-related bootstrap tasks.
* `devscripts_layout`: Dev-scripts OCP layout tasks (libvirt path).
* `ocp_layout`: OCP layout tasks (libvirt path).
* `bm_ocp_layout`: Agent-based bare metal OCP layout tasks.

## Parameters

* `cifmw_reproducer_basedir`: (String) Base directory. Defaults to `cifmw_basedir`, which defaults to `~/ci-framework-data`.
* `cifmw_reproducer_controller_user`: (String) User on controller-0. Defaults to `ansible_ssh_user` from controller-0's `hostvars` if available, otherwise defaults to `zuul`.
* `cifmw_reproducer_controller_user_dir`: (String) Controller-0 user's home dir. Defaults to `/home/{{ cifmw_reproducer_controller_user }}`
* `cifmw_reproducer_controller_basedir`: (String) Path to the `ci-framework-data` dir on controller-0. Defaults to `"{{ cifmw_reproducer_controller_user_dir }}/ci-framework-data"`
* `cifmw_reproducer_compute_repos`: (List[mapping]) List of yum repository that must be deployed on the compute nodes during their creation. Defaults to `[]`.
* `cifmw_reproducer_compute_set_repositories`: (Bool) Deploy repositories (rhos-release) on Compute nodes. Defaults to `true`.
* `cifmw_reproducer_play_extravars`: (List[string]) List of extra-vars you want to pass down to the EDPM deployment playbooks. Defaults to `[]`.
* `cifmw_reproducer_kubecfg`: (String) Path to the CRC kubeconfig file. Defaults to the image_local_dir defined in the cifmw_libvirt_manager_configuration dict.
* `cifmw_reproducer_repositories`: (List[mapping]) List of repositories you want to synchronize from your local machine to the ansible controller.
* `cifmw_reproducer_run_job`: (Bool) Run actual CI job. Defaults to `true`.
* `cifmw_reproducer_run_content_provider`: (Bool) Run content-provider job. Defaults to `true`.
* `cifmw_reproducer_params`: (Dict) Specific parameters you want to pass to the reproducer. Defaults to `{}`.
* `cifmw_reproducer_dns_servers`: List of dns servers which should be used by the CRC VM as upstream dns servers. Reads from group_var `{{ cifmw_default_dns_servers }}`. Defaults to 1.1.1.1, 8.8.8.8.
* `cifmw_reproducer_hp_rhos_release`: (Bool) Allows to consume rhos-release on the hypervisor. Defaults to `false`.
* `cifmw_reproducer_dnf_tweaks`: (List) Options you want to inject in dnf.conf, both on controller-0 and hypervisor. Defaults to `[]`.
* `cifmw_reproducer_skip_fetch_repositories`: (Bool) Skip fetching repositories from zuul var and simply copy the code from the ansible controller. Defaults to `false`.
* `cifmw_reproducer_supported_hypervisor_os`: (List) List of supported hypervisor operating systems and their minimum version.
* `cifmw_reproducer_minimum_hardware_requirements`: (Dict) Define minimum hardware requirements for specific scenarios. Example below
* `cifmw_reproducer_computes_rhos_release_args`: (String) Arguments to use when installing rhos-release repos on compute nodes. Not defined by default, and `cifmw_repo_setup_rhos_release_args` is used instead.
* `cifmw_reproducer_bm_ocp`: (Bool) Enable agent-based bare metal OCP SNO deployment instead of libvirt/dev-scripts. Defaults to `false`.

### Advanced parameters
Those parameters shouldn't be used, unless the user is able to understand potential issues in their environment.

* `cifmw_reproducer_validate_network`: (Bool) Toggle network validations. Those validations ensure all of listed networks in VMs are defined. Defaults to `true`.
* `cifmw_reproducer_validate_ocp_layout`: (Bool) Toggle OCP layout validations. Those validations ensure volumes, amounts and resources are properly defined for OCP cluster members (masters and workers). Defaults to `true`.
* `cifmw_reproducer_validate_network_host`: (String) Specify the hostname that should be pinged in order to validate network connectivity from the ctlplane network. Default value is `controller-0.utility`

### run_job and run_content_provider booleans and risks.

- For jobs with content-provider, both steps will be running by default.
- For jobs without content-provider, only the job will run by default.
- If a job with content-provider is launched with `cifmw_reproducer_run_job: false`, it will
  then run the content-provider, and stop.
- If a job with content-provider is launched for a second time with `cifmw_reproducer_run_content_provider: false`,
  if the first run did deploy the content-provider, it will pass.
- If a job with content-provider is launched a **first** time with `cifmw_reproducer_run_content_provider: false`,
  it will NOT RUN the content-provider, **leading to a crash of the job run**.

## Agent-based bare metal OCP SNO deployment

When `cifmw_reproducer_bm_ocp: true`, the role performs an agent-based
installation on a physical bare metal host managed
via iDRAC Redfish APIs. The workflow generates a self-contained agent ISO on
the Zuul controller, pushes it to the target host's iDRAC via Redfish
VirtualMedia, and waits for the host to self-install.

### Network architecture

Three routed isolated networks (no shared L2 domain required):

| Network | Purpose |
| --- | --- |
| BMC management | iDRAC interfaces; controller reaches iDRAC via routing |
| BMO provision | Node's 1st NIC, OS interface IP; VirtualMedia boot |
| Controller | Zuul controller; serves the agent ISO to iDRAC |

A 2nd NIC on the node carries isolated MetalLB networks for RHOSO EDPM
services (ctlplane, internalapi, storage, tenant) via VLANs.

The `api` and `*.apps` DNS names resolve directly to the node's BMO
provision IP via `/etc/hosts` entries managed by the role.

### Bare metal parameters

#### Required (typically set in the scenario's vars.yaml)

| Parameter | Type | Description |
| --- | --- | --- |
| `cifmw_bm_agent_cluster_name` | str | OpenShift cluster name |
| `cifmw_bm_agent_base_domain` | str | Base domain for the cluster |
| `cifmw_bm_agent_machine_network` | str | BMO provision network CIDR |
| `cifmw_bm_agent_node_ip` | str | Node IP on the BMO provision network |
| `cifmw_bm_agent_node_iface` | str | RHCOS interface name on the BMO provision network |
| `cifmw_bm_agent_bmc_host` | str | iDRAC hostname or IP on the BMC management network |
| `cifmw_devscripts_bm_nodes` | list | Single-element list with `mac` and `root_device` keys |
| `cifmw_bm_agent_openshift_version` | str | OCP version (e.g. `"4.18.3"`); or set `cifmw_bm_agent_release_image` instead |

#### Optional (have defaults or are auto-discovered)

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `cifmw_bm_agent_release_image` | str | `$OPENSHIFT_RELEASE_IMAGE` | Alternative to version: extract `openshift-install` from a release image |
| `cifmw_bm_agent_iso_http_port` | int | `80` | Port for the podman HTTP server that serves the agent ISO (only a privileged port may accept external traffic on Zuul controllers) |
| `cifmw_bm_agent_installer_timeout` | int | `7200` | Total seconds before the installer times out (split between bootstrap and install phases) |
| `cifmw_manage_secrets_pullsecret_file` | str | `~/pull-secret` | Path to the pull secret JSON file |
| `cifmw_bmc_credentials_file` | str | `~/secrets/idrac_access.yaml` | Path to a YAML file with `username` and `password` keys for iDRAC |
| `cifmw_bm_agent_enable_usb_boot` | bool | `false` | Allow the role to automatically enable `GenericUsbBoot` in BIOS (requires a power cycle) |
| `cifmw_bm_agent_vmedia_uefi_path` | str | auto-discovered | UEFI device path for the Virtual Optical Drive; auto-discovered from UEFI boot options if omitted |
| `cifmw_bm_agent_core_password` | str | — | Set a `core` user password post-install via MachineConfig |
| `cifmw_bm_agent_live_debug` | bool | `false` | Patch the agent ISO with password, autologin, and systemd debug shell on `tty6` for discovery-phase console access (requires `cifmw_bm_agent_core_password`) |

### Secrets management

The bare metal path requires two secret files:

#### BMC credentials

A YAML file at `cifmw_bmc_credentials_file` (default `~/secrets/idrac_access.yaml`)
with the following structure:

```yaml
username: root
password: <idrac-password>
```

#### Pull secret

The OCP pull secret JSON at `cifmw_manage_secrets_pullsecret_file`
(default `~/pull-secret`).

### Bare metal task files

The agent-based deployment is composed of reusable task files under
`tasks/bm_*.yml`:

| Task file | Description |
| --- | --- |
| `bm_ocp_layout.yml` | Main orchestrator: validates variables, generates ISO, serves it via HTTP, manages VirtualMedia, waits for install completion |
| `bm_power_on.yml` | Idempotent power-on via Redfish with POST wait (retries 30x at 10s intervals) |
| `bm_power_off.yml` | Idempotent force power-off via Redfish with confirmation wait |
| `bm_check_usb_boot.yml` | Reads `GenericUsbBoot` BIOS attribute and fails if disabled |
| `bm_ensure_usb_boot.yml` | Wraps `bm_check_usb_boot.yml`; if disabled and `cifmw_bm_agent_enable_usb_boot` is true, sets the BIOS attribute, creates a config job, and power-cycles to apply |
| `bm_eject_vmedia.yml` | Ejects VirtualMedia from the iDRAC Virtual Optical Drive |
| `bm_discover_vmedia_target.yml` | Discovers or validates the UEFI device path for VirtualMedia, clears pending iDRAC config jobs, and sets a one-time boot override |
| `bm_patch_agent_iso.yml` | Patches the agent ISO ignition with core password, autologin, and debug shell (used when `cifmw_bm_agent_live_debug` is true) |
| `bm_core_password_machineconfig.yml` | Generates a MachineConfig manifest to set the core user password hash post-install |

### openshift-install acquisition

The `openshift-install` binary is obtained automatically via one of two
methods, depending on which variable is set:

* **By version** (`cifmw_bm_agent_openshift_version`): downloads the tarball
  from `https://mirror.openshift.com/pub/openshift-v4/clients/ocp/<version>/openshift-install-linux.tar.gz`
  and extracts it.
* **By release image** (`cifmw_bm_agent_release_image` or
  `OPENSHIFT_RELEASE_IMAGE` env var): runs
  `oc adm release extract --command=openshift-install` against the image.

If the binary already exists in the working directory it is reused.

### Deployment workflow

1. Validate required variables
2. Ensure `GenericUsbBoot` is enabled in BIOS (auto-enable with power cycle if allowed)
3. Power off the host
4. Generate SSH keys, template `install-config.yaml` and `agent-config.yaml`
5. Acquire `openshift-install` binary (see above) and run `openshift-install agent create image` to build the agent ISO
6. Optionally patch the ISO for discovery-phase console access
7. Serve the ISO via a root podman httpd container (rootless podman cannot use privileged ports)
8. Eject any existing VirtualMedia, then insert the agent ISO
9. Discover the Virtual Optical Drive UEFI path and set a one-time boot override
10. Power on the host
11. Verify BIOS `GenericUsbBoot` is enabled after POST
12. Add `/etc/hosts` entries for `api`/`api-int` and `*.apps` domains
13. Wait for bootstrap and install to complete
14. Copy kubeconfig and kubeadmin-password to the dev-scripts-compatible auth directory
15. Eject VirtualMedia and stop the HTTP server

## Molecule tests

### bm_redfish scenario

The `bm_redfish` Molecule scenario validates the bare metal Redfish task files
(`bm_power_on`, `bm_power_off`, `bm_check_usb_boot`, `bm_ensure_usb_boot`,
`bm_eject_vmedia`, `bm_discover_vmedia_target`) against a stateful Python
mock iDRAC server that simulates Redfish API responses over HTTPS.

The mock server (`molecule/bm_redfish/files/mock_idrac.py`) provides:

* Stateful GET/POST/PATCH handlers for power, BIOS, VirtualMedia, boot
  override, and job queue Redfish endpoints
* A `/test/reset` admin endpoint to set mock state between test cases
* A `/test/state` endpoint to query current mock state for assertions
* Self-signed TLS certificates generated during `prepare.yml`

Test coverage:

| Test file | Scenarios |
| --- | --- |
| `test_power_off.yml` | Already off (idempotent), On -> Off |
| `test_power_on.yml` | Already on (idempotent), Off -> On |
| `test_check_usb_boot.yml` | Enabled (succeeds), Disabled (expected failure) |
| `test_ensure_usb_boot.yml` | Already enabled (no cycle), Disabled + auto-enable (BIOS change + cycle), Disabled + no auto-enable (expected failure) |
| `test_eject_vmedia.yml` | Inserted (ejects), Not inserted (idempotent) |
| `test_discover_vmedia.yml` | Auto-discover, user-provided valid path, user-provided invalid path (expected failure) |

## Warning
This role isn't intended to be called outside of the `reproducer.yml` playbook.

## Examples
Please follow the [documentation about the overall "reproducer" feature](https://ci-framework.readthedocs.io/en/latest/roles/reproducer.html).

### Push repositories
#### Local repositories on your laptop
```YAML
local_home_dir: "{{ lookup('env', 'HOME') }}"
local_base_dir: "{{ local_home_dir }}/src/github.com/openstack-k8s-operators"
remote_base_dir: "/home/zuul/src/github.com/openstack-k8s-operators"
cifmw_reproducer_repositories:
  - src: "{{ local_base_dir }}/ci-framework"
    dest: "{{ remote_base_dir }}"
  - src: "{{ local_base_dir }}/install_yamls"
    dest: "{{ remote_base_dir }}"
```
Notes:
* `ansible_user_dir` isn't really usable due to the use of `delegate_to` in order to sync those local repositories.
* You therefore really want to use absolute paths - while the `dest` may be relative with the use of a plain `rsync` command

#### Github code
```YAML
remote_base_dir: "/home/zuul/src/github.com/openstack-k8s-operators"
cifmw_reproducer_repositories:
  # Fetch specific version
  - src: "https://github.com/cjeanner/ci-framework"
    dest: "{{ remote_base_dir }}/ci-framework"
    version: some-version
  # Fetch a pull-request and checkout the specific content
  - src: "https://github.com/foo/install_yamls"
    dest: "{{ remote_base_dir }}/install_yamls"
    refspec: pull/510/head:my-patch
    version: my-patch
  # Just get HEAD
  - src: "https://github.com/openstack-k8s-operators/openstack-operators"
    dest: "{{ remote_base_dir }}/openstack-operators"
```

### Agent-based bare metal SNO

Minimal vars.yaml for a bare metal SNO deployment:

```YAML
cifmw_reproducer_bm_ocp: true
cifmw_bm_agent_cluster_name: ocp
cifmw_bm_agent_base_domain: example.com
cifmw_bm_agent_machine_network: "192.168.10.0/24"
cifmw_bm_agent_node_ip: "192.168.10.50"
cifmw_bm_agent_node_iface: eno12399np0
cifmw_bm_agent_bmc_host: idrac.mgmt.example.com
cifmw_bm_agent_openshift_version: "4.18.3"
cifmw_bm_agent_enable_usb_boot: true

cifmw_devscripts_bm_nodes:
  - mac: "b0:7b:25:xx:yy:zz"
    root_device: /dev/sda
```

#### Example `cifmw_reproducer_minimum_hardware_requirements`:
```YAML
cifmw_reproducer_minimum_hardware_requirements:
  vcpu: 16
  memory: "32 GB"
  disk: "200 GB"
```

## References

* [ci-framework reproducer documentation](https://ci-framework.readthedocs.io/en/latest/roles/reproducer.html)
* [dev-scripts](https://github.com/openshift-metal3/dev-scripts)
* [Redfish API specification](https://www.dmtf.org/standards/redfish)
* [Dell iDRAC Redfish API Guide](https://developer.dell.com/apis/2978/versions/6.xx/reference)
