# Frequently Asked Questions

## local_env_create known issues

### Could not connect to libvirt
This is because your user wasn't in the `libvirt` group. While the `libvirt_manager` role adds you to it,
the playbook doesn't reload your environment, mostly because we're using the `local` connection.

In order to solve this issue, please logout and re-login your account.

### Spice graphics are not supported with this QEMU
This graphic driver/feature isn't supported on CentOS Stream 9. In order to work around this issue, please pass
the following to the initial `make` command:
```Bash
make local_env_create LOCAL_ENV_OPTS="-K -e cifmw_local_env_vm_graphics=none"
```

The important part here is the `-e cifmw_local_env_vm_graphics=none` - it will instruct virsh to start the VM
without any graphics. This will NOT prevent `virsh -c qemu:///system console` accesses.
