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
