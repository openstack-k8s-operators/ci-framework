# bm_sno

Agent-based bare metal OCP SNO deployment via iDRAC Redfish APIs.

This role is included by the `reproducer` role when
`cifmw_bm_sno: true`. It performs an agent-based installation on a
physical bare metal host managed via iDRAC Redfish APIs. The workflow generates
a self-contained agent ISO on the Zuul controller, pushes it to the target
host's iDRAC via Redfish VirtualMedia, and waits for the host to self-install.

## Privilege escalation

Bare metal deployment requires privilege escalation for `/etc/hosts`
management and running the ISO HTTP server via podman.

## Exposed tags

* `bm_ocp_layout`: Agent-based bare metal OCP layout tasks.

## Network architecture

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

## Parameters

### Required (typically set in the scenario's vars.yaml)

| Parameter | Type | Description |
| --- | --- | --- |
| `cifmw_bm_agent_cluster_name` | str | OpenShift cluster name |
| `cifmw_bm_agent_base_domain` | str | Base domain for the cluster |
| `cifmw_bm_agent_machine_network` | str | BMO provision network CIDR |
| `cifmw_bm_agent_node_ip` | str | Node IP on the BMO provision network |
| `cifmw_bm_agent_node_iface` | str | RHCOS interface name on the BMO provision network |
| `cifmw_bm_agent_bmc_host` | str | iDRAC hostname or IP on the BMC management network |
| `cifmw_bm_nodes` | list | Single-element list with `mac` and `root_device` keys |
| `cifmw_bm_agent_openshift_version` | str | OCP version (e.g. `"4.18.3"`); or set `cifmw_bm_agent_release_image` instead |

### Optional (have defaults or are auto-discovered)

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

## Secrets management

The bare metal path requires two secret files:

### BMC credentials

A YAML file at `cifmw_bmc_credentials_file` (default `~/secrets/idrac_access.yaml`)
with the following structure:

```yaml
username: root
password: <idrac-password>
```

### Pull secret

The OCP pull secret JSON at `cifmw_manage_secrets_pullsecret_file`
(default `~/pull-secret`).

## Task files

The agent-based deployment is composed of reusable task files under
`tasks/`:

| Task file | Description |
| --- | --- |
| `main.yml` | Main orchestrator: validates variables, generates ISO, serves it via HTTP, manages VirtualMedia, waits for install completion |
| `bm_power_on.yml` | Idempotent power-on via Redfish with POST wait (retries 30x at 10s intervals) |
| `bm_power_off.yml` | Idempotent force power-off via Redfish with confirmation wait |
| `bm_check_usb_boot.yml` | Reads `GenericUsbBoot` BIOS attribute and fails if disabled |
| `bm_ensure_usb_boot.yml` | Wraps `bm_check_usb_boot.yml`; if disabled and `cifmw_bm_agent_enable_usb_boot` is true, sets the BIOS attribute, creates a config job, and power-cycles to apply |
| `bm_eject_vmedia.yml` | Ejects VirtualMedia from the iDRAC Virtual Optical Drive |
| `bm_discover_vmedia_target.yml` | Discovers or validates the UEFI device path for VirtualMedia, clears pending iDRAC config jobs, and sets a one-time boot override |
| `bm_patch_agent_iso.yml` | Patches the agent ISO ignition with core password, autologin, and debug shell on tty6 (used when `cifmw_bm_agent_live_debug` is true) |
| `bm_core_password_machineconfig.yml` | Generates a MachineConfig manifest to set the core user password hash post-install |

## openshift-install acquisition

The `openshift-install` binary is obtained automatically via one of two
methods, depending on which variable is set:

* **By version** (`cifmw_bm_agent_openshift_version`): downloads the tarball
  from `https://mirror.openshift.com/pub/openshift-v4/clients/ocp/<version>/openshift-install-linux.tar.gz`
  and extracts it.
* **By release image** (`cifmw_bm_agent_release_image` or
  `OPENSHIFT_RELEASE_IMAGE` env var): runs
  `oc adm release extract --command=openshift-install` against the image.

If the binary already exists in the working directory it is reused.

## Deployment workflow

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

## Examples

Minimal vars.yaml for a bare metal SNO deployment:

```YAML
cifmw_bm_sno: true
cifmw_bm_agent_cluster_name: ocp
cifmw_bm_agent_base_domain: example.com
cifmw_bm_agent_machine_network: "192.168.10.0/24"
cifmw_bm_agent_node_ip: "192.168.10.50"
cifmw_bm_agent_node_iface: eno12399np0
cifmw_bm_agent_bmc_host: idrac.mgmt.example.com
cifmw_bm_agent_openshift_version: "4.18.3"
cifmw_bm_agent_enable_usb_boot: true

cifmw_bm_nodes:
  - mac: "b0:7b:25:xx:yy:zz"
    root_device: /dev/sda
```

## Local debugging on an autoheld Zuul node

When a Zuul job is held (`autohold`), you can SSH into the Zuul controller
and iterate on the deployment without re-provisioning SNO from scratch.

### 1. Prepare the environment

Edit `~/configs/zuul_vars.yaml` to skip SNO re-provisioning and OpenStack
cleanup (there is nothing to clean up if doing the first RHOSO deployment):

```yaml
cifmw_cleanup_architecture: false
reuse_ocp: true
run_cleanup: false
```

### 2. Run the playbook

From the `ci-framework-jobs` checkout on the Zuul controller:

```bash
cd ~/src/gitlab.cee.redhat.com/ci-framework/ci-framework-jobs

ansible-playbook playbooks/baremetal/run-sno-bm.yaml \
  --flush-cache \
  -e@/home/zuul/configs/default-vars.yaml \
  -e@/home/zuul/src/gitlab.cee.redhat.com/ci-framework/ci-framework-jobs/scenarios/test/test-tool-versions.yaml \
  -e@/home/zuul/src/gitlab.cee.redhat.com/ci-framework/ci-framework-jobs/scenarios/uni/default-vars.yaml \
  -e@/home/zuul/src/gitlab.cee.redhat.com/ci-framework/ci-framework-jobs/scenarios/baremetal/vaf/rhel-vars.yaml \
  -e@/home/zuul/configs/networking_defintion.yaml \
  -e@/home/zuul/configs/nmstate_config.yaml \
  -e@/home/zuul/configs/scenario-vars.yaml \
  -e@/home/zuul/configs/secrets.yaml \
  -e@/home/zuul/configs/vars.yaml \
  -e@/home/zuul/configs/zuul_vars.yaml
```

With `reuse_ocp: true`, `run-sno-bm.yaml` will:

1. Copy the SNO kubeconfig from `dev-scripts/ocp/<cluster>/auth/` to
   `~/.kube/config` and `oc login` as `kubeadmin` with
   `--insecure-skip-tls-verify` (agent-based installer uses self-signed certs)
2. Generate `openshift-login-params.yml` via the `openshift_login` role
3. Write a static inventory mapping `controller-0` to `localhost`
4. Run `deploy-edpm-reuse.yaml` instead of `reproducer.yml`, which skips
   OCP provisioning and goes straight to architecture deployment

### 3. Subsequent iterations

Once the first EDPM deployment succeeds, set `cifmw_cleanup_architecture`
back to `true` so that `cleanup-architecture.sh` tears down the previous
OpenStack deployment before re-applying:

```yaml
cifmw_cleanup_architecture: true
reuse_ocp: true
run_cleanup: false
```

### 4. Quick OCP and agent/SNO SSH access

The SNO kubeconfig and kubeadmin password live in the dev-scripts auth
directory:

```bash
export KUBECONFIG=~/src/github.com/openshift-metal3/dev-scripts/ocp/<cluster>/auth/kubeconfig
oc login -u kubeadmin \
  -p "$(cat ~/src/github.com/openshift-metal3/dev-scripts/ocp/<cluster>/auth/kubeadmin-password)" \
  --insecure-skip-tls-verify=true
oc get nodes
```

For ssh access into SNO host:
```bash
ssh -i ~/ci-framework-data/artifacts/agent-install/agent_ssh_key \
  core@<cluster>.<cifmw_bm_agent_base_domain>
```

Replace `<cluster>` with the value of `cifmw_bm_agent_cluster_name` (e.g.
`sno`).

For ssh into agent-install appliance, use `-i ci-framework-data/artifacts/cifmw_ocp_access_key`.
You can also get autologin and debug shell on tty6 of the agent with:
```bash
cifmw_bm_agent_core_password: changeme
cifmw_bm_agent_live_debug: true
```

## References

* [ci-framework reproducer documentation](https://ci-framework.readthedocs.io/en/latest/roles/reproducer.html)
* [Redfish API specification](https://www.dmtf.org/standards/redfish)
* [Dell iDRAC Redfish API Guide](https://developer.dell.com/apis/2978/versions/6.xx/reference)
