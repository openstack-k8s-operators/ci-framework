# run_hook
Run hooks during a playbook. Hooks may be in the form of a playbook, or a
plain CRD.

## Privilege escalation
None from the module, but a hooked playbook may require privilege escalation.
Note that, in such a case, the password prompt will be masked, and the overall
play has a great chance of failure.

## Parameters
* `hooks`: A list of hooks

## Hooks expected format
### Playbook
In such a case, the following data can be provided to the hook:
* `config_file`: (String) Ansible configuration file. Defaults to `ansible_config_file`.
* `creates`: (String) Refer to the `ansible.builtin.command` "creates" parameter. Defaults to `omit`.
* `inventory`: (String) Refer to the `--inventory` option for `ansible-playbook`. Defaults to `inventory_file`.
* `name`: (String) Describe the hook.
* `source`: (String) Source of the playbook. If it's a filename, the playbook is expected in `ci_framwork/hooks/playbooks`. It can be an absolute path.
* `type`: (String) Type of the hook. In this case, set it to `playbook`.
* `extra_vars`: (Dict) Structure listing the extra variables you want to pass down

#### Hook callback
A hook may generate new parameters that will be fed into the main play. In order
to do so, the hook playbook has to create a YAML file as follow:
```YAML
- name: Feed generated content to main play
  ansible.builtin.copy:
    dest: "{{ cifmw_basedir }}/artifacts/{{ step }}_{{ hook_name }}.yml"
    content: |
      foo: bar
      star: {{ my_favorit }}
```
The location and name are fixed. Both `cifmw_basedir`, `step` and `hook_name` are passed
down to the hook playbook. Note that the value of `cifmw_basedir` will default
to `~/ci-framework-data` if you don't pass it.

In the same way, hooks may be able to consume data from a previous hook by loading
the generated fil using `ansible.builtin.include_vars`, using the mentioned path.

Note that `step` is fixed in the main playbooks, and are following the name of
the various hook "timing" (`pre_infra`, `post_infra`, etc). The `hook_name` is
a cleaned version of the `name` parameter you pass down in the hook description.

#### Examples
```YAML
pre_deploy:
    - name: My hook
      source: ceph-deploy.yml
      type: playbook
      extra_vars:
        UUID: <some generated UUID>
```


### CRD
In such a case, the following data can be provided to the hook:
* `type`: (String) Type of the hook. In this case, set it to `crd`.
* `source`: (String) Source of the CRD. If it's a filename, the CRD is expected in `ci_framwork/hooks/crds`. It can be an absolute path.
* `host`: (String) Cluster API endpoint. Defaults to `https://api.crc.testing:6443`.
* `username`: (String) Username for authentication against the cluster. Defaults to `kubeadmin`.
* `password`: (String) Password for authentication against the cluster. Defaults to `12345678`.
* `state`: (String) State of the service. Can be `present` or `absent`. Defaults to `present`.
* `validate_certs`: (Boolean) Whether to validate or not the cluster certificates.
* `wait_condition`: (Dict) Wait condition for the service.

Note that the `wait_condition` must match the format used by the
`kubernetes.core.k8s` module. More information here:
https://docs.ansible.com/ansible/latest/collections/kubernetes/core/k8s_module.html
