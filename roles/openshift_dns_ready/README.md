# openshift_dns_ready

A role to wait for the OpenShift DNS operator to be ready before proceeding with tasks that require DNS resolution.

## Privilege escalation

None required.

## Parameters

* `cifmw_openshift_dns_ready_timeout`: (Integer) Timeout in seconds for `oc wait --timeout`. Default: `60`.
* `cifmw_openshift_dns_ready_path_prefix`: (String) Directories prepended to `PATH` when `cifmw_path` is unset, so non-interactive SSH finds `oc` (e.g. under `~/.crc/bin`). Default includes `~/.crc/bin`, `~/bin`, `~/.local/bin`.
* `cifmw_path`: (String) When set (framework bootstrap / CRC), used as `PATH` for `oc` instead of the prefix above.
* `cifmw_openshift_kubeconfig`: (String) Path to kubeconfig file. If set, exported as `KUBECONFIG`. Inherited from framework defaults.
* `cifmw_openshift_dns_ready_delegate_to`: (String) Optional inventory hostname to run `oc` on. If unset, uses `cifmw_target_host` (hypervisor in adoption/reproducer), then the current host. Override only when needed; a host without `oc` fails.

## Usage

Used before tasks that require DNS resolution in OpenShift, such as downloading certificates from URLs or accessing external services.

## How it works

The role runs `oc wait dns.operator.openshift.io/default --for=condition=Available=true` so the cluster DNS operator is ready before proceeding. The command is delegated when `cifmw_target_host` is set so `oc` runs on the hypervisor (or another host that has the CLI and kubeconfig). `PATH` is set explicitly so delegated runs match interactive shells (where `oc` is often on `PATH` via profile).
