# Reproducer scenarios usage

These environment files should be used with the "reproducer.yml" playbook.
Please refer to [the doc](https://ci-framework.readthedocs.io/en/latest/roles/reproducer.html)
about its usage.

## Available Scenarios

### OpenShift Deployment Methods

| Scenario | OpenShift Method | Description |
|----------|------------------|-------------|
| `3-nodes.yml` | CRC | Quick deployment using pre-built CRC image |
| `sno.yml` | SNO (devscripts) | Single Node OpenShift using devscripts |
| `sno-minimal.yml` | SNO (devscripts) | SNO with OCP 4.18 minimum resources |
| `va-*.yml` | devscripts (3 masters) | Full OCP cluster for VA scenarios |

### SNO (Single Node OpenShift) Scenarios

SNO is a standard OCP deployment with a single control plane node, following
[OCP 4.18 SNO best practices](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html/installing_on_a_single_node/).

Key characteristics:
- Uses devscripts for OCP deployment (same as VA scenarios)
- Full control over OpenShift version via `stable-X.Y` notation
- OVN-Kubernetes network plugin (required for SNO)
- Single node runs both control plane and workloads

#### Available SNO Scenarios

| File | OCP Resources | Use Case |
|------|---------------|----------|
| `sno.yml` | 16 vCPU, 64GB RAM, 200GB disk | Full integration testing |
| `sno-minimal.yml` | 8 vCPU, 16GB RAM, 120GB disk | Development/basic testing |

#### Usage

```bash
# Standard SNO deployment
ansible-playbook reproducer.yml \
  -e @scenarios/reproducers/sno.yml \
  -e @scenarios/reproducers/networking-definition.yml \
  -e cifmw_manage_secrets_pullsecret_file=/path/to/pull-secret.json \
  -e cifmw_manage_secrets_citoken_file=/path/to/ci-token

# Minimal SNO for resource-constrained environments
ansible-playbook reproducer.yml \
  -e @scenarios/reproducers/sno-minimal.yml \
  -e @scenarios/reproducers/networking-definition.yml \
  -e cifmw_manage_secrets_pullsecret_file=/path/to/pull-secret.json \
  -e cifmw_manage_secrets_citoken_file=/path/to/ci-token
```

#### Requirements

- OpenShift pull secret from https://console.redhat.com/openshift/downloads
- CI Token from https://console-openshift-console.apps.ci.l2s4.p1.openshiftapps.com/
- Hypervisor requirements:
  - `sno.yml`: ~80GB RAM, ~300GB storage
  - `sno-minimal.yml`: ~32GB RAM, ~200GB storage

#### SNO vs CRC vs 3-master OCP Comparison

| Aspect | CRC | SNO | 3-master OCP (VA) |
|--------|-----|-----|-------------------|
| Setup time | ~10-15 min | ~45-60 min | ~60-90 min |
| Min RAM (hypervisor) | ~32GB | ~32GB (minimal), ~80GB (full) | ~128GB |
| OCP version | Fixed to CRC release | Any (`stable-X.Y`) | Any (`stable-X.Y`) |
| Customization | Limited | Full control | Full control |
| HA capable | No | No | Yes |
| Best for | Quick local dev | Testing, edge scenarios | Production-like testing |

### CRC-based Scenarios

For quick local development with limited resources:

```bash
ansible-playbook reproducer.yml \
  -e @scenarios/reproducers/3-nodes.yml \
  -e @scenarios/reproducers/networking-definition.yml
```

### VA (Validated Architecture) Scenarios

For full OCP cluster deployments with 3 masters:

```bash
ansible-playbook reproducer.yml \
  -e @scenarios/reproducers/va-hci.yml \
  -e @scenarios/reproducers/networking-definition.yml \
  -e cifmw_architecture_scenario=hci \
  -e cifmw_manage_secrets_pullsecret_file=/path/to/pull-secret.json \
  -e cifmw_manage_secrets_citoken_file=/path/to/ci-token
```

## Scenario Files Structure

### Common files

| File | Purpose |
|------|---------|
| `networking-definition.yml` | Network definitions (required for all) |
| `va-common.yml` | Common settings for devscripts deployments |
| `sno-common.yml` | Common settings for SNO deployments |

### Inheritance pattern

Scenarios use `cifmw_parent_scenario` to inherit common settings:

```
va-hci.yml -> va-hci-base.yml -> va-common.yml
sno.yml -> sno-common.yml
sno-minimal.yml -> sno-common.yml
```
