# validations
The Validations role provides a framework for performing state verification.
This is useful for QE purposes and will be leveraged post-deployment to assert
that required conditions have been satisfied. For example, if I update a certain
value in my `OpenStackDataPlaneNodeSet`. I want to validate that the change has
been applied as per my expectations on the relevant OpenStack Compute nodes.

## Privilege escalation
Privilege escalation will be dependent on the specific job being executed. Some jobs
may require privilege escalation. Check with the individual jobs to determine
requirements.

## Parameters
The parameters will ultimately depend on what is implemented in each validation task.
But in order to launch this role, at a minimum the following should be defined:

- `cifmw_validations_list`: (List) List of validation jobs to run. Found under `roles/validations/tasks/*`
- `cifmw_validations_run_all`: (Bool) Defaults to false
- `cifmw_validations_default_path`: (String) Defaults to `"{{ role_path }}/tasks"`

## Examples
The following variables would be used to trigger the EDPM job for Huge Pages:
```yaml
  vars:
    cifmw_execute_validations: true
    cifmw_validations_list:
      - edpm/hugepages_and_reboot.yml
    cifmw_validations_edpm_check_node: 192.168.122.100
```
