# discover_latest_image

An Ansible role to discover latest Centos image.

## Requirements

This role is currently written for Centos.

## Role Variables

* `cifmw_discover_latest_image_base_url`: (String) Base Url from where we can pull the Centos Image. Defaults to `<https://cloud.centos.org/centos/{{ ansible_distribution_major_version }}-stream/x86_64/images/.`
* `cifmw_discover_latest_image_qcow_prefix`: (String) Qcow2 image prefix on base_url which will be used as a filter to find latest Centos Image. Defaults to `CentOS-Stream-GenericCloud-`.


## Examples

### 1. Sample playbook to call the role
```YAML
- name: Discover latest CentOS qcow2 image
    include_role:
    name: discover-latest-image
```
