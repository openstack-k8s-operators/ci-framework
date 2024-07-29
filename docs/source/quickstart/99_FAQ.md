# Frequently Asked Questions

## General questions

### Where can I see the ansible logs?

On the machine from where you launched the `ansible-playbook` command, you
can access `~/ansible.log`.

### What's the root password on the virtual machines?

By default, the very secure `fooBar` password is set for all of the created machines. You can
override it from within the [layout description](../roles/libvirt_manager.md#structure-for-cifmw-libvirt-manager-configuration)

### How can I see the deployed libvirt resources?

On the hypervisor, you can check the deployed resources using `virsh` command, for instance:

Check on deployed virtual machines
```Bash
[hypervisor]$ virsh -c qemu:///system list --all
```

Check on deployed virtual networks
```Bash
[hypervisor]$ virsh -c qemu:///system net-list --all
```

Please refer to the `virsh` manpage for more commands.

### My deployment fails with...

#### timed out waiting for the condition on openstackdataplanenodesets/openstack-edpm

The error is shown as follow:

```
TASK [edpm_deploy : Wait for OpenStackDataPlaneNodeSet to be deployed _raw_params=oc wait OpenStackDataPlaneNodeSet {{ cr_name }} --namespace={{ cifmw_install_yamls_defaults['NAMESPACE'] }} --for=condition=ready --timeout={{ cifmw_edpm_deploy_timeout }}m] ***
Wednesday 25 October 2023  13:20:26 +0300 (0:00:00.657)       0:27:44.152 *****
fatal: [localhost]: FAILED! => {
  "changed": true,
  "cmd": [
    "oc", "wait", "OpenStackDataPlaneNodeSet", "openstack-edpm", "--namespace=openstack", "--for=condition=ready", "--timeout=40m"
  ],
  "delta": "0:40:00.116342",
  "end": "2023-10-25 14:00:26.634070",
  "msg": "non-zero return code",
  "rc": 1,
  "start": "2023-10-25 13:20:26.517728",
  "stderr": "error: timed out waiting for the condition on openstackdataplanenodesets/openstack-edpm",
  "stderr_lines": ["error: timed out waiting for the condition on openstackdataplanenodesets/openstack-edpm"],
  "stdout": "",
  "stdout_lines": []
}
```

~~~{admonition} Cause
:class: error
There are multiple causes, but usually its because NTP can't be properly configured. This usually happens when running in a network
without access to public NTP servers.
~~~

~~~{admonition} Solution
:class: tip
Ensure you're passing the following parameter to your deploy:

```{code-block} YAML
:caption: custom/ntp-server.yml
:linenos:
cifmw_install_yamls_vars:
  DATAPLANE_NTP_SERVER: <your selected NTP server>
```
~~~

#### internal error: Network is already in use by interface virbr0

The error is shown as follow:

```
TASK [libvirt_manager : Ensure networks are created/started command=create, name=cifmw-{{ item.key }}, uri=qemu:///system] ***********************
Tuesday 14 November 2023  13:07:50 -0600 (0:00:01.938)       0:53:45.117 ******
failed: [hypervisor] (item=osp_trunk) => {
  "ansible_loop_var": "item",
  "changed": false,
  "item": {
    "key": "osp_trunk",
    "value": "<network>\n  <name>osp_trunk</name>\n  <forward mode=\"nat\" />\n  <bridge name='osp_trunk' stp='on' delay='0' />\n  <mtu size=\"9000\"/>\n  <ip address='192.168.122.1' netmask='255.255.255.0' />\n</network>"
  },
  "msg": "internal error: Network is already in use by interface virbr0"
}
```

~~~{admonition} Cause
:class: error
There's currently a conflict between the `default` network created by libvirt during its first startup, and the `osp_trunk` network
we create within the CI Framework: they are both consuming the same range, `192.168.122.0/24`. This is mostly due to hard-coded values in the
product, not the Framework. We're working on getting rid of them.
~~~

~~~{admonition} Solution
:class: tip
Connect to the hypervisor, and issue this command:

```Bash
[hypervisor]$ virsh -c qemu:///system net-destroy default
```
~~~

This will stop the network (while keeping it available for later use). You then want to start the `osp_trunk` network, else you'll hit another issue
during the next run (see [below](#network-cifmw-osp-trunk-is-not-active)):


```Bash
[hypervisor]$ virsh -c qemu:///system net-start cifmw-osp_trunk
```

#### network 'cifmw-osp_trunk' is not active

The error is shown as follow:

```
An exception occurred during task execution. To see the full traceback, use -vvv.
The error was: libvirt.libvirtError: Requested operation is not valid: network
'cifmw-osp_trunk' is not active
```

~~~{admonition} Cause
:class: error
The `cifmw-osp_trunk` virtual network didn't start properly. This usually happens
because a previous run hit another issue (see [above](#internal-error-network-is-already-in-use-by-interface-virbr0)).
~~~

~~~{admonition} Solution
Either clean the deployment, or connect to the hypervisor, and run the following command:

```Bash
[hypervisor]$ virsh -c qemu:///system net-start cifmw-osp_trunk
```
and re-start the deployment.
~~~


### How can I clean the deployed layout?

There are two ways of cleaning up the layout.

#### Light cleanup

This one will remove the running resources, mostly:

- running VM which name start with `cifmw-`
- running networks which name start with `cifmw-`

It's probably the most used, since it allows a faster re-deploy later.

```Bash
[laptop]$ ansible-playbook [-i custom/inventory.yml] \
    [-e cifmw_target_host=hypervisor-1] \
    reproducer-clean.yml
```

#### Deep cleaning

This one will remove all of the running resources, but also remove all of the
dev-scripts related resources such as repository, OCP resources and so on.


```Bash
[laptop]$ ansible-playbook [-i custom/inventory.yml] \
    [-e cifmw_target_host=hypervisor-1] \
    reproducer-clean.yml \
    --tags deepscrub
```

~~~{tip}
`hypervisor-1` is the name we use in the example inventories through the documentation.
Please be sure to pass the proper inventory hostname.
~~~

### How can I reauthenticate?

After my deployment has been running for a few days I'm unable to access k8s from the controller and I see the following error message. What do I do?
```
[zuul@controller-0 ~]$ oc get pods
E0729 08:58:18.781204   67525 memcache.go:265] couldn't get current server API group list: the server has asked for the client to provide credentials
E0729 08:58:18.805259   67525 memcache.go:265] couldn't get current server API group list: the server has asked for the client to provide credentials
E0729 08:58:18.829791   67525 memcache.go:265] couldn't get current server API group list: the server has asked for the client to provide credentials
E0729 08:58:18.848560   67525 memcache.go:265] couldn't get current server API group list: the server has asked for the client to provide credentials
E0729 08:58:18.866136   67525 memcache.go:265] couldn't get current server API group list: the server has asked for the client to provide credentials
error: You must be logged in to the server (the server has asked for the client to provide credentials)
[zuul@controller-0 ~]$
```
After running the following you should be able to authenticate.
```
export PASS=$(cat ~/.kube/kubeadmin-password)
oc login -u kubeadmin -p $PASS https://api.ocp.openstack.lab:6443
```
