# Copyright: (c) 2026, Red Hat

# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

import inspect
import unittest

from ansible.errors import AnsibleFilterError, AnsibleFilterTypeError

from ansible_collections.cifmw.general.plugins.filter.from_ini import (
    FilterModule,
)


CEPH_CONF = """[global]
osd pool default size = 1
public_network = 192.168.122.0/24
cluster_network = 172.18.0.0/24
fsid = 5b5fd001-8e21-4a0a-ba87-c12e77892b2c
path = /var/lib/ceph/%s/osd
[mon]
mon_warn_on_pool_no_redundancy = false
"""

# uni03gamma / OSPRH-6675 writes ctlplane, not the storage network range
OSPRH_6675_CONF = """[global]
public_network = 192.168.122.0/24
"""


class TestFromIni(unittest.TestCase):
    def setUp(self):
        self.from_ini = FilterModule().filters()["from_ini"]

    def test_reads_public_network(self):
        self.assertEqual(
            self.from_ini(CEPH_CONF, "public_network"),
            "192.168.122.0/24",
        )

    def test_reads_cluster_network(self):
        self.assertEqual(
            self.from_ini(CEPH_CONF, "cluster_network"),
            "172.18.0.0/24",
        )

    def test_reads_fsid(self):
        self.assertEqual(
            self.from_ini(CEPH_CONF, "fsid"),
            "5b5fd001-8e21-4a0a-ba87-c12e77892b2c",
        )

    def test_reads_option_with_spaces_in_name(self):
        self.assertEqual(
            self.from_ini(CEPH_CONF, "osd pool default size"),
            "1",
        )

    def test_missing_key_returns_default(self):
        self.assertEqual(self.from_ini(CEPH_CONF, "missing"), "")
        self.assertEqual(
            self.from_ini(CEPH_CONF, "missing", default="unset"),
            "unset",
        )

    def test_missing_section_returns_default(self):
        self.assertEqual(
            self.from_ini(CEPH_CONF, "public_network", section="osd"),
            "",
        )

    def test_other_section(self):
        self.assertEqual(
            self.from_ini(
                CEPH_CONF,
                "mon_warn_on_pool_no_redundancy",
                section="mon",
            ),
            "false",
        )

    def test_interpolation_disabled(self):
        # %s must not be treated as a ConfigParser interpolation marker
        self.assertEqual(
            self.from_ini(CEPH_CONF, "path"),
            "/var/lib/ceph/%s/osd",
        )

    def test_bytes_input(self):
        self.assertEqual(
            self.from_ini(CEPH_CONF.encode("utf-8"), "public_network"),
            "192.168.122.0/24",
        )

    def test_osp_rh_6675_ctlplane_not_storage(self):
        self.assertEqual(
            self.from_ini(OSPRH_6675_CONF, "public_network"),
            "192.168.122.0/24",
        )
        self.assertEqual(
            self.from_ini(OSPRH_6675_CONF, "cluster_network"),
            "",
        )

    def test_rejects_non_string_content(self):
        with self.assertRaises(AnsibleFilterTypeError):
            self.from_ini({"public_network": "x"}, "public_network")

    def test_rejects_empty_key(self):
        with self.assertRaises(AnsibleFilterTypeError):
            self.from_ini(CEPH_CONF, "")

    def test_invalid_ini_raises(self):
        with self.assertRaises(AnsibleFilterError):
            self.from_ini("[global\npublic_network = x", "public_network")

    def test_implementation_uses_read_file_not_readfp(self):
        source = inspect.getsource(FilterModule)
        self.assertIn("read_file", source)
        self.assertNotIn("readfp", source)
