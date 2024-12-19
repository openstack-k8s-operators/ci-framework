# HSM Role

In order to use HSMs, the barbican images need to be customized to include the HSM software.

The purpose of this role is to:
* Generate new images for the barbican-api and barbican-worker containing the HSM software
* Upload those images to a private repository for use in setting up a CI job.
* Create any required config to be mounted by the barbican images to interact with the HSM

For the Lunasa, we expect some preparatory steps to be completed prior to execution in order for the
role to complete successfully.
* The lunasa software is uploaded somewhere and will be fetched by the role
  * The contents of the minimal linux client in a zipped tar file should be made available at cifmw_hsm_luna_minclient_src.
  * The lunasa binaries that need to be added to the image are made available at cifmw_hsm_luna_binaries_src.
  * The lunasa HSM cacert file is made available at cifmw_hsm_luna_server_cert_src.  For an HA configuration,
    this will be a concatenation of all the server certs for the servers in the HA partition.
  * The client certificate and key made available at cifmw_hsm_luna_client_cert_src.  The files are expected
    to be of the form "(cifmw_hsm_client_ip)".pem and "(cifmw_hsm_client_ip)"Key.pem
* The certs will be retrieved and stored in a secret (cifmw_hsm_luna_cert_secret)
* The password to log into the HSM partition will be stored in a secret (cifmw_hsm_login_secret)

A minimal (one that takes the defaults) invocation of this role is shown below.  In this case, the lunaclient
software and certs are stored locally under /opt/luna.

- name: Set up Luna
  hosts: lunaclient
  ansible.builtin.include_role: hsm_prep
  tags:
    - image_prep
    - cert_prep
    - secret_prep
  vars:
    cifmw_hsm_client_ip: "IP of the client - this could be the hypervisor where the Openshift nodes run"

Note that tags have been provided to allow the caller to select specific operations.  This may be necessary
because different operations may need to executed in different CI jobs.  The current tags available are:
image_prep, cert_prep, secret_prep, cleanup

## Parameters

### HSM Details
* `cifmw_hsm_hsmtype`: (String) The type of HSM required.  Currently, only "luna" is supported. Default value: `luna`
* `cifmw_hsm_login_secret`: (String) The secret to store the password to log into the HSM partition. Default: `hsm-login`

### Role Parameters
* `cifmw_hsm_cleanup`: (Boolean) Delete all resources created by the role at the end of the testing. Default value: `false`
* `cifmw_hsm_working_dir`: (String) Working directory to store artifacts.  Default value: `/tmp/hsm-prep-working-dir`
* `cifmw_hsm_client_ip`: (String) ip address or hostname of the client VM

### Image Details
* `cifmw_hsm_barbican_src_image_registry`: (String) Registry of the source image. Default value: `quay.io`
* `cifmw_hsm_barbican_src_image_namespace: (String) Namespace of the source image. Default value: `podified-antelope-centos9`
* `cifmw_hsm_barbican_src_image_tag: (String) Tag of the source image. Default value: `current-podified`
* `cifmw_hsm_barbican_dest_image_registry`: (String) Registry of the modified image. Default value: `quay.io`
* `cifmw_hsm_barbican_dest_image_namespace: (String) Namespace of the modified image. Default value: `podified-antelope-centos9`
* `cifmw_hsm_barbican_dest_image_tag: (String) Tag of the modified image. Default value: `current-podified-luna`

### Luna Parameters
* `cifmw_hsm_luna_minclient_src`: (String) Location of linux minimal client tarball. Default value: `file:///opt/luna/Linux-Minimal-Client.tar.gz`
* `cifmw_hsm_luna_binaries_src`: (String) Location of the luna binaries. Default value: `file:///opt/luna/bin`
* `cifmw_hsm_luna_server_cert_src`: (String) Location of HSM server CA cert.  Default value: `file:///opt/luna/cert/server/cacert.pem`
* `cifmw_hsm_luna_client_cert_src`: (String) Location of HSM client certs.  Default value: `file:///opt/luna/cert/client`
* `cifmw_hsm_server_ca_file`: (String) Name of the cacert file in the container.  Default value: `cacert.pem`
* `cifmw_hsm_luna_cert_secret`: (String) Name of the secret that stores all of the needed certs for luna.  Default value: `barbican-luna-certs`
* `cifmw_hsm_luna_cert_secret_namespace`: (String) Namespace of the secret that stores all of the needed certs for luna.  Default value: `openstack`
