# On your own hardware
While nested virtualization is a clean way to run tests, you may want to get
some better speed and easier access to the resources.

This is why the Framework is also able to consume your own hardware directly,
starting the CRC and Compute(s) VM directly on your hypervisor.

Make sure your test user has proper sudo access and
access to libvirtd. Verify you have `git` and `make` installed.

## Prepare your environment
In order to do so, some steps should be done beforehand.

### 0. Ensure you meet the requirements
Please check [this page](./01_requirements.md) first.

### 1. Get the project and its dependencies
```Bash
$ cd $HOME
$ git clone https://github.com/openstack-k8s-operators/install_yamls
$ cd install_yamls/devsetup
$ make cifmw_prepare
$ cd ci-framework
```

### 2. Install dependencies
```Bash
$ make setup_molecule
```

### 3. Prepare an environment file with needed data
In order to deploy without any issue, the following data should be set, for
instance in `~/my-env.yml`:
```YAML
---
cifmw_repo_setup_os_release: 'centos'
cifmw_repo_setup_dist_major_version: 9
cifmw_basedir: "{{ ansible_user_dir }}/ci-framework-data"
cifmw_rhol_crc_use_installyamls: true
cifmw_installyamls_repos: "{{ ansible_user_dir }}/install_yamls"
cifmw_install_yamls_vars:
  BMO_SETUP: false
cifmw_rhol_crc_config:
  pull-secret-file: "{{ ansible_user_dir }}/pull-secret"
  cpus: 10
  memory: 30520
  disk-size: 120
cifmw_use_libvirt: true
cifmw_deploy_edpm: true
cifmw_use_crc: true
cifmw_operator_build_push_registry: "default-route-openshift-image-registry.apps-crc.testing"
cifmw_operator_build_meta_build: false
pre_infra:
  - name: Download needed tools
    inventory: "{{ cifmw_installyamls_repos }}/devsetup/hosts"
    type: playbook
    source: "{{ cifmw_installyamls_repos }}/devsetup/download_tools.yaml"
```

⚠️ Ensure you're not over provisioning the CRC VM - here, it's allocating
about 30G of RAM, 10 Cores and 120G of disk space. It's more than the minimal
requirements.

### 4. Place a pull secret in place

Get the pull secret from [here](https://cloud.redhat.com/openshift/create/local)
and save it in `$HOME/pull-secret`.

### 5. Run the playbook
```Bash
$ ansible-playbook deploy-edpm.yml -e @~/my-env.yml
```

### 6. Go grab some coffee
... and you should get a ready to test EDPM deploy, with one compute VM and
the CRC one.

### Cleanup

Check if the `roles_path` in `install_yamls/devsetup/ci-framework/ansible.cfg`
points to the right `cifmw_basedir`, in case you are using a custom config.

```
cd $HOME/install_yamls/devsetup/ci-framework
ansible-playbook cleanup-edpm.yml -e @~/my-env.yml
cd ..
make crc_cleanup edpm_compute_cleanup
rm -rf ~/ci-framework-data
```
