# federation

This role sets up OpenStack Keystone federation with Keycloak (Red Hat SSO) as the Identity Provider.

## Overview

The federation role configures:
- Keycloak realm(s) with test users and groups
- Keystone Identity Provider and protocol configuration
- OIDC authentication for OpenStack CLI
- Comprehensive authentication testing

## Supported OIDC Authentication Methods

This role supports testing all OIDC authentication methods available in keystoneauth1:

| Plugin Name | Description | Status |
|-------------|-------------|--------|
| `v3oidcpassword` | Resource Owner Password Credentials flow | ✅ Supported |
| `v3oidcclientcredentials` | Client Credentials flow | ✅ Supported |
| `v3oidcaccesstoken` | Reuse existing access token | ✅ Supported |
| `v3oidcauthcode` | Authorization Code flow | ✅ Supported |
| `v3oidcdeviceauthz` | Device Authorization flow (RFC 8628) | ⚠️ Requires Python 3.10+ |

## Variables

### Infrastructure Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `cifmw_federation_keycloak_namespace` | `openstack` | Kubernetes namespace for Keycloak |
| `cifmw_federation_run_osp_cmd_namespace` | `openstack` | Kubernetes namespace for openstackclient |
| `cifmw_federation_domain` | - | Base domain for service URLs |

### Keycloak Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `cifmw_federation_keycloak_realm` | `openstack` | Primary Keycloak realm name |
| `cifmw_federation_keycloak_realm2` | `openstack2` | Secondary realm (multirealm mode) |
| `cifmw_federation_keycloak_admin_username` | `admin` | Keycloak admin username |
| `cifmw_federation_keycloak_admin_password` | `nomoresecrets` | Keycloak admin password |
| `cifmw_federation_deploy_multirealm` | `false` | Deploy multiple realms |

### Test Users

| Variable | Default | Description |
|----------|---------|-------------|
| `cifmw_federation_keycloak_testuser1_username` | `kctestuser1` | Test user 1 username |
| `cifmw_federation_keycloak_testuser1_password` | `nomoresecrets1` | Test user 1 password |
| `cifmw_federation_keycloak_testuser2_username` | `kctestuser2` | Test user 2 username |
| `cifmw_federation_keycloak_testuser2_password` | `nomoresecrets2` | Test user 2 password |

### Keystone Integration

| Variable | Default | Description |
|----------|---------|-------------|
| `cifmw_federation_IdpName` | `kcIDP` | Identity Provider name in Keystone |
| `cifmw_federation_keystone_domain` | `SSO` | Keystone domain for federated users |
| `cifmw_federation_mapping_name` | `SSOmap` | Keystone mapping name |
| `cifmw_federation_project_name` | `SSOproject` | Project for federated users |
| `cifmw_federation_group_name` | `SSOgroup` | Group for federated users |

### OIDC Client Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `cifmw_federation_keystone_OIDC_ClientID` | `rhoso` | OIDC client ID |
| `cifmw_federation_keystone_OIDC_ClientSecret` | `COX8bmlKAWn56XCGMrKQJj7dgHNAOl6f` | OIDC client secret |
| `cifmw_federation_keystone_OIDC_Scope` | `openid email profile` | OIDC scopes |

### Testing Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `cifmw_federation_run_oidc_auth_tests` | `true` | Run OIDC auth tests |

## Task Files

### Main Tasks

- `hook_pre_deploy.yml` - Deploys Keycloak before OpenStack
- `hook_post_deploy.yml` - Configures federation after OpenStack deployment
- `hook_controlplane_config.yml` - Adds federation config to control plane

### Setup Tasks

- `run_keycloak_setup.yml` - Deploy Keycloak operator and instance
- `run_keycloak_realm_setup.yml` - Configure Keycloak realm, users, and client
- `run_keycloak_client_setup.yml` - Enable advanced client features (Service Accounts, Device Auth)
- `run_openstack_setup.yml` - Configure Keystone IdP and mappings
- `run_openstack_auth_setup.yml` - Deploy authentication scripts to openstackclient pod

### Test Tasks

- `run_openstack_auth_test.yml` - Basic v3oidcpassword authentication test
- `run_openstack_oidc_auth_tests.yml` - Comprehensive OIDC authentication test suite

## Authentication Scripts

The following scripts are deployed to `/home/cloud-admin/` in the openstackclient pod:

| Script | Description |
|--------|-------------|
| `get-token.sh <user>` | Get token using v3oidcpassword |
| `oidc-clientcredentials.sh` | Configure v3oidcclientcredentials auth |
| `oidc-accesstoken.sh <token>` | Configure v3oidcaccesstoken auth |
| `oidc-authcode.sh <code>` | Configure v3oidcauthcode auth |
| `get-keycloak-token.sh` | Helper to obtain tokens from Keycloak |

### Example Usage

```bash
# v3oidcpassword - Password flow
kubectl exec -n openstack openstackclient -- bash -c \
  'source /home/cloud-admin/kctestuser1 && openstack token issue'

# v3oidcclientcredentials - Client Credentials flow
kubectl exec -n openstack openstackclient -- bash -c \
  'source /home/cloud-admin/oidc-clientcredentials.sh && openstack token issue'

# v3oidcaccesstoken - Access Token flow
ACCESS_TOKEN=$(/home/cloud-admin/get-keycloak-token.sh access_token kctestuser1 nomoresecrets1)
kubectl exec -n openstack openstackclient -- bash -c \
  "source /home/cloud-admin/oidc-accesstoken.sh '$ACCESS_TOKEN' && openstack token issue"

# v3oidcauthcode - Authorization Code flow
AUTH_CODE=$(/home/cloud-admin/get-keycloak-token.sh auth_code kctestuser1 nomoresecrets1)
kubectl exec -n openstack openstackclient -- bash -c \
  "source /home/cloud-admin/oidc-authcode.sh '$AUTH_CODE' && openstack token issue"
```

## Test Execution

The OIDC authentication tests are automatically run during the `hook_post_deploy.yml` phase when `cifmw_federation_run_oidc_auth_tests` is `true` (default).

To run the tests manually:

```yaml
- name: Run OIDC authentication tests
  ansible.builtin.include_role:
    name: federation
    tasks_from: run_openstack_oidc_auth_tests.yml
```

## Notes

- **Device Authorization Flow**: The `v3oidcdeviceauthz` plugin requires keystoneauth1 with Python 3.10+ support. OSP18 ships with Python 3.9 and does not include this plugin.
- **Multirealm**: CLI-based OIDC authentication testing only works in single realm mode. Multirealm federation is supported for Horizon-based authentication.
- **Keycloak Client**: The role automatically enables Service Accounts and Device Authorization on the Keycloak client to support all authentication methods.
