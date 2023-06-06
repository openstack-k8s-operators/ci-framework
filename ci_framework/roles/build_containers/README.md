# build_containers
Role to build openstack containers using tcib

## Privilege escalation
become - Required to install and execute tcib

## Parameters

* `cifmw_build_containers_tcib_src`: (String) Repository of tcib to be installed
* `cifmw_build_containers_basedir`: (String) Directory where we will hold all tcib files. Default to `cifmw_basedir/artifacts/containers_build` which defaults to `~/ci-framework-data/`.
* `cifmw_build_containers_authfile_path`: (String) Authorization file to push containers to registry. Default to `${XDG_RUNTIME_DIR}/containers/auth.json`.
* `cifmw_build_containers_push_containers`: (Boolean) Whether push containers after build or not. Default to `false`.
* `cifmw_build_containers_timestamper_cmd`: (String) Timestamp to be added in the logs
* `cifmw_build_containers_container_name_prefix`: (String) Prefix to be added in the name of the containers. Default to `openstack`.
* `cifmw_build_containers_buildah_push`: (Boolean) Whether push containers with buildah or not. Default to `false`.
* `cifmw_build_containers_distro`: (String) Distro to be used as base to build the containers. Default to `ansible_distribution`.
* `cifmw_build_containers_release`: (String) Distro release version. Default to `ansible_distribution_major_version`.
* `cifmw_build_containers_openstack_release`: (String) Openstack release name. Default to `master`.
* `cifmw_build_containers_dist_major_version`: (String) Distro major version. Default to `ansible_distribution_major_version`.
* `cifmw_build_containers_registry_namespace`: (String) Registry namespace in quay, docker or other registry service. Default to `podified-master-centos9`.
* `cifmw_build_containers_push_registry`: (String) Container registry URL. Default to `localhost`.
* `cifmw_build_containers_rhel_modules`: (String) A comma separated list of RHEL modules to enable with their version. Example: 'mariadb:10.3,virt:8.3'.
* `cifmw_build_containers_exclude_containers`: (List) List of containers to match against the list of containers to be built to skip. Default to `[]`.
* `cifmw_build_containers_config_file`: (String) YAML config file specifying the images to build. Default to `containers.yaml`.
* `cifmw_build_containers_config_path`: (String) Base configuration path. Default to `/usr/share/tcib/container-images`.
* `cifmw_build_containers_build_timeout`: (Integer) Build timeout in seconds.
* `cifmw_build_containers_dockerfile_labels`: (List) Add labels to the containers. Default to `[]`.
* `cifmw_build_containers_volume_mounts:`: (List) Container bind mounts used when building the image. Default to `['/usr/share/tcib/container-images:/usr/share/tcib/container-images:z']`.
* `cifmw_build_containers_extra_config`: (List) TCIB extra variables you want to pass.
* `cifmw_build_containers_repo_dir`: (String) Define a custom directory containing the repo files.
* `cifmw_build_containers_image_tag`: (String) Image tag suffix. Default to `current-podified`.
* `cifmw_build_containers_containers_base_image`: (String) Base image name, with optional version. Can be 'centos:8', base name image will be 'centos' but 'centos:8' will be pulled to build the base image. Default to `centos:stream9`.
