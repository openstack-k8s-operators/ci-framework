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

## Lightweight vs Validated Architecture

The Lightweight layout, consuming CRC as an OpenShift provider, is mostly targeted for light CI and dev usage.
CRC doesn't have HA, since it's a single-node deployment, and has a lot of hacks embedded to make it work like that.

The Validated Architecture wants to be closer to an actual production infrastructure, allowing to test more features,
especially related to HA.

The OCP cluster as deployed by dev-scripts still presents some hacks, but they are really light compared to CRC. It's
a really good way to test the product against a "close to reality" infrastructure.
