"""Tests for output formatter."""

import json
import unittest
from unittest.mock import patch

from summit_seo.cli.output_formatter import (
    OutputFormat,
    PlainFormatter,
    JsonFormatter,
    CsvFormatter,
    TableFormatter,
    YamlFormatter,
    OutputManager,
    format_result,
    format_error,
    format_summary,
    format_list,
    set_output_format
)


class TestOutputFormatters(unittest.TestCase):
    """Test cases for output formatters."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test data
        self.test_result = {
            "title": "Test Analysis",
            "score": 85.5,
            "issues": [
                {"description": "Issue 1", "severity": "high", "location": "header"},
                {"description": "Issue 2", "severity": "medium", "location": "body"}
            ],
            "recommendations": [
                {"description": "Recommendation 1", "priority": "high", "impact": "major"},
                {"description": "Recommendation 2", "priority": "medium", "impact": "moderate"}
            ],
            "details": {
                "key1": "value1",
                "key2": "value2"
            }
        }
        
        self.test_summary = {
            "title": "Test Summary",
            "total_score": 85.5,
            "issues_count": 2,
            "recommendations_count": 2
        }
        
        self.test_list = [
            {"name": "Item 1", "value": 10},
            {"name": "Item 2", "value": 20},
            {"name": "Item 3", "value": 30}
        ]
        
        self.test_error = "Test error message"
    
    def test_plain_formatter(self):
        """Test plain text formatter."""
        formatter = PlainFormatter()
        
        # Test result formatting
        result_str = formatter.format_result(self.test_result)
        self.assertIn("Test Analysis", result_str)
        self.assertIn("Score: 85.5/100", result_str)
        self.assertIn("Issue 1", result_str)
        self.assertIn("Severity: high", result_str)
        self.assertIn("Recommendation 1", result_str)
        
        # Test error formatting
        error_str = formatter.format_error(self.test_error)
        self.assertIn("Error: Test error message", error_str)
        
        # Test summary formatting
        summary_str = formatter.format_summary(self.test_summary)
        self.assertIn("Test Summary", summary_str)
        self.assertIn("total_score: 85.5", summary_str)
        
        # Test list formatting
        list_str = formatter.format_list(self.test_list, "Test List")
        self.assertIn("Test List", list_str)
        self.assertIn("Item 1", list_str)
        self.assertIn("value: 10", list_str)
    
    def test_json_formatter(self):
        """Test JSON formatter."""
        formatter = JsonFormatter()
        
        # Test result formatting
        result_str = formatter.format_result(self.test_result)
        result_dict = json.loads(result_str)
        self.assertEqual(result_dict["title"], "Test Analysis")
        self.assertEqual(result_dict["score"], 85.5)
        self.assertEqual(len(result_dict["issues"]), 2)
        
        # Test error formatting
        error_str = formatter.format_error(self.test_error)
        error_dict = json.loads(error_str)
        self.assertEqual(error_dict["error"], "Test error message")
        
        # Test summary formatting
        summary_str = formatter.format_summary(self.test_summary)
        summary_dict = json.loads(summary_str)
        self.assertEqual(summary_dict["title"], "Test Summary")
        
        # Test list formatting
        list_str = formatter.format_list(self.test_list, "Test List")
        list_dict = json.loads(list_str)
        self.assertEqual(list_dict["title"], "Test List")
        self.assertEqual(len(list_dict["items"]), 3)
    
    def test_csv_formatter(self):
        """Test CSV formatter."""
        formatter = CsvFormatter()
        
        # Test result formatting
        result_str = formatter.format_result(self.test_result)
        self.assertIn("Issues", result_str)
        self.assertIn("Description,Severity,Location", result_str)
        self.assertIn("Issue 1,high,header", result_str)
        self.assertIn("Recommendations", result_str)
        
        # Test error formatting
        error_str = formatter.format_error(self.test_error)
        self.assertIn("Error,", error_str)
        self.assertIn("Test error message", error_str)
        
        # Test list formatting
        list_str = formatter.format_list(self.test_list, "Test List")
        self.assertIn("Test List", list_str)
        self.assertIn("name,value", list_str)
        self.assertIn("Item 1,10", list_str)
    
    def test_table_formatter(self):
        """Test table formatter."""
        # Use fixed width for predictable output
        formatter = TableFormatter(max_width=100)
        
        # Test result formatting
        result_str = formatter.format_result(self.test_result)
        self.assertIn("Test Analysis", result_str)
        self.assertIn("Score", result_str)
        self.assertIn("85.5/100", result_str)
        self.assertIn("DESCRIPTION", result_str)
        self.assertIn("SEVERITY", result_str)
        self.assertIn("Issue 1", result_str)
        
        # Test error formatting
        error_str = formatter.format_error(self.test_error)
        self.assertIn("Error", error_str)
        self.assertIn("Test error message", error_str)
        
        # Test list formatting
        list_str = formatter.format_list(self.test_list, "Test List")
        self.assertIn("Test List", list_str)
        self.assertIn("NAME", list_str)
        self.assertIn("VALUE", list_str)
        self.assertIn("Item 1", list_str)
    
    @patch('summit_seo.cli.output_formatter.logger')
    def test_yaml_formatter_with_yaml(self, mock_logger):
        """Test YAML formatter with yaml module available."""
        # Mock yaml module
        mock_yaml = unittest.mock.MagicMock()
        
        # Create formatter with mocked yaml
        formatter = YamlFormatter()
        formatter.yaml = mock_yaml
        
        # Test result formatting
        formatter.format_result(self.test_result)
        mock_yaml.dump.assert_called()
        
        # Test error formatting
        formatter.format_error(self.test_error)
        self.assertEqual(mock_yaml.dump.call_count, 2)
        
        # Test summary formatting
        formatter.format_summary(self.test_summary)
        self.assertEqual(mock_yaml.dump.call_count, 3)
        
        # Test list formatting
        formatter.format_list(self.test_list, "Test List")
        self.assertEqual(mock_yaml.dump.call_count, 4)
    
    @patch('summit_seo.cli.output_formatter.logger')
    def test_yaml_formatter_without_yaml(self, mock_logger):
        """Test YAML formatter with yaml module not available."""
        # Create formatter with yaml set to None
        formatter = YamlFormatter()
        formatter.yaml = None
        
        # Test result formatting (should fall back to JSON)
        result_str = formatter.format_result(self.test_result)
        result_dict = json.loads(result_str)
        self.assertEqual(result_dict["title"], "Test Analysis")
        
        # Test error formatting
        error_str = formatter.format_error(self.test_error)
        error_dict = json.loads(error_str)
        self.assertEqual(error_dict["error"], "Test error message")


class TestOutputManager(unittest.TestCase):
    """Test cases for output manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = OutputManager()
        self.test_data = {"key": "value"}
    
    def test_default_formatter(self):
        """Test default formatter is PlainFormatter."""
        self.assertIsInstance(self.manager.formatter, PlainFormatter)
    
    def test_set_format(self):
        """Test changing the output format."""
        # Change to JSON format
        self.manager.set_format(OutputFormat.JSON)
        self.assertIsInstance(self.manager.formatter, JsonFormatter)
        
        # Change to CSV format
        self.manager.set_format(OutputFormat.CSV)
        self.assertIsInstance(self.manager.formatter, CsvFormatter)
        
        # Change to TABLE format
        self.manager.set_format(OutputFormat.TABLE)
        self.assertIsInstance(self.manager.formatter, TableFormatter)
        
        # Change to YAML format
        self.manager.set_format(OutputFormat.YAML)
        self.assertIsInstance(self.manager.formatter, YamlFormatter)
        
        # Change back to PLAIN format
        self.manager.set_format(OutputFormat.PLAIN)
        self.assertIsInstance(self.manager.formatter, PlainFormatter)
    
    def test_format_methods(self):
        """Test all formatting methods."""
        # Mock formatter
        mock_formatter = unittest.mock.MagicMock()
        self.manager.formatter = mock_formatter
        
        # Test all methods
        self.manager.format_result(self.test_data)
        mock_formatter.format_result.assert_called_with(self.test_data)
        
        self.manager.format_error("error")
        mock_formatter.format_error.assert_called_with("error")
        
        self.manager.format_summary(self.test_data)
        mock_formatter.format_summary.assert_called_with(self.test_data)
        
        self.manager.format_list([1, 2, 3], "title")
        mock_formatter.format_list.assert_called_with([1, 2, 3], "title")


class TestGlobalFunctions(unittest.TestCase):
    """Test cases for global formatting functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_data = {"key": "value"}
    
    @patch('summit_seo.cli.output_formatter.output_manager')
    def test_format_functions(self, mock_manager):
        """Test global formatting functions."""
        # Test all global functions
        format_result(self.test_data)
        mock_manager.format_result.assert_called_with(self.test_data)
        
        format_error("error")
        mock_manager.format_error.assert_called_with("error")
        
        format_summary(self.test_data)
        mock_manager.format_summary.assert_called_with(self.test_data)
        
        format_list([1, 2, 3], "title")
        mock_manager.format_list.assert_called_with([1, 2, 3], "title")
        
        # Test set format function
        set_output_format(OutputFormat.JSON, indent=4)
        mock_manager.set_format.assert_called_with(OutputFormat.JSON, indent=4)


if __name__ == '__main__':
    unittest.main() 