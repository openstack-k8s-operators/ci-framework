# openshift_setup
Prepares the target OpenShift cluster to be used by further steps:
- Project/Namespace creation

## Privilege escalation
No privilege escalation needed.

## Parameters
* `cifmw_openshift_setup_dry_run`: (Boolean) Skips resources creation. Defaults to `false`.
* `cifmw_openshift_setup_create_namespaces`: (Strings) Namespaces to create beforehand. Defaults to `[]`.
* `cifmw_openshift_setup_skip_internal_registry`: (Boolean) Skips login and setup of the Internal Openshift registry. Defaults to `false`.
* `cifmw_openshift_setup_skip_internal_registry_tls_verify`: (Boolean) Skip TLS verification for Podman login. Defaults to `false`.
* `cifmw_openshift_setup_ca_registry_to_add`: (String) Registry to which the CA
should be configured for in an OCP/CRC cluster.
* `cifmw_openshift_setup_ca_bundle_path`: (String) Path to the CA bundle.
Defaults to `/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem`. Only has an
effect if `cifmw_openshift_setup_ca_registry_to_add` is set.
* `cifmw_openshift_setup_digest_mirrors`: (List) List of alternative mirrored repository locations for digest-based image pulls. Used to create ImageDigestMirrorSet resources. Defaults to `[]`.
    * Example:
        ```yaml
        cifmw_openshift_setup_digest_mirrors:
          - source: quay.io
            mirrors:
              - mirror.quay.io
          - source: quay.rdoproject.org
            mirrors:
              - mirror.quay.rdoproject.org
        ```
* `cifmw_openshift_setup_tag_mirrors`: (List) List of alternative mirrored repository locations for tag-based image pulls. Used to create ImageTagMirrorSet resources. When both digest and tag mirrors are configured, digest mirrors take precedence for digest-based pulls, while tag mirrors act as a fallback for tag-based pulls. Defaults to `[]`.
    * Example:
        ```yaml
        cifmw_openshift_setup_tag_mirrors:
          - source: quay.io
            mirrors:
              - mirror.quay.io
          - source: registry.redhat.io
            mirrors:
              - my-mirror.example.com
        ```
* `cifmw_openshift_setup_allowed_registries`: (List) List of allowed registries when setting up insecure registry configuration. Used in conjunction with `cifmw_update_containers_registry`. Defaults to common registries.
    * Example:
        ```yaml
        cifmw_openshift_setup_allowed_registries:
          - "quay.io"
          - "registry.redhat.io"
          - "my-internal-registry.example.com"
        ```
* `cifmw_openshift_setup_allowed_extra_registries`: (List) List of extra registries we want to allow. Intended to be by CI jobs using the framework.
* `cifmw_openshift_setup_catalog_registry_credentials`: (Dict or List) Credentials for one or more catalog registries (e.g., Konflux image-rbac-proxy, registry.stage.redhat.io). When defined, the role merges the credentials into `openshift-config/pull-secret` and adds the registries to `insecureRegistries` and `allowedRegistries` in the Image cluster config. This allows CatalogSource pods to pull from private registries and bypasses signature validation for Konflux-built FBC catalogs.
    * Format (single): `{registry: "hostname", username: "user", password: "pass"}`
    * Format (multiple): `[{registry: "host1", username: "user1", password: "pass1"}, {registry: "host2", ...}]`
    * Example (single registry):
        ```yaml
        cifmw_openshift_setup_catalog_registry_credentials:
          registry: "quay.io/redhat-user-workloads"
          username: "serviceaccount"
          password: "{{ lookup('file', '/path/to/secret') }}"
        ```
    * Example (multiple registries):
        ```yaml
        cifmw_openshift_setup_catalog_registry_credentials:
          - registry: "quay.io/redhat-user-workloads"
            username: "serviceaccount"
            password: "{{ lookup('file', '/path/to/konflux_secret') }}"
          - registry: "registry.stage.redhat.io"
            username: "{{ registry_username }}"
            password: "{{ registry_password }}"
        ```
* `cifmw_openshift_setup_apply_marketplace_fix`: (Boolean) Apply openshift-marketplace workaround which is recreating all pods in the namespace. NOTE: same step is done in `base` job.
* `cifmw_openshift_setup_samples_registry`: (String) Registry sample
* `cifmw_disconnected_containers_registry`: (String) Location of the mirror registry when doing a disconnected deployment.
