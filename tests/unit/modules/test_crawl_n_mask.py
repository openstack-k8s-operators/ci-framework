from xmlrpc.client import Fault

import pytest
from unittest.mock import patch, MagicMock, mock_open

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
            "plugins.modules.crawl_n_mask.mask"
        ) as mock_mask:
            mock_walk.return_value = expected_files
            mock_mask.return_value = True
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
            "plugins.modules.crawl_n_mask.mask"
        ) as mock_mask:
            mock_walk.return_value = expected_files
            mock_mask.return_value = False
            module = MagicMock()
            changed = cnm.crawl(module, test_dir)
            assert not changed

    @patch("builtins.open", new_callable=mock_open, read_data="key: value")
    @patch("yaml.safe_load_all")
    def test_read_yaml_success(self, mock_load, mock_open_file):
        mock_load.return_value = [{"key": "value"}]
        module = MagicMock()
        result = cnm.read_yaml(module, "/fake/file.yaml")
        assert result == [{"key": "value"}]

    def test_apply_regex(self):
        value = "password=supersecret"
        masked = cnm.apply_regex(value)
        assert cnm.MASK_STR in masked

    def test_apply_regex_no_match(self):
        value = "normal=stuff"
        result = cnm.apply_regex(value)
        assert result == value

    @pytest.mark.parametrize(
        "data, ismasked",
        [
            ([{"password": "secret"}], True),
            ([{"secret": "value"}], True),
            ([{True: "test_bool_key"}], False),
            ([{1: "int_key"}], False),
            ([{1.1: "float_key"}], False),
        ],
    )
    def test_process_list(self, data, ismasked):
        cnm.process_list(data)
        if ismasked:
            assert cnm.MASK_STR in [list(item.values())[0] for item in data]
        else:
            assert cnm.MASK_STR not in [list(item.values())[0] for item in data]

    def test_apply_mask(self):
        data = {"password": "secret", "normal": "data"}
        cnm.apply_mask(data)
        assert data["password"] == cnm.MASK_STR

    @patch("plugins.modules.crawl_n_mask.read_yaml")
    @patch("plugins.modules.crawl_n_mask.write_yaml")
    def test_mask_yaml(self, mock_write, mock_read):
        mock_read.return_value = [{"password": "secret"}]
        mock_write.return_value = True
        module = MagicMock()
        changed = cnm.mask_yaml(module, "/fake/file.yaml")
        assert changed
