# Copyright: Contributors to the OpenStack-K8s-Operators project
# SPDX-License-Identifier: Apache-2.0

from __future__ import absolute_import, division, print_function

import unittest

from ansible.errors import AnsibleFilterError, AnsibleFilterTypeError

from ansible_collections.cifmw.general.plugins.filter.osp_pod_pick import (
    FilterModule,
)


class TestOspPodPick(unittest.TestCase):
    def setUp(self):
        self.osp_pod_pick = FilterModule().filters()["osp_pod_pick"]

    def test_picks_sorted_index_zero(self):
        # Already label-filtered lists may mix hashed and bare names across envs
        self.assertEqual(
            self.osp_pod_pick(["cinder-a4403-api-1", "cinder-a4403-api-0"]),
            "cinder-a4403-api-0",
        )

    def test_picks_index(self):
        self.assertEqual(
            self.osp_pod_pick(
                ["cinder-a4403-api-0", "cinder-a4403-api-1"],
                index=1,
            ),
            "cinder-a4403-api-1",
        )

    def test_k8s_resources(self):
        pods = [
            {"metadata": {"name": "cinder-8bcd4-api-1"}},
            {"metadata": {"name": "cinder-8bcd4-api-0"}},
        ]
        self.assertEqual(self.osp_pod_pick(pods), "cinder-8bcd4-api-0")

    def test_empty_raises(self):
        with self.assertRaises(AnsibleFilterError):
            self.osp_pod_pick([])

    def test_bad_index_raises(self):
        with self.assertRaises(AnsibleFilterError):
            self.osp_pod_pick(["cinder-api-0"], index=1)

    def test_rejects_non_list(self):
        with self.assertRaises(AnsibleFilterTypeError):
            self.osp_pod_pick("cinder-api-0")


if __name__ == "__main__":
    unittest.main()
