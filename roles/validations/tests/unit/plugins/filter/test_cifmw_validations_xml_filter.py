#!/usr/bin/python3
"""
Unit tests for cifmw_validations_xml_filter.

These tests verify that the filter:
1. Returns str (not bytes) - fixes the hang issue
2. Handles malformed input gracefully
3. Generates valid XML output
"""

import pytest
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, 'roles/validations/filter_plugins')
from cifmw_validations_xml_filter import FilterModule


class TestFilterReturnType:
    """Tests to verify the fix for the hang issue"""
    
    def setup_method(self):
        self.filter_module = FilterModule()
        self.filter_func = self.filter_module.filters()['cifmw_validations_xml_filter']
    
    def test_returns_string_not_bytes(self):
        """
        CRITICAL TEST: Ensure filter returns str, not bytes.
        
        This test verifies the fix for the hang issue.
        Before fix: returned bytes → Ansible hangs
        After fix: returns str → Ansible processes normally
        """
        result = self.filter_func({})
        assert isinstance(result, str), \
            f"Filter must return str, not {type(result).__name__}. " \
            "Returning bytes causes Ansible to hang!"
    
    def test_empty_results(self):
        """Test with empty test results"""
        result = self.filter_func({})
        assert isinstance(result, str)
        assert 'tests="0"' in result
    
    def test_single_passing_test(self):
        """Test with single passing test"""
        result = self.filter_func({"test-1": {"time": 1.5}})
        assert isinstance(result, str)
        assert 'tests="1"' in result
        assert 'failures="0"' in result
    
    def test_single_failing_test(self):
        """Test with single failing test"""
        result = self.filter_func({
            "test-1": {"time": 1.0, "error": "Test failed"}
        })
        assert 'failures="1"' in result
    
    def test_multiple_mixed_tests(self):
        """Test with multiple passing and failing tests"""
        result = self.filter_func({
            "test-1": {"time": 1.0},
            "test-2.yml": {"time": 2.0, "error": "failed"},
            "test-3.yaml": {"time": 1.5}
        })
        assert 'tests="3"' in result
        assert 'failures="1"' in result
    
    def test_valid_xml_output(self):
        """Verify output is valid, parseable XML"""
        result = self.filter_func({
            "test-1": {"time": 1.0, "error": "err"}
        })
        
        # Should be parseable as XML (not corrupted)
        root = ET.fromstring(result)
        assert root.tag == 'testsuites'
        
        # Verify structure
        ts = root.find('testsuite')
        assert ts is not None
        assert ts.attrib['name'] == 'validations'


class TestMalformedInput:
    """Tests with malformed/edge-case input to ensure robustness"""
    
    def setup_method(self):
        self.filter_module = FilterModule()
        self.filter_func = self.filter_module.filters()['cifmw_validations_xml_filter']
    
    def test_missing_time_field(self):
        """Test with missing time field in results"""
        result = self.filter_func({
            "test-1": {"error": "some error"},
            "test-2": {"time": 1.5}
        })
        assert isinstance(result, str)
        assert 'tests="2"' in result
    
    def test_very_long_error_message(self):
        """Test with very long error message (5000+ chars)"""
        long_error = "x" * 5000
        result = self.filter_func({
            "test-1": {"time": 1.0, "error": long_error}
        })
        assert isinstance(result, str)
        # Should still be valid XML
        root = ET.fromstring(result)
        assert root is not None
    
    def test_xml_special_characters_in_error(self):
        """Test with XML special characters in error message"""
        result = self.filter_func({
            "test-1": {"time": 1.0, "error": "<tag> & special > chars"}
        })
        assert isinstance(result, str)
        # Should be properly escaped
        root = ET.fromstring(result)
        assert root is not None
    
    def test_unicode_characters(self):
        """Test with unicode characters in test names and errors"""
        result = self.filter_func({
            "test-unicode": {"time": 1.0, "error": "Error with unicode"}
        })
        assert isinstance(result, str)
        assert 'tests="1"' in result
    
    def test_large_number_of_tests(self):
        """Test with large number of test cases (100+)"""
        large_test_data = {
            f"test-{i}": {"time": 0.1 * i}
            for i in range(100)
        }
        result = self.filter_func(large_test_data)
        assert isinstance(result, str)
        assert 'tests="100"' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
