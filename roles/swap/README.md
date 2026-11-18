# swap

Creates and enables a swap file on the target host. Useful for CI hosts
where the combined memory of the CRC VM and an EDPM compute VM exceeds the
flavor size — idle pages are swapped out instead of OOM-killing qemu.

## Privilege escalation

The role runs with `become: true` — it creates a file under `/var`, runs
`mkswap`/`swapon`, and writes to `/etc/fstab`.

## Parameters

* `cifmw_swap_file`: (String) Path to the swap file. Defaults to `/var/swap_file`.
  `/var` is used instead of `/` because CRC images are RHEL CoreOS/bootc
  where `/` is read-only while `/var` is writable on both CoreOS and CentOS.
* `cifmw_swap_size`: (Integer) Size of the swap file in MiB. Defaults to `16384` (16 GiB).

## Examples

```yaml
- name: Enable swap on all hosts
  hosts: all
  tasks:
    - name: Configure swap
      ansible.builtin.include_role:
        name: swap
```

With a custom size:

```yaml
- hosts: crc_hosts
  vars:
    cifmw_swap_size: 8192
  roles:
    - swap
```
