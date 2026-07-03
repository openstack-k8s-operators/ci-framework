# Copyright Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Unit tests for merge_yaml_override.py deep_merge function."""

import sys
import unittest
from pathlib import Path

# Import the deep_merge function from the reproducer role
sys.path.insert(0, str(Path(__file__).parents[3] / "roles" / "reproducer" / "files"))
from merge_yaml_override import deep_merge


class TestDeepMerge(unittest.TestCase):
    """Test deep_merge function behavior."""

    def test_empty_dict_overrides_non_empty_dict(self):
        """Empty dict in override should replace base dict entirely."""
        base = {"hook": {"type": "playbook", "source": "test.yml"}}
        override = {"hook": {}}
        result = deep_merge(base, override)
        self.assertEqual(result, {"hook": {}})

    def test_nested_empty_dict_override(self):
        """Empty dict at nested level should override base value."""
        base = {"outer": {"inner": {"key": "value"}}}
        override = {"outer": {"inner": {}}}
        result = deep_merge(base, override)
        self.assertEqual(result, {"outer": {"inner": {}}})

    def test_normal_dict_merge(self):
        """Non-empty dicts should merge recursively, combining keys."""
        base = {"a": {"x": 1, "y": 2}}
        override = {"a": {"y": 3, "z": 4}}
        result = deep_merge(base, override)
        expected = {"a": {"x": 1, "y": 3, "z": 4}}
        self.assertEqual(result, expected)

    def test_scalar_override(self):
        """Scalar values should override base completely."""
        base = {"key": "old"}
        override = {"key": "new"}
        result = deep_merge(base, override)
        self.assertEqual(result, {"key": "new"})

    def test_list_override(self):
        """Lists should override entirely, not merge elements."""
        base = {"items": [1, 2, 3]}
        override = {"items": [4, 5]}
        result = deep_merge(base, override)
        self.assertEqual(result, {"items": [4, 5]})

    def test_none_base(self):
        """When base is None, override should win."""
        base = None
        override = {"key": "value"}
        result = deep_merge(base, override)
        self.assertEqual(result, {"key": "value"})

    def test_none_override(self):
        """When override is None, base should win."""
        base = {"key": "value"}
        override = None
        result = deep_merge(base, override)
        self.assertEqual(result, {"key": "value"})

    def test_both_none(self):
        """When both are None, None should be returned."""
        base = None
        override = None
        result = deep_merge(base, override)
        self.assertIsNone(result)

    def test_manila_hook_disable_scenario(self):
        """Real-world scenario: disabling Manila hook in day2 scenarios.

        This is the regression test for the PreMetal bug where empty dict
        failed to override the hook definition from bootstrap phase.
        """
        # Bootstrap phase - hook defined in 05-hooks.yaml
        base = {
            "post_admin_setup_05_create_manila_resources": {
                "type": "playbook",
                "source": "manila_create_default_resources.yml",
            }
        }
        # Testing phase - day2/scenario.yaml tries to disable with {}
        override = {"post_admin_setup_05_create_manila_resources": {}}

        result = deep_merge(base, override)

        # Hook should be disabled (empty dict)
        expected = {"post_admin_setup_05_create_manila_resources": {}}
        self.assertEqual(result, expected)

    def test_multiple_hooks_disable(self):
        """Test disabling multiple hooks simultaneously."""
        base = {
            "post_admin_setup_05_create_manila_resources": {
                "type": "playbook",
                "source": "manila.yml",
            },
            "post_deploy_90_Watcher_Download_needed_tools": {
                "inventory": "/path/to/inventory",
                "source": "/path/to/download_tools.yaml",
            },
            "post_deploy_91_Watcher_Patch_Prometheus": {
                "source": "/path/to/prometheus.yaml",
                "type": "playbook",
            },
        }
        override = {
            "post_admin_setup_05_create_manila_resources": {},
            "post_deploy_90_Watcher_Download_needed_tools": {},
            "post_deploy_91_Watcher_Patch_Prometheus": {},
        }

        result = deep_merge(base, override)

        expected = {
            "post_admin_setup_05_create_manila_resources": {},
            "post_deploy_90_Watcher_Download_needed_tools": {},
            "post_deploy_91_Watcher_Patch_Prometheus": {},
        }
        self.assertEqual(result, expected)

    def test_partial_hook_override_with_empty_dict(self):
        """Test scenario where some hooks are disabled, others modified."""
        base = {
            "hook_a": {"type": "playbook", "source": "a.yml"},
            "hook_b": {"type": "playbook", "source": "b.yml"},
            "hook_c": {"type": "playbook", "source": "c.yml"},
        }
        override = {
            "hook_a": {},  # Disable this one
            "hook_b": {"type": "shell", "source": "b_modified.yml"},  # Modify
            # hook_c not mentioned - should keep base
        }

        result = deep_merge(base, override)

        expected = {
            "hook_a": {},
            "hook_b": {"type": "shell", "source": "b_modified.yml"},
            "hook_c": {"type": "playbook", "source": "c.yml"},
        }
        self.assertEqual(result, expected)

    def test_deeply_nested_empty_dict(self):
        """Test empty dict override at multiple nesting levels."""
        base = {"level1": {"level2": {"level3": {"level4": {"key": "value"}}}}}
        override = {"level1": {"level2": {"level3": {}}}}  # Clear everything at level3

        result = deep_merge(base, override)

        expected = {"level1": {"level2": {"level3": {}}}}
        self.assertEqual(result, expected)

    def test_empty_dict_alongside_normal_merge(self):
        """Test empty dict override mixed with normal dict merging."""
        base = {
            "section_a": {"x": 1, "y": 2},
            "section_b": {"p": "old", "q": "old"},
        }
        override = {
            "section_a": {},  # Clear section_a
            "section_b": {"q": "new", "r": "new"},  # Merge into section_b
        }

        result = deep_merge(base, override)

        expected = {
            "section_a": {},
            "section_b": {"p": "old", "q": "new", "r": "new"},
        }
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
