# cleanup_openstack

Cleans up openstack resources created by CIFMW by deleting CRs

## Privilege escalation
None

## Parameters
As this role is for cleanup it utilizes default vars from other roles which can be referenced at their role readme page: kustomize_deploy, deploy_bmh

* `cifmw_cleanup_openstack_detach_bmh`: (Boolean) Detach BMH when cleaning flag, this is used to avoid deprovision when is not required. Default: `true`
* `cifmw_cleanup_openstack_operators_wait_timeout`: (Integer) Seconds to wait for the operator CRs and the OpenStack namespace to be removed before giving up and force-draining a namespace stuck in `Terminating`. Kept short so the recovery (strip leftover finalizers + retry) kicks in quickly instead of burning the full default deletion timeout. Default: `300`
