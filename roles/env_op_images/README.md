# env_op_images

This role collects OpenStack operator image references from the ClusterServiceVersion and running pods into `operator_images.yaml`, builds a **pulled-images policy report** by combining ICSP/IDMS mirror rules with pod status image references, and enriches that report with digest-level **CRI-O pull evidence** from node journals (writing a separate verified YAML artifact).

All steps that talk to the cluster require `cifmw_openshift_kubeconfig` to be defined.

## Workflow

1. **Operator images artifact** — When OpenStack is installed (or when `cifmw_env_op_images_dryrun` is true), collects images from the OpenStack operator CSV/pods and writes `{{ cifmw_env_op_images_dir }}/artifacts/{{ cifmw_env_op_images_file }}`.
2. **Pulled-images report** (`tasks/pulled_images_report.yml`) — Policy-oriented view (not node-verified): loads `ImageContentSourcePolicy` and `ImageDigestMirrorSet` via `oc`, flattens mirror rules, lists pods in configured namespaces, and emits YAML with a `summary` plus per-container `images` rows (expected pull basis vs. ICSP/IDMS).
3. **CRI-O verification** (`tasks/verify_pulled_report_crio.yml`) — If the pulled report file exists, fetches CRI-O unit logs per node (`oc adm node-logs <node> -u crio --since=-24h`), saves them under `cifmw_env_op_images_crio_logs_dir`, then runs the `verify_pulled_report_crio` module to write the verified report. This include is non-fatal (`ignore_errors: true`) so a failure here does not abort the rest of the play.

## Parameters

* `cifmw_env_op_images_dir`: (String) Base directory for role outputs. Defaults to `{{ cifmw_basedir }}`. Under this path, `artifacts/` (and `logs/`) are created as needed.
* `cifmw_env_op_images_file`: (String) Filename for the operator images YAML under `artifacts/`. Defaults to `operator_images.yaml`.
* `cifmw_env_op_images_dryrun`: (Boolean) When true, image collection can run even if OpenStack is not reported Ready. Defaults to `false`.
* `cifmw_env_op_images_pulled_report_namespaces`: (List) Namespaces whose pods are scanned for the pulled report. Defaults to `{{ cifmw_openstack_namespace | default('openstack') }}` and `{{ operator_namespace | default('openstack-operators') }}`.
* `cifmw_env_op_images_pulled_report_path`: (String) Destination YAML for the pulled report: top-level `summary` (including embedded `mirror_rules` from ICSP/IDMS) and `images`. Defaults to `{{ cifmw_env_op_images_dir }}/artifacts/pulled_images_report.yaml`.
* `cifmw_env_op_images_verified_report_path`: (String) Output YAML after CRI-O enrichment (same structure as the pulled report, with extra fields on rows that could be matched). Defaults to `{{ cifmw_env_op_images_dir }}/artifacts/pulled_images_report_verified.yaml`.
* `cifmw_env_op_images_crio_logs_dir`: (String) Directory for per-node `*.crio.log` files produced before verification. Defaults to `{{ cifmw_env_op_images_dir }}/artifacts/crio_logs`.

### Pulled report (`cifmw_env_op_images_pulled_report_path`)

The pulled report prefix-matches each container’s **status `image` string** (from `containerStatuses` / `initContainerStatuses`) against ICSP/IDMS `source` values; it also records `image_id`, but `expected_pull_basis` / `expected_pull_location` come from the `image` string, not from `imageID`. The first matching rule sets `expected_pull_basis` to `mirror` and `expected_pull_location` to the mirror registry host; otherwise the row uses the image reference’s host and `source`. Pod status may still show the upstream registry name even when the runtime pulled via a mirror.

### Verified report (`cifmw_env_op_images_verified_report_path`)

Same document shape as the pulled report (`summary` + `images`). The `verify_pulled_report_crio` module parses CRI-O journal lines of the form `msg="Pulled image: …@sha256:…"` and, when a row’s digest matches it adds:

* `node_verified_image_origin` — `mirror` or `source` (mirror-rule hostnames vs. pull URI domain), or `cached/unknown` if no matching pull line.
* `log_evidence_uri` / `log_evidence_node` — registry/image URI and node where that pull appeared (may differ from the pod’s node if evidence is only on another node).

## Examples

```YAML
- name: Collect container images used in the environment
  ansible.builtin.import_role:
    name: env_op_images
```
