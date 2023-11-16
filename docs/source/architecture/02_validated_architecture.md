# Validated Architecture

This layout involves a lot more resources than the lightweight one.
The schema bellow will help understanding the networking and communications

## Layout overview

The following schema will help understanding the validated architecture layout:

```
._____________________________________.
|          Hypervisor                 |
|                                     |
|  [controller-0]                     |
|      | |                            |
|      | '---------------------.      |
|      '-----------------.     |      |
|                  osp_trunk   |      |
|  [ compute-0/1/2 ]     |   ocpbm    |
|      | |               |     |      |
|      | '---------------|     |------|--{Internet, external resources}
|      '-----------------|-----|      |
|                        |     |      |
|  [ ocp-0/1/2 ]         |     |      |
|     |  |   |           |     |      |
|     |  |   |           |     |      |
|     |  |   '-----------'     |      |
|     |  '---------------------'      |
|     '------ ocppr                   |
|_____________________________________|

```

### Networks description

- `osp_trunk` is the "usual" private network that will be used to deploy with network isolation (vlans).
- `ocpbm` is a dev-scripts managed network. We "piggy-back" on it since it provides the needed public access.
- `ocppr` is a dev-scripts managed network. It's used in order to provision the OCP cluster from a temporary machine,
  or provision computes when no OS is present.

## Images and overlays

The layout is consuming two kind of resources for the VMs: base images, being the original QCOW2 disk images, and overlays.

When you run the playbook, it will fetch the base image from the location you set in the variable file (by default CentOS mirrors)
for the controller and computes, bootstrap the OCP cluster, and stop it once it's ready.

Then, it will create image overlays based on the base image as well as from the generated OCP images. That way,
a second deployment will be far, far quicker, allowing you to iterate over and over.

Of course, in the best possible world, you shouldn't need to redeploy the infra in order to iterate developments, but having
this possibility is a real help, especially when times come to start over a fresh, clean environment.
