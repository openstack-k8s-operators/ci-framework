# Copyright: (c) 2026, Red Hat

# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

import base64
import struct
import unittest.mock  # noqa: F401 — required so unittest.mock is loaded for utils.py setUp

from ansible_collections.cifmw.general.tests.unit.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleBaseTestCase,
    set_module_args,
)
from ansible_collections.cifmw.general.plugins.modules import cephx_key


class TestCephxKey(ModuleBaseTestCase):
    """Unit tests for the cephx_key Ansible module."""

    def _decode_key(self, key_b64):
        """Decode a base64 CephX key and return (header_tuple, key_bytes)."""
        raw = base64.b64decode(key_b64)
        # Header is 12 bytes: struct.pack("<hiih", type, sec, nsec, key_len)
        header = struct.unpack("<hiih", raw[:12])
        key_bytes = raw[12:]
        return header, key_bytes

    def test_default_cipher_returns_aes128_key(self):
        """No args: default cipher produces a 28-byte (AES-128) encoded key."""
        set_module_args({})
        with self.assertRaises(AnsibleExitJson) as ctx:
            cephx_key.main()
        result = ctx.exception.args[0]
        self.assertIn("key", result)
        key_b64 = result["key"]
        raw = base64.b64decode(key_b64)
        self.assertEqual(len(raw), 28)
        header, key_bytes = self._decode_key(key_b64)
        # type=1, key_len=16
        self.assertEqual(header[0], 1)
        self.assertEqual(header[3], 16)
        self.assertEqual(len(key_bytes), 16)

    def test_aes_cipher_returns_aes128_key(self):
        """cipher=aes produces a 28-byte (AES-128) encoded key."""
        set_module_args({"cipher": "aes"})
        with self.assertRaises(AnsibleExitJson) as ctx:
            cephx_key.main()
        result = ctx.exception.args[0]
        key_b64 = result["key"]
        raw = base64.b64decode(key_b64)
        self.assertEqual(len(raw), 28)
        header, key_bytes = self._decode_key(key_b64)
        self.assertEqual(header[0], 1)
        self.assertEqual(header[3], 16)
        self.assertEqual(len(key_bytes), 16)

    def test_aes256k_cipher_returns_aes256k_key(self):
        """cipher=aes256k produces a 44-byte (AES-256k) encoded key."""
        set_module_args({"cipher": "aes256k"})
        with self.assertRaises(AnsibleExitJson) as ctx:
            cephx_key.main()
        result = ctx.exception.args[0]
        key_b64 = result["key"]
        raw = base64.b64decode(key_b64)
        self.assertEqual(len(raw), 44)
        header, key_bytes = self._decode_key(key_b64)
        # type=2, key_len=32
        self.assertEqual(header[0], 2)
        self.assertEqual(header[3], 32)
        self.assertEqual(len(key_bytes), 32)

    def test_invalid_cipher_fails(self):
        """cipher=invalid raises AnsibleFailJson (AnsibleModule enforces choices)."""
        set_module_args({"cipher": "invalid"})
        with self.assertRaises(AnsibleFailJson) as ctx:
            cephx_key.main()
        result = ctx.exception.args[0]
        self.assertTrue(result["failed"])

    def test_aes_key_is_valid_base64(self):
        """AES-128 key is valid base64 and ends with ==."""
        set_module_args({"cipher": "aes"})
        with self.assertRaises(AnsibleExitJson) as ctx:
            cephx_key.main()
        key_b64 = ctx.exception.args[0]["key"]
        # Should not raise
        decoded = base64.b64decode(key_b64)
        self.assertIsInstance(decoded, bytes)
        self.assertTrue(
            key_b64.endswith("=="), f"Expected == suffix, got: {key_b64[-2:]}"
        )

    def test_aes256k_key_is_valid_base64(self):
        """AES-256k key is valid base64 and ends with a single =."""
        set_module_args({"cipher": "aes256k"})
        with self.assertRaises(AnsibleExitJson) as ctx:
            cephx_key.main()
        key_b64 = ctx.exception.args[0]["key"]
        decoded = base64.b64decode(key_b64)
        self.assertIsInstance(decoded, bytes)
        self.assertTrue(
            key_b64.endswith("=") and not key_b64.endswith("=="),
            f"Expected single = suffix, got: {key_b64[-2:]}",
        )

    def test_key_changes_on_each_call(self):
        """Two successive calls produce different keys (randomness check)."""
        set_module_args({"cipher": "aes"})
        with self.assertRaises(AnsibleExitJson) as ctx1:
            cephx_key.main()
        key1 = ctx1.exception.args[0]["key"]

        set_module_args({"cipher": "aes"})
        with self.assertRaises(AnsibleExitJson) as ctx2:
            cephx_key.main()
        key2 = ctx2.exception.args[0]["key"]

        self.assertNotEqual(key1, key2)

    def test_aes256k_key_changes_on_each_call(self):
        """Two successive aes256k calls produce different keys (randomness check)."""
        set_module_args({"cipher": "aes256k"})
        with self.assertRaises(AnsibleExitJson) as ctx1:
            cephx_key.main()
        key1 = ctx1.exception.args[0]["key"]

        set_module_args({"cipher": "aes256k"})
        with self.assertRaises(AnsibleExitJson) as ctx2:
            cephx_key.main()
        key2 = ctx2.exception.args[0]["key"]

        self.assertNotEqual(key1, key2)
