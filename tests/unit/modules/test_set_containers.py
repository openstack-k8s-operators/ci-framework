# Copyright Red Hat, Inc.
# Apache License Version 2.0

from __future__ import absolute_import, division, print_function

import unittest
from unittest.mock import MagicMock, mock_open, patch

import yaml

from ansible_collections.cifmw.general.tests.unit.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleBaseTestCase,
    set_module_args,
)
from ansible_collections.cifmw.general.plugins.modules import set_containers
from ansible_collections.cifmw.general.plugins.modules.set_containers import (
    _build_cr,
    _build_url,
    _resolve_backend,
    _resolve_image,
)

_MOD = "ansible_collections.cifmw.general.plugins.modules.set_containers"

REG = "quay.io"
ORG = "openstack-k8s-operators"
PREFIX = "openstack"
TAG = "current-podified"


class TestBuildUrl(unittest.TestCase):
    def test_with_prefix(self):
        self.assertEqual(
            _build_url(REG, ORG, PREFIX, "nova-api", TAG),
            "quay.io/openstack-k8s-operators/openstack-nova-api:current-podified",
        )

    def test_empty_prefix_no_dash(self):
        url = _build_url(REG, ORG, "", "ironic-python-agent", TAG)
        self.assertEqual(
            url,
            "quay.io/openstack-k8s-operators/ironic-python-agent:current-podified",
        )
        self.assertNotIn("/-", url)


class TestResolveImage(unittest.TestCase):
    def test_full_registry_returned_as_is(self):
        spec = dict(name="novaAPIImage", full_registry="custom.io/ns/nova:v1")
        self.assertEqual(
            _resolve_image(spec, REG, ORG, PREFIX, TAG),
            "custom.io/ns/nova:v1",
        )

    def test_container_suffix_builds_url(self):
        spec = dict(name="novaAPIImage", container_suffix="nova-api")
        self.assertEqual(
            _resolve_image(spec, REG, ORG, PREFIX, TAG),
            "quay.io/openstack-k8s-operators/openstack-nova-api:current-podified",
        )

    def test_suffix_lookup_from_table(self):
        spec = dict(name="keystoneAPIImage")
        self.assertEqual(
            _resolve_image(spec, REG, ORG, PREFIX, TAG),
            "quay.io/openstack-k8s-operators/openstack-keystone:current-podified",
        )

    def test_partial_override_tag_only(self):
        spec = dict(name="barbicanAPIImage", tag="my-hsm-tag")
        self.assertEqual(
            _resolve_image(spec, REG, ORG, PREFIX, TAG),
            "quay.io/openstack-k8s-operators/openstack-barbican-api:my-hsm-tag",
        )

    def test_per_image_registry_org_prefix_tag(self):
        spec = dict(
            name="octaviaAPIImage",
            registry="mirror.example.com",
            org="myorg",
            name_prefix="rhosp",
            tag="18.0",
        )
        self.assertEqual(
            _resolve_image(spec, REG, ORG, PREFIX, TAG),
            "mirror.example.com/myorg/rhosp-octavia-api:18.0",
        )

    def test_empty_name_prefix_no_dash(self):
        spec = dict(
            name="osContainerImage",
            container_suffix="edpm-hardened-uefi",
            name_prefix="",
        )
        url = _resolve_image(spec, REG, ORG, PREFIX, TAG)
        self.assertEqual(
            url,
            "quay.io/openstack-k8s-operators/edpm-hardened-uefi:current-podified",
        )
        self.assertNotIn("/-", url)

    def test_unknown_name_without_suffix_returns_none(self):
        spec = dict(name="unknownCustomImage")
        self.assertIsNone(_resolve_image(spec, REG, ORG, PREFIX, TAG))

    def test_unknown_name_without_suffix_calls_fail_json(self):
        module = MagicMock()
        _resolve_image(
            dict(name="unknownCustomImage"), REG, ORG, PREFIX, TAG, module=module
        )
        module.fail_json.assert_called_once()
        self.assertIn("unknownCustomImage", module.fail_json.call_args[1]["msg"])


class TestResolveBackend(unittest.TestCase):
    _parent = "quay.io/openstack-k8s-operators/openstack-cinder-volume:current-podified"

    def test_string_backend_uses_parent_url(self):
        name, url = _resolve_backend("default", self._parent, REG, ORG, PREFIX, TAG)
        self.assertEqual(name, "default")
        self.assertEqual(url, self._parent)

    def test_dict_backend_full_registry(self):
        backend = dict(
            name="netapp", full_registry="registry.example.com/netapp/cinder:24.1"
        )
        name, url = _resolve_backend(backend, self._parent, REG, ORG, PREFIX, TAG)
        self.assertEqual(name, "netapp")
        self.assertEqual(url, "registry.example.com/netapp/cinder:24.1")

    def test_dict_backend_container_suffix_with_tag_override(self):
        backend = dict(name="lvm", container_suffix="cinder-volume", tag="v2")
        name, url = _resolve_backend(backend, self._parent, REG, ORG, PREFIX, TAG)
        self.assertEqual(name, "lvm")
        self.assertEqual(
            url, "quay.io/openstack-k8s-operators/openstack-cinder-volume:v2"
        )

    def test_dict_backend_unresolvable_falls_back_to_parent(self):
        backend = dict(name="unknown-backend")
        name, url = _resolve_backend(backend, self._parent, REG, ORG, PREFIX, TAG)
        self.assertEqual(name, "unknown-backend")
        self.assertEqual(url, self._parent)

    def test_dict_backend_missing_name_without_module_returns_none(self):
        backend = dict(container_suffix="cinder-volume")
        name, url = _resolve_backend(backend, self._parent, REG, ORG, PREFIX, TAG)
        self.assertIsNone(name)
        self.assertEqual(url, self._parent)

    def test_dict_backend_missing_name_with_module_calls_fail_json(self):
        mock_module = MagicMock()
        backend = dict(container_suffix="cinder-volume")
        _resolve_backend(backend, self._parent, REG, ORG, PREFIX, TAG, mock_module)
        mock_module.fail_json.assert_called_once()
        self.assertIn("name", mock_module.fail_json.call_args[1]["msg"])


class TestBuildCr(unittest.TestCase):
    def _params(self, **kwargs):
        p = dict(
            state="present",
            apply=False,
            namespace="openstack",
            metadata_name="controlplane",
            dest_path="/tmp/cr.yml",
            registry=REG,
            org=ORG,
            tag=TAG,
            name_prefix=PREFIX,
            include_openstack=False,
            images=[],
            kubeconfig=None,
        )
        p.update(kwargs)
        return p

    def test_cr_structure(self):
        cr = _build_cr(self._params())
        self.assertEqual(cr["apiVersion"], "core.openstack.org/v1beta1")
        self.assertEqual(cr["kind"], "OpenStackVersion")
        self.assertEqual(cr["metadata"]["name"], "controlplane")
        self.assertEqual(cr["metadata"]["namespace"], "openstack")

    def test_include_openstack_populates_all_standard_images(self):
        cr = _build_cr(self._params(include_openstack=True))
        images = cr["spec"]["customContainerImages"]
        self.assertEqual(
            images["novaAPIImage"],
            "quay.io/openstack-k8s-operators/openstack-nova-api:current-podified",
        )
        self.assertEqual(
            images["keystoneAPIImage"],
            "quay.io/openstack-k8s-operators/openstack-keystone:current-podified",
        )
        self.assertIn("swiftProxyImage", images)
        self.assertIn("barbicanAPIImage", images)

    def test_images_list_without_include_openstack(self):
        cr = _build_cr(
            self._params(
                images=[
                    dict(name="novaAPIImage", container_suffix="nova-api"),
                ]
            )
        )
        images = cr["spec"]["customContainerImages"]
        self.assertEqual(list(images.keys()), ["novaAPIImage"])
        self.assertEqual(
            images["novaAPIImage"],
            "quay.io/openstack-k8s-operators/openstack-nova-api:current-podified",
        )

    def test_images_list_overrides_include_openstack(self):
        cr = _build_cr(
            self._params(
                include_openstack=True,
                images=[dict(name="novaAPIImage", tag="my-override")],
            )
        )
        images = cr["spec"]["customContainerImages"]
        self.assertEqual(
            images["novaAPIImage"],
            "quay.io/openstack-k8s-operators/openstack-nova-api:my-override",
        )
        self.assertEqual(
            images["keystoneAPIImage"],
            "quay.io/openstack-k8s-operators/openstack-keystone:current-podified",
        )

    def test_backends_produce_nested_dict(self):
        cr = _build_cr(
            self._params(
                images=[
                    dict(
                        name="cinderVolumeImages",
                        container_suffix="cinder-volume",
                        backends=[
                            "lvm",
                            dict(
                                name="netapp",
                                full_registry="registry.example.com/netapp/cinder:1.0",
                            ),
                        ],
                    )
                ]
            )
        )
        cinder = cr["spec"]["customContainerImages"]["cinderVolumeImages"]
        self.assertIsInstance(cinder, dict)
        self.assertEqual(
            cinder["lvm"],
            "quay.io/openstack-k8s-operators/openstack-cinder-volume:current-podified",
        )
        self.assertEqual(cinder["netapp"], "registry.example.com/netapp/cinder:1.0")

    def test_empty_name_prefix(self):
        cr = _build_cr(
            self._params(
                images=[
                    dict(
                        name="osContainerImage",
                        container_suffix="edpm-hardened-uefi",
                        name_prefix="",
                    ),
                ]
            )
        )
        url = cr["spec"]["customContainerImages"]["osContainerImage"]
        self.assertEqual(
            url,
            "quay.io/openstack-k8s-operators/edpm-hardened-uefi:current-podified",
        )

    def test_custom_namespace_and_name(self):
        cr = _build_cr(self._params(namespace="custom-ns", metadata_name="myplane"))
        self.assertEqual(cr["metadata"]["namespace"], "custom-ns")
        self.assertEqual(cr["metadata"]["name"], "myplane")


class TestRunModule(ModuleBaseTestCase):
    def _args(self, **kwargs):
        args = dict(dest_path="/tmp/set_containers.yml", registry=REG, org=ORG, tag=TAG)
        args.update(kwargs)
        return args

    def test_present_writes_new_file(self):
        set_module_args(self._args())
        with patch(_MOD + ".os.path.exists", return_value=False), patch(
            _MOD + ".os.makedirs"
        ), patch("builtins.open", mock_open()):
            with self.assertRaises(AnsibleExitJson) as cm:
                set_containers.run_module()
        self.assertTrue(cm.exception.args[0]["changed"])

    def test_present_no_change_when_file_identical(self):
        params = dict(
            state="present",
            apply=False,
            namespace="openstack",
            metadata_name="controlplane",
            dest_path="/tmp/set_containers.yml",
            registry=REG,
            org=ORG,
            tag=TAG,
            name_prefix="openstack",
            include_openstack=False,
            images=[],
            kubeconfig=None,
        )
        existing = yaml.dump(
            _build_cr(params), default_flow_style=False, sort_keys=False
        )

        set_module_args(self._args())
        with patch(_MOD + ".os.path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data=existing)
        ):
            with self.assertRaises(AnsibleExitJson) as cm:
                set_containers.run_module()
        self.assertFalse(cm.exception.args[0]["changed"])

    def test_present_apply_calls_oc(self):
        set_module_args(self._args(apply=True))
        with patch(_MOD + ".os.path.exists", return_value=False), patch(
            _MOD + ".os.makedirs"
        ), patch("builtins.open", mock_open()), patch(
            _MOD + "._run_oc", return_value=(0, "", "")
        ) as mock_oc:
            with self.assertRaises(AnsibleExitJson) as cm:
                set_containers.run_module()
        mock_oc.assert_called_once()
        self.assertEqual(mock_oc.call_args[0][1][0], "apply")
        self.assertTrue(cm.exception.args[0]["changed"])

    def test_present_apply_oc_failure_fails(self):
        set_module_args(self._args(apply=True))
        with patch(_MOD + ".os.path.exists", return_value=False), patch(
            _MOD + ".os.makedirs"
        ), patch("builtins.open", mock_open()), patch(
            _MOD + "._run_oc", return_value=(1, "", "oc: command not found")
        ):
            with self.assertRaises(AnsibleFailJson) as cm:
                set_containers.run_module()
        self.assertIn("oc apply failed", cm.exception.args[0]["msg"])

    def test_absent_file_missing_is_noop(self):
        set_module_args(self._args(state="absent"))
        with patch(_MOD + ".os.path.exists", return_value=False):
            with self.assertRaises(AnsibleExitJson) as cm:
                set_containers.run_module()
        self.assertFalse(cm.exception.args[0]["changed"])

    def test_absent_removes_existing_file(self):
        set_module_args(self._args(state="absent"))
        with patch(_MOD + ".os.path.exists", return_value=True), patch(
            _MOD + ".os.remove"
        ) as mock_rm:
            with self.assertRaises(AnsibleExitJson) as cm:
                set_containers.run_module()
        mock_rm.assert_called_once_with("/tmp/set_containers.yml")
        self.assertTrue(cm.exception.args[0]["changed"])

    def test_absent_with_kubeconfig_and_apply_calls_oc_delete(self):
        set_module_args(
            self._args(state="absent", apply=True, kubeconfig="/home/zuul/.kube/config")
        )
        with patch(_MOD + ".os.path.exists", return_value=True), patch(
            _MOD + ".os.remove"
        ), patch(_MOD + "._run_oc", return_value=(0, "", "")) as mock_oc:
            with self.assertRaises(AnsibleExitJson) as cm:
                set_containers.run_module()
        mock_oc.assert_called_once()
        self.assertEqual(mock_oc.call_args[0][1][0], "delete")
        self.assertTrue(cm.exception.args[0]["changed"])

    def test_absent_with_kubeconfig_but_no_apply_skips_oc_delete(self):
        set_module_args(
            self._args(
                state="absent", apply=False, kubeconfig="/home/zuul/.kube/config"
            )
        )
        with patch(_MOD + ".os.path.exists", return_value=True), patch(
            _MOD + ".os.remove"
        ), patch(_MOD + "._run_oc", return_value=(0, "", "")) as mock_oc:
            with self.assertRaises(AnsibleExitJson) as cm:
                set_containers.run_module()
        mock_oc.assert_not_called()
        self.assertTrue(cm.exception.args[0]["changed"])

    def test_dest_path_is_directory_fails(self):
        set_module_args(self._args(dest_path="/tmp"))
        with patch(_MOD + ".os.path.isdir", return_value=True):
            with self.assertRaises(AnsibleFailJson) as cm:
                set_containers.run_module()
        self.assertIn("directory", cm.exception.args[0]["msg"])

    def test_dest_path_invalid_yaml_fails(self):
        set_module_args(self._args())
        with patch(_MOD + ".os.path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data="[invalid: yaml: :\n")
        ), patch(_MOD + ".yaml.safe_load", side_effect=yaml.YAMLError("bad yaml")):
            with self.assertRaises(AnsibleFailJson) as cm:
                set_containers.run_module()
        self.assertIn("invalid YAML", cm.exception.args[0]["msg"])

    def test_dest_path_non_mapping_yaml_fails(self):
        set_module_args(self._args())
        with patch(_MOD + ".os.path.exists", return_value=True), patch(
            "builtins.open", mock_open(read_data="- item1\n- item2\n")
        ), patch(_MOD + ".yaml.safe_load", return_value=["item1", "item2"]):
            with self.assertRaises(AnsibleFailJson) as cm:
                set_containers.run_module()
        self.assertIn("YAML mapping", cm.exception.args[0]["msg"])

    def test_os_remove_failure_fails(self):
        set_module_args(self._args(state="absent"))
        with patch(_MOD + ".os.path.exists", return_value=True), patch(
            _MOD + ".os.remove", side_effect=OSError("permission denied")
        ):
            with self.assertRaises(AnsibleFailJson) as cm:
                set_containers.run_module()
        self.assertIn("Cannot remove", cm.exception.args[0]["msg"])

    def test_file_write_failure_fails(self):
        set_module_args(self._args())
        with patch(_MOD + ".os.path.exists", return_value=False), patch(
            _MOD + ".os.makedirs"
        ), patch("builtins.open", side_effect=OSError("no space left")):
            with self.assertRaises(AnsibleFailJson) as cm:
                set_containers.run_module()
        self.assertIn("Cannot write", cm.exception.args[0]["msg"])

    def test_validation_missing_registry_fails(self):
        set_module_args(dict(dest_path="/tmp/cr.yml", include_openstack=True))
        with self.assertRaises(AnsibleFailJson) as cm:
            set_containers.run_module()
        self.assertIn("registry", cm.exception.args[0]["msg"])

    def test_validation_full_registry_and_suffix_exclusive(self):
        set_module_args(
            self._args(
                images=[
                    dict(
                        name="novaAPIImage",
                        full_registry="quay.io/ns/nova:v1",
                        container_suffix="nova-api",
                    )
                ]
            )
        )
        with patch(_MOD + ".os.path.exists", return_value=False):
            with self.assertRaises(AnsibleFailJson) as cm:
                set_containers.run_module()
        self.assertIn("mutually exclusive", cm.exception.args[0]["msg"])

    def test_include_openstack_with_images_override(self):
        set_module_args(
            self._args(
                include_openstack=True,
                images=[dict(name="novaAPIImage", tag="special-tag")],
            )
        )
        with patch(_MOD + ".os.path.exists", return_value=False), patch(
            _MOD + ".os.makedirs"
        ), patch("builtins.open", mock_open()):
            with self.assertRaises(AnsibleExitJson) as cm:
                set_containers.run_module()
        self.assertTrue(cm.exception.args[0]["changed"])
