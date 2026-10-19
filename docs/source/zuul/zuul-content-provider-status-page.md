# Content provider status page

Besides the `zuul_return` data for dependent jobs, the content provider
publishes a plain-HTTP status document that jobs running **in parallel**
with the provider (no Zuul dependency) can consume. The provider pre
playbook, `ci/playbooks/content_provider/pre.yml`, starts a small
`busybox` `httpd` container serving
`~/zuul-output/.cifmw-status/content.json` on port 8080, and prints this
single-line console marker that parallel consumers grep from the
provider's live console stream (via the Zuul console-stream API) to
discover the endpoint:

```
CIFMW_CONTENT_PROVIDER_STATUS_URL: http://<provider-ip>:8080/content.json
```

The document is written atomically (staged to a temporary name, then
moved into place) by the shared task file
`ci/playbooks/tasks/publish-content-status.yaml` and moves through two
states:

- `building` — published in the pre phase, as soon as the provider's
  IPv4 is discovered; carries the registry endpoint plus the Zuul
  change/patchset the content is built from.
- `ready` — published by the outer run playbooks just before
  `zuul_return`; carries the same payload returned to dependent jobs.

The `ready` fields depend on the provider job:

| Job | Additional `ready` fields |
|---|---|
| `openstack-k8s-operators-content-provider` (+ `-bootc`) | `cifmw_operator_build_output`, `cifmw_build_images_output` |
| `openstack-meta-content-provider` | the above plus `content_provider_dlrn_md5_hash`, `content_provider_os_registry_url`, `content_provider_os_registry_namespace`, `content_provider_gating_repo_available`, `content_provider_gating_repo_url` |
| `cifmw-content-provider-build-images` | `cifmw_build_images_output` |
| `cifmw-tcib` | `content_provider_dlrn_md5_hash`, `content_provider_os_registry_url`, `content_provider_os_registry_namespace`, `content_provider_gating_repo_available`, `content_provider_gating_repo_url` |

All providers also expose `registry`, `content_provider_registry_available`,
`content_provider_registry_ip` and `content_provider_registry_ip_port`.

A parallel consumer waits for the provider job to pause — detected
through the Zuul status API it already polls for discovery — then
fetches `content.json` and consumes the payload. A `result: FAILURE` on
the provider job means the run failed; the status endpoint disappearing
while the consumer still waits indicates node loss or an aborted
provider job. Because such a consumer does not depend on the provider
in Zuul, a noop anchor job depending on both the provider and the
consumer is required to keep the paused provider's node (and registry)
alive until the consumer completes. Dependent jobs receive the status
URL as `content_provider_status_url` in the returned data.

The status server keeps running for the whole job lifetime. Like the
registry, it is not torn down explicitly — it is abandoned when
nodepool deletes the provider node once the job and its dependents
complete. The publication contract (building to ready) is covered by
the `registry_deploy` `status_page` molecule scenario.
