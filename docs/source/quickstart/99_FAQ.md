# Frequently Asked Questions

## local_env_create known issues

### Could not connect to libvirt
This is because your user wasn't in the `libvirt` group. While the `libvirt_manager` role adds you to it,
the playbook doesn't reload your environment, mostly because we're using the `local` connection.

In order to solve this issue, please logout and re-login your account.

### Spice graphics are not supported with this QEMU
This graphic driver/feature isn't supported on CentOS Stream 9. In case you would like to use it with Fedora,
the following to the initial `make` command:
```Bash
make local_env_create LOCAL_ENV_OPTS="-K -e cifmw_local_env_vm_graphics=spice"
```

In case you do not need graphics at all `-e cifmw_local_env_vm_graphics=none` - it will instruct virsh to start the VM
without any graphics. This will NOT prevent `virsh -c qemu:///system console` accesses.

### Debug control plane deployment failures
If the control plane deployment fails or timeout, you can try debug the failure with the command
outputs below:

To check the virtual machines that are running/active:

```Bash
$ virsh -c qemu:///system list
 Id   Name             State
--------------------------------
 1    crc              running
 2    edpm-compute-0   running
```

If the control plane deployment fails, you will likely see the crc node active but
the edpm-compute not visible.

Next, check which openstack services and/or operators might have failed to deploy:

```Bash
$ oc get pods -n openstack
$ oc get pods -n openstack-operators
```

For example, if the cinder-api service failed, you might see:

```Bash
$ oc get pods -n openstack

ceilometer-central-5b4d7f8887-4jgvg    3/3     Running   0             25m
ceph                                   1/1     Running   0             38m
cinder-api-7dfb87d7cc-l4ldp           0/1     CrashLoopBackOff   6 (71s ago)     5m58s
dnsmasq-dns-76f9584644-8246v           1/1     Running   0             23m
...
```

You can review the logs to see the error with:

```Bash
oc logs -n openstack -l component=cinder-api
```
