# env_op_images
A role to gather the container images used in the openstack deployment with specific tags.

## Parameters
* `cifmw_env_op_images_dir`: (String) Directory where the operator_images.yaml will be stored. Defaults to `~/ci-framework-data/artifacts`
* `cifmw_env_op_images_file`: (String) Name of the file storing the operator images and tags. Defaults to `operator_images.yaml`
* `cifmw_env_op_images_pulled_report_path`: Pulled-images policy report (ICSP/IDMS + pod image refs).
* `cifmw_env_op_images_verified_report_path`: Output path for the CRI-O-enriched report. After the pulled report runs, fetches `oc adm node-logs NODE -u crio` per node, then writes this file with digest-level CRI-O fields (`node_verified_image_origin`, `log_evidence_uri`, `log_evidence_node`).
* `cifmw_env_op_images_crio_logs_dir`: Directory for per-node `*.crio.log` files used during verification.

## Examples
```YAML
- name: Collect container images used in the environment
  ansible.builtin.import_role:
    name: env_op_images
```
