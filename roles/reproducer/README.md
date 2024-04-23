# reproducer
Role to deploy close to CI layout on a hypervisor.

## Privilege escalation
None

## Parameters

* `cifmw_reproducer_basedir`: (String) Base directory. Defaults to `cifmw_basedir`, which defaults to `~/ci-framework-data`.
* `cifmw_reproducer_compute_repos`: (List[mapping]) List of yum repository that must be deployed on the compute nodes during their creation. Defaults to `[]`.
* `cifmw_reproducer_compute_set_repositories`: (Bool) Deploy repositories (rhos-release) on Compute nodes. Defaults to `true`.
* `cifmw_reproducer_play_extravars`: (List[string]) List of extra-vars you want to pass down to the EDPM deployment playbooks. Defaults to `[]`.
* `cifmw_reproducer_kubecfg`: (String) Path to the CRC kubeconfig file. Defaults to the image_local_dir defined in the cifmw_libvirt_manager_configuration dict.
* `cifmw_reproducer_repositories`: (List[mapping]) List of repositories you want to synchronize from your local machine to the ansible controller.
* `cifmw_reproducer_run_job`: (Bool) Run actual CI job. Defaults to `true`.
* `cifmw_reproducer_run_content_provider`: (Bool) Run content-provider job. Defaults to `true`.
* `cifmw_reproducer_params`: (Dict) Specific parameters you want to pass to the reproducer. Defaults to `{}`.
* `cifmw_reproducer_dns_servers`: List of dns servers which should be used by the CRC VM as upstream dns servers. Defaults to 1.1.1.1, 8.8.8.8.
* `cifmw_reproducer_hp_rhos_release`: (Bool) Allows to consume rhos-release on the hypervisor. Defaults to `false`.
* `cifmw_reproducer_dnf_tweaks`: (List) Options you want to inject in dnf.conf, both on controller-0 and hypervisor. Defaults to `[]`.
* `cifmw_reproducer_skip_fetch_repositories`: (Bool) Skip fetching repositories from zuul var and simply copy the code from the ansible controller. Defaults to `false`.
* `cifmw_reproducer_supported_hypervisor_os`: (List) List of supported hypervisor operating systems and their minimum version.

### run_job and run_content_provider booleans and risks.

- For jobs with content-provider, both steps will be running by default.
- For jobs without content-provider, only the job will run by default.
- If a job with content-provider is launched with `cifmw_reproducer_run_job: false`, it will
  then run the content-provider, and stop.
- If a job with content-provider is launched for a second time with `cifmw_reproducer_run_content_provider: false`,
  if the first run did deploy the content-provider, it will pass.
- If a job with content-provider is launched a **first** time with `cifmw_reproducer_run_content_provider: false`,
  it will NOT RUN the content-provider, **leading to a crash of the job run**.


## Warning
This role isn't intended to be called outside of the `reproducer.yml` playbook.

## Examples
Please follow the [documentation about the overall "reproducer" feature](https://ci-framework.readthedocs.io/en/latest/roles/reproducer.html).

### Push repositories
#### Local repositories on your laptop
```YAML
local_home_dir: "{{ lookup('env', 'HOME') }}"
local_base_dir: "{{ local_home_dir }}/src/github.com/openstack-k8s-operators"
remote_base_dir: "/home/zuul/src/github.com/openstack-k8s-operators"
cifmw_reproducer_repositories:
  - src: "{{ local_base_dir }}/ci-framework"
    dest: "{{ remote_base_dir }}"
  - src: "{{ local_base_dir }}/install_yamls"
    dest: "{{ remote_base_dir }}"
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
