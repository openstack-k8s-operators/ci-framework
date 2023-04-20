## Role: registry_deploy

An Ansible role to deploy local registry using registry:2 container image

### Parameters
* `cifmw_rp_registry_image`: The registry2 container image url.
* `cifmw_rp_registry_image_fallback`: Alternate registry2 container image url. It will be used when `cifmw_rp_registry_image` fails.
* `cifmw_rp_registry_ip:` The registry IP address.
* `cifmw_rp_registry_port:`: The registry port.
