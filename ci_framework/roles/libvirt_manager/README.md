## Role: libvirt_manager

Used for checking if:
    - there’s SVM/VMX virtualization, enable it if not
    - install libvirt packages and dependencies and add group and user to libvirt group if necessary,


### Privilege escalation

`become` - Required in:
    - `virsh_checks.yml`: For creating libvirt group if needed and also append user to this group if it's not there.
    - `virtualization_prerequisites.yml`: For enabling VMX/SVM module with modprobe.
    - `packages.yml`: Install all libvirt dependencies.
    - `polkit_rules.yml`: Add polkit rules under `/etc/`.

### Parameters
* `cifmw_libvirt_manager_enable_virtualization_module`: If `true` it will enable the virtualization module in case it's not already and if the hosts allow it. Default: `false`.
* `cifmw_libvirt_manager_user`: user used for libvirt. Default: the one in the environment variable `USER`.
