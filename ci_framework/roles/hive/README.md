# Role: hive
This role can be used to claim clusters from a clusterpool.
It assumes that oc > 4 is installed and configured.

## Privilege escalation
None

## Parameters
* `cifmw_hive_platform`: (Required), the platform to install OpenShift. It
  could be a cloud provider or baremetal. Supported values are ('openstack').
* `cifmw_hive_kubeconfig`: (Required), absolute path to the kubeconfig file to
  be used for communicating with the Hive operator.
* `cifmw_hive_namespace`: (Required), OpenShift namespace that can be used for
  creating the required resources (secrets, clusterimageset, etc.).
* `cifmw_hive_action`: (Required), The action to be performed. Support values
  are (claim_cluster' and 'unclaim_cluster').
* `cifmw_hive_openstack_pool_name`: The name of OCP clusterpool to be used for
  claim. Required when platform is openstack and clusterpool exists.
* `cifmw_hive_openstack_claim_name`: The name of the claim to be used for the
  claimed OCP resource in Hive.
* `cifmw_hive_openstack_claim_life_time`: Time after which the cluster gets automatically deleted by the Hive operator. Defaults to 24h.
* `cifmw_hive_openstack_claim_timeout`: Time after which the cluster claim times out. Defaults to 59m.
* `cifmw_hive_oc_delete_timeout`: Time after which cluster delete times out. Defaults to 59m.
* `cifmw_hive_basedir`: Base directory to  be used.
* `cifmw_hive_artifacts_dir`: Directory where all artifacts produced (eg: kubeconfig file) will be stored.
