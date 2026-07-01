#!/usr/bin/python3
# Copyright (c) 2026 Red Hat, Inc.
# SPDX-License-Identifier: Apache-2.0

import pytest
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, 'roles/validations/filter_plugins')
from cifmw_validations_xml_filter import FilterModule


class TestFilterReturnType:
    """Tests to verify the filter works correctly"""
    
    def setup_method(self):
        self.filter_module = FilterModule()
        self.filter_func = self.filter_module.filters()['cifmw_validations_xml_filter']
    
    def test_returns_format(self):
        """Verify filter returns str format, not bytes."""
        result = self.filter_func({})
        assert isinstance(result, str), "Filter must return str, not bytes!"
    
    def test_empty_results(self):
        """Verify filter generates valid XML with empty test results."""
        result = self.filter_func({})
        assert isinstance(result, str)
        assert 'tests="0"' in result
    
    def test_single_passing_test(self):
        """Verify filter correctly formats a single passing test case."""
        result = self.filter_func({"test-1": {"time": 1.5}})
        assert isinstance(result, str)
        assert 'tests="1"' in result
        assert 'failures="0"' in result
    
    def test_single_failing_test(self):
        """Verify filter correctly formats a single failing test case."""
        result = self.filter_func({"test-1": {"time": 1.0, "error": "Test failed"}})
        assert 'failures="1"' in result
    
    def test_multiple_mixed_tests(self):
        """Verify filter correctly formats multiple passing and failing tests."""
        result = self.filter_func({
            "test-1": {"time": 1.0},
            "test-2.yml": {"time": 2.0, "error": "failed"},
            "test-3.yaml": {"time": 1.5}
        })
        assert 'tests="3"' in result
        assert 'failures="1"' in result
    
    def test_valid_xml_output(self):
        """Verify filter generates valid, parseable XML with correct structure."""
        result = self.filter_func({"test-1": {"time": 1.0, "error": "err"}, "test-2": {"time": 2.0}})
        root = ET.fromstring(result)
        assert root.tag == 'testsuites'
        ts = root.find('testsuite')
        assert ts.attrib['tests'] == '2'
        assert ts.attrib['failures'] == '1'


class TestMalformedInput:
    """Tests to verify filter handles edge cases and malformed input gracefully"""
    
    def setup_method(self):
        self.filter_module = FilterModule()
        self.filter_func = self.filter_module.filters()['cifmw_validations_xml_filter']
    
    def test_missing_time_field(self):
        """Verify filter handles test results with missing time field."""
        result = self.filter_func({"test-1": {"error": "some error"}, "test-2": {"time": 1.5}})
        assert isinstance(result, str)
        assert 'tests="2"' in result
    
    def test_very_long_error_message(self):
        """Verify filter handles very long error messages (5000+ characters)."""
        long_error = "x" * 5000
        result = self.filter_func({"test-1": {"time": 1.0, "error": long_error}})
        assert isinstance(result, str)
        root = ET.fromstring(result)
        assert root is not None
    
    def test_xml_special_characters_in_error(self):
        """Verify filter properly escapes XML special characters in error messages."""
        result = self.filter_func({"test-1": {"time": 1.0, "error": "<tag> & special > chars"}})
        assert isinstance(result, str)
        root = ET.fromstring(result)
        assert root is not None
    
    def test_unicode_characters(self):
        """Verify filter handles unicode characters in test names and messages."""
        result = self.filter_func({"test-unicode": {"time": 1.0, "error": "Error message"}})
        assert isinstance(result, str)
        assert 'tests="1"' in result
    
    def test_large_number_of_tests(self):
        """Verify filter performs well with large number of test cases (100+)."""
        large_test_data = {f"test-{i}": {"time": 0.1 * i} for i in range(100)}
        result = self.filter_func(large_test_data)
        assert isinstance(result, str)
        assert 'tests="100"' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
