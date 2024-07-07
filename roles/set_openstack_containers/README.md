# set_openstack_containers
A role to set the environment variables for openstack services containers and friends
used during OpenStack services deployment for any openstack operator.

The role will generate two 2 files in ~/ci-framework-data/artifacts/ directory after execution.
- `update_env_vars.sh`: Reusable script to update the env variable from the job (useful for reproducing locally)
- `operator_env.txt`: List of updated env variables


## Parameters
* `cifmw_set_openstack_containers_basedir`: Directory to store role generated contents. Defaults to `"{{ cifmw_basedir | default(ansible_user_dir ~ '/ci-framework-data') }}"`
* `cifmw_set_openstack_containers_registry`: Name of the container registry to pull containers from. Defaults to `quay.io`
* `cifmw_set_openstack_containers_namespace`: Name of the container namespace. Defaults to `podified-antelope-centos9`
* `cifmw_set_openstack_containers_tag`: Container tag. Defaults to `current-podified`
* `cifmw_set_openstack_containers_tag_from_md5`: Get the tag from delorean.repo.md5. Defaults to `false`.
* `cifmw_set_openstack_containers_dlrn_md5_path`: Full path of delorean.repo.md5. Defaults to `/etc/yum.repos.d/delorean.repo.md5`.
* `cifmw_set_openstack_containers_overrides`: Extra container overrides. Defaults to `{}`
* `cifmw_set_openstack_containers_prefix`: Update container containing. Defaults to `openstack`
* `cifmw_set_openstack_containers_openstack_version_change`: (Boolean) Set environment variables for openstack services containers for specific OPENSTACK_RELEASE_VERSION defined in cifmw_set_openstack_containers_update_target_version. It should be used only for meta openstack operator in prepare for openstack minor update. Defaults to `false`.
* `cifmw_set_openstack_containers_update_target_version`: Value of OPENSTACK_RELEASE_VERSION env in openstack operator that should be set. Defaults to `0.0.2`.

## Examples

Notes: Make sure we installed the meta operator before updating the environment variable(s) for
all openstack services. openstack-baremetal-operator is not installed by meta operator. Make
sure we first install it openstack-baremetal-operator and update the environment variable for
this baremetal operator.

### Update all openstack services containers env vars with podified-ci-testing tag in meta operator

It is used in edpm-prepare role to update all openstack service containers.

```yaml
- hosts: all
  tasks:
      # It will generate delorean.md5 file using podified-ci-testing dlrn tag
      # in ~/ci-framework-data/artifacts/repositories/delorean.repo.md5
    - name: Populate podified-ci-testing repo with repo-setup role
      ansible.builtin.include_role:
        name: repo-setup
      vars:
        cifmw_repo_setup_promotion: podified-ci-testing
        cifmw_repo_setup_branch: antelope

    - name: Update all openstack services containers env vars in meta operator with podified-ci-testing
      vars:
        cifmw_set_openstack_containers_dlrn_md5_path: "~/ci-framework-data//artifacts/repositories/delorean.repo.md5"
        cifmw_set_openstack_containers_tag_from_md5: true
        cifmw_set_openstack_containers_registry: quay.rdoproject.org
      ansible.builtin.include_role:
        name: set_openstack_containers
```

### Update all the openstack services containers env vars with podified-ci-testing for a single operator `baremetal`

It is used in edpm_deploy_baremetal role to update the UEFI image
```yaml
- hosts: all
  tasks:
      # It will generate delorean.md5 file using podified-ci-testing dlrn tag
      # in ~/ci-framework-data/artifacts/repositories/delorean.repo.md5
    - name: Populate podified-ci-testing repo with repo-setup role
      ansible.builtin.include_role:
        name: repo-setup
      vars:
        cifmw_repo_setup_promotion: podified-ci-testing
        cifmw_repo_setup_branch: antelope

    - name: Update all openstack services containers env vars in baremetal operator with podified-ci-testing
      vars:
        cifmw_set_openstack_containers_operator_name: openstack-baremetal
        cifmw_set_openstack_containers_dlrn_md5_path: "~/ci-framework-data//artifacts/repositories/delorean.repo.md5"
        cifmw_set_openstack_containers_tag_from_md5: true
        cifmw_set_openstack_containers_registry: quay.rdoproject.org
      ansible.builtin.include_role:
        name: set_openstack_containers
```

### Update an specific environment variables for a particular operator

It is used in edpm-ansible job to update the `ANSIBLEEE_IMAGE_URL_DEFAULT`.

```yaml
- hosts: all
  tasks:
    - name: Update ANSIBLEEE_IMAGE_URL_DEFAULT environment variable with custom image.
      vars:
        ansibleee_runner_img: "quay.io/openstack-k8s-operators/openstack-ansibleee-runner:<random_hash>"
        cifmw_set_openstack_containers_operator_name: openstack-ansibleee
        cifmw_set_openstack_containers_overrides:
          ANSIBLEEE_IMAGE_URL_DEFAULT: "{{ ansibleee_runner_img }}"
      ansible.builtin.include_role:
        name: set_openstack_containers
```

### Update all openstack services containers env vars in meta operator with tag from delorean and set OPENSTACK_RELEASE_VERSION env

It is used in update job to set openstack services containers in prepare for running openstack update.

```yaml
    - name: Update all openstack services containers env vars in meta operator with tag from delorean and set OPENSTACK_RELEASE_VERSION
      vars:
        cifmw_set_openstack_containers_dlrn_md5_path:  "~/ci-framework-data//artifacts/repositories/delorean.repo.md5"
        cifmw_set_openstack_containers_tag_from_md5: true
        cifmw_set_openstack_containers_registry: quay.rdoproject.org
        cifmw_set_openstack_containers_openstack_version_change: true
        cifmw_set_openstack_containers_update_target_version: 0.0.2
      ansible.builtin.include_role:
        name: set_openstack_containers
```
