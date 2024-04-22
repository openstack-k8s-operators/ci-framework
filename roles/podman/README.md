# podman

Install podman and enable sessions without login (linger).

## Privilege escalation

Requested to install packages.

## Parameters

* `cifmw_podman_packages`: (List) list of packages to install for Podman. Defaults to `[podman]`.
* `cifmw_podman_enable_linger`: (Bool) toggle session linger. Defaults to `true`.

## Examples

```YAML
- name: Configure podman
  vars:
    cifmw_podman_enable_linger: false
    cifmw_podman_packages:
      - podman
      - skopeo
  ansible.builtin.import_role:
    name: podman
```
