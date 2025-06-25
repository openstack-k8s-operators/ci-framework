import pytest
from unittest.mock import patch, MagicMock
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

    def test_partial_mask_scenario_1(self):
        example_value = " 'test1234'\n"
        expected_value = " 'te**********34'\n"
        test_value = cnm.partial_mask(example_value)
        assert expected_value == test_value

    def test_partial_mask_scenario_2(self):
        example_value = " osp_ci_framework_keytab\n"
        expected_value = " 'os**********ab'\n"
        test_value = cnm.partial_mask(example_value)
        assert expected_value == test_value

    def test_partial_mask_scenario_3(self):
        example_value = " ''\n"
        test_value = cnm.partial_mask(example_value)
        assert test_value is None

    def test_partial_mask_scenario_4(self):
        example_value = "tet"
        expected_value = "'te**********'"
        test_value = cnm.partial_mask(example_value)
        assert expected_value == test_value
