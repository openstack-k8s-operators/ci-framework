# Deploy nodes with different discovered OS images

This page documents the reproducer workflow for nodes with different discovered
OS images than other nodes.

With the `discover_latest_image` role, it is possible to find the latest qcow2
OS images from multiple different URLs. With those discovered images, we can
then modify the Libvirt configuration to run different OS versions on different
nodes.

In the below example, we will modify a reproducer to run CentOS 10 on the
compute nodes, and CentOS 9 on a controller and a networker node.

## Request the discovery of multiple different images

Provide a `cifmw_discover_latest_image_requests` dict with the required fields
for multiple different image URLs to discover multiple different images. For
example:

```yaml
cifmw_discover_latest_image_requests:
  centos10:
    base_url: "https://cloud.centos.org/centos/10-stream/x86_64/images/"
    qcow_prefix: "CentOS-Stream-GenericCloud-x86_64-"
    images_file: CHECKSUM
  centos9:
    base_url: "https://cloud.centos.org/centos/9-stream/x86_64/images/"
    qcow_prefix: "CentOS-Stream-GenericCloud-x86_64-"
    images_file: CHECKSUM
```

## Update VM Image Sources In the Libvirt Config

Use one of the following patterns depending on how
`cifmw_libvirt_manager_configuration` is defined in your scenario.

### Direct configuration

If you wish to modify a `cifmw_libvirt_manager_configuration` directly, edit
the `image_url`, `sha256_image_name`, and `disk_file_name` fields in your
desired entries. For example:

```yaml
cifmw_libvirt_manager_configuration:
  vms:
    compute:
      image_url: "{{ cifmw_discovered_images_dict.centos10.image_url }}"
      sha256_image_name: "{{ cifmw_discovered_images_dict.centos10.hash }}"
      disk_file_name: "base-os-centos10.qcow2"
    controller:
      image_url: "{{ cifmw_discovered_images_dict.centos9.image_url }}"
      sha256_image_name: "{{ cifmw_discovered_images_dict.centos9.hash }}"
      disk_file_name: "base-os-centos9.qcow2"
    networker:
      image_url: "{{ cifmw_discovered_images_dict.centos9.image_url }}"
      sha256_image_name: "{{ cifmw_discovered_images_dict.centos9.hash }}"
      disk_file_name: "base-os-centos9.qcow2"
```
~~~{tip}
Be careful to supply different filenames to the `disk_file_name` field for
different VM types when you don't want them to use the same OS image. Failing
to do so will cause the different VM types to be created using the same OS
image.

When two different VM types are using the same base VM image, then they can
use the same `disk_file_name` to avoid downloading the same image multiple
times.
~~~

### Configuration sourced from external file

If the `cifmw_libvirt_manager_configuration` is sourced from an external file
and you wish to modify it to use separate images for separate VM types, use
`cifmw_libvirt_manager_configuration_patch_*` variables instead:

```yaml
cifmw_libvirt_manager_configuration_patch_01_compute_image:
  vms:
    compute:
      image_url: "{{ cifmw_discovered_images_dict.centos10.image_url }}"
      sha256_image_name: "{{ cifmw_discovered_images_dict.centos10.hash }}"
      disk_file_name: "base-os-centos10.qcow2"

cifmw_libvirt_manager_configuration_patch_02_controller_image:
  vms:
    controller:
      image_url: "{{ cifmw_discovered_images_dict.centos9.image_url }}"
      sha256_image_name: "{{ cifmw_discovered_images_dict.centos9.hash }}"
      disk_file_name: "base-os-centos9.qcow2"

cifmw_libvirt_manager_configuration_patch_03_networker_image:
  vms:
    networker:
      image_url: "{{ cifmw_discovered_images_dict.centos9.image_url }}"
      sha256_image_name: "{{ cifmw_discovered_images_dict.centos9.hash }}"
      disk_file_name: "base-os-centos9.qcow2"
```

The `libvirt_manager` role collects all
`cifmw_libvirt_manager_configuration_patch_*` variables, sorts them by variable
name, then merges them recursively on top of the base configuration.

## Run the reproducer

Run the reproducer, and once the virtual machines are up, validate that they
are running the appropriate operating systems. For example, run commands like:

```bash
ssh controller-0 "cat /etc/redhat-release"
ssh compute-0 "cat /etc/redhat-release"
ssh networker-0 "cat /etc/redhat-release"
```
