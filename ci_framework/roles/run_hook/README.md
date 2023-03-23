## Role: run_hook
Run hooks during a playbook. Hooks may be in the form of a playbook, or a
plain CRD.

### Privilege escalation
None from the module, but a hooked playbook may require privilege escalation.
Note that, in such a case, the password prompt will be masked, and the overall
play has a great chance of failure.

### Parameters
* `hooks`: A list of hooks

### Hooks expected format
#### Playbook
In such a case, the following data can be provided to the hook:
* `type`: Type of the hook. In this case, set it to `playbook`.
* `source`: Source of the playbook. If it's a filename, the playbook is
expected in ci_framwork/hooks/playbooks. It can be an absolute path.
* `name`: Describe the hook.
* `inventory`: Refer to the `--inventory` option for `ansible-playbook`.
Defaults to `localhost,`.
* `connection`: Refer to the `--connection` option for `ansible-playbook`.
Defaults to `local`.

#### CRD
In such a case, the following data can be provided to the hook:
* `type`: Type of the hook. In this case, set it to `crd`.
* `source`: Source of the CRD. If it's a filename, the CRD is expected in
ci_framwork/hooks/crds. It can be an absolute path.
* `host`: Cluster API endpoint. Defaults to `https://api.crc.testing:6443`.
* `username`: Username for authentication against the cluster. Defaults to `kubeadmin`.
* `password`: Password for authentication against the cluster. Defaults to `12345678`.
* `state`: State of the service. Can be `present` or `absent`. Defaults to `present`.
* `validate_certs`: Whether to validate or not the cluster certificates.
* `wait_condition`: Wait condition for the service

Note that the `wait_condition` must match the format used by the
`kubernetes.core.k8s` module. More information here:
https://docs.ansible.com/ansible/latest/collections/kubernetes/core/k8s_module.html
