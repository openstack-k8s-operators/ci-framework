# local_env_vm
This role bootstrap a VM on your host, and makes it ready for the ci-framework
usage directly on it.

Running in a VM might be slow, so you want to get proper hardware (especially
regarding to the I/O performances) - please note it's using nested virtualization
in the end (CRC + Compute VMs will be running from within the virtual machine
this role creates).

## Privilege escalation
None.

## Parameters
* `cifmw_local_env_vm_basedir`: (String) Base directory. Defaults to `{{ cifmw_basedir | default(ansible_user_dir ~ '/ci-framework-data') }}`.
* `cifmw_local_env_vm_pullsecret`: (String) Location of the pull-secret file. Defaults to `{{ ansible_user_dir }}/pull-secret`.
* `cifmw_local_env_vm_space`: (String) Disk space allocated to the VM. Defaults to `120G`.
* `cifmw_local_env_vm_memory`: (Integer) Allocated memory. Defaults to `22572`.
* `cifmw_local_env_vm_cpu`: (Integer) Allocated CPU. Defaults to `6`.
* `cifmw_local_env_vm_root_passwd`: (String) Root password on the virtual machine. Defaults to `fooBar`.
* `cifmw_local_env_vm_network`: (String) Virtual network used by the VM. Defaults to `network=default`.
* `cifmw_local_env_vm_graphics`: (String) Graphic mode. Please refer to the `--graphics` accepted values. Defaults to `spice`.
