# openshift_obs

The purpose of this role is to deploy the cluster observability operator.

## Privilege escalation

No, privilege escalation is required for using the role. However,
`cluster-admin` privileges is required for deploying the operator.

## Parameters

Requires `cifmw_openshift_kubeconfig` variable to point to right configuration.

`cifmw_openshift_obs_definition` (dict) The `Subscription` resource definition to
be used to install the Cluster Observability Operator.
