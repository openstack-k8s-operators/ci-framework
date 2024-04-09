# run_hook

Run hooks during a playbook. Hooks may be in the form of a playbook, or a
plain CRD.

## Privilege escalation

None from the module, but a hooked playbook may require privilege escalation.
Note that, in such a case, the password prompt will be masked, and the overall
play has a great chance of failure.

## Parameters

* `hooks`: A list of hooks
* `step`: (String) Prefix for the hooks you want to run. Mandatory.

## Hook sorting

The "name" is taken as a key to sort the various hooks in a selected step.

In case of "single hook in its own parameter", the `name` is computed from the parameter
name:

* `pre_infra_01_my_hook` will end as `01 my hook`
* `post_infra_my_hook` will end as `My hook`

## Hooks expected format

### Playbook

#### Single hook in its own parameter

* `config_file`: (String) Ansible configuration file. Defaults to `ansible_config_file`.
* `connection`: (String) Set the connection type for ansible. Defaults to `omit`.
* `creates`: (String) Refer to the `ansible.builtin.command` "creates" parameter. Defaults to `omit`.
* `inventory`: (String) Refer to the `--inventory` option for `ansible-playbook`. Defaults to `inventory_file`.
* `source`: (String) Source of the playbook. If it's a filename, the playbook is expected in `hooks/playbooks`. It can be an absolute path.
* `type`: (String) Type of the hook. In this case, set it to `playbook`.
* `extra_vars`: (Dict) Structure listing the extra variables you want to pass down

#### Multiple hooks in a list

* `config_file`: (String) Ansible configuration file. Defaults to `ansible_config_file`.
* `connection`: (String) Set the connection type for ansible. Defaults to `omit`.
* `creates`: (String) Refer to the `ansible.builtin.command` "creates" parameter. Defaults to `omit`.
* `inventory`: (String) Refer to the `--inventory` option for `ansible-playbook`. Defaults to `inventory_file`.
* `name`: (String) Describe the hook.
* `source`: (String) Source of the playbook. If it's a filename, the playbook is expected in `hooks/playbooks`. It can be an absolute path.
* `type`: (String) Type of the hook. In this case, set it to `playbook`.
* `extra_vars`: (Dict) Structure listing the extra variables you want to pass down

#### Hook callback

A hook may generate new parameters that will be fed into the main play. In order
to do so, the hook playbook has to create a YAML file as follows:

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

pre_infra_my_nice_hook:
    source: noop.yml
    type: playbook
```

### CR

#### Single hook

* `type`: (String) Type of the hook. In this case, set it to `cr`.
* `source`: (String) Source of the CR. If it's a filename, the CR is expected in `hooks/crs`. It can be an absolute path.
* `state`: (String) State of the service. Can be `absent | patched | present`. Defaults to `present`.
* `validate_certs`: (Boolean) Whether to validate or not the cluster certificates.
* `wait_condition`: (Dict) Wait condition for the service.
* `definition` (Dict) Mapping holding information or configuration of the k8s object.

#### Multiple hooks

Users can choose to pass a list of the above parameters.

Note that the `wait_condition` must match the format used by the
`kubernetes.core.k8s` module. More information here:
https://docs.ansible.com/ansible/latest/collections/kubernetes/core/k8s_module.html

OpenShift cluster is accessed using `cifmw_openshift_kubeconfig`.
