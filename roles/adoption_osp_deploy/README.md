# adoption_osp_deploy

Deploy OSP 17.1 environment for adoption based on DTs.

## Privilege escalation

`become` - Required in:
    - `login_registries`: For running subscription manager if needed,
    install packages and podman login as root.
    - `prepare_overcloud`: For setting up repositories, installing packages,
    create folders in /etc and running os-net-config.
    - `prepare_undercloud`: For setting up repositories, installing packages,
    create folders in /etc and running os-net-config.


## Parameters
* `cifmw_adoption_osp_deploy_ntp_server`: (String) NTP server to use in the 17.1
deployment. Defaults to `pool.ntp.org`
* `cifmw_adoption_osp_deploy_repos`: (List) List of 17.1 repos to enable. Defaults to
`[rhel-9-for-x86_64-baseos-eus-rpms, rhel-9-for-x86_64-appstream-eus-rpms, rhel-9-for-x86_64-highavailability-eus-rpms, openstack-17.1-for-rhel-9-x86_64-rpms, fast-datapath-for-rhel-9-x86_64-rpms, rhceph-6-tools-for-rhel-9-x86_64-rpms]`
* `cifmw_adoption_osp_deploy_stopper`: (String) Step at which to stop the run.  See `Break point` section below for possible values.
* `cifmw_adoption_osp_deploy_scenario`: (Dict) Define the parameter to
configure the OSP17.1 deployment.

### Break point

You can also stop the automated deploy by setting
`cifmw_adoption_osp_deploy_stopper`
parameter to a specific value.

Break point names are built using either `undercloud` or `overcloud`,
and the code currently supports the following seven different stoppers:

- Before calling pre undercloud hook: `before_pre_hook_undercloud`
- Before deploying undercloud: `before_deploy_undercloud`
- After deploying undercloud: `after_deploy_undercloud`
- After calling post undercloud hook: `after_post_hook_undercloud`
- Before calling pre overcloud hook: `before_pre_hook_overcloud`
- Before deploying overcloud: `before_deploy_overcloud`
- After deploying overcloud: `after_deploy_overcloud`

## Examples

```YAML
- name: Deploy source osp environment
  vars:
    cifmw_adoption_osp_deploy_scenario:
       undercloud:
         config:
           - section: DEFAULT
             option: undercloud_hostname
             value: undercloud.localdomain
       stacks:
         name: overcloud
  ansible.builtin.import_role:
    name: "adoption_osp_deploy"
```
