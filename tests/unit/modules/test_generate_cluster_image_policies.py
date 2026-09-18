# Copyright: (c) 2026, Red Hat

# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import os
import tempfile

from unittest.mock import patch

from ansible_collections.cifmw.general.tests.unit.utils import (
    ModuleBaseTestCase,
    set_module_args,
    AnsibleExitJson,
    AnsibleFailJson,
)
from ansible_collections.cifmw.general.plugins.modules import (
    generate_cluster_image_policies,
)


class TestGenerateClusterImagePolicies(ModuleBaseTestCase):

    def test_negative_missing_params(self):
        """Check failure when missing parameters."""

        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            generate_cluster_image_policies.main()

    def test_no_input_files(self):
        """Check failure when no input files are in an existing input directory."""

        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(AnsibleFailJson):
                set_module_args(
                    {
                        "input_dir": temp_dir,
                        "output_file": os.path.join(temp_dir, "Cluster.yaml"),
                    }
                )
                generate_cluster_image_policies.main()

    def test_invalid_input_file(self):
        """Check failure for an input file with correct name that doesn't contain spec section."""

        oc_mirror_contents = [
            "  imageDigestMirrors:\n",
            "  - mirrors:\n",
            "    - controller-0.ocp.openstack.lab:8443/rhoso\n",
            "    source: registry.redhat.io/rhoso\n",
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, "idms-oc-mirror.yaml"), "w") as file:
                file.writelines(oc_mirror_contents)

            with self.assertRaises(AnsibleFailJson):
                set_module_args(
                    {
                        "input_dir": temp_dir,
                        "output_file": os.path.join(temp_dir, "Cluster.yaml"),
                    }
                )
                generate_cluster_image_policies.main()

    def test_valid_input_file(self):
        """Check valid input file."""

        oc_mirror_contents = [
            "spec:\n",
            "  imageDigestMirrors:\n",
            "  - mirrors:\n",
            "    - controller-0.ocp.openstack.lab:8443/rhoso\n",
            "    source: registry.redhat.io/rhoso\n",
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, "idms-oc-mirror.yaml"), "w") as file:
                file.writelines(oc_mirror_contents)

            with self.assertRaises(AnsibleExitJson):
                set_module_args(
                    {
                        "input_dir": temp_dir,
                        "output_file": os.path.join(temp_dir, "Cluster.yaml"),
                    }
                )
                generate_cluster_image_policies.main()
