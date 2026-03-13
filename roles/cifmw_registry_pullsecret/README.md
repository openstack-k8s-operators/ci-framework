# cifmw_registry_pullsecret

Extract registry credentials from OpenShift pull-secret and update the registry token used for EDPM deployment.

## Privilege escalation

None required.

## Parameters

* `cifmw_registry_pullsecret_enabled`: (Boolean) Enable/disable pull-secret credential extraction. Default: `false`
* `cifmw_registry_pullsecret_registry_url`: (String) Registry URL to extract credentials for. Example: `<registry-url>`
* `cifmw_registry_pullsecret_update_file`: (Boolean) Whether to update the registry token file. Default: `true`
* `cifmw_registry_pullsecret_dest_file`: (String) Destination file for registry token credentials. Default: `{{ ansible_user_dir }}/secrets/registry_token_creds.yaml`

## Usage

This role is designed to be called during EDPM deployment, after OpenShift is deployed but before EDPM nodesets are created.

It extracts credentials from the OpenShift pull-secret in the `openshift-config` namespace and updates the `cifmw_registry_token` variable and optionally the registry token file.

### Example configuration which can be used in the zuul jobs

```yaml
vars:
  cifmw_registry_pullsecret_enabled: true
  cifmw_registry_pullsecret_registry_url: <registry-url>
```

### Integration point

This role is automatically called by `cifmw_setup/tasks/deploy_architecture.yml` when `cifmw_registry_pullsecret_enabled` is `true`.

## Requirements

* OpenShift cluster must be deployed and accessible
* `kubernetes.core.k8s_info` module must be available
* Pull-secret must exist in `openshift-config/pull-secret`
* The specified registry URL must be present in the pull-secret

## Error handling

If extraction fails for any reason (OpenShift not accessible, registry not in pull-secret, etc.), the role will log a warning and continue, keeping the existing credentials from pre-run.
