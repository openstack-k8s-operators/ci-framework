# Lightweight infrastructure

The lightweight infrastructures involves [CRC](https://crc.dev/crc/getting_started/getting_started/introducing/),
by default 2 other virtual machines, and 2 networks.

## Layout overview

The following schema will help understanding the lightweight layout:

```
.__________________________________________.
|              Hypervisor                  |
|                                          |
|  [controller-0]  [crc-0]  [compute-0]    |
|       |   |        |  |     |   |        |
|       |   '--------'--|-----'   |        |
|       |    osp_trunk  |         |        |
|       '---------------'---------'--------|---{Internet/external resources}
|             public                       |
|__________________________________________|
```

### Networks description

- `osp_trunk` is the "usual" private network that will be used to deploy with network isolation (vlans).
- `public` is bridged to the outside, allowing the installer to fetch the needed packages, operators and container images.

## Images and overlays

The layout is consuming two kind of resources for the VMs: base images, being the original QCOW2 disk images, and overlays.

When you run the playbook, it will fetch the base image from the location you set in the variable file (by default CentOS mirrors)
for the controller and computes, bootstrap the CRC service, and stop it once it's ready.

Then, it will create image overlays based on the base image as well as from the generated CRC image. That way,
a second deployment will be far, far quicker, allowing you to iterate over and over.

Of course, in the best possible world, you shouldn't need to redeploy the infra in order to iterate developments, but having
this possibility is a real help, especially when times come to start over a fresh, clean environment.
