# Copyright: (c) 2026, Red Hat

# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

import os
import tempfile

import yaml

from ansible_collections.cifmw.general.tests.unit.utils import (
    ModuleBaseTestCase,
    set_module_args,
    AnsibleExitJson,
    AnsibleFailJson,
)
from ansible_collections.cifmw.general.plugins.modules import strip_dict_keys


class TestStripDictKeys(ModuleBaseTestCase):

    def _write_yaml(self, data, path):
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f)

    def _read_yaml(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_strip_single_source(self):
        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, "base.yml")
            kf = os.path.join(td, "exclude.yml")
            self._write_yaml({"a": 1, "b": 2, "c": 3}, src)
            self._write_yaml({"a": "x", "c": "y"}, kf)

            set_module_args({"src": src, "keys_from": [kf]})
            with self.assertRaises(AnsibleExitJson) as ctx:
                strip_dict_keys.run_module()

            result = ctx.exception.args[0]
            self.assertTrue(result["changed"])
            self.assertEqual(sorted(result["removed_keys"]), ["a", "c"])
            self.assertEqual(self._read_yaml(src), {"b": 2})

    def test_strip_multiple_sources(self):
        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, "base.yml")
            kf1 = os.path.join(td, "ex1.yml")
            kf2 = os.path.join(td, "ex2.yml")
            self._write_yaml({"a": 1, "b": 2, "c": 3, "d": 4}, src)
            self._write_yaml({"a": "x"}, kf1)
            self._write_yaml({"c": "y"}, kf2)

            set_module_args({"src": src, "keys_from": [kf1, kf2]})
            with self.assertRaises(AnsibleExitJson) as ctx:
                strip_dict_keys.run_module()

            result = ctx.exception.args[0]
            self.assertTrue(result["changed"])
            self.assertEqual(self._read_yaml(src), {"b": 2, "d": 4})

    def test_no_matching_keys(self):
        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, "base.yml")
            kf = os.path.join(td, "exclude.yml")
            self._write_yaml({"a": 1, "b": 2}, src)
            self._write_yaml({"x": "foo"}, kf)

            set_module_args({"src": src, "keys_from": [kf]})
            with self.assertRaises(AnsibleExitJson) as ctx:
                strip_dict_keys.run_module()

            result = ctx.exception.args[0]
            self.assertFalse(result["changed"])
            self.assertEqual(result["removed_keys"], [])
            self.assertEqual(self._read_yaml(src), {"a": 1, "b": 2})

    def test_write_to_dest(self):
        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, "base.yml")
            dest = os.path.join(td, "out.yml")
            kf = os.path.join(td, "exclude.yml")
            self._write_yaml({"a": 1, "b": 2}, src)
            self._write_yaml({"a": "x"}, kf)

            set_module_args({"src": src, "keys_from": [kf], "dest": dest})
            with self.assertRaises(AnsibleExitJson) as ctx:
                strip_dict_keys.run_module()

            result = ctx.exception.args[0]
            self.assertTrue(result["changed"])
            self.assertEqual(result["dest"], dest)
            self.assertEqual(self._read_yaml(src), {"a": 1, "b": 2})
            self.assertEqual(self._read_yaml(dest), {"b": 2})

    def test_missing_src(self):
        set_module_args({"src": "/nonexistent.yml", "keys_from": []})
        with self.assertRaises(AnsibleFailJson) as ctx:
            strip_dict_keys.run_module()
        self.assertIn("not found", ctx.exception.args[0]["msg"])

    def test_missing_keys_from_file(self):
        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, "base.yml")
            self._write_yaml({"a": 1}, src)

            set_module_args({"src": src, "keys_from": ["/nonexistent.yml"]})
            with self.assertRaises(AnsibleFailJson) as ctx:
                strip_dict_keys.run_module()
            self.assertIn("not found", ctx.exception.args[0]["msg"])

    def test_empty_keys_from_list(self):
        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, "base.yml")
            self._write_yaml({"a": 1, "b": 2}, src)

            set_module_args({"src": src, "keys_from": []})
            with self.assertRaises(AnsibleExitJson) as ctx:
                strip_dict_keys.run_module()

            result = ctx.exception.args[0]
            self.assertFalse(result["changed"])
            self.assertEqual(self._read_yaml(src), {"a": 1, "b": 2})

    def test_empty_keys_from_file(self):
        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, "base.yml")
            kf = os.path.join(td, "empty.yml")
            self._write_yaml({"a": 1}, src)
            self._write_yaml(None, kf)

            set_module_args({"src": src, "keys_from": [kf]})
            with self.assertRaises(AnsibleExitJson) as ctx:
                strip_dict_keys.run_module()

            result = ctx.exception.args[0]
            self.assertFalse(result["changed"])
