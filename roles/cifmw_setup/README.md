# cifmw_setup

Generic role to contain various cifmw setup-related tasks.

**NOTE:** Refrain from adding tasks that could have their own dedicated role.

## Example

Since this role does not contain `main.yml`, you must use `tasks_from` to select the specific task you want to run.

```YAML
- name: Run cifmw_setup admin_setup.yml
  ansible.builtin.import_role:
    name: cifmw_setup
    tasks_from: admin_setup.yml
  tags:
    - admin-setup
```
