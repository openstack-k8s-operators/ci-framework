# devscripts_sno

Deploy a Single Node OpenShift (SNO) cluster on libvirt/KVM using the
[dev-scripts](https://github.com/openshift-metal3/dev-scripts) agent installer
(`make agent`).

This role is a thin wrapper around the `devscripts` role: it prepares secrets
and host prerequisites, runs the dev-scripts configuration and host-prep steps,
executes `make agent`, and copies the resulting kubeconfig to `~/.kube/config`.

It complements the full `devscripts` deployment path (baremetal/libvirt with
`make all`) and the physical bare metal path documented in
[bm_sno](../bm_sno/README.md) (`cifmw_bm_sno: true`).

When used from the reproducer, set `cifmw_devscripts_sno: true` so the
`devscripts` configuration template exports SNO-specific variables (see
[dev-scripts AGENTS.md](https://github.com/openshift-metal3/dev-scripts/blob/master/AGENTS.md)).
That flag is separate from including this role by name; reproducer scenarios
such as `scenarios/reproducers/va-hci-minimal-sno.yml` combine the flag with
`cifmw_devscripts_config_overrides` for a one-master layout.

## Parameters

### Role-specific

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `cifmw_devscripts_sno_installer_timeout` | int | `7200` | Seconds before `make agent` is killed by `timeout` (2 hours) |
| `cifmw_devscripts_sno_repo_dir` | str | `~/src/github.com/openshift-metal3/dev-scripts` | Path to the dev-scripts repository |
| `cifmw_devscripts_sno_data_dir` | str | `~/ci-framework-data` | Base directory for CI Framework data on the host |
| `cifmw_devscripts_sno_artifacts_dir` | str | `{{ cifmw_devscripts_sno_data_dir }}/artifacts` | Directory for role script artifacts and logs |

### Required for standalone use

When running this role outside the reproducer playbook, provide secret content
(the role writes files from these variables in `pre.yml`):

| Parameter | Description |
| --- | --- |
| `cifmw_manage_secrets_citoken_content` | CI token string written to `cifmw_manage_secrets_citoken_file` |
| `cifmw_manage_secrets_pullsecret_content` | Pull secret JSON written to `cifmw_manage_secrets_pullsecret_file` |

Default secret file paths (from `defaults/main.yml`):

| Parameter | Default |
| --- | --- |
| `cifmw_manage_secrets_citoken_file` | `{{ ansible_user_dir }}/secrets/ci_token` |
| `cifmw_manage_secrets_pullsecret_file` | `{{ ansible_user_dir }}/secrets/pull_secret.json` |

Alternatively, use the file-based variables documented in the
[devscripts role README](../devscripts/README.md#secrets-management) if you
integrate with `manage_secrets` directly.

### SNO and dev-scripts configuration

Set `cifmw_devscripts_sno: true` so `conf_ciuser.j2` exports the reduced SNO
variable set (`NUM_MASTERS=1`, `NUM_WORKERS=0`, and agent-related keys).

Cluster version, networking, and VM sizing are controlled through
`cifmw_devscripts_config_overrides` (and optional
`cifmw_devscripts_config_overrides_patch.*` keys), same as the `devscripts`
role. See [devscripts README](../devscripts/README.md#parameters) and
[Supported keys in cifmw_devscripts_config_overrides](../devscripts/README.md#supported-keys-in-cifmw_devscripts_config_overrides).

Common SNO overrides (also used in `scenarios/reproducers/va-hci-minimal-sno.yml`):

| Key | Example | Description |
| --- | --- | --- |
| `num_masters` | `1` | Single control-plane node |
| `master_memory` | `16384` | Memory (MiB) for the master VM |
| `master_disk` | `120` | Root disk size (GiB) |
| `master_vcpu` | `12` | vCPUs for the master VM |
| `agent_e2e_test_scenario` | `SNO_IPV4` | Agent installer test scenario |
| `agent_platform_type` | `none` | Agent platform type |
| `openshift_version` | `stable-4.18` | OpenShift version (minor or `stable-X.Y`) |
| `openshift_release_type` | `ga` | Release type (`nightly`, `ga`, `okd`) |
| `external_subnet_v4` | `192.168.111.0/24` | External network for the cluster |
| `ip_stack` | `v4` | IP stack (`v4`, `v6`, `v6v4`) |

Additional dev-scripts variables (for example `cifmw_devscripts_cpu_passthrough`,
`cifmw_devscripts_host_bm_net_ip_addr`) follow the `devscripts` role
documentation.

## Task files

| Task file | Description |
| --- | --- |
| `main.yml` | Orchestrates pre, QEMU ACL, setup, and post phases |
| `pre.yml` | Maps role vars to `devscripts`, writes secrets, installs packages |
| `prepare_qemu_home_access.yml` | Installs `acl`/`qemu-kvm` and grants `qemu` traverse on the user home |
| `setup.yml` | Runs `devscripts` `build_config.yml` and `100_pre.yml`, then `make agent` |
| `post.yml` | Copies cluster kubeconfig to `~/.kube/config` |

## Examples

### Standalone playbook

See `example-playbook.yaml` in this role directory:

```bash
ansible-playbook \
  -e @secrets.yaml \
  -e @scenarios/reproducers/va-hci-minimal-sno.yml \
  -i inventory.yaml \
  roles/devscripts_sno/example-playbook.yaml
```

Minimal `secrets.yaml` for standalone runs:

```yaml
cifmw_devscripts_sno: true
cifmw_manage_secrets_citoken_content: "{{ lookup('env', 'CI_TOKEN') }}"
cifmw_manage_secrets_pullsecret_content: |
  {{ lookup('file', lookup('env', 'HOME') ~ '/pull-secret') }}

cifmw_devscripts_config_overrides:
  openshift_version: "stable-4.18"
  openshift_release_type: ga
  num_masters: 1
  master_memory: 16384
  master_disk: 120
  master_vcpu: 12
  external_subnet_v4: 192.168.111.0/24
  ip_stack: v4
  agent_e2e_test_scenario: SNO_IPV4
  agent_platform_type: none
```

### Reproducer scenario (libvirt SNO)

From `scenarios/reproducers/va-hci-minimal-sno.yml`:

```yaml
cifmw_devscripts_sno: true
cifmw_reproducer_allow_one_ocp: true
cifmw_devscripts_cpu_passthrough: true
cifmw_devscripts_host_bm_net_ip_addr: "192.168.111.1"

cifmw_devscripts_config_overrides:
  num_masters: 1
  master_memory: 16384
  master_disk: 120
  master_vcpu: 12
  external_subnet_v4: 192.168.111.0/24
  ip_stack: v4
  agent_e2e_test_scenario: SNO_IPV4
  agent_platform_type: none
  openshift_release_type: ga
  openshift_version: stable-4.18
```

After deployment, credentials are under the dev-scripts auth directory:

```bash
export KUBECONFIG=~/src/github.com/openshift-metal3/dev-scripts/ocp/ocp/auth/kubeconfig
oc login -u kubeadmin \
  -p "$(cat ~/src/github.com/openshift-metal3/dev-scripts/ocp/ocp/auth/kubeadmin-password)"
```

## SNO deployment methods in CI Framework

| Flag | Role / method | Environment |
| --- | --- | --- |
| `cifmw_devscripts_sno: true` | dev-scripts agent (`make agent`) on libvirt/KVM | Virtual machine on the hypervisor |
| `cifmw_bm_sno: true` | `bm_sno` (agent-based, iDRAC Redfish) | Physical bare metal host |

See [reproducer README](../reproducer/README.md#sno-deployment-methods) for how
these paths fit into full reproducer jobs.

## References

* [devscripts role](../devscripts/README.md)
* [bm_sno role](../bm_sno/README.md)
* [dev-scripts](https://github.com/openshift-metal3/dev-scripts)
* [dev-scripts agent installer](https://github.com/openshift-metal3/dev-scripts/tree/master/agent)
* [dev-scripts AGENTS.md](https://github.com/openshift-metal3/dev-scripts/blob/master/AGENTS.md)
* [dev-scripts config_example.sh](https://github.com/openshift-metal3/dev-scripts/blob/master/config_example.sh)
