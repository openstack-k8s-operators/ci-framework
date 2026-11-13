# edpm_build_images
This role will build EDPM hardened uefi, ironic-python-agent, and bootc images.
This role also call the `discover_latest_image` and download the latest image,
set proper exports for element and build images.
It will package the images inside a container image based on
the variables `cifmw_edpm_build_images_ironic_python_agent_package` and
`cifmw_edpm_build_images_hardened_uefi_package`.

## Privilege escalation
Bootc container builds, qcow2 generation, and publication use root's container
storage. Host package installation also requires privilege escalation.

## CS9 and CS10 bootc providers

CS9 builds use the `bootc/` Containerfile in `edpm-image-builder`.
`cifmw-content-provider-bootc-cs10` instead checks out
`s2i-openstack-containers` and invokes its `build.sh build-parallel` entry point
for `base,edpm/edpm-bootc`. The base image supplies the CS10 RPM repositories.
Both paths then generate and package a qcow2 disk and publish the existing
`edpm-bootc` and `edpm-bootc-qcow2` image references for deployment consumers.
The CS10 provider also builds IPA and tags its artifacts with the speculative
s2i checkout's commit. Consumers that already depend on an s2i provider can
instead set `cifmw_edpm_build_images_bootc_source_image` and reuse the conversion
and packaging tasks without another host-image build or paused provider.

### Deployment consumer job

`cifmw-crc-podified-edpm-baremetal-bootc-prebuilt` is an abstract CRC job for
that case. A child job selects the exact published image in its `pre-run` and
sets `cifmw_edpm_build_images_bootc_source_image` and
`cifmw_edpm_build_images_tag` as cacheable facts so they survive separate Zuul
Ansible invocations. Static job variables can be used instead. The child also
declares its provider dependency.
The parent's first `run` playbook, `ci/playbooks/edpm_build_images/bootc_prepare.yml`,
converts and publishes the disk on the controller and merges the image
references and registry address into the deployment parameters.
Packaging is controller-local and does not connect to CRC. The second `run`
playbook performs the normal bare-metal deployment: after its existing CRC
inventory and SSH setup, it configures registry trust using the shared helper,
then starts deployment. Registry configuration runs in nested Ansible on the
controller using the existing inventory, so CRC DNS and private keys are used
from the correct machine rather than the Zuul executor. API calls stay local
to the controller; only CRI-O configuration is delegated to CRC.
This step is enabled only for consumer jobs through
`cifmw_edpm_deploy_baremetal_configure_crc_registry`.

Set `cifmw_edpm_build_images_base_image` for the desired disk-wrapper base
and `cifmw_edpm_build_images_bootc_source_tls_verify: false` only when using
a trusted insecure provider registry. The consumer uses the default IPA
image; it does not rebuild IPA or allocate a second paused provider.

## Parameters
* `cifmw_edpm_build_images_basedir`: Base directory. Defaults to `cifmw_basedir` which  defaults to `~/ci-framework`.
* `cifmw_edpm_build_images_via_rpm`: Whether to install `edpm-image-builder` repo using rpm or not.
* `cifmw_build_host_packages`: List of packages required to build the images.
* `cifmw_edpm_build_images_elements`: Elements path which contains `edpm-image-builder` and `ironic-python-agent-builder` repo.
* `cifmw_edpm_build_images_all`: (Boolean) Build both the `edpm-hardened-uefi` and `ironic-python-agent` images when it true. Default to false.
* `cifmw_edpm_build_images_hardened_uefi`: (Boolean) Build `edpm-hardened-uefi` image when it true. Default to false.
* `cifmw_edpm_build_images_ironic_python_agent`: (Boolean) Build `ironic-python-agent-builder` image when it true. Default to false.
* `cifmw_edpm_build_images_bootc`: (Boolean) Build the bootc image workflow. Default to false.
* `cifmw_edpm_build_images_bootc_use_s2i`: (Boolean) Build the CS10 bootc host image with s2i's `build.sh`, including its `base` dependency. Default: false (CS9 uses `edpm-image-builder`). Both paths reuse the qcow2 packaging and output image contract.
* `cifmw_edpm_build_images_bootc_source_image`: (String) Existing bootc container image to pull into root's storage and convert to qcow2 without rebuilding the host image. Default: empty (build the host image). Takes precedence over `cifmw_edpm_build_images_bootc_use_s2i`.
* `cifmw_edpm_build_images_bootc_source_tls_verify`: (Boolean) Verify TLS when pulling the source image. Default: true. Set false only for a trusted insecure CI provider registry.
* `cifmw_edpm_build_images_bootc_s2i_repo_path`: (String) Path to the speculative `s2i-openstack-containers` checkout. Defaults to `~/src/github.com/openstack-k8s-operators/s2i-openstack-containers`. Jobs enabling s2i must include that repository in `required-projects`.
* `cifmw_edpm_build_images_hardened_uefi_package`: (Boolean) Packaged `edpm-hardened-uefi` image inside a container image for distribution. Default to false.
* `cifmw_edpm_build_images_ironic_python_agent_package`: (Boolean) Packaged  `ironic-python-agent-builder` image inside a container image for distribution. Default to false.
* `cifmw_edpm_build_images_bootc_repo`: (String) Repository used to push the bootc container image. Default: `{{ cifmw_edpm_build_images_push_registry }}/[{{ cifmw_edpm_build_images_push_registry_namespace }}/]edpm-bootc`.
* `cifmw_edpm_build_images_bootc_repo_path`: (String) Path to the bootc content within `edpm-image-builder`.
* `cifmw_edpm_build_images_bootc_base_image`: (String) Base bootc image used for the build. Default: `quay.io/centos-bootc/centos-bootc:stream9`.
* `cifmw_edpm_build_images_bootc_builder_image`: (String) Bootc builder image used to produce the qcow2 artifact. Default: `quay.io/centos-bootc/bootc-image-builder:latest`.
* `cifmw_edpm_build_images_bootc_qcow2_name`: (String) Output qcow2 file name for the bootc image. Default: `edpm-bootc.qcow2`.
* `cifmw_edpm_build_images_bootc_rhsm_script`: (String) Script name copied into the bootc build context to handle RHSM registration. Default: `empty.sh`.
* `cifmw_edpm_build_images_bootc_fips`: (String) Whether to enable FIPS in the bootc image build. Default: `1`.
* `cifmw_edpm_build_images_bootc_user_packages`: (String) Additional packages appended to the bootc image build. Default: empty string.
* `cifmw_edpm_build_images_dib_yum_repo_conf_centos`:  (List) List of yum repos to be used on centos node.
* `cifmw_edpm_build_images_dib_yum_repo_conf_rhel`: (List) List of yum repos to be used on rhel node.
* `cifmw_edpm_build_images_dib_yum_repo_conf`: (List) List of yum repos to be used, By default we select i.e. `cifmw_edpm_build_images_dib_yum_repo_conf_centos` var or `cifmw_edpm_build_images_dib_yum_repo_conf_rhel` based on distro var.
* `cifmw_edpm_build_images_tag`: (String) Tag with which we want to build container images. Default: `latest`.
* `cifmw_edpm_build_images_dry_run`: (Boolean) Whether to perform a dry run of the image build. Default: false.
* `cifmw_edpm_build_images_push_container_images`: (Boolean) Whether to push container images to remote registry. Default: false.
* `cifmw_edpm_build_images_push_registry`: (String) Push registry where we want to push container images. Default: `quay.rdoproject.org`.
* `cifmw_edpm_build_images_push_registry_namespace`: (String) Namespace on registry where we want to push container images. Default: `podified-master-centos9`.
* `cifmw_edpm_build_images_cert_path`: (String) Cert path. Default: `/etc/pki/ca-trust/source/anchors/rh.crt`
* `cifmw_edpm_build_images_cert_install`: (Boolean) Whether to install cert in the image. Default: false
* `cifmw_edpm_build_images_base_image`: (String) Base image to package the edpm and ipa qcow2 images into the container images for rhel distro.

* `cifmw_edpm_build_images_cert_dest`: (String) The path where the certificates should be placed inside the image builder. Default: `/etc/pki/ca-trust/source/anchors/edpm-build-images.crt`.
* `cifmw_edpm_build_images_cert_filter_ou`: (String) Optional. If given, filter out by OU the source certs using this regex.
* `cifmw_edpm_build_images_cert_filter_cn`: (String) Optional. If given, filter out by CN the source certs using this regex.

## Example
```YAML
---
- hosts: localhost
  gather_facts: true
  tasks:
    - ansible.builtin.import_role:
        name: edpm_build_images
