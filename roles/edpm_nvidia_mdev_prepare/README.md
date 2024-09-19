# edpm_nvidia_mdev_prepare

This Ansible role prepares an EDPM node by configuring it for nvidia mediated
devices usage by installing from an external location a RPM package containing
the nvidia driver.

## Privilege escalation
`become` will be set to True during the phase1 task in order to blacklist
the nouveau driver, regenerate the initramfs and then install the nvidia RPM
package. During phase2, we'll also create system files.

## Parameters

* `cifmw_edpm_nvidia_mdev_prepare_disable_nouveau`: (boolean) Whether to disable the `nouveau` kernel driver. Default: `true`.

* `cifmw_edpm_nvidia_mdev_prepare_driver_url`: (string) The location of the proprietary nvidia driver RPM package so that we can install it. Can be any URI supported by DNF.

* `cifmw_edpm_nvidia_mdev_prepare_package_name`: (string) The installed package name, which can't be inferred from the package name, usually set as `NVIDIA-vGPU-rhel`.

* `cifmw_edpm_nvidia_mdev_prepare_sriov_devices`: (list) List of PCI addresses corresponding to the nvidia physical SR-IOV GPUs that require virtual functions creation. Leave it defaulted to ALL if you want to enable SR-IOV VFs for all your nvidia GPUs.

# Should we start the service for automatically creating the VFs ?
* `cifmw_edpm_nvidia_mdev_prepare_sriov_manage_start`: (boolean) Whether you want the virtual functions to be created upon reboot. Default: `true`.
