# Frequently Asked Questions

## General questions

### Where can I see the ansible logs?

On the machine from where you launched the `ansible-playbook` command, you
can access `~/ansible.log`.

### How can I see the deployed libvirt resources?

On the hypervisor, you can check the deployed resources using `virsh` command, for instance:

Check on deployed virtual machines
```Bash
$ virsh -c qemu:///system list --all
```

Check on deployed virtual networks
```Bash
$ virsh -c qemu:///system net-list --all
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

Cause: there are multiple causes, but usually its because NTP can't be properly configured. This usually happens when running in a network
without access to public NTP servers.

Solution: ensure you're passing the following parameter to your deploy:

```YAML
cifmw_install_yamls_vars:
  DATAPLANE_NTP_SERVER: <your selected NTP server>
```

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

Cause: there's currently a conflict between the `default` network created by libvirt during its first startup, and the `osp_trunk` network
we create within the CI Framework: they are both consuming the same range, `192.168.122.0/24`. This is mostly due to hard-coded values in the
product, not the Framework. We're working on getting rid of them.

Solution: connect to the hypervisor, and issue this command:

```Bash
$ virsh -c qemu:///system net-destroy default
```

This will stop the network (while keeping it available for later use). You then want to start the `osp_trunk` network, else you'll hit another issue
during the next run (see [below](#network-cifmw-osp-trunk-is-not-active)):


```Bash
$ virsh -c qemu://system net-start cifmw-osp_trunk
```

#### network 'cifmw-osp_trunk' is not active

The error is shown as follow:

```
An exception occurred during task execution. To see the full traceback, use -vvv.
The error was: libvirt.libvirtError: Requested operation is not valid: network
'cifmw-osp_trunk' is not active
```

Cause: the `cifmw-osp_trunk` virtual network didn't start properly. This usually happen
because a previous run hit another issue (see [above](#internal-error-network-is-already-in-use-by-interface-virbr0)).

Solution: either clean the deployment, or connect to the hypervisor, and run the following command:

```Bash
$ virsh -c qemu:///system net-start cifmw-osp_trunk
```
and re-start the deployment.


### How can I clean the deployed layout?

There are two ways of cleaning up the layout.

#### Light cleanup

This one will remove the running resources, mostly:

- running VM which name start with `cifmw-`
- running networks which name start with `cifmw-`

It's probably the most used, since it allows a faster re-deploy later.

```Bash
$ ansible-playbook [-i inventory.yml] \
    [-e cifmw_target_host=HYPERVISOR] \
    reproducer-clean.yml
```

#### Deep cleaning

This one will remove all of the running resources, but also remove all of the
dev-scripts related resources such as repository, OCP resources and so on.


```Bash
$ ansible-playbook [-i inventory.yml] \
    [-e cifmw_target_host=HYPERVISOR] \
    reproducer-clean.yml \
    --tags deepscrub
```

## Lightweight layout


## Validated Architecture layout

### Where can I check for dev-scripts logs?
You can connect to your hypervisor using the non-root user you defined, and check for
the logs in `~/src/github.com/openshift-metal3/dev-scripts/logs` directory.
