# Molecule configuration/testing

All of the roles should get proper molecule tests. When you generate a new
role using `make new_role ROLE_NAME=my_role`, you will end with a basic role
structure, including the molecule part.

[More information about molecule](https://molecule.readthedocs.io/)

## Testing

Any extra configuration required for any Zuul CI job will be added in the following file [ci/config/molecule.yaml](https://github.com/openstack-k8s-operators/ci-framework/blob/main/ci/config/molecule.yaml).

For example if we need to set a timeout to the job `cifmw-molecule-rhol_crc` then we need to append the following lines:

~~~{code-block} YAML
:caption: zuul.d/job.yaml
:linenos:
- job:
    name: cifmw-molecule-rhol_crc
    timeout: 3600
~~~

These directives will be merged with the job definition created in the script [scripts/create_role_molecule.py](https://github.com/openstack-k8s-operators/ci-framework/blob/main/scripts/create_role_molecule.py)

## Regenerate molecule job

Once you have edited the script, re-generate the molecule job:
`make role_molecule`.

## My test needs CRC

The guide how to setup CRC VM was described in [guide](./01_nested_crc.md).
This would be needed to start the molecule test.

## Start molecule

Below would be an example, how to run `reproducer crc_layout` molecule job.
NOTE: make sure, it is executed as `zuul` user, otherwise it might fail (currently).

Steps:

```shell
# Install required packages
sudo yum install -y git vim golang ansible-core

# Clone required repos
git clone https://github.com/openstack-k8s-operators/ci-framework src/github.com/openstack-k8s-operators/ci-framework
# optionally
git clone https://github.com/openstack-k8s-operators/install_yamls src/github.com/openstack-k8s-operators/install_yamls

cd src/github.com/openstack-k8s-operators/ci-framework

# workaround for old Go lang binary
go install github.com/mikefarah/yq/v4@v4.40.1
export PATH=$PATH:~/go/bin

# Add host key to authorized keys
if ! [ -f ~/.ssh/id_ed25519.pub ]; then
    ssh-keygen -t ed25519 -a 200 -f ~/.ssh/id_ed25519 -N ""
fi
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys

# Create required directories
mkdir -p ~/ci-framework-data/artifacts/{parameters,roles}

cat << EOF > custom-vars.yaml
---
ansible_user_dir: /home/$(whoami)
zuul:
  projects:
    github.com/openstack-k8s-operators/ci-framework:
      src_dir: "src/github.com/openstack-k8s-operators/ci-framework"
cifmw_internal_registry_login: false
cifmw_basedir: "{{ ansible_user_dir }}/ci-framework-data"
cifmw_openshift_setup_skip_internal_registry: true
cifmw_artifacts_basedir: "{{ ansible_user_dir }}/ci-framework-data/artifacts "
nodepool:
  cloud: ""
mol_config_dir: /home/$(whoami)/src/github.com/openstack-k8s-operators/ci-framework/.config/molecule/config_local.yml
cifmw_zuul_target_host: localhost
EOF

ansible-galaxy install -r requirements.yml

# Mock some roles, that are needed for Zuul CI, but not for local deployment
mkdir -p roles/mirror-info-fork/tasks
mkdir -p roles/prepare-workspace/tasks
mkdir -p group_vars

# Execute Ansible to prepare molecule environment
ansible-playbook -i inventory.yml \
    -e@custom-vars.yaml \
    ci/playbooks/molecule-prepare.yml

##########################
### START MOLECULE JOB ###
##########################

# Execute molecule job
## Example
##    role: reproducer, scenario: crc_layout

# It can be done using:

### - Ansible - recommended ###

ansible-playbook -i inventory.yml \
    -e roles_dir="$(pwd)/roles/reproducer" \
    -e@custom-vars.yaml \
    ci/playbooks/molecule-test.yml

#### - shell steps ####
pip3 install -r test-requirements.txt
cd roles/reproducer

# NOTE: Usually it is: config_local.yml. There is also config_podman.yml scenario
# NOTE: In some cases, when molecule provides all parameters,
# do not include config file (skip adding '-c' parameter)
molecule -c ../../.config/molecule/config_local.yml test --all

# or just one scenario
molecule -c ../../.config/molecule/config_local.yml test -s crc_layout

# Sometimes it is required to force recreate preparation.
# For example for crc_layout scenario
cd roles/reproducer
molecule prepare --force -s crc_layout
```

### SSH to controller-0 - molecule VM

Sometimes it is required to SSH to the controller-0 (or other VM, here is
just an example), to verify the env. To achieve that, you can do:

```shell
ssh controller-0
```

And that's it!
