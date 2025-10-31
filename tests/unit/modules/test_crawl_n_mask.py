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

    @pytest.mark.parametrize(
        "file_format, example_value, expected_value",
        [
            ("yaml", " 'test1234'\n", " 'te**********34'\n"),
            ("yaml", " osp_ci_framework_keytab\n", " 'os**********ab'\n"),
            ("yaml", " ''\n", None),
            ("yaml", "tet", "'te**********'"),
            ("json", ' "test1234",\n', ' "te**********34",\n'),
            ("json", ' "osp_ci_framework_keytab",\n', ' "os**********ab",\n'),
            ("json", " ''\n", None),
            ("json", '"tet"', '"te**********"'),
        ],
    )
    def test_partial_mask(self, file_format, example_value, expected_value):
        test_value = cnm.partial_mask(example_value, file_format)
        assert expected_value == test_value
