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

## Parameters

* `cifmw_setup_validate_public_endpoints` (bool) Before the tests of `run_tests.yml`, run the
  `public_endpoints_validate.yml` hook: every public endpoint of the Keystone catalog (plus
  Horizon and the `noVNC` proxy when enabled) must be served by a Route or a `LoadBalancer`
  Service (a custom `endpointURL` of the control plane CR must be a `LoadBalancer`), and must
  be reachable with a valid certificate from the node running the hook. Only runs when `cifmw_run_tests` is true. Defaults to `true`.
