# env_op_images
A role to gather the container images used in the openstack deployment with specific tags.

## Parameters
* `cifmw_env_op_images_dir`: (String) Directory where the operator_images.yaml will be stored. Defaults to `~/ci-framework-data/artifacts`
* `cifmw_env_op_images_file`: (String) Name of the file storing the operator images and tags. Defaults to `operator_images.yaml`

## Examples
```YAML
- name: Collect container images used in the environment
  ansible.builtin.import_role:
    name: env_op_images
```
