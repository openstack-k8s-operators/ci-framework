# install_openstack_ca
Extract CA data from the OpenstackControlPlane and install it on the host

Note that this role assumes that an OpenstackControlPlane is deployed.

## Parameters
* `cifmw_install_openstack_ca_dest_path`: (String) Path where to store the
OpenstackControlPlane CA. Defaults to `~/ci-framework/artifacts/manifests`.
* `cifmw_install_openstack_ca_file`: (String) File name to the extracted CA file
that will be installed. Defaults to `tls-ca-bundle.pem`.

## Examples
```YAML
- name: Inject Red Hat downstream CA bundle
  vars:
    cifmw_install_openstack_ca_dest_path: "{{ cifmw_basedir }}"
  ansible.builtin.include_role:
    role: install_openstack_ca
```
