# pkg_build
This role will build a container image, allowing to push it to some remote
registry, and then run one container per package to build.

## Privilege escalation
None

## Parameters
* `cifmw_pkg_build_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which  defaults to `~/ci-framework`.
* `cifmw_pkg_build_ctx_name`: (String) Container full name. Defaults to `localhost/cifmw-buildpkgs`.
* `cifmw_pkg_build_ctx_tag`: (String) Container tag. Defaults to `latest`.
* `cifmw_pkg_build_ctx_push`: (Boolean) Whether the container has to be pushed to some remote registry. Defaults to `false`.
* `cifmw_pkg_build_ctx_baseimg`: (String) Container base image (FROM tag). Defaults to `quay.io/centos/centos:stream9`.
* `cifmw_pkg_build_pkg_basedir`: (String) Default location for the package repository sources. Defaults to `~/src`.
* `cifmw_pkg_build_list`: (List) List of packages to build, described as a dict. Defaults to `[]`.
* `cifmw_pkg_build_ctx_push_args`: (String) Optional parameter for the container push arguments. Defaults to `omit`.
* `cifmw_pkg_build_ctx_authfile`: (String) Optional parameter for the container registry authentication file. Defaults to `omit`.
* `cifmw_pkg_build_bop_env`: (String) Options to pass to the build_openstack_packages role.

## Examples
```YAML
---
- hosts: localhost
  gather_facts: true
  vars:
    cifmw_pkg_build_list:
      - name: neutron-tempest-plugin
      - name: nova-tempest-plugin
        src: "{{ ansible_user_dir }}/nova/tempest-plugin"
  roles:
    - role: "pkg_build"
  tasks:
    - name: Build package
      ansible.builtin.include_role:
        name: "pkg_build"
        tasks_from: "build.yml"
```
