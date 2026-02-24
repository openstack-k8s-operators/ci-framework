# discover_latest_image

An Ansible role to discover latest Centos/RHEL image.

## Requirements

This role is currently written for Centos and RHEL.

## Role Variables

* `cifmw_discover_latest_image_base_url`: (String) Base Url from where we can pull the Centos Image. Defaults to `<https://cloud.centos.org/centos/{{ ansible_distribution_major_version }}-stream/x86_64/images/.`
* `cifmw_discover_latest_image_qcow_prefix`: (String) Qcow2 image prefix on base_url which will be used as a filter to find latest Centos Image. Defaults to `CentOS-Stream-GenericCloud-`.
* `cifmw_discover_latest_image_images_file`: (String) Name of the file that contain the images with the corresponding hash. Default: `CHECKSUM`. Check the `IMAGES_FILES` constant of the `discover_latest_image.py` plugin.
* `cifmw_discover_latest_image_requests`: (Dict) A collection of data used
to discover the latest images from several sources. See the section on
[discovering multiple images](#discovering-multiple-images). Default:
```
cifmw_discover_latest_image_requests:
  default:
    base_url: "{{ cifmw_discover_latest_image_base_url }}"
    qcow_prefix: "{{ cifmw_discover_latest_image_qcow_prefix }}"
    images_file: "{{ cifmw_discover_latest_image_images_file }}"
```
* `cifmw_discovered_images_dict`: (Dict) The collection of discovered images
found by this role. Default: `{}`

## Discovering Multiple Images

This role can discover multiple images from multiple separate sources when
provided the dict `cifmw_discover_latest_image_requests`. For multi-image
discovery to work properly, it is required that this dict has the following
schema:
```
cifmw_discover_latest_image_requests:
  some_name:
    base_url: ...
    qcow_prefix: ...
    images_file: ...
  some_other_name:
    base_url: ...
    qcow_prefix: ...
    images_file: ...
```
Each entry in the `requests` dict must have these 3 entries (`base_url`,
`qcow_prefix`, and `images_file`) set, and no additional entries. Assuming these
conditions are met, and an image can be discovered for each provided `base_url`,
`qcow_prefix`, and `images_file`, this role will set a fact called
`cifmw_discovered_images_dict` with all of the data from the discovered images.
Given the above requests dict, the resulting
`cifmw_discovered_images_dict` would be:
```
cifmw_discovered_images_dict:
  some_name:
    hash: ...
    hash_algorithm: ...
    image_name: ...
    image_url: ...
  some_other_name:
    hash: ...
    hash_algorithm: ...
    image_name: ...
    image_url: ...
```

The entries in the `cifmw_discovered_images_dict` will persist between calls to
this role, accumulating discovered images as this role is called. For example,
if this role is called once with the following requests dict:
```
cifmw_discover_latest_image_requests:
  rhel9:
    base_url: ...
    qcow_prefix: ...
    images_file: ...
```
and then separately called a second time with this requests dict:
```
cifmw_discover_latest_image_requests:
  rhel10:
    base_url: ...
    qcow_prefix: ...
    images_file: ...
```
the discovered images dict after these two calls would be:
```
cifmw_discovered_images_dict:
  rhel9:
    hash: ...
    hash_algorithm: ...
    image_name: ...
    image_url: ...
  rhel10:
    hash: ...
    hash_algorithm: ...
    image_name: ...
    image_url: ...
```

If this role is called once more with a requests dict that has an entry that
shares a name with an already-existing entry in the discovered images dict,
a new image will be discovered, and the old entry in the `discovered_images`
dict will be overwritten.

In the above example, if we were to call this role a
third time with a `cifmw_discovered_images_dict` that has a `rhel10` entry with
a different url/qcow prefix/images file from the previous call, then the
`rhel10` entry in the `cifmw_discovered_images_dict` would be overwritten with
the new data.

### The `default` image

If the `cifmw_discover_latest_image_requests` dict has an entry named
`default`, the `default` entry's discovered `hash`, `hash_algorithm`,
`image_name`, and `image_url` will be set as the `cifmw_discovered_hash`,
`cifmw_discovered_hash_algorithm`, `cifmw_discovered_image_name`, and
`cifmw_discovered_image_url` facts respectively.

It should be noted that the method of discovering a single image via the
`cifmw_discover_latest_image_[base_url,qcow_prefix,images_file]` variables
now works by putting those variables into the `default` entry of a single-entry
`cifmw_discover_latest_image_requests` dict (see the
`cifmw_discover_latest_image_requests` default value).
This means that in single-image mode, this role not only sets the
`cifmw_discovered_*` facts as expected, but also creates a
`cifmw_discovered_images_dict` dict with a single `default` entry.

## Examples

```YAML
- name: Discover latest CentOS qcow2 image
  ansible.builtin.include_role:
    name: discover-latest-image

- name: Output discovered data
  ansible.builtin.debug:
    msg: "{{ cifmw_discovered_image_name }} - {{ cifmw_discovered_image_url }}"
```
