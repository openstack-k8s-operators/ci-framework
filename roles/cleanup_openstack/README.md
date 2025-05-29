# cleanup_openstack

Cleans up openstack resources created by CIFMW by deleting CRs

## Privilege escalation
None

## Parameters
As this role is for cleanup it utilizes default vars from other roles which can be referenced at their role readme page: kustomize_deploy, deploy_bmh

* `cifmw_cleanup_openstack_detach_bmh`: (Boolean) Detach BMH when cleaning flag, this is used to avoid deprovision when is not required. Default: `true`
