# install_yamls
An ansible role wrapper around [install_yamls](https://github.com/openstack-k8s-operators/install_yamls) Makefile.

It contains a set of playbooks to deploy podified control plane.

## Parameters
* `cifmw_install_yamls_envfile`: (String) Environment file containing all the Makefile overrides. Defaults to `install_yamls`.
* `cifmw_install_yamls_out_dir`: (String) `install_yamls` output directory to store generated output. Defaults to `{{ cifmw_basedir | default(ansible_user_dir ~ '/ci-framework') }}/artifacts"`.
* `cifmw_install_yamls_vars`: (Dict) A dict containing Makefile overrides.
* `cifmw_install_yamls_repo`: (String) `install_yamls` repo path. Defaults to `{{ ansible_user_dir }}/src/github.com/openstack-k8s-operators/install_yamls`.
* `cifmw_install_yamls_whitelisted_vars`: (List) Allowed variables in `cifmw_install_yamls_vars` that are not part of `install_yamls` Makefiles.
