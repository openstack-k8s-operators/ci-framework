# reproducer
Role to deploy close to CI layout on a hypervisor.

## Privilege escalation
None

## Parameters
* `cifmw_reproducer_basedir`: (String) Base directory. Defaults to `cifmw_basedir`, which defaults to `~/ci-framework-data`.
* `cifmw_reproducer_compute_repos`: (List[mapping]) List of yum repository that must be deployed on the compute nodes during their creation. Defaults to `[]`.
* `cifmw_reproducer_kubecfg`: (String) Path to the CRC kubeconfig file. Defaults to the image_local_dir defined in the cifmw_libvirt_manager_configuration dict.
* `cifmw_reproducer_repositories`: (List[mapping]) List of repositories you want to synchronize from your local machine to the ansible controller.
* `cifmw_reproducer_run_job`: (Bool) Run actual CI job. Defaults to `true`.
* `cifmw_reproducer_params`: (Dict) Specific parameters you want to pass to the reproducer. Defaults to `{}`.
* `cifmw_reproducer_dns_servers`: List of dns servers which should be used by the CRC VM as upstream dns servers. Defaults to 1.1.1.1, 8.8.8.8.
* `cifmw_reproducer_hp_rhos_release`: (Bool) Allows to consume rhos-release on the hypervisor. Defaults to `false`.
* `cifmw_reproducer_dnf_tweaks`: (List) Options you want to inject in dnf.conf, both on controller-0 and hypervisor. Defaults to `[]`.

## Warning
This role isn't intended to be called outside of the `reproducer.yml` playbook.

## Examples
Please follow the [documentation about the overall "reproducer" feature](https://ci-framework.readthedocs.io/en/latest/cookbooks/reproducer.html).

### Push repositories
#### Local repositories on your laptop
```YAML
local_home_dir: "{{ lookup('env', 'HOME') }}"
local_base_dir: "{{ local_home_dir }}/src/github.com/openstack-k8s-operators"
remote_base_dir: "/home/zuul/src/github.com/openstack-k8s-operators"
cifmw_reproducer_repositories:
  - src: "{{ local_base_dir }}/ci-framework"
    dest: "{{ remote_base_dir }}/ci-framework"
  - src: "{{ local_base_dir }}/install_yamls"
    dest: "{{ remote_base_dir }}/install_yamls"
```
Notes:
* `ansible_user_dir` isn't really usable due to the use of `delegate_to` in order to sync those local repositories.
* You therefore really want to use absolute paths - while the `dest` may be relative with the use of a plain `rsync` command

#### Github code
```YAML
remote_base_dir: "/home/zuul/src/github.com/openstack-k8s-operators"
cifmw_reproducer_repositories:
  # Fetch specific version
  - src: "https://github.com/cjeanner/ci-framework"
    dest: "{{ remote_base_dir }}/ci-framework"
    version: some-version
  # Fetch a pull-request and checkout the specific content
  - src: "https://github.com/foo/install_yamls"
    dest: "{{ remote_base_dir }}/install_yamls"
    refspec: pull/510/head:my-patch
    version: my-patch
  # Just get HEAD
  - src: "https://github.com/openstack-k8s-operators/openstack-operators"
    dest: "{{ remote_base_dir }}/openstack-operators"
```
