# mirror_registry
This role can be used to deploy mirror-registry:
https://github.com/quay/mirror-registry

This is the tool used facilitate disconnected deployments of OpenShift.

## Privilege escalation
This role requires privilege escalation to facilitate the following two objectives:

- It escalates privileges to create a directory under /opt that will be used to store
  artefacts from the mirror-registry deployment; and,
- mirror-registry leverages podman, and podman volumes. It is necessary to run podman
  as root to create the podman volume for Quay and it's Database.

## Parameters
`cifmw_mirror_registry_basedir`: /opt/mirror-registry
`cifmw_mirror_registry_fqdn`: quay.openstack.lab
`cifmw_mirror_registry_release_version`: v1.3.10

## Examples
- host: localhost
  roles:
    - mirror-registry
  vars:
    cifmw_mirror_registry_basedir: /home/m3/basedir
    cifmw_mirror_registry_fqdn: quay.openstack.dev
    cifmw_mirror_registry_install_dir: /opt/mirror-registry
    cifmw_mirror_registry_release_version: v1.3.10
