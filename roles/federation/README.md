# Federation Role

This role sets up OpenStack Keystone federation with Keycloak as the Identity Provider (IdP).

## Overview

The federation role enables OpenStack Keystone to authenticate users through external identity providers using OpenID Connect (OIDC) protocol. It supports both single and multi-realm configurations.

## Key Features

- **Multi-realm support**: Configure multiple Keycloak realms for different user groups
- **Security hardening**: Configurable security settings with secure defaults
- **Flexible configuration**: Organized variable structure for easy customization
- **Error handling**: Comprehensive error handling and validation
- **Modular design**: Shared tasks reduce code duplication

## Architecture

The role is designed to be called through hook files with specific task imports:

- `hook_pre_deploy.yml` - Sets up Keycloak and realms
- `hook_controlplane_config.yml` - Configures single realm federation
- `hook_multirealm_controlplane_config.yml` - Configures multi-realm federation  
- `hook_horizon_controlplane_config.yml` - Configures Horizon for WebSSO
- `hook_post_deploy.yml` - Sets up authentication and runs tests

## Configuration

### Basic Configuration

```yaml
cifmw_federation_keycloak_namespace: openstack
cifmw_federation_run_osp_cmd_namespace: openstack
cifmw_federation_domain: "apps.ocp.example.com"
```

### Security Configuration

```yaml
cifmw_federation_debug_enabled: false
cifmw_federation_insecure_debug: false
cifmw_federation_keycloak_url_validate_certs: true
cifmw_federation_log_level: warn
```

### Realm Configuration

```yaml
cifmw_federation_realms:
  - name: "openstack"
    idp_name: "kcIDP"
    domain: "SSO"
    project: "SSOproject"
    group: "SSOgroup"
    mapping: "SSOmap"
    client_id: "rhoso"
    client_secret: "secure-secret"
    test_users:
      - username: "testuser1"
        password: "secure-password"
        group: "testgroup1"
```

## Usage

The role is typically called through CI framework hook files:

```bash
# Pre-deployment setup
ansible-playbook hooks/playbooks/federation-pre-deploy.yml

# Configure single realm federation
ansible-playbook hooks/playbooks/federation-controlplane-config.yml

# Configure multi-realm federation  
ansible-playbook hooks/playbooks/federation-multirealm-controlplane-config.yml

# Configure Horizon WebSSO
ansible-playbook hooks/playbooks/federation-horizon-controlplane-config.yml

# Post-deployment setup and testing
ansible-playbook hooks/playbooks/federation-post-deploy.yml
```

## Requirements

- Ansible 2.9+
- Kubernetes cluster with OpenShift
- OpenStack deployment
- Required collections:
  - kubernetes.core
  - community.general

## Variables

See `defaults/main.yml` for a complete list of available variables with their default values.

## Security Considerations

- Change default passwords in production
- Enable certificate validation
- Disable debug logging in production
- Use secure secrets management

## Troubleshooting

- Check Keycloak pod logs for authentication issues
- Verify OpenStack Keystone configuration
- Ensure network connectivity between components
- Validate certificate trust chains
