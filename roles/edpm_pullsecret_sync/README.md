# edpm_pullsecret_sync

Extract container registry credentials from OpenShift pull-secret and make them available for EDPM nodesets.

## Description

This role extracts registry credentials from the OpenShift cluster pull-secret (`openshift-config/pull-secret`)
and exposes them as Ansible facts that can be used by other roles, particularly for configuring EDPM nodesets
with correct registry authentication.

## Why this role is needed

When deploying EDPM (External Data Plane Management) nodes, they need to authenticate to container registries
to pull images. The credentials in the EDPM nodeset configuration must match those in the OpenShift cluster's
pull-secret to avoid authentication failures.

Common issues this role solves:
- JWT tokens expiring or being different between external files and the cluster pull-secret
- Registry login failures with "invalid username/password" errors
- Image pull failures due to credential mismatches

## Privilege escalation

None

## Parameters

### Required parameters

* `cifmw_edpm_pullsecret_sync_registry`: (String) Registry URL to extract credentials for. Required. Example: `registry.stage.redhat.io`

### Optional parameters

* `cifmw_openshift_kubeconfig`: (String) Path to kubeconfig file. Defaults to `~/.kube/config`.
* `cifmw_openshift_context`: (String) Kubernetes context to use. Defaults to current context.
* `cifmw_openshift_token`: (String) OpenShift authentication token. Defaults to omit (uses kubeconfig).
* `cifmw_edpm_pullsecret_sync_fact_name`: (String) Name of the fact to create with extracted credentials. Defaults to `cifmw_edpm_pullsecret_credentials`.

## Output variables

This role sets the following facts:

* `cifmw_edpm_pullsecret_credentials`: (Dictionary) Extracted credentials
  ```yaml
  cifmw_edpm_pullsecret_credentials:
    registry: "registry.stage.redhat.io"
    username: "6340056|rhos-gitops-konflux"
    password: "eyJhbGci..."  # JWT token
  ```

* `cifmw_edpm_pullsecret_credentials_dict`: (Dictionary) Credentials formatted for `edpm_container_registry_logins`
  ```yaml
  cifmw_edpm_pullsecret_credentials_dict:
    "6340056|rhos-gitops-konflux": "eyJhbGci..."
  ```

## Dependencies

* `kubernetes.core` collection (for `k8s_info` module)

## Example Playbook

### Basic usage

```yaml
- name: Extract registry.stage.redhat.io credentials
  hosts: controller
  tasks:
    - name: Extract credentials from pull-secret
      ansible.builtin.include_role:
        name: edpm_pullsecret_sync
      vars:
        cifmw_edpm_pullsecret_sync_registry: "registry.stage.redhat.io"

    - name: Display extracted credentials
      ansible.builtin.debug:
        msg: "Username: {{ cifmw_edpm_pullsecret_credentials.username }}"
```

### Use with ci_gen_kustomize_values

```yaml
- name: Generate nodeset with pull-secret credentials
  hosts: controller
  tasks:
    - name: Extract credentials
      ansible.builtin.include_role:
        name: edpm_pullsecret_sync
      vars:
        cifmw_edpm_pullsecret_sync_registry: "registry.stage.redhat.io"

    - name: Generate kustomize values with extracted credentials
      ansible.builtin.include_role:
        name: ci_gen_kustomize_values
      vars:
        cifmw_architecture_user_kustomize_registry_credentials:
          edpm-nodeset:
            edpm-nodeset-values:
              data:
                nodeset:
                  ansible:
                    ansibleVars:
                      edpm_container_registry_logins:
                        "{{ cifmw_edpm_pullsecret_credentials.registry }}": "{{ cifmw_edpm_pullsecret_credentials_dict }}"
```

### Extract multiple registries

```yaml
- name: Extract credentials for multiple registries
  hosts: controller
  tasks:
    - name: Extract registry.redhat.io
      ansible.builtin.include_role:
        name: edpm_pullsecret_sync
      vars:
        cifmw_edpm_pullsecret_sync_registry: "registry.redhat.io"
        cifmw_edpm_pullsecret_sync_fact_name: cifmw_registry_redhat_io_creds

    - name: Extract registry.stage.redhat.io
      ansible.builtin.include_role:
        name: edpm_pullsecret_sync
      vars:
        cifmw_edpm_pullsecret_sync_registry: "registry.stage.redhat.io"
        cifmw_edpm_pullsecret_sync_fact_name: cifmw_registry_stage_creds
```

## Integration with EDPM deployment

This role is typically called before deploying EDPM nodes to ensure nodesets have correct credentials:

```yaml
# Pre-deployment: extract credentials
- name: Setup EDPM credentials
  hosts: controller
  tasks:
    - name: Extract registry credentials from cluster
      ansible.builtin.include_role:
        name: edpm_pullsecret_sync
      vars:
        cifmw_edpm_pullsecret_sync_registry: "registry.stage.redhat.io"

# Deployment: use extracted credentials
- name: Deploy EDPM
  hosts: controller
  tasks:
    - name: Deploy with architecture
      ansible.builtin.include_role:
        name: kustomize_deploy
      vars:
        # Credentials are automatically available from previous role
        ...
```

## Troubleshooting

### Error: "Registry not found in pull-secret"

The specified registry doesn't exist in the cluster's pull-secret.

**Solution**: Check available registries:
```bash
oc get secret pull-secret -n openshift-config -o jsonpath='{.data.\.dockerconfigjson}' | \
  base64 -d | jq '.auths | keys'
```

### Error: "Failed to decode auth credentials"

The auth field in the pull-secret is not valid base64 or has unexpected format.

**Solution**: Verify pull-secret format:
```bash
oc get secret pull-secret -n openshift-config -o jsonpath='{.data.\.dockerconfigjson}' | \
  base64 -d | jq '.auths["registry.stage.redhat.io"]'
```

## Notes

- Credentials are extracted with `no_log: true` to avoid exposing sensitive data in logs
- The role validates that the specified registry exists in the pull-secret
- JWT tokens are preserved exactly as stored in the pull-secret to ensure they work correctly
- This role does not modify the cluster pull-secret, only reads it
