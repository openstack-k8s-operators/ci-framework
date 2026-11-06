# discover_osp_pod

Discover OpenStack control-plane pods by **namespace + Kubernetes labels**,
not by hardcoded names like `cinder-api-0`.

Architecture deployments enable `uniquePodNames` for Cinder/Glance, so pod
names gain a short OpenStackControlPlane UID hash (`cinder-a4403-api-0`).
Labels from [lib-common](https://github.com/openstack-k8s-operators/lib-common)
stay stable:

| Label key   | lib-common constant   | Examples                          |
|-------------|-----------------------|-----------------------------------|
| `component` | `ComponentSelector`   | `cinder-api`, `glance-api`        |
| `service`   | `AppSelector`         | `cinder`, `glance`                |

## Requirements

- `kubernetes.core` collection
- Credentials / kubeconfig usable by `kubernetes.core.k8s_info`

## Role variables

See `defaults/main.yml`. Required:

- `cifmw_discover_osp_pod_component` – `component=` label value

Optional:

- `cifmw_discover_osp_pod_namespace` (default `openstack`)
- `cifmw_discover_osp_pod_service` – also select `service=`
- `cifmw_discover_osp_pod_labels` – extra equality labels (dict)
- `cifmw_discover_osp_pod_index` – which sorted match to return (default `0`)

## Facts set

- `cifmw_discover_osp_pod_name` – selected pod name
- `cifmw_discover_osp_pod_names` – all matching names (sorted)
- `cifmw_discover_osp_pod_resources` – raw `k8s_info` resources

## Examples

```yaml
- name: Resolve cinder-api pod (uniquePodNames safe)
  ansible.builtin.include_role:
    name: discover_osp_pod
  vars:
    cifmw_discover_osp_pod_component: cinder-api
    cifmw_discover_osp_pod_service: cinder

- name: Exec into discovered pod
  kubernetes.core.k8s_exec:
    namespace: openstack
    pod: "{{ cifmw_discover_osp_pod_name }}"
    container: cinder-api
    command: cinder-manage service list
```

```yaml
- name: Resolve glance default external API pod
  ansible.builtin.include_role:
    name: discover_osp_pod
  vars:
    cifmw_discover_osp_pod_component: glance-api
    cifmw_discover_osp_pod_service: glance
    cifmw_discover_osp_pod_labels:
      api-name: default
```

Equivalent imperative form used by adoption tests:

```bash
oc get pods -n openstack -l component=cinder-api,service=cinder \
  -o custom-columns=NAME:.metadata.name --no-headers
```

## Architecture post-deploy verification

`playbooks/06-deploy-architecture.yml` runs `tasks/verify.yml` when
`cifmw_discover_osp_pod_verify` is true (default). It probes each entry in
`cifmw_discover_osp_pod_verify_targets` and discovers pods that exist.

Disable with:

```yaml
cifmw_discover_osp_pod_verify: false
```

A Zuul testproject job can validate a change with:

```
Depends-On: https://github.com/openstack-k8s-operators/ci-framework/pull/<N>
```
