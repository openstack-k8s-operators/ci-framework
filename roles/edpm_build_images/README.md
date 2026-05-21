# edpm_build_images
This role will build EDPM hardened uefi, ironic-python-agent, and bootc images.
This role also call the `discover_latest_image` and download the latest image,
set proper exports for element and build images.
It will package the images inside a container image based on
the variables `cifmw_edpm_build_images_ironic_python_agent_package` and
`cifmw_edpm_build_images_hardened_uefi_package`.

## Privilege escalation
None

## Parameters
* `cifmw_edpm_build_images_basedir`: Base directory. Defaults to `cifmw_basedir` which  defaults to `~/ci-framework`.
* `cifmw_edpm_build_images_via_rpm`: Whether to install `edpm-image-builder` repo using rpm or not.
* `cifmw_build_host_packages`: List of packages required to build the images.
* `cifmw_edpm_build_images_elements`: Elements path which contains `edpm-image-builder` and `ironic-python-agent-builder` repo.
* `cifmw_edpm_build_images_all`: (Boolean) Build both the `edpm-hardened-uefi` and `ironic-python-agent` images when it true. Default to false.
* `cifmw_edpm_build_images_hardened_uefi`: (Boolean) Build `edpm-hardened-uefi` image when it true. Default to false.
* `cifmw_edpm_build_images_ironic_python_agent`: (Boolean) Build `ironic-python-agent-builder` image when it true. Default to false.
* `cifmw_edpm_build_images_bootc`: (Boolean) Build the bootc image workflow. Default to false.
* `cifmw_edpm_build_images_hardened_uefi_package`: (Boolean) Packaged `edpm-hardened-uefi` image inside a container image for distribution. Default to false.
* `cifmw_edpm_build_images_ironic_python_agent_package`: (Boolean) Packaged  `ironic-python-agent-builder` image inside a container image for distribution. Default to false.
* `cifmw_edpm_build_images_bootc_repo`: (String) Repository used to push the bootc container image. Default: `{{ cifmw_edpm_build_images_push_registry }}/edpm-bootc`.
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
