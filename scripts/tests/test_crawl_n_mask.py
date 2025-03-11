#!/usr/bin/python
import copy
import unittest
import os
import yaml
from typing import Optional, Union
from scripts.crawl_n_mask import SecretMask

# sample directory used to load yaml files
SAMPLE_DIR = "samples"


class TestSecretMask(unittest.TestCase):
    """
    The class that implements basic tests for
    SecretMask.
    """

    def _read_yaml_sample(self, path) -> Optional[Union[list, None]]:
        """
        utility function to load a sample yaml file.
        """
        try:
            assert path is not None
            with open(path, "r") as f:
                return list(yaml.safe_load_all(f))
        except (FileNotFoundError, yaml.YAMLError) as e:
            print(f"Error while reading YAML: {e}")
            # sys.exit(-1)
        return None

    def test_mask_yaml(self):
        """
        For each file present in the tests/samples we:
        - Load the file by reading the yaml definition
        - Process using the SecreMask module
        - assert the content of the secret is
          different
        """
        for root, _, files in os.walk(SAMPLE_DIR):
            for f in files:
                print("Processing file %s" % f)
                actual = self._read_yaml_sample(os.path.join(root, f))
                expected = copy.deepcopy(actual)
                # Mask secret by processing the data section
                # of the yaml file we got
                SecretMask(os.path.join(root, f))._process_list(expected)

                """
                files are named secret{1, 2, 3, ... N}: for these secrets
                we expect a change in their content because sensitive
                data has been masked; the sample file named "nochange.yaml",
                instead, is the one that does not contain any sensitive data,
                hence no masking is applied and we expect the original data
                content being the same as the processed one.
                """
                if "nochange" in f:
                    # the content in nochange.yaml should
                    # not change after processing it
                    self.assertEqual(actual, expected)
                else:
                    # The content (secret values) should be
                    # different
                    self.assertNotEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
