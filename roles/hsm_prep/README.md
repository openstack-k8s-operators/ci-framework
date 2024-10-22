# HSM Role

In order to use HSMs, the barbican images need to be customized to include the HSM software.  For now, this is something
that we expect customers to do with scripts that we will provide as part of the barbican-operator code.

The purpose of this role is to:
* Generate new images for the barbican-api and barbican-worker containing the HSM software
* Upload those images to a private repository for use in setting up a CI job.
* Create any required config to be mounted by the barbican images to interact with the HSM

For the Lunasa, we expect some preparatory steps to be completed prior to execution in order for the
role to complete successfully.
* We expect a VM that contains the Lunasa client software and that is registered as a lunasa client.
  This VM should contain the following contents:
  * The contents of the minimal linux client in a zipped tar file.
  * The lunasa binaries that need to be added to the image under a specified directory.
  * The lunasa HSM server cert.
* The above contents will be fetched by the role.
* The VM will be used to generate client certificates.  For this, we will need the cifmw_hsm_client_ip , which
  is the VM of the hypervisor hosting the openshift node.  If a cert has already been generated, then
  that certificate will be retrieved instead.
* The certs will be retrieved and stored in a secret (cifmw_hsm_luna_cert_secret)
* The password to log into the HSM partition will be stored in a secret (cifmw_hsm_login_secret)
* As input to this role, we will require the ssh connection details and credentials for this VM.

A minimal (one that takes the defaults) invocation of this role is shown below, where the lunaclient
is the running client VM described above.

- name: Set up Luna
  hosts: lunaclient
  ansible.builtin.include_role: hsm_prep
  tags:
    - image_prep
    - cert_prep
    - secret_prep
  vars:
    cifmw_hsm_admin_password: "<HSM admin password>"
    cifmw_hsm_server_ip: "IP of HSM"
    cifmw_hsm_client_ip: "IP of the client - this could be the hypervisor where the Openshift nodes run"
    cifmw_hsm_luna_partition: "HSM partition for the client to join"
    cifmw_hsm_partition_password: "<HSM partition password>"

Note that tags have been provided to allow the caller to select specific operations.  This may be necessary
because different operations may need to executed in different CI jobs.  The current tags available are:
image_prep, cert_prep, secret_prep, cleanup

## Parameters

### HSM Details
* `cifmw_hsm_hsmtype`: (String) The type of HSM required.  Currently, only "luna" is supported. Default value: `luna`
* `cifmw_hsm_admin_user`: (String) The user to log into the HSM.  Default value: `admin`
* `cifmw_hsm_admin_password`: (String) The password to log into the HSM.
* `cifmw_hsm_server_ip`: (String) ip address or hostname of the HSM
* `cifmw_hsm_partition_password: (String) The password to log into the HSM partition
* `cifmw_hsm_login_secret`: (String) The secret to store the password to log into the HSM partition. Default: `hsm-login`

### Barbican Image and Details to get buildah script
* `cifmw_hsm_barbican_operator_repo`: (String) Repo for barbican-operator. Default value: "https://github.com/openstack-k8s-operators/barbican-operator.git"
* `cifmw_hsm_barbican_operator_version`: (String) Version for barbican-operator.  Default value: "main"
* `cifmv_hsm_barbican_image_namespace`: (String) Namespace for barbican-operator source image.  Default value: "podified-antelope-centos9"
* `cifmw_hsm_barbican_image_tag`: (String) Tag for barbican-operator source image.  Default value: "current-podified"

### Role Parameters
* `cifmw_hsm_cleanup`: (Boolean) Delete all resources created by the role at the end of the testing. Default value: `false`
* `cifmw_hsm_working_dir`: (String) Working directory to store artifacts.  Default value: `/tmp/hsm-prep-working-dir`
* `cifmw_hsm_client_ip`: (String) ip address or hostname of the client VM

### Luna Parameters
* `cifmw_hsm_luna_minclient_src`: (String) Location of linux minimal client tarball on the luna client VM. Default value: `/opt/data/Linux-Minimal-Client.tar.gz`
* `cifmw_hsm_luna_binaries_src`: (String) Location of the luna binaries on the luna client VM. Default value: `/opt/data/bin`
* `cifmw_hsm_luna_server_cert_src`: (String) Location of HSM server cert on the luna client VM.  Default value: `/usr/safenet/lunaclient/cert/server`
* `cifmw_hsm_luna_client_cert_src`: (String) Location of HSM client cert on the luna client VM.  Default value: `/usr/safenet/lunaclient/cert/client`
* `cifmw_hsm_luna_cert_secret`: (String) Name of the secret that stores all of the needed certs for luna.  Default value: `barbican-luna-certs`
* `cifmw_hsm_luna_cert_secret_namespace`: (String) Namespace of the secret that stores all of the needed certs for luna.  Default value: `openstack`
* `cifmw_hsm_luna_partition`: (String) HSM partition for the client to join.
