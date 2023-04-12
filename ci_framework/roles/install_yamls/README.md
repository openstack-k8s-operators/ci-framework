## Role: install_yamls
An ansible role wrapper around install_yamls Makefile.

It contains a set of playbooks to deploy podified control plane.

### How to generate required task file before consuming the role?

Go to ci-framework project root directory and run following commands:
```
$ cd <ci-framework project root directory>
$ python tools/generate_install_yamls_playbooks.py -m <full path to install_yamls makefile> -o <Output directory>
```
It generate the task files under install_yamls role directory.

### Parameters
* cifmw_install_yamls_envfile: Environment file containing all the Makefile overrides. Defaults to "install_yamls"
* cifmw_install_yamls_out_dir: Install_yamls output directory to store generated output. Defaults to "{{ cifmw_basedir | default(ansible_user_dir ~ '/ci-framework') }}/artifacts"
* cifmw_install_yamls_vars: A dict containing Makefile overrides.
* cifmw_install_yamls_repo: Install_yamls repo path. Defaults to  "{{ ansible_user_dir }}/src/github.com/openstack-k8s-operators/install_yamls"
* cifmw_install_yamls_dryrun: Dry run of install_yaml role. Defaults "True"
