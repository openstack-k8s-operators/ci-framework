## Role: artifacts
This role allow to gather data from the environment. It will then output files
in the defined base directory.

### Privilege escalation
None - writes happen only in the user home.

### Parameters
* `cifmw_artifacts_basedir`: Base directory. Defaults to `cifmw_basedir` which
defaults to `~/ci-framework`.

### Usage
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
    - name: Do some other tasks:
      block:
        - name: Taks 1
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
