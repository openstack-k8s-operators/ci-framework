# discover_latest_image

An Ansible role to discover latest Centos/RHEL image.

## Requirements

This role is currently written for Centos and RHEL.

## Role Variables

* `cifmw_discover_latest_image_base_url`: (String) Base Url from where we can pull the Centos Image. Defaults to `<https://cloud.centos.org/centos/{{ ansible_distribution_major_version }}-stream/x86_64/images/.`
* `cifmw_discover_latest_image_qcow_prefix`: (String) Qcow2 image prefix on base_url which will be used as a filter to find latest Centos Image. Defaults to `CentOS-Stream-GenericCloud-`.
* `cifmw_discover_latest_image_images_file`: (String) Name of the file that contain the images with the corresponding hash. Default: `CHECKSUM`. Check the `IMAGES_FILES` constant of the `discover_latest_image.py` plugin.


## Examples

```YAML
- name: Discover latest CentOS qcow2 image
  ansible.builtin.include_role:
    name: discover-latest-image

- name: Output discovered data
  ansible.builtin.debug:
    msg: "{{ cifmw_discovered_image_name }} - {{ cifmw_discovered_image_url }}"
```
