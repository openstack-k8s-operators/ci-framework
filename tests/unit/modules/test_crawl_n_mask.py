import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from plugins.modules import crawl_n_mask as cnm


class TestCrawlNMask:

    @pytest.mark.parametrize(
        "test_dir, expected_files",
        [
            ("/test", [("/test", [], ["file.yaml"])]),
            ("/controller", [("/controller", [], ["another.yaml"])]),
        ],
    )
    def test_crawl_true(self, test_dir, expected_files):
        with patch("os.walk") as mock_walk, patch(
            "plugins.modules.crawl_n_mask.Pool"
        ) as mock_pool:
            mock_walk.return_value = expected_files
            # Mock the Pool context manager and map method
            mock_pool_instance = MagicMock()
            mock_pool.return_value.__enter__.return_value = mock_pool_instance
            mock_pool_instance.map.return_value = [True]  # At least one file changed
            module = MagicMock()
            changed = cnm.crawl(module, test_dir)
            assert changed

    @pytest.mark.parametrize(
        "test_dir, expected_files",
        [
            ("/tmp", [("/tmp", [], ["ignore.yaml"])]),
            ("/controller", [("/controller", [], ["notyaml.log"])]),
            ("venv", [("venv", [], ["should_be_skipped.yaml"])]),
            ("crc", [("crc", [], ["skip_me_venv.yaml"])]),
        ],
    )
    def test_crawl_false(self, test_dir, expected_files):
        with patch("os.walk") as mock_walk, patch(
            "plugins.modules.crawl_n_mask.Pool"
        ) as mock_pool:
            mock_walk.return_value = expected_files
            # Mock the Pool context manager and map method
            mock_pool_instance = MagicMock()
            mock_pool.return_value.__enter__.return_value = mock_pool_instance
            mock_pool_instance.map.return_value = [False]  # No files changed
            module = MagicMock()
            changed = cnm.crawl(module, test_dir)
            assert not changed

    def test_get_masked_string_scenario_1(self):
        example_value = "test1234"
        expected_value = "te**********34"
        test_value = cnm._get_masked_string(example_value)
        assert expected_value == test_value

    def test_get_masked_string_scenario_2(self):
        example_value = "examplea_keytab"
        expected_value = "ex**********ab"
        test_value = cnm._get_masked_string(example_value)
        assert expected_value == test_value

    def test_get_masked_string_scenario_3(self):
        example_value = ""
        expected_value = ""
        test_value = cnm._get_masked_string(example_value)
        assert expected_value == test_value

    def test_get_masked_string_scenario_4(self):
        example_value = "test"
        expected_value = "te**********"
        test_value = cnm._get_masked_string(example_value)
        assert expected_value == test_value

    @pytest.mark.parametrize(
        "input_line, expected_output",
        [
            # Test python dict quoted pattern
            (
                "'admin_password': 'SuperSecret123'",
                "'admin_password': 'Su**********23'",
            ),
            (
                '"AdminPassword": "MyP@ssw0rd"',
                '"AdminPassword": "My**********rd"',
            ),
            # Test numeric passwords
            (
                "'db-password': 123456789",
                "'db-password': 12**********89",
            ),
            # Test empty value
            (
                "password: ''",
                "password: ''",
            ),
            # Test plain key-value pattern
            (
                "admin_password: secret123",
                "admin_password: se**********23",
            ),
            (
                'password: "abc123"',
                'password: "ab**********23"',
            ),
            (
                "password: 'abc123'",
                "password: 'ab**********23'",
            ),
            (
                "mysql_root_password=MyPassword",
                "mysql_root_password=My**********rd",
            ),
            # Test SHA256 tokens - treated as plain key:value
            (
                "X-Auth-Token sha256~abc123def456ghi789",
                "X-Auth-Token sha256~**********",
            ),
            # Test Bearer tokens - value gets masked
            (
                "bearerToken: eyJhbGciOiJIU2d12ansnR5cCI6IkpXVCJ9",
                "bearerToken: ey**********J9",
            ),
            # Test connection strings - credentials in URL get masked
            (
                "admin_password in mysql://user:password123@localhost:3306/db",
                "admin_password in mysql://**********:**********@:3306/db",
            ),
            # Test line without secrets - should remain unchanged
            (
                "This is a normal log line without secrets",
                "This is a normal log line without secrets",
            ),
            # Test multiple secrets in one line
            (
                "'admin_password': 'secret1' and 'db-password'= 'secret2'",
                "'admin_password': 'se**********t1' and 'db-password'= 'se**********t2'",
            ),
            # Test additional keys from PROTECT_KEYS
            (
                "redis_password: myRedisSecret",
                "redis_password: my**********et",
            ),
            (
                "clientSecret:oauth2secret",
                "clientSecret:oa**********et",
            ),
            (
                "postgresPassword :dbP@ssw0rd!",
                "postgresPassword :db**********d!",
            ),
            (
                "'BARBICAN_SIMPLE_CRYPTO_ENCRYPTION_KEY' : 'sE12312341==48943y21'",
                "'BARBICAN_SIMPLE_CRYPTO_ENCRYPTION_KEY' : 'sE**********21'",
            ),
        ],
    )
    def test_mask_log_line(self, input_line, expected_output):
        result = cnm.mask_log_line(input_line)
        assert result == expected_output

    def test_should_skip_ansible_line(self):
        assert cnm.should_skip_ansible_line("TASK [Install packages]") == True
        assert cnm.should_skip_ansible_line("TASK: Configure database") == True
        assert cnm.should_skip_ansible_line("PLAY [Deploy application]") == True
        assert cnm.should_skip_ansible_line("Some regular log line") == False

    def test_mask_file_with_real_file(self):
        # Create a temporary file with secrets
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            f.write("admin_password: SuperSecret123\n")
            f.write(
                "db_connection: admin_password in mysql://user:pass123@localhost/db\n"
            )
            f.write("normal_config: some_value\n")
            temp_path = f.name

        try:
            # Mask the file
            changed = cnm.mask_file(temp_path)

            # Verify it was changed
            assert changed == True

            # Read the masked file
            with open(temp_path, "r") as f:
                content = f.read()

            # Verify secrets are masked
            assert "SuperSecret123" not in content
            assert "pass123" not in content
            assert "**********" in content

            # Verify normal content is preserved
            assert "normal_config: some_value" in content

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_mask_file_no_changes(self):
        # Create a temporary file without secrets
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as f:
            f.write("normal_config: some_value\n")
            f.write("another_config: another_value\n")
            temp_path = f.name

        try:
            # Mask the file
            changed = cnm.mask_file(temp_path)

            # Verify it was not changed
            assert changed == False

            # Read the file
            with open(temp_path, "r") as f:
                content = f.read()

            # Verify content is unchanged
            assert "normal_config: some_value" in content
            assert "another_config: another_value" in content

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_mask_file_preserves_ansible_task_headers(self):
        # Create a temporary file with Ansible task headers
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            f.write("TASK [Setup admin_password variable]\n")
            f.write("admin_password: SuperSecret123\n")
            f.write("PLAY [Configure mysql_root_password]\n")
            temp_path = f.name

        try:
            # Mask the file
            changed = cnm.mask_file(temp_path)

            # Read the masked file
            with open(temp_path, "r") as f:
                content = f.read()

            # Verify task headers are preserved exactly
            assert "TASK [Setup admin_password variable]" in content
            assert "PLAY [Configure mysql_root_password]" in content

            # Verify the actual secret is masked
            assert "SuperSecret123" not in content
            assert "**********" in content

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
