# Virtualized environment setup

In this section, you will learn how to set up your local development environment.

> ⚠️ **Warning**
> For now, the ci-framework is only supported on CentOS machines. More platforms will be supported in the future.

## Pre-setup

### Meet the requirements
Please check [this page](./01_requirements.md) first.

### Nested virtualization support
Ensure you have nested virtualization support on your hardware. You can follow [this documentation](https://docs.fedoraproject.org/en-US/quick-docs/using-nested-virtualization-in-kvm/).

### OpenShift pull-secret
Create and download a pull-secret.

ℹ️ To do so, please visit [this link](https://console.redhat.com/openshift/create/local).

## Steps to Set Up Local Dev Environment

1. **Clone the Repository**

```bash
git clone https://github.com/openstack-k8s-operators/ci-framework.git
```

2. **Move to the repository folder**

```Bash
cd ci-framework
```

4. **Install dependencies**
```Bash
make setup_molecule
```

5. **Create a new VM by running**

Before running the following command, make sure to download a pull-secret file from [here](https://cloud.redhat.com/openshift/create/local) and save it at `~/pull-secret`.

```Bash
make local_env_create LOCAL_ENV_OPTS="-K"
```
ℹ️ The `-K` option is passed down to the `ansible-playbook` command directly. It will require your user password for `sudo` (wrapped in the `become` directives nested
in the roles - please refer to the READMEs located in the used roles: libvirt_manager). Of course, if you have a NOPASSWD directive in your sudoers, you don't need
to pass that option/parameter.

ℹ️ You may want to check the local_env_vm role README in order to find all of the available parameters. You can then pass them as follow:
```Bash
make local_env_create LOCAL_ENV_OPTS="-K -e param_name='param_value' -e @my-custom-file.yml"
```

6. **Verify the setup**
If everything goes as expected, you should see the following message:

```Bash
 "msg": "You may connect to your lab instance using *ssh cifmw-vm*.
```
7. **Ssh into the VM**

```Bash
ssh cifmw-vm
```

ℹ️ This is possible because your `~/.ssh/config` has a configuration block allowing an easy access to the VM.

8. **Run the ci-framework**

Navigate to the ci-framework folder

```Bash
cd /home/zuul/src/ci-framework
```
Run the ansible command

```Bash
ansible-playbook -e @scenarios/centos-9/local-env.yml deploy-edpm.yml
```

ℹ️ You may want to discover other existing scenarios in the `/scenarios` location.

## Cleaning the local_env VM

```Bash
make local_env_vm_cleanup
```

## I want some details

The `make` target will call `ansible-playbook` against the dev-local-env.yml playbook. This playbook will then:
- create some directories located in `~/ci-framework-data`
- generate an ephemeral SSH keypair in `~/ci-framework-data/artifacts` and allow it in the VM
- fetch the latest CentOS Stream 9 image and store it in `~/ci-framework-data/images`
- create a layered image based upon that CS9 image, and store i in `~/ci-framework-data/images`
- bootstrap the VM, installing some softwares, configuring services and all
- inject a block in your `~/.ssh/config` file for an easy access
