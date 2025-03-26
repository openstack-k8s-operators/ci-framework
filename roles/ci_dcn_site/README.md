# ci_dcn_site

Deploys DCN sites for testing. Each DCN site is a new EDPM nodeset
with a collocated Ceph cluster.

## Privilege escalation

- Applies CRDs in openstack namespace
- Runs openstack client commands to create aggregates and discover new
  compute hosts

## Parameters

* `_az`: The name of the availability zone for the AZ, e.g. `az1`
* `_az_to_scaledown`: The name of the availability zone for the deployed AZ to be scaled down.
* `_group_name`: The name of the group of nodes to be deployed, e.g. `dcn1-computes`
* `_subnet`: The name of the subnet the DCN site will use, e.g. `subnet2`
* `_subnet_network_range`: The range of the subnet the DCN site will use, e.g. `192.168.133.0/24`
* `_node_to_remove`: The hostname of the node to be removed from the DCN deployment.
* `_node_to_add`: The hostname of the node to be added to the specified AZ.

## Examples

To deploy two nodesets named dcn1-computes and dcn2-computes,
the role may be called like this.
```yaml
- name: Deploy
  include_role: ci_dcn_site
  with_items: "{{ groups | dict2items | selectattr('key', 'search', 'compute') | list }}"
  loop_control:
    index_var: idx
    loop_var: item
  vars:
    _subnet: "subnet{{ idx + 1 }}"
    _group_name: "{{ item.key }}"
    _az: "az{{ idx }}"
    _subnet_network_range: "{{ _network_ranges[idx] }}"
```
The above assumes the following values for each iteration:
```
_subnet: subnet2 | _group_name: dcn1-computes | _az: az1 | _subnet_network_range: 192.168.133.0/24
_subnet: subnet3 | _group_name: dcn2-computes | _az: az2 | _subnet_network_range: 192.168.144.0/24
```
It relies on the `ci-framework-data/artifacts/zuul_inventory.yml` which the
ci-framework will populate correctly when the `dt-dcn.yml` scenario is used.
The variables above can then be built with the following tasks before
the above is run.
```yaml
  - name: Load reproducer-variables
    ansible.builtin.include_vars:
      file: "~/reproducer-variables.yml"

  - name: Load networking-environment-definition
    ansible.builtin.include_vars:
      file: "/etc/ci/env/networking-environment-definition.yml"
      name: cifmw_networking_env_definition

  - name: Create a network subnet list
    ansible.builtin.set_fact:
      _network_ranges: >-
        {{
          cifmw_networking_env_definition.networks
          | dict2items
          | selectattr('key', 'search', '^ctlplane')
          | map(attribute='value.network_v4')
          | list
        }}
```

## Integration with Architecture Repository

The directions in the
[DCN DT](https://github.com/openstack-k8s-operators/architecture/tree/main/examples/dt/dcn)
end with deploying the first Availability Zone (AZ) called `az0`.
Additional AZs may be deployed for testing by calling this role.

The DCN DT contains values yaml files which may be passed to
kustomize. This role generates additional instances of the same
type of values files from jinja templates. The templates are populated
with the values in the environment which are set when the `dt-dcn.yml`
scenario is used. The role then calls kustomize to apply the CRDs.

The role is executed by the dcn.yml playbook found in the playbooks
directory. This same playbook is called by the automation structure
in the DCN DT (`automation/vars/dcn.yaml`) by using a
`post_stage_run`.

## Maintainers

This role is maintained by the following

- https://github.com/sbekkerm
- https://github.com/krcmarik
- https://github.com/fultonj
