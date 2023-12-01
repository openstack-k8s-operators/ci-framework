# General considerations

## Overlays instead of images

The infrastructure is based on [image overlays](https://www.libvirt.org/kbase/backing_chains.html)
instead of actual base qcow2. This allows for a faster redeployment, and saves disk capacities.

It also allows to modify one base image, and get multiple VMs based on that single image - this is what
we're doing for the compute and controller: they share the same base image.

CRC, on the other hand, consumes an already deployed CRC image - same goes for the OCP cluster.

In that case, the first run will deploy the OpenShift service you want (CRC or dev-scripts based),
then stop the involved VM(s), undefine all the resources in libvirt, and create overlays.

That way, you're in a "deploy once, use many times", with the capacity to get a clean environment in a
matter of minutes instead of hours.

## No root access

The whole framework relies on a non-root user, either on your local laptop/desktop or on the remote
hypervisor. We leverage `sudo` and `become: true` when we need actual privileges.
