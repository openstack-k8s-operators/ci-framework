# Environment reproducers general considerations
## Tested environment
This reproducer has been successfully tested on a CentOS Stream 9 hypervisor
running latest CRC qcow2, and latest CentOS Stream 9 qcow2 images.

It also works on RHEL based hypervisor and VMs, provided you give the correct
information for the [discover_latest_image](../roles/discover_latest_image.md)
role/plugin, or download beforehand the images and consume them from within the
configuration, but this will **not** be covered in this documentation.

## Custom extra variables files
You can push your custom variables files in the `custom` directory available
at the root of the `ci-framework` git repository. Its content is ignored via the
provided `.gitignore` file.

## Prerequisites
### CRC
You have to get a working [pull-secret](https://console.redhat.com/openshift/create/local) and
pass it to the deployment using a custom parameter file, for instance:

~~~{code-block} YAML
:caption: custom/private-params.yml
:linenos:
cifmw_manage_secrets_pullsecret_file: "{{ lookup('env', 'HOME') }}/pull-secret.txt"
~~~

### Ssh authorized_keys
On the target hypervisor, you have to ensure the ~/.ssh/authorized_keys has all
of the needed public keys. It will then be copied in the various virtual machines
the reproducer will create.

## Needed parameters
While we provide the "simple" layout, consuming three nodes, you may want
to provide your own layout, maybe with more compute, or some other kind of
node.

In any cases, the following data is the bare minimal:

- `cifmw_path`: you can take the same value as in the provided file, or extend it as needed
- `cifmw_libvirt_manager_configuration`: this dict is mandatory in order to create the layout.

In the `cifmw_libvirt_manager_configuration`, there are also some conventions
and mandatory content/information.

In the `vms` section, please ensure you have at least "controller" and "crc".
Those names are fixed and used later as static reference.

In the `networks` section, you can define your own custom networks. Usually,
you can take the same values we provide in the existing layout.

Note that, if you just want to get more compute, you can play with the `amount`
value. It will then create `compute-[0..n]` virtual machines.

Usually, you can pass the provided `scenarios/reproducers/3-nodes.yml` environment.
