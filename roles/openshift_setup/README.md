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
* `cifmw_openshift_setup_digest_mirrors`: (List) List of alternative mirrored repository locations. Defaults to `[]`.
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
* `cifmw_openshift_setup_metal3_watch_all_ns`: (Boolean) Tells Metal3 BMO to watch resources out of its namespace. Defaults to `false`.
