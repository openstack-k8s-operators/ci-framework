# config_drive
Role to build a `NoCloud` config-drive ISO image.

## Privilege escalation
Required to installed required packages.

## Parameters
* `cifmw_config_drive_basedir`: (String) Base directory. Defaults to `{{ cifmw_basedir }}` which defaults to `~/ci-framework-data`.
* `cifmw_config_drive_workdir`: (String) Working directory. Defaults to: `{{ cifmw_config_drive_basedir }}/cifmw_config_drive`
* `cifmw_config_drive_instancedir`: (String) Per-instance working directory. Defaults to: `{{ cifmw_config_drive_workdir }}/{{ cifmw_config_drive_uuid }}`
* `cifmw_config_drive_iso_image`: (String) Path to built ISO image. Defaults to: `{{ cifmw_config_drive_workdir }}/{{ cifmw_config_drive_uuid }}.iso`
* `cifmw_config_drive_uuid`: (String) Instance UUID. Defaults to `uuid-test`.
* `cifmw_config_drive_name`: (String) Instance Name. Defaults to `test`.
* `cifmw_config_drive_hostname`: (String) Instance hostname. Defaults to `test.example.com`.
* `cifmw_config_drive_userdata`: (Dict) cloud-init user-data, in cloud-config-data format. Defaults to `none`.
* `cifmw_config_drive_networkconfig`: (Dict) cloud-init network-config. Defaults to `none`.

## Examples

```
- name: Build config-drive image playbook
  hosts: "{{ cifmw_target_host | default('localhost') }}"
  tasks:
    - name: Include config_drive role
      vars:
        cifmw_config_drive_uuid: de2f369a-1886-4a90-8e50-e419289e6850
        cifmw_config_drive_name: test01
        cifmw_config_drive_hostname: test01.example.com
        cifmw_config_drive_userdata:
          ssh_authorized_keys:
            - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCg1LHRahLiT1NFv4l/XH
          packages:
            - git
            - bind-utils
          write_files:
            - path: /root/test.file
              owner: root:root
              content: |
                # Test file content
          runcmd:
            - [ 'sh', '-c', 'echo foo | tee -a /tmp/foo' ]
        cifmw_config_drive_networkconfig:
          network:
            version: 2
            ethernets:
              id0:
                match:
                  macaddress: "aa:bb:cc:dd:ee:ff"
                addresses:
                  - 192.168.0.101/24
                routes:
                  - to: 0.0.0.0/0
                    via: 192.168.0.1
                    on-link: true
                nameservers:
                  addresses:
                    - 192.168.0.1
      ansible.builtin.include_role:
        name: config_drive
```
