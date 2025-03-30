"""Tests for the Visual HTML Reporter."""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import os
from pathlib import Path

from summit_seo.reporter.visual_html_reporter import VisualHTMLReporter
from summit_seo.reporter.base import ReportResult, ReportGenerationError

# Sample analysis results for testing
SAMPLE_RESULTS = {
    "url": "https://example.com",
    "timestamp": "2023-01-01 00:00:00",
    "results": {
        "test_analyzer": {
            "score": 75,
            "issues": ["Test issue 1", "Test issue 2"],
            "warnings": ["Test warning"],
            "suggestions": ["Test suggestion"]
        },
        "another_analyzer": {
            "score": 85,
            "issues": ["Another issue"],
            "warnings": [],
            "suggestions": ["Another suggestion 1", "Another suggestion 2"]
        }
    }
}

@pytest.fixture
def mock_visual_report_generator():
    """Mock the VisualReportGenerator class."""
    with patch("summit_seo.reporter.visual_html_reporter.VisualReportGenerator") as mock_generator:
        # Mock the generate_report method
        instance = mock_generator.return_value
        instance.generate_report = AsyncMock()
        instance.generate_report.return_value = {
            "html": "<html>Test Visual Report</html>",
            "charts": {
                "score_distribution": {"data_uri": "data:image/png;base64,test_data"},
                "issue_severity": {"data_uri": "data:image/png;base64,test_data"},
                "recommendation_priority": {"data_uri": "data:image/png;base64,test_data"},
                "quick_wins": {"data_uri": "data:image/png;base64,test_data"}
            },
            "timestamp": "2023-01-01 00:00:00"
        }
        yield mock_generator

class TestVisualHTMLReporter:
    """Tests for VisualHTMLReporter."""

    @pytest.fixture
    def reporter(self, mock_visual_report_generator):
        """Create a VisualHTMLReporter for testing."""
        return VisualHTMLReporter()

    def test_init(self, reporter, mock_visual_report_generator):
        """Test initialization."""
        # Verify visual report generator was created with default settings
        mock_visual_report_generator.assert_called_once()
        assert reporter.config == {}

    def test_init_with_custom_config(self, mock_visual_report_generator):
        """Test initialization with custom config."""
        config = {
            'visualizer_name': 'custom_visualizer',
            'visualizer_config': {'key': 'value'},
            'include_dashboard': False,
            'include_analyzer_details': False,
            'template_path': 'custom_template.html',
            'minify': True
        }
        reporter = VisualHTMLReporter(config)
        
        # Verify visual report generator was created with custom settings
        mock_visual_report_generator.assert_called_once_with({
            'visualizer_name': 'custom_visualizer',
            'visualizer_config': {'key': 'value'},
            'include_dashboard': False,
            'include_analyzer_details': False,
            'template_path': 'custom_template.html'
        })
        assert reporter.config == config

    @pytest.mark.asyncio
    async def test_generate_report(self, reporter, tmp_path):
        """Test report generation."""
        # Create temp file path for output
        output_file = tmp_path / "test_report.html"
        
        # Add output file to data
        data = SAMPLE_RESULTS.copy()
        data["output_file"] = str(output_file)
        
        # Mock file writing
        mock_open = MagicMock()
        file_handle = MagicMock()
        mock_open.return_value.__enter__.return_value = file_handle
        
        with patch("builtins.open", mock_open):
            # Generate report
            result = await reporter.generate_report(data)
            
            # Verify file was written
            mock_open.assert_called_once_with(str(output_file), 'w', encoding='utf-8')
            file_handle.write.assert_called_once_with("<html>Test Visual Report</html>")
            
            # Verify result properties
            assert isinstance(result, ReportResult)
            assert result.content == "<html>Test Visual Report</html>"
            assert result.format == "html"
            assert result.path == str(output_file)
            
            # Verify metadata
            assert "timestamp" in result.metadata
            assert "url" in result.metadata
            assert "charts" in result.metadata
            assert result.metadata["url"] == "https://example.com"

    @pytest.mark.asyncio
    async def test_generate_report_with_minify(self, reporter, tmp_path):
        """Test report generation with minification."""
        # Set minify config
        reporter.config["minify"] = True
        
        # Create temp file path for output
        output_file = tmp_path / "test_report.html"
        
        # Add output file to data
        data = SAMPLE_RESULTS.copy()
        data["output_file"] = str(output_file)
        
        # Override mock to return HTML with newlines and spaces
        reporter.visual_report_generator.generate_report.return_value = {
            "html": "<html>\n  <body>\n    Test Visual Report\n  </body>\n</html>",
            "charts": {},
            "timestamp": "2023-01-01 00:00:00"
        }
        
        # Mock file writing
        mock_open = MagicMock()
        file_handle = MagicMock()
        mock_open.return_value.__enter__.return_value = file_handle
        
        with patch("builtins.open", mock_open):
            # Generate report
            result = await reporter.generate_report(data)
            
            # Verify minified content
            assert result.content == "<html> <body> Test Visual Report </body> </html>"
            file_handle.write.assert_called_once_with("<html> <body> Test Visual Report </body> </html>")

    @pytest.mark.asyncio
    async def test_generate_report_error(self, reporter):
        """Test error handling during report generation."""
        # Mock generator to raise an exception
        reporter.visual_report_generator.generate_report.side_effect = ValueError("Test error")
        
        # Try to generate report
        with pytest.raises(ReportGenerationError):
            await reporter.generate_report(SAMPLE_RESULTS)

    @pytest.mark.asyncio
    async def test_generate_batch_report(self, reporter, tmp_path):
        """Test batch report generation."""
        # Create temp file path for output
        output_file = tmp_path / "test_batch_report.html"
        
        # Create sample batch data
        batch_data = [
            {
                "url": "https://example1.com",
                "results": {"analyzer1": {"score": 80}}
            },
            {
                "url": "https://example2.com",
                "results": {"analyzer1": {"score": 90}}
            }
        ]
        
        # Mock _aggregate_results method
        with patch.object(reporter, '_aggregate_results') as mock_aggregate:
            mock_aggregate.return_value = {
                "url": "Multiple URLs",
                "output_file": str(output_file),
                "results": {"analyzer1": {"score": 85}}
            }
            
            # Generate batch report
            result = await reporter.generate_batch_report(batch_data)
            
            # Verify _aggregate_results was called
            mock_aggregate.assert_called_once_with(batch_data)
            
            # Verify generate_report was called with aggregated data
            reporter.visual_report_generator.generate_report.assert_called_once()
            
            # Verify result
            assert isinstance(result, ReportResult)
            assert result.format == "html"

    @pytest.mark.asyncio
    async def test_generate_batch_report_empty(self, reporter):
        """Test batch report generation with empty data."""
        # Try to generate batch report with empty data
        with pytest.raises(ValueError):
            await reporter.generate_batch_report([])

    @pytest.mark.asyncio
    async def test_generate_batch_report_error(self, reporter):
        """Test error handling during batch report generation."""
        # Mock _aggregate_results to raise an exception
        with patch.object(reporter, '_aggregate_results') as mock_aggregate:
            mock_aggregate.side_effect = ValueError("Test error")
            
            # Try to generate batch report
            with pytest.raises(ReportGenerationError):
                await reporter.generate_batch_report([SAMPLE_RESULTS]) 