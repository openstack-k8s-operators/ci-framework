# deploy_loki

Ansible role that deploys the **Loki operator** (OLM Subscription / OperatorGroup) on OpenShift and creates an **S3-compatible secret** in the OpenStack namespace for CloudKitty / Loki integration. It can **optionally deploy MinIO first** via the **`deploy_minio`** role, or assume MinIO (or another S3 endpoint) is already present.

All variables owned by this role use the **`cifmw_deploy_loki_`** prefix. Namespace and S3-style credentials for the Loki secret are **`cifmw_deploy_loki_minio_*`**; when `deploy_minio` is included, namespace and the same values are passed as **`cifmw_deploy_minio_namespace`**, **`cifmw_deploy_minio_root_user`**, and **`cifmw_deploy_minio_root_password`**.

## Description

The role:

1. Optionally runs **`include_role: deploy_minio`** with **`cifmw_deploy_minio_namespace`**, **`cifmw_deploy_minio_root_user`**, and **`cifmw_deploy_minio_root_password`** set from **`cifmw_deploy_loki_minio_*`** (see **MinIO: bundled vs external** below).
2. Renders `templates/deploy_loki_for_ck.yaml.j2` (Loki operator CRs + S3 secret) to disk.
3. Applies that manifest with **`kubernetes.core.k8s`**.
4. Optionally waits until the **ClusterServiceVersion** for the Loki subscription reports phase **`Succeeded`** (when **`cifmw_deploy_loki_wait_for_csv`** is true).

If you should not run Loki at all, do **not** import this role—or use **`when:`** on **`import_role` / `include_role`** (see **Skipping the role** below). There is no in-role master toggle.

The S3 secret is created in **`cifmw_deploy_loki_openstack_namespace`** (default `openstack`) and uses:

- **`cifmw_deploy_loki_minio_access_key`** / **`cifmw_deploy_loki_minio_secret_key`**
- **`cifmw_deploy_loki_s3_bucket`**
- A fixed in-cluster endpoint pattern:
  **`http://minio.{{ cifmw_deploy_loki_minio_namespace }}.svc.cluster.local:9000`**

So the object store Service must be named **`minio`** in namespace **`cifmw_deploy_loki_minio_namespace`**, or the secret will not match your actual S3 endpoint (see **External MinIO**).

## Requirements

- Ansible collection **`kubernetes.core`**.
- Valid cluster credentials (same variables as `deploy_minio`; kubeconfig defaults to `~/.kube/config` if `cifmw_openshift_kubeconfig` is unset).
- For the CSV wait task: permissions to list **ClusterServiceVersion** in `cifmw_deploy_loki_operator_namespace`.

## Skipping the role

Calling **`import_role: deploy_loki`** or **`include_role: deploy_loki`** is the signal that you want this deployment. To make execution conditional, put **`when`** on that task (or omit the task). Example:

```yaml
- ansible.builtin.import_role:
    name: deploy_loki
  when: my_condition | default(false) | bool
```

## MinIO: bundled vs external

### A) Let `deploy_loki` deploy MinIO (default)

- Set **`cifmw_deploy_loki_deploy_minio: true`** (default).
- The role runs **`deploy_minio`** first with task **`vars`** mapping namespace and credentials (**`cifmw_deploy_loki_minio_access_key`** / **`secret_key`** → **`cifmw_deploy_minio_root_user`** / **`root_password`**), then renders and applies Loki manifests.

**Variable flow**

- Set **`cifmw_deploy_loki_minio_namespace`**, **`cifmw_deploy_loki_minio_access_key`**, and **`cifmw_deploy_loki_minio_secret_key`** (defaults in `defaults/main.yml`) or override them in inventory / extra-vars.
- The S3 secret template reads only **`cifmw_deploy_loki_minio_*`**.
- Other MinIO settings (image, PVC size, routes, …) still come from **`cifmw_deploy_minio_*`** defaults on **`deploy_minio`** unless you pass them into the included role (for example via play vars).

**Typical usage**

```yaml
- hosts: localhost
  gather_facts: true
  tasks:
    - ansible.builtin.import_role:
        name: deploy_loki
```

Override **`cifmw_deploy_loki_minio_*`** and **`cifmw_deploy_loki_*`** as needed. Override **`cifmw_deploy_minio_*`** when you need non-default MinIO image, storage class, etc.

### B) Pre-deployed MinIO (or you run `deploy_minio` separately)

- Set **`cifmw_deploy_loki_deploy_minio: false`** so `deploy_loki` does **not** call `include_role: deploy_minio`.
- Set **`cifmw_deploy_loki_minio_namespace`**, **`cifmw_deploy_loki_minio_access_key`**, and **`cifmw_deploy_loki_minio_secret_key`** so the S3 secret matches your running MinIO (plus **`cifmw_deploy_loki_s3_bucket`**).

**Endpoint expectation**

- The template always sets
  `endpoint: http://minio.<cifmw_deploy_loki_minio_namespace>.svc.cluster.local:9000`
  Your cluster must expose the S3 API as Service **`minio`** in that namespace on port **9000**. If your Service name or port differs, this role’s template would need to be extended (for example a dedicated `cifmw_deploy_loki_s3_endpoint` variable); today it is fixed to the in-cluster `minio` Service pattern.

### C) Hook playbook `hooks/playbooks/deploy-loki-for-ck.yaml`

This playbook:

1. Loads **`roles/deploy_loki/defaults/main.yml`** via **`vars_files`** so **`cifmw_deploy_loki_minio_*`** are defined before any role runs.
2. Runs **`import_role: deploy_minio`** with **`vars`** mapping namespace and MinIO root user/password from **`cifmw_deploy_loki_minio_*`**.
3. Runs **`import_role: deploy_loki`** with **`cifmw_deploy_loki_deploy_minio: false`** so MinIO is not applied a second time.

Customize namespace and keys by overriding **`cifmw_deploy_loki_minio_*`** at the play or inventory level (or by editing the role defaults).

## Role variables (`cifmw_deploy_loki_*`)

| Variable | Default | Description |
|----------|---------|-------------|
| `cifmw_deploy_loki_parent_dir` | `{{ ansible_user_dir }}/ci-framework-data` | Root for artifact paths; `group_vars/all.yml` sets this to `{{ cifmw_basedir }}` in framework plays. |
| `cifmw_deploy_loki_base_dir` | `{{ cifmw_deploy_loki_parent_dir }}` | Base directory containing `artifacts/manifests/`. |
| `cifmw_deploy_loki_deploy_minio` | `true` | When true, run `deploy_minio` before Loki. Set false when MinIO is deployed separately (including the CloudKitty hook). |
| `cifmw_deploy_loki_wait_for_csv` | `true` | When true, wait for Loki CSV phase `Succeeded`. Set false to skip the wait (for example in constrained CI). |
| `cifmw_deploy_loki_operator_namespace` | `openshift-operators-redhat` | Namespace for OperatorGroup / Subscription. |
| `cifmw_deploy_loki_subscription_channel` | `stable-6.4` | OLM channel for Loki. |
| `cifmw_deploy_loki_subscription_name` | `loki-operator` | Package / subscription name; also used to find the CSV by name substring. |
| `cifmw_deploy_loki_catalog_source` | `redhat-operators` | CatalogSource name. |
| `cifmw_deploy_loki_catalog_namespace` | `openshift-marketplace` | CatalogSource namespace. |
| `cifmw_deploy_loki_openstack_namespace` | `openstack` | Namespace for the S3 secret. |
| `cifmw_deploy_loki_s3_secret_name` | `cloudkitty-loki-s3` | Name of the S3 secret. |
| `cifmw_deploy_loki_s3_bucket` | `loki` | Bucket name in the secret. |
| `cifmw_deploy_loki_minio_namespace` | `minio-dev` | MinIO namespace (S3 endpoint URL and, when embedded, passed to `deploy_minio`). |
| `cifmw_deploy_loki_minio_access_key` | `minio` | S3 access key in secret; passed to `deploy_minio` when embedded. |
| `cifmw_deploy_loki_minio_secret_key` | `minio123` | S3 secret key in secret; passed to `deploy_minio` when embedded. |
| `cifmw_deploy_loki_csv_wait_retries` | `30` | Retries for CSV wait. |
| `cifmw_deploy_loki_csv_wait_delay` | `10` | Delay seconds between retries. |

## Usage examples

**Single role import (Loki + embedded MinIO)**

```yaml
- ansible.builtin.import_role:
    name: deploy_loki
```

**Loki only; MinIO already deployed**

```yaml
- ansible.builtin.import_role:
    name: deploy_loki
  vars:
    cifmw_deploy_loki_deploy_minio: false
    cifmw_deploy_loki_minio_namespace: my-minio-ns
    cifmw_deploy_loki_minio_access_key: "{{ vault_minio_key }}"
    cifmw_deploy_loki_minio_secret_key: "{{ vault_minio_secret }}"
```

**Match the hook pattern (MinIO role, then Loki without double MinIO)**

Ensure **`cifmw_deploy_loki_minio_*`** are set (defaults file or play vars), then:

```yaml
- ansible.builtin.import_role:
    name: deploy_minio
  vars:
    cifmw_deploy_minio_namespace: "{{ cifmw_deploy_loki_minio_namespace }}"
    cifmw_deploy_minio_root_user: "{{ cifmw_deploy_loki_minio_access_key }}"
    cifmw_deploy_minio_root_password: "{{ cifmw_deploy_loki_minio_secret_key }}"
- ansible.builtin.import_role:
    name: deploy_loki
  vars:
    cifmw_deploy_loki_deploy_minio: false
```

## See also

- **`deploy_minio`** — `roles/deploy_minio/README.md`
- Hook — `hooks/playbooks/deploy-loki-for-ck.yaml`
