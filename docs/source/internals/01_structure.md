# Structure

## Roles, Playbooks & Plugins

We can find them here: https://github.com/openstack-k8s-operators/ci-framework/tree/main/ci_framework

Each role, playbook and plugin has README.md with the related documentation.

Some roles used the [install_yamls](https://github.com/openstack-k8s-operators/install_yamls) project. Although it is not part directly of the CI Framework project, it's good to keep it in mind. We may need to do changes there.

We will also find in the root of the project the [deploy-edpm.yml](https://github.com/openstack-k8s-operators/ci-framework/blob/main/deploy-edpm.yml) file that imports all the playbooks needed to setup everything - these playbooks import all the roles that are part of the framework -, it means that it will setup a CRC environment with EDPM VMs. We have more information in [Using the framework](https://github.com/openstack-k8s-operators/ci-framework#using-the-framework).

To cleanup everything [cleanup-edpm.yml](https://github.com/openstack-k8s-operators/ci-framework/blob/main/cleanup-edpm.yml).

## Scripts

In the [scripts](https://github.com/openstack-k8s-operators/ci-framework/tree/main/scripts) folder of the CI Framework project we can see different scripts that are being used for the [Makefile](https://github.com/openstack-k8s-operators/ci-framework/blob/main/Makefile) file.
