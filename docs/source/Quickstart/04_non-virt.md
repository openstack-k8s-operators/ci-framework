# On your own hardware
While nested virtualization is a clean way to run tests, you may want to get
some better speed and easier access to the resources.

This is why the Framework is also able to consume your own hardware directly,
starting the CRC and Compute(s) VM directly on your hypervisor.

## Prepare your environment
In order to do so, some steps should be done beforehand.

### 1. Get the project and its dependencies
```Bash
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
  KUBECONFIG: "{{ ansible_user_dir }}/.crc/machines/crc/kubeconfig"
  OUTPUT_DIR: "{{ cifmw_basedir }}/artifacts/edpm_compute" # used by gen-ansibleee-ssh-key.sh
  OUTPUT_BASEDIR: "{{ cifmw_basedir }}/artifacts/edpm_compute" # used by gen-edpm-compute-node.sh
  SSH_KEY: "{{ cifmw_basedir }}/artifacts/edpm_compute/ansibleee-ssh-key-id_rsa"
  BMO_SETUP: false
cifmw_rhol_crc_config:
  pull-secret-file: "{{ ansible_user_dir }}/pull-secret"
  cpus: 10
  memory: 30520
  disk-size: 120
cifmw_use_libvirt: true
cifmw_use_crc: true
cifmw_operator_build_push_registry: "default-route-openshift-image-registry.apps-crc.testing"
cifmw_operator_build_meta_build: false
pre_infra:
  - name: Download needed tools
    inventory: "{{ cifmw_installyamls_repos }}/devsetup/hosts"
    type: playbook
    source: "{{ cifmw_installyamls_repos }}/devsetup/download_tools.yaml"
```

⚠️ Ensure you're not overprovisioning the CRC VM - here, it's allocating
about 30G of RAM, 10 Cores and 120G of disk space. It's more than the minimal
requirements.

### 4. Run the playbook
```Bash
$ ansible-playbook deploy-edpm -e @~/my-env.yml
```

### 5. Go grab some coffee
... and you should get a ready to test EDPM deploy, with one compute VM and
the CRC one.
