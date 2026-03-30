# deploy_minio

Ansible role that renders and applies a minimal **MinIO** deployment on OpenShift (namespace, PVC, Pod, Service, Routes). It provides S3-compatible object storage for lab, CI, backup/restore, or any workload that needs an in-cluster S3 endpoint.

## Description

The role:

1. Ensures the manifest output directory exists.
2. Renders `templates/minio.yaml.j2` to a YAML file on disk (multi-document manifest).
3. When `cifmw_deploy_minio` is true, applies that manifest with **`kubernetes.core.k8s`** (server-side apply semantics).

Before starting the server, the pod creates one directory under `/data` for each name in **`cifmw_deploy_minio_buckets`** (MinIO standalone maps buckets to top-level directories on the data volume).

MinIO is exposed in-cluster as Service `minio` on ports **9000** (API) and **9090** (console). Consumers typically use the API at:

`http://minio.<namespace>.svc.cluster.local:9000`

## Requirements

- Ansible collection **`kubernetes.core`** (declared in this role’s `meta/main.yml`).
- A valid **kubeconfig** (see below) and credentials that can create Namespaces, PVCs, Pods, Services, and Routes in the target cluster.
- For OpenShift Routes, a cluster with the **Route** API (`route.openshift.io/v1`).

## Cluster authentication

The role passes connection settings into `kubernetes.core` modules:

| Mechanism | Variable | Notes |
|-----------|----------|-------|
| Kubeconfig file | `cifmw_openshift_kubeconfig` | If unset, defaults to `{{ ansible_env.HOME }}/.kube/config`. |
| API token | `cifmw_openshift_token` | Optional; passed when set. |
| Context | `cifmw_openshift_context` | Optional; passed when set. |

You do **not** need the `oc` binary on `PATH` for this role’s tasks.

## Role variables

| Variable | Default | Description |
|----------|---------|-------------|
| `cifmw_deploy_minio` | `true` | When true, apply manifests to the cluster. When false, only render the template (useful for Molecule or dry inspection). |
| `cifmw_deploy_minio_parent_dir` | `{{ ansible_user_dir }}/ci-framework-data` | Root directory for artifact layout. In ci-framework, `group_vars/all.yml` sets this to `{{ cifmw_basedir }}` so it stays aligned with the rest of the framework. |
| `cifmw_deploy_minio_base_dir` | `{{ cifmw_deploy_minio_parent_dir }}` | Same as parent dir; manifests live under `<base>/artifacts/manifests/`. |
| `cifmw_deploy_minio_manifest_dest` | `<base>/artifacts/manifests/deploy_minio.yaml` | Output path for the rendered manifest. |
| `cifmw_deploy_minio_namespace` | `minio-dev` | Namespace for MinIO resources. |
| `cifmw_deploy_minio_buckets` | `[loki]` | Bucket names to create on the data volume before `minio server` starts. Use `[]` for none. Names should follow S3 bucket naming rules. |
| `cifmw_deploy_minio_image` | `quay.io/minio/minio:latest` | Container image for the MinIO pod. |
| `cifmw_deploy_minio_pvc_storage` | `10Gi` | PVC size request. |
| `cifmw_deploy_minio_storage_class` | `lvms-local-storage` | Storage class for the PVC. |
| `cifmw_deploy_minio_route_console_host` | `""` | If non-empty, sets an explicit host on the console Route; otherwise OpenShift assigns one. |
| `cifmw_deploy_minio_route_api_host` | `""` | Same for the API Route. |
| `cifmw_deploy_minio_root_user` | `minio` | MinIO root user; set in the pod as **`MINIO_ROOT_USER`**. |
| `cifmw_deploy_minio_root_password` | `minio123` | MinIO root password; set in the pod as **`MINIO_ROOT_PASSWORD`** (**change for anything beyond lab use**). |

## Usage

### Apply MinIO only

```yaml
- hosts: localhost
  gather_facts: true
  tasks:
    - name: Deploy MinIO
      ansible.builtin.import_role:
        name: deploy_minio
```

Override variables at play, `import_role` `vars`, or `host_vars` / `group_vars` as usual.

### Render manifests without applying

```yaml
- ansible.builtin.import_role:
    name: deploy_minio
  vars:
    cifmw_deploy_minio: false
```
