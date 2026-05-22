#!/usr/bin/python

# Copyright: (c) 2026, Red Hat
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: set_containers

short_description: Generate and optionally apply an OpenStackVersion CR

description:
- Generates an OpenStackVersion custom resource that controls which container
  images OpenStack services, AnsibleEE, and EDPM nodes use.
- With C(state=present) the CR file is written and optionally applied to the
  cluster with C(oc apply -f).
- With C(state=absent) the CR is optionally deleted from the cluster and the
  local file is removed.
- Module-level C(registry), C(org), C(name_prefix), and C(tag) act as
  defaults for all image URL construction. Every C(images) entry can override
  any of those four fields individually, so callers only need to specify what
  differs from the module defaults.
- C(include_openstack=true) populates the full standard set of OpenStack
  service images using the module-level (or per-image) defaults.
- The C(images) list handles everything else and can also transparently
  override individual images from the C(include_openstack) set. Overrides are
  merged on top; unspecified images keep their default values.
- URL resolution order for each C(images) entry.
  1. C(full_registry) is set - used as the complete URL.
  2. C(container_suffix) is set - URL built from the effective
     C(registry/org/name_prefix-suffix:tag) (per-image values take precedence
     over module-level values).
  3. Partial overrides only (e.g. C(tag) alone) - the standard suffix for the
     field C(name) is looked up in the built-in OpenStack image table and the
     URL is rebuilt with only the specified fields changed. Useful for
     overriding a single image from the C(include_openstack) set without
     repeating the suffix.
requirements:
  - PyYAML
  - oc (only when apply=true or state=absent)
options:
  state:
    description:
    - C(present) writes the CR file and optionally applies it.
    - C(absent) optionally deletes it from the cluster then removes the file.
    type: str
    choices: [present, absent]
    default: present
  apply:
    description:
    - When C(true) and C(state=present), run C(oc apply -f dest_path).
    type: bool
    default: false
  namespace:
    description:
    - Kubernetes namespace for the OpenStackVersion CR.
    type: str
    default: openstack
  metadata_name:
    description:
    - Name field of the OpenStackVersion CR metadata.
    type: str
    default: controlplane
  dest_path:
    description:
    - Absolute path where the generated CR YAML file is written.
    required: true
    type: path
  registry:
    description:
    - Default container registry host (e.g. C(quay.io)).
    - Required when C(include_openstack=true) or any C(images) entry needs to
      build a URL from parts and does not provide its own C(registry).
    type: str
  org:
    description:
    - Default registry namespace or organisation.
    - Required under the same conditions as C(registry).
    type: str
  tag:
    description:
    - Default container image tag.
    - Required under the same conditions as C(registry).
    type: str
  name_prefix:
    description:
    - Default container image name prefix prepended before the suffix when
      building an image URL.
    type: str
    default: openstack
  include_openstack:
    description:
    - Populate the full set of standard OpenStack service container images
      using the module-level C(registry), C(org), C(name_prefix), and C(tag).
      When C(true) those four parameters are required.
    type: bool
    default: false
  images:
    description:
    - List of container image specifications added to or overriding
      C(spec.customContainerImages).
    - Entries are merged on top of images produced by C(include_openstack).
    - Each entry can override the module-level C(registry), C(org),
      C(name_prefix), and C(tag) individually. Only the fields that differ
      from the module defaults need to be specified.
    type: list
    elements: dict
    default: []
    suboptions:
      name:
        description:
        - CR field name, e.g. C(ironicPythonAgentImage) or C(cinderVolumeImages).
          When only partial overrides are given with no C(container_suffix),
          this name is looked up in the built-in OpenStack suffix table to
          rebuild the URL.
        type: str
        required: true
      full_registry:
        description:
        - Complete image URL including the tag. When set, all other image-
          building fields are ignored. Mutually exclusive with C(container_suffix).
        type: str
      container_suffix:
        description:
        - Image name suffix. The URL is built as
          C(registry/org/name_prefix-container_suffix:tag) using the effective
          per-image or module-level values. Mutually exclusive with C(full_registry).
        type: str
      registry:
        description:
        - Per-image registry override. Falls back to the module-level C(registry).
        type: str
      org:
        description:
        - Per-image organisation override. Falls back to the module-level C(org).
        type: str
      name_prefix:
        description:
        - Per-image name prefix override. Falls back to the module-level C(name_prefix).
        type: str
      tag:
        description:
        - Per-image tag override. Falls back to the module-level C(tag).
        type: str
      backends:
        description:
        - List of backend names. When present the CR field becomes a dict
          mapping each backend name to its image URL
          (e.g. C(cinderVolumeImages) or C(manilaShareImages)).
        - Each item is either a plain string (inherits the parent image URL)
          or a dict with C(name) plus any subset of C(full_registry),
          C(container_suffix), C(registry), C(org), C(name_prefix), C(tag).
        type: list
        elements: raw
  kubeconfig:
    description:
    - Path to the kubeconfig file used when running C(oc) commands.
    - Falls back to the C(KUBECONFIG) environment variable when not set.
    type: path

author:
  - Arx Cruz (@arxcruz)
"""

EXAMPLES = r"""
- name: Generate CR with the full OpenStack image set (no apply)
  cifmw.general.set_containers:
    metadata_name: controlplane
    dest_path: /home/zuul/ci-framework-data/artifacts/manifests/set_containers.yml
    registry: quay.io
    org: openstack-k8s-operators
    tag: current-podified
    include_openstack: true

- name: Full set, override barbican tag and add AnsibleEE, then apply
  cifmw.general.set_containers:
    metadata_name: controlplane
    dest_path: /home/zuul/ci-framework-data/artifacts/manifests/set_containers.yml
    registry: quay.io
    org: openstack-k8s-operators
    tag: current-podified
    include_openstack: true
    apply: true
    kubeconfig: /home/zuul/.kube/config
    images:
      # override only the tag - suffix is looked up from the built-in table
      - name: barbicanAPIImage
        tag: my-hsm-tag
      - name: barbicanWorkerImage
        tag: my-hsm-tag
      # pull from a different registry with a different prefix
      - name: octaviaAPIImage
        registry: mirror.example.com
        org: myorg
        name_prefix: rhosp
        tag: "18.0"
      # full URL override
      - name: ansibleeeImage
        full_registry: quay.rdoproject.org/openstack-k8s-operators/openstack-ansibleee-runner:current-podified

- name: Watcher and cinder/manila backends (no include_openstack)
  cifmw.general.set_containers:
    dest_path: /tmp/set_containers.yml
    registry: quay.io
    org: openstack-k8s-operators
    tag: current-podified
    images:
      - name: watcherAPIImage
        container_suffix: watcher-api
      - name: watcherApplierImage
        container_suffix: watcher-applier
      - name: watcherDecisionEngineImage
        container_suffix: watcher-decision-engine
      - name: cinderVolumeImages
        container_suffix: cinder-volume
        backends:
          - default
          - name: netapp
            full_registry: registry.example.com/netapp/cinder-volume:24.1
          - name: hpe
            name_prefix: hpe
            org: hpe-storage
            tag: "1.2.3"
      - name: manilaShareImages
        container_suffix: manila-share
        backends:
          - share1
          - share2

- name: Remove the CR from the cluster and delete the local file
  cifmw.general.set_containers:
    state: absent
    dest_path: /home/zuul/ci-framework-data/artifacts/manifests/set_containers.yml
    kubeconfig: /home/zuul/.kube/config
"""

RETURN = r"""
dest_path:
    description: Absolute path to the generated CR file.
    type: str
    returned: when state=present
changed:
    description: Whether the module made any changes.
    type: bool
    returned: always
"""

import os

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.arg_spec import ArgumentSpecValidator

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Maps every standard OpenStack CR field name to its container image suffix.
# Used when an images entry specifies only partial overrides (e.g. tag only)
# with no container_suffix or full_registry, enabling transparent per-field
# overrides without repeating the suffix.
_OPENSTACK_SUFFIXES = {
    "aodhAPIImage": "aodh-api",
    "aodhEvaluatorImage": "aodh-evaluator",
    "aodhListenerImage": "aodh-listener",
    "aodhNotifierImage": "aodh-notifier",
    "barbicanAPIImage": "barbican-api",
    "barbicanKeystoneListenerImage": "barbican-keystone-listener",
    "barbicanWorkerImage": "barbican-worker",
    "ceilometerCentralImage": "ceilometer-central",
    "ceilometerComputeImage": "ceilometer-compute",
    "ceilometerIpmiImage": "ceilometer-ipmi",
    "ceilometerNotificationImage": "ceilometer-notification",
    "cinderAPIImage": "cinder-api",
    "cinderBackupImage": "cinder-backup",
    "cinderSchedulerImage": "cinder-scheduler",
    "cinderVolumeImage": "cinder-volume",
    "cloudkittyAPIImage": "cloudkitty-api",
    "cloudkittyProcImage": "cloudkitty-processor",
    "designateAPIImage": "designate-api",
    "designateBackendbind9Image": "designate-backend-bind9",
    "designateCentralImage": "designate-central",
    "designateMdnsImage": "designate-mdns",
    "designateProducerImage": "designate-producer",
    "designateUnboundImage": "unbound",
    "designateWorkerImage": "designate-worker",
    "edpmFrrImage": "frr",
    "edpmIscsidImage": "iscsid",
    "edpmLogrotateCrondImage": "cron",
    "edpmMultipathdImage": "multipathd",
    "edpmNeutronDhcpAgentImage": "neutron-dhcp-agent",
    "edpmNeutronMetadataAgentImage": "neutron-metadata-agent-ovn",
    "edpmNeutronOvnAgentImage": "neutron-ovn-agent",
    "edpmNeutronSriovAgentImage": "neutron-sriov-agent",
    "edpmOvnBgpAgentImage": "ovn-bgp-agent",
    "glanceAPIImage": "glance-api",
    "heatAPIImage": "heat-api",
    "heatCfnapiImage": "heat-api-cfn",
    "heatEngineImage": "heat-engine",
    "horizonImage": "horizon",
    "infraDnsmasqImage": "neutron-server",
    "infraMemcachedImage": "memcached",
    "ironicAPIImage": "ironic-api",
    "ironicConductorImage": "ironic-conductor",
    "ironicInspectorImage": "ironic-inspector",
    "ironicNeutronAgentImage": "ironic-neutron-agent",
    "ironicPxeImage": "ironic-pxe",
    "keystoneAPIImage": "keystone",
    "manilaAPIImage": "manila-api",
    "manilaSchedulerImage": "manila-scheduler",
    "manilaShareImage": "manila-share",
    "mariadbImage": "mariadb",
    "neutronAPIImage": "neutron-server",
    "novaAPIImage": "nova-api",
    "novaComputeImage": "nova-compute",
    "novaConductorImage": "nova-conductor",
    "novaNovncImage": "nova-novncproxy",
    "novaSchedulerImage": "nova-scheduler",
    "octaviaAPIImage": "octavia-api",
    "octaviaHealthmanagerImage": "octavia-health-manager",
    "octaviaHousekeepingImage": "octavia-housekeeping",
    "octaviaWorkerImage": "octavia-worker",
    "openstackClientImage": "openstackclient",
    "ovnControllerImage": "ovn-controller",
    "ovnControllerOvsImage": "ovn-base",
    "ovnNbDbclusterImage": "ovn-nb-db-server",
    "ovnNorthdImage": "ovn-northd",
    "ovnSbDbclusterImage": "ovn-sb-db-server",
    "placementAPIImage": "placement-api",
    "rabbitmqImage": "rabbitmq",
    "swiftAccountImage": "swift-account",
    "swiftContainerImage": "swift-container",
    "swiftObjectImage": "swift-object",
    "swiftProxyImage": "swift-proxy-server",
    "testTempestImage": "tempest-all",
}


def _effective(per_image_val, module_val):
    """Return the per-image value when explicitly set (including ""), otherwise the module-level default."""
    return per_image_val if per_image_val is not None else module_val


def _build_url(registry, org, prefix, suffix, tag):
    name = "{}-{}".format(prefix, suffix) if prefix else suffix
    return "{}/{}/{}:{}".format(registry, org, name, tag)


def _resolve_image(spec, mod_registry, mod_org, mod_prefix, mod_tag, module=None):
    """Resolve the image URL for one spec dict.

    Resolution order:
      1. full_registry   -> returned as-is.
      2. container_suffix -> URL built from effective registry/org/prefix/suffix/tag.
      3. Partial overrides only -> suffix looked up from _OPENSTACK_SUFFIXES by
         field name, URL rebuilt with the overridden fields substituted in.
    Returns None when no URL can be resolved.
    """
    if spec.get("full_registry"):
        return spec["full_registry"]

    reg = _effective(spec.get("registry"), mod_registry)
    org = _effective(spec.get("org"), mod_org)
    prefix = _effective(spec.get("name_prefix"), mod_prefix)
    tag = _effective(spec.get("tag"), mod_tag)
    suffix = spec.get("container_suffix")

    if not suffix:
        suffix = _OPENSTACK_SUFFIXES.get(spec["name"])
        if not suffix:
            if module:
                module.fail_json(
                    msg=(
                        "images entry '{}': no container_suffix given and the field "
                        "name is not in the standard OpenStack image set. "
                        "Provide container_suffix or full_registry."
                    ).format(spec["name"])
                )
            return None

    return _build_url(reg, org, prefix, suffix, tag)


def _resolve_backend(
    backend, parent_url, mod_registry, mod_org, mod_prefix, mod_tag, module=None
):
    """Return (backend_name, image_url) for one item in a backends list."""
    if isinstance(backend, str):
        return backend, parent_url
    name = backend.get("name")
    if not name:
        if module:
            module.fail_json(msg="backends entry is a dict but has no 'name' key")
        return None, parent_url
    url = _resolve_image(backend, mod_registry, mod_org, mod_prefix, mod_tag, module)
    return name, (url if url is not None else parent_url)


def _build_openstack_images(registry, org, prefix, tag):
    return {
        field: _build_url(registry, org, prefix, suffix, tag)
        for field, suffix in _OPENSTACK_SUFFIXES.items()
    }


def _build_cr(params, module=None):
    mod_registry = params["registry"]
    mod_org = params["org"]
    mod_prefix = params["name_prefix"]
    mod_tag = params["tag"]

    images = {}

    if params["include_openstack"]:
        images.update(
            _build_openstack_images(mod_registry, mod_org, mod_prefix, mod_tag)
        )

    for spec in params.get("images") or []:
        name = spec["name"]
        backends = spec.get("backends")
        parent_url = _resolve_image(
            spec, mod_registry, mod_org, mod_prefix, mod_tag, module
        )

        if backends is not None:
            backend_dict = {}
            for backend in backends:
                bname, burl = _resolve_backend(
                    backend,
                    parent_url,
                    mod_registry,
                    mod_org,
                    mod_prefix,
                    mod_tag,
                    module,
                )
                backend_dict[bname] = burl
            images[name] = backend_dict
        elif parent_url is not None:
            images[name] = parent_url

    return {
        "apiVersion": "core.openstack.org/v1beta1",
        "kind": "OpenStackVersion",
        "metadata": {
            "name": params["metadata_name"],
            "namespace": params["namespace"],
        },
        "spec": {"customContainerImages": images},
    }


def _needs_module_registry(params):
    """Return True when module-level registry/org/tag may be needed as fallbacks."""
    if params["include_openstack"]:
        return True
    for spec in params.get("images") or []:
        if not spec.get("full_registry"):
            if not (spec.get("registry") and spec.get("org") and spec.get("tag")):
                return True
        for backend in spec.get("backends") or []:
            if isinstance(backend, dict) and not backend.get("full_registry"):
                if not (
                    backend.get("registry")
                    and backend.get("org")
                    and backend.get("tag")
                ):
                    return True
    return False


def _run_oc(module, args, kubeconfig):
    oc_bin = module.get_bin_path("oc", required=True)
    environ_update = {"KUBECONFIG": kubeconfig} if kubeconfig else None
    rc, out, err = module.run_command([oc_bin] + args, environ_update=environ_update)
    return rc, out, err


_IMAGE_ELEMENT_SPEC = dict(
    name=dict(type="str", required=True),
    full_registry=dict(type="str"),
    container_suffix=dict(type="str"),
    registry=dict(type="str"),
    org=dict(type="str"),
    name_prefix=dict(type="str"),
    tag=dict(type="str"),
    backends=dict(type="list", elements="raw"),
)
_IMAGE_MUTUALLY_EXCLUSIVE = [["full_registry", "container_suffix"]]


def run_module():
    module_args = dict(
        state=dict(type="str", choices=["present", "absent"], default="present"),
        apply=dict(type="bool", default=False),
        namespace=dict(type="str", default="openstack"),
        metadata_name=dict(type="str", default="controlplane"),
        dest_path=dict(type="path", required=True),
        registry=dict(type="str", default=None),
        org=dict(type="str", default=None),
        tag=dict(type="str", default=None),
        name_prefix=dict(type="str", default="openstack"),
        include_openstack=dict(type="bool", default=False),
        images=dict(
            type="list",
            elements="dict",
            default=[],
            options=dict(
                name=dict(type="str", required=True),
                full_registry=dict(type="str", default=None),
                container_suffix=dict(type="str", default=None),
                registry=dict(type="str", default=None),
                org=dict(type="str", default=None),
                name_prefix=dict(type="str", default=None),
                tag=dict(type="str", default=None),
                backends=dict(type="list", elements="raw", default=None),
            ),
        ),
        kubeconfig=dict(type="path", default=None),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if not HAS_YAML:
        module.fail_json(msg="PyYAML is required for this module.")

    state = module.params["state"]
    dest_path = module.params["dest_path"]
    kubeconfig = module.params["kubeconfig"]
    result = dict(changed=False, dest_path=dest_path)

    if not os.path.isabs(dest_path):
        module.fail_json(
            msg="dest_path must be an absolute path: '{}'".format(dest_path)
        )
    if os.path.isdir(dest_path):
        module.fail_json(
            msg="dest_path '{}' is a directory, not a file".format(dest_path)
        )

    if state == "absent":
        if not os.path.exists(dest_path):
            module.exit_json(**result)
        if not module.check_mode:
            if kubeconfig and module.params["apply"]:
                rc, out, err = _run_oc(module, ["delete", "-f", dest_path], kubeconfig)
                if rc != 0:
                    module.fail_json(
                        msg="oc delete failed", rc=rc, stdout=out, stderr=err
                    )
            try:
                os.remove(dest_path)
            except OSError as exc:
                module.fail_json(msg="Cannot remove '{}': {}".format(dest_path, exc))
        result["changed"] = True
        module.exit_json(**result)

    # state == "present"
    if _needs_module_registry(module.params):
        for param in ("registry", "org", "tag"):
            if not module.params.get(param):
                module.fail_json(
                    msg=(
                        "'{}' is required as a module-level default when "
                        "include_openstack=true or any images entry does not "
                        "provide its own value for that field"
                    ).format(param)
                )

    for i, spec in enumerate(module.params.get("images") or []):
        # Ansible sets all option keys to None when not provided by the caller.
        # ArgumentSpecValidator.count_terms() counts by key presence, not by
        # non-None value, so stripping Nones is required before the
        # mutually_exclusive check to avoid false positives.
        cleaned = {k: v for k, v in spec.items() if v is not None}
        v = ArgumentSpecValidator(
            _IMAGE_ELEMENT_SPEC, mutually_exclusive=_IMAGE_MUTUALLY_EXCLUSIVE
        )
        vresult = v.validate(cleaned)
        if vresult.error_messages:
            module.fail_json(
                msg="images[{}]: {}".format(i, "; ".join(vresult.error_messages))
            )

    cr = _build_cr(module.params, module)
    cr_yaml = yaml.dump(cr, default_flow_style=False, sort_keys=False)

    existing = None
    if os.path.exists(dest_path):
        try:
            with open(dest_path, "r") as fh:
                existing = fh.read()
        except OSError as exc:
            module.fail_json(msg="Cannot read '{}': {}".format(dest_path, exc))
        try:
            parsed = yaml.safe_load(existing)
            if not isinstance(parsed, dict):
                module.fail_json(
                    msg="dest_path '{}' does not contain a YAML mapping".format(
                        dest_path
                    )
                )
        except yaml.YAMLError as exc:
            module.fail_json(
                msg="dest_path '{}' contains invalid YAML: {}".format(dest_path, exc)
            )

    if cr_yaml != existing:
        result["changed"] = True
        if not module.check_mode:
            try:
                dest_dir = os.path.dirname(dest_path)
                if dest_dir:
                    os.makedirs(dest_dir, exist_ok=True)
                with open(dest_path, "w") as fh:
                    fh.write(cr_yaml)
            except OSError as exc:
                module.fail_json(msg="Cannot write '{}': {}".format(dest_path, exc))

    if module.params["apply"] and not module.check_mode:
        rc, out, err = _run_oc(module, ["apply", "-f", dest_path], kubeconfig)
        if rc != 0:
            module.fail_json(msg="oc apply failed", rc=rc, stdout=out, stderr=err)
        result["changed"] = True

    module.exit_json(**result)


if __name__ == "__main__":
    run_module()
