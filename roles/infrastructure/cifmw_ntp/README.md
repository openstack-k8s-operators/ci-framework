# cifmw_ntp

This role allows to install and configure an NTP service (chrony) on an host.
It's a *heavily* stripped down version of the [timesync](https://github.com/linux-system-roles/timesync) role.
It shouldn't be used outside the cifmw scope because it only sets the NTP server/pool to use.

## Privilege escalation

Privilege escalation is needed to install packages,render the templates in /etc directory and deal with systemd services.

## Parameters
* `cifmw_ntp_servers` (list) List of NTP servers or pool of NTP servers. It defaults to `pool.ntp.org` if the (global) variable `cifmw_ntp_server` isn't defined.
* `cifmw_ntp_chrony_conf_file` (string) The path of the chrony configuration file. It defaults to `/etc/chrony.conf`.
* `cifmw_ntp_chrony_extra_conf_file` (string) The path of the custom configuration file for chrony. It defaults to `/etc/chrony-cifmw.conf`.

## Examples

```
- name: Configure chrony on controller-0
  hosts: controller-0
  vars:
    cifmw_ntp_server: "custom.ntp.server"
  roles:
    - role: "cifmw_ntp"
```
