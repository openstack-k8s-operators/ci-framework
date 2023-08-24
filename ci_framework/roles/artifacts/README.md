# artifacts
This role allow to gather data from the environment. It will then output files
in the defined base directory.

## Privilege escalation
None - writes happen only in the user home.

## Parameters
* `cifmw_artifacts_basedir`: (String) Base directory. Defaults to `cifmw_basedir` which defaults to `~/ci-framework-data`.
* `cifmw_artifacts_crc_host`: (String) Hostname of the CRC instance. Defaults to `api.crc.testing`.
* `cifmw_artifacts_crc_user`: (String) Username to connect to the CRC instance. Defaults to `core`.
* `cifmw_artifacts_crc_sshkey`: (String) Path to the private SSH key to connect to CRC. Defaults to `~/.crc/machines/crc/id_ecdsa`.
* `cifmw_artifacts_gather_logs`: (Boolean) Force gathering of logs, even in the case of successful test run. Defaults to `false`

## Examples
Usually we'll import the role as-is at the very start of the playbook, and
import the tasks from `packages.yml` at the very end:
```YAML
---
- hosts: all
  gather_facts: false
  roles:
    - artifacts
    - (some other roles)
  tasks:
    - name: Do some other tasks
      block:
        - name: Tasks 1
          ansible.builtin.file:
            path: /tmp/foo
            state: present
        - (some other tasks)
      always:
        - name: Gather install packages
          ansible.builtin.import_role:
            name: artifacts
            tasks_from: packages.yml
```
