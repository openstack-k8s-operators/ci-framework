# s2i_content_set

Resolve a promoted S2I service content set once and export
`cifmw_set_containers_images` for `edpm_prepare` /
`cifmw.general.set_containers` to patch `OpenStackVersion`.

The set is identified by `s2iCommit` plus image **digests**, not the floating
`:master-latest` tag. Operator manager images stay on
`openstack-k8s-operators-content-provider`; this role only injects service
containers from `quay.io/openstack-s2i-containers`.

## Privilege escalation

None.

## Parameters

* `cifmw_s2i_content_set_commit`: (String) Explicit s2i-openstack-containers
  git SHA. Wins over the pin file and over inspecting `:master-latest`.
  Default: empty.
* `cifmw_s2i_content_set_pin_file`: (String) Optional YAML with `s2iCommit`.
  Default: `openstack-operator/config/s2i-content-set.yaml` in the Zuul
  checkout.
* `cifmw_s2i_content_set_catalog_file`: (String) Optional digest catalog
  (`content-set.yaml`). Used when it exists and its `s2iCommit` matches the
  resolved commit (or no commit is set yet). Default: `containers/content-set.yaml`
  in the s2i checkout.
* `cifmw_s2i_content_set_mappings_file`: (String) `image-mappings.yaml` used
  when inspecting Quay. Default: s2i `containers/image-mappings.yaml`.
* `cifmw_s2i_content_set_src`: Checkout of `s2i-openstack-containers`. Default:
  `{{ ansible_user_dir }}/src/github.com/openstack-k8s-operators/s2i-openstack-containers`.
* `cifmw_s2i_content_set_registry` / `cifmw_s2i_content_set_namespace` /
  `cifmw_s2i_content_set_stream` / `cifmw_s2i_content_set_prefix`: Promoted
  registry and image name prefix. Defaults: `quay.io` /
  `openstack-s2i-containers` / `master` / `openstack`.
* `cifmw_s2i_content_set_probe_image`: Image inspected at `:master-latest` to
  read `org.opencontainers.image.revision` when no pin is set. Default:
  `openstack-keystone`.
* `cifmw_s2i_content_set_skip_images`: (List) OpenStackVersion field names to
  omit so `preserve_unlisted` keeps payload defaults.
* `cifmw_s2i_content_set_ignore_missing`: (Boolean) Continue when an inspect
  fails. Default: `false`.
* `cifmw_s2i_content_set_dest_path`: Artifact YAML. Default:
  `{{ cifmw_basedir }}/artifacts/s2i-content-set.yaml`.
* `cifmw_s2i_content_set_backend_images`: Cinder volume / Manila share map
  entries (not expressible as scalars in `image-mappings.yaml`).

Existing `cifmw_set_containers_images` entries win (speculative overlay).
When the role runs, `cifmw_set_containers_preserve_unlisted` defaults to
`true` if unset.

## Examples

Enable from a Zuul job (and from `deploy-edpm.yml`):

```yaml
vars:
  cifmw_s2i_content_set: true
  cifmw_s2i_content_set_skip_images:
    - neutronAPIImage
    - edpmNeutronMetadataAgentImage
    - mariadbImage
```
