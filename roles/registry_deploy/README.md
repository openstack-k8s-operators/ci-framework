# registry_deploy

An Ansible role to deploy local registry using registry:2 container image

## Parameters
* `cifmw_rp_registry_image`: (String) The registry2 container image url. Defaults to `docker.io/library/registry:2`.
* `cifmw_rp_registry_image_fallback`: (String) Alternate registry2 container image url. It will be used when `cifmw_rp_registry_image` fails. Defaults to `quay.rdoproject.org/openstack-k8s-operators/registry:2`
* `cifmw_rp_registry_ip:` (String) The registry IP address. Defaults to `0.0.0.0`.
* `cifmw_rp_registry_port:`: (Integer) The registry port. Defaults to `5001`.
* `cifmw_rp_registry_firewall`: (Bool) Configure nftables.
