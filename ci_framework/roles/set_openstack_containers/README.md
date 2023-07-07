# set_openstack_containers
A role to set the environment variables for openstack services containers and friends
used during OpenStack services deployment using meta operator.

## Parameters
* `cifmw_set_openstack_containers_basedir`: Directory to store role generated contents. Defaults to `"{{ cifmw_basedir | default(ansible_user_dir ~ '/ci-framework-data') }}"`
* `cifmw_set_openstack_containers_registry`: Name of the container registry to pull containers from. Defaults to `quay.io`
* `cifmw_set_openstack_containers_namespace`: Name of the container namespace. Defaults to `podified-antelope-centos9`
* `cifmw_set_openstack_containers_tag`: Container tag. Defaults to `current-podified`
* `cifmw_set_openstack_containers_tag_from_md5`: Get the tag from delorean.repo.md5. Defaults to `false`.
* `cifmw_set_openstack_containers_dlrn_md5_path`: Full path of delorean.repo.md5. Defaults to `/etc/yum.repos.d/delorean.repo.md5`.
* `cifmw_set_openstack_containers_overrides`: Extra container overrides. Defaults to `{}`

## Examples
```yaml
- hosts: all
  tasks:
    - name: Generate env file for OpenStack containers services
      ansible.builtin.include_role:
        name: set_openstack_containers
```
