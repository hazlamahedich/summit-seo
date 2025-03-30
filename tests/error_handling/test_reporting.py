"""Tests for the error reporting module."""

import json
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

import pytest

from summit_seo.error_handling.reporting import (
    ErrorContext,
    ReportedError,
    ConsoleErrorReporter,
    FileErrorReporter
)
from summit_seo.error_handling.suggestions import (
    ActionableSuggestion,
    SuggestionSeverity,
    SuggestionCategory
)


class TestErrorContext:
    """Tests for the ErrorContext class."""
    
    def test_init_with_defaults(self):
        """Test initialization with default values."""
        context = ErrorContext()
        
        assert isinstance(context.timestamp, datetime)
        assert context.operation is None
        assert context.component is None
        assert context.user_action is None
        assert "python_version" in context.environment
        assert "platform" in context.environment
        assert "timestamp" in context.environment
        assert context.inputs == {}
    
    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        timestamp = datetime.now()
        env = {"custom_env": "test_value"}
        inputs = {"url": "https://example.com"}
        
        context = ErrorContext(
            timestamp=timestamp,
            operation="Test operation",
            component="TestComponent",
            user_action="User clicked button",
            environment=env,
            inputs=inputs
        )
        
        assert context.timestamp == timestamp
        assert context.operation == "Test operation"
        assert context.component == "TestComponent"
        assert context.user_action == "User clicked button"
        assert context.environment == env
        assert context.inputs == inputs


class TestReportedError:
    """Tests for the ReportedError class."""
    
    def test_init_with_minimal_values(self):
        """Test initialization with minimal required values."""
        error = ValueError("Test error")
        
        report = ReportedError(
            error=error,
            error_type="ValueError",
            error_message="Test error"
        )
        
        assert report.error == error
        assert report.error_type == "ValueError"
        assert report.error_message == "Test error"
        assert isinstance(report.traceback, str)
        assert isinstance(report.context, ErrorContext)
        assert report.suggestions == []
    
    def test_init_with_full_values(self):
        """Test initialization with all values."""
        error = ValueError("Test error")
        traceback = "Traceback information"
        context = ErrorContext(
            operation="Test operation",
            component="TestComponent"
        )
        suggestions = [
            ActionableSuggestion(
                message="Test suggestion",
                steps=["Test step"]
            )
        ]
        
        report = ReportedError(
            error=error,
            error_type="ValueError",
            error_message="Test error",
            traceback=traceback,
            context=context,
            suggestions=suggestions
        )
        
        assert report.error == error
        assert report.error_type == "ValueError"
        assert report.error_message == "Test error"
        assert report.traceback == traceback
        assert report.context == context
        assert report.suggestions == suggestions
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        error = ValueError("Test error")
        context = ErrorContext(
            operation="Test operation",
            component="TestComponent"
        )
        suggestions = [
            ActionableSuggestion(
                message="Test suggestion",
                steps=["Test step"],
                severity=SuggestionSeverity.HIGH,
                category=SuggestionCategory.GENERAL
            )
        ]
        
        report = ReportedError(
            error=error,
            error_type="ValueError",
            error_message="Test error",
            traceback="Traceback information",
            context=context,
            suggestions=suggestions
        )
        
        result = report.to_dict()
        
        assert result["error_type"] == "ValueError"
        assert result["error_message"] == "Test error"
        assert result["traceback"] == "Traceback information"
        assert "context" in result
        assert result["context"]["operation"] == "Test operation"
        assert result["context"]["component"] == "TestComponent"
        assert "suggestions" in result
        assert len(result["suggestions"]) == 1
        assert result["suggestions"][0]["message"] == "Test suggestion"
        assert result["suggestions"][0]["steps"] == ["Test step"]
        assert result["suggestions"][0]["severity"] == "high"
        assert result["suggestions"][0]["category"] == "general"
    
    def test_to_json(self):
        """Test conversion to JSON."""
        error = ValueError("Test error")
        
        report = ReportedError(
            error=error,
            error_type="ValueError",
            error_message="Test error"
        )
        
        json_str = report.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["error_type"] == "ValueError"
        assert parsed["error_message"] == "Test error"


class TestConsoleErrorReporter:
    """Tests for the ConsoleErrorReporter class."""
    
    def test_init_with_defaults(self):
        """Test initialization with default values."""
        reporter = ConsoleErrorReporter()
        
        assert reporter.show_traceback is False
        assert reporter.colored_output is True
        assert reporter.output_stream == sys.stderr
        assert reporter.verbose is False
        assert "red" in reporter.colors
        assert "green" in reporter.colors
        assert "reset" in reporter.colors
    
    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        output_stream = MagicMock()
        
        reporter = ConsoleErrorReporter(
            show_traceback=True,
            colored_output=False,
            output_stream=output_stream,
            verbose=True
        )
        
        assert reporter.show_traceback is True
        assert reporter.colored_output is False
        assert reporter.output_stream == output_stream
        assert reporter.verbose is True
        assert reporter.colors["red"] == ""  # No color when colored_output is False
    
    def test_color_text(self):
        """Test coloring text."""
        # With colors enabled
        reporter_colored = ConsoleErrorReporter(colored_output=True)
        colored_text = reporter_colored.color_text("Test", "red")
        assert colored_text.startswith("\033[31m")
        assert colored_text.endswith("\033[0m")
        
        # With colors disabled
        reporter_plain = ConsoleErrorReporter(colored_output=False)
        plain_text = reporter_plain.color_text("Test", "red")
        assert plain_text == "Test"
        
        # With invalid color
        invalid_color = reporter_colored.color_text("Test", "invalid_color")
        assert invalid_color == "Test"
    
    @patch('summit_seo.error_handling.reporting.get_suggestion_for_error')
    def test_report_error_basic(self, mock_get_suggestion):
        """Test basic error reporting without suggestions."""
        mock_get_suggestion.return_value = []
        
        error = ValueError("Test error")
        output_stream = MagicMock()
        
        reporter = ConsoleErrorReporter(
            colored_output=False,  # Disable colors for easier testing
            output_stream=output_stream,
            verbose=False
        )
        
        with patch('summit_seo.error_handling.reporting.print') as mock_print:
            result = reporter.report_error(error)
            
            # Check that the error was reported correctly
            assert isinstance(result, ReportedError)
            assert result.error == error
            assert result.error_type == "ValueError"
            assert result.error_message == "Test error"
            
            # Verify print calls
            mock_print.assert_any_call("ERROR: ValueError", file=output_stream)
            mock_print.assert_any_call("Test error", file=output_stream)
    
    @patch('summit_seo.error_handling.reporting.get_suggestion_for_error')
    def test_report_error_with_suggestions(self, mock_get_suggestion):
        """Test error reporting with suggestions."""
        # Create test suggestions
        suggestions = [
            ActionableSuggestion(
                message="Suggestion 1",
                steps=["Step 1.1", "Step 1.2"],
                severity=SuggestionSeverity.HIGH
            ),
            ActionableSuggestion(
                message="Suggestion 2",
                steps=["Step 2"],
                severity=SuggestionSeverity.LOW,
                documentation_url="https://example.com"
            )
        ]
        mock_get_suggestion.return_value = suggestions
        
        error = ValueError("Test error")
        output_stream = MagicMock()
        
        reporter = ConsoleErrorReporter(
            colored_output=False,  # Disable colors for easier testing
            output_stream=output_stream
        )
        
        with patch('summit_seo.error_handling.reporting.print') as mock_print:
            result = reporter.report_error(error)
            
            # Check that suggestions were included
            assert result.suggestions == suggestions
            
            # Verify print calls
            mock_print.assert_any_call("Suggested actions:", file=output_stream)
            mock_print.assert_any_call("1. Suggestion 1", file=output_stream)
            mock_print.assert_any_call("   1. Step 1.1", file=output_stream)
            mock_print.assert_any_call("   2. Step 1.2", file=output_stream)
            mock_print.assert_any_call("2. Suggestion 2", file=output_stream)
            mock_print.assert_any_call("   1. Step 2", file=output_stream)
            mock_print.assert_any_call("   For more information: https://example.com", file=output_stream)


class TestFileErrorReporter:
    """Tests for the FileErrorReporter class."""
    
    def test_init_with_defaults(self):
        """Test initialization with default values."""
        with patch('os.makedirs') as mock_makedirs:
            reporter = FileErrorReporter()
            
            assert reporter.output_dir == Path("error_reports")
            assert reporter.format == "json"
            assert reporter.include_traceback is True
            assert reporter.log_to_stderr is True
            
            # Check that the output directory was created
            mock_makedirs.assert_called_once_with(Path("error_reports"), exist_ok=True)
    
    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        with patch('os.makedirs') as mock_makedirs:
            reporter = FileErrorReporter(
                output_dir="custom_dir",
                format="text",
                include_traceback=False,
                log_to_stderr=False
            )
            
            assert reporter.output_dir == Path("custom_dir")
            assert reporter.format == "text"
            assert reporter.include_traceback is False
            assert reporter.log_to_stderr is False
            
            # Check that the output directory was created
            mock_makedirs.assert_called_once_with(Path("custom_dir"), exist_ok=True)
    
    def test_generate_filename(self):
        """Test generating filenames for error reports."""
        reporter = FileErrorReporter(format="json")
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        
        # Test with a simple error type
        filename = reporter._generate_filename("ValueError", timestamp)
        assert filename.startswith("error_ValueError_")
        assert filename.endswith(".json")
        assert "20230101_120000" in filename
        
        # Test with a complex error type
        filename = reporter._generate_filename("Custom.Error:Type", timestamp)
        assert "Custom_Error_Type" in filename
    
    @patch('summit_seo.error_handling.reporting.get_suggestion_for_error')
    def test_report_error_json_format(self, mock_get_suggestion):
        """Test reporting errors in JSON format."""
        # Create test suggestions
        suggestions = [
            ActionableSuggestion(
                message="Test suggestion",
                steps=["Test step"],
                severity=SuggestionSeverity.MEDIUM
            )
        ]
        mock_get_suggestion.return_value = suggestions
        
        error = ValueError("Test error")
        
        # Use a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            reporter = FileErrorReporter(
                output_dir=temp_dir,
                format="json"
            )
            
            # Mock the file opening and writing
            with patch('builtins.open', mock_open()) as mock_file, \
                 patch('summit_seo.error_handling.reporting.print') as mock_print, \
                 patch.object(reporter, '_generate_filename', return_value="test_error.json"):
                
                result = reporter.report_error(error)
                
                # Check that the error was reported correctly
                assert isinstance(result, ReportedError)
                assert result.error == error
                assert result.suggestions == suggestions
                
                # Verify file operations
                mock_file.assert_called_once_with(Path(temp_dir) / "test_error.json", "w", encoding="utf-8")
                mock_file().write.assert_called_once()
                
                # Check that a message was printed to stderr
                mock_print.assert_called_once()
    
    @patch('summit_seo.error_handling.reporting.get_suggestion_for_error')
    def test_report_error_text_format(self, mock_get_suggestion):
        """Test reporting errors in text format."""
        # Create test suggestions
        suggestions = [
            ActionableSuggestion(
                message="Test suggestion",
                steps=["Test step"],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.GENERAL,
                documentation_url="https://example.com",
                code_example="Example code"
            )
        ]
        mock_get_suggestion.return_value = suggestions
        
        error = ValueError("Test error")
        context = ErrorContext(
            operation="Test operation",
            component="TestComponent"
        )
        
        # Use a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            reporter = FileErrorReporter(
                output_dir=temp_dir,
                format="text"
            )
            
            # Mock the file opening and writing
            with patch('builtins.open', mock_open()) as mock_file, \
                 patch('summit_seo.error_handling.reporting.print') as mock_print, \
                 patch.object(reporter, '_generate_filename', return_value="test_error.txt"):
                
                result = reporter.report_error(error, context)
                
                # Check that the error was reported correctly
                assert isinstance(result, ReportedError)
                assert result.error == error
                assert result.context == context
                assert result.suggestions == suggestions
                
                # Verify file operations
                mock_file.assert_called_once_with(Path(temp_dir) / "test_error.txt", "w", encoding="utf-8")
                
                # Check file write operations for text format
                write_calls = mock_file().write.call_args_list
                
                # Check that key elements were written
                assert any("ERROR: ValueError" in str(call) for call in write_calls)
                assert any("Message: Test error" in str(call) for call in write_calls)
                assert any("Component: TestComponent" in str(call) for call in write_calls)
                assert any("Operation: Test operation" in str(call) for call in write_calls)
                assert any("Suggested actions:" in str(call) for call in write_calls)
                assert any("1. Test suggestion" in str(call) for call in write_calls)
                assert any("Severity: medium" in str(call) for call in write_calls)
                assert any("Category: general" in str(call) for call in write_calls)
                assert any("Documentation: https://example.com" in str(call) for call in write_calls)
                assert any("Example:" in str(call) for call in write_calls) 