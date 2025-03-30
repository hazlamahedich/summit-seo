"""Tests for the Visual Report Generator."""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import time
from pathlib import Path

from summit_seo.reporter.visual_report import VisualReportGenerator
from summit_seo.visualization import AnalyzerVisualization

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
def mock_visualization():
    """Mock the AnalyzerVisualization class."""
    with patch("summit_seo.reporter.visual_report.AnalyzerVisualization") as mock_viz:
        # Mock the visualization methods
        instance = mock_viz.return_value
        instance.visualize_score_distribution = AsyncMock()
        instance.visualize_score_distribution.return_value = {
            "data_uri": "data:image/png;base64,test_base64_data"
        }
        instance.visualize_issue_severity = AsyncMock()
        instance.visualize_issue_severity.return_value = {
            "data_uri": "data:image/png;base64,test_base64_data"
        }
        instance.visualize_recommendation_priority = AsyncMock()
        instance.visualize_recommendation_priority.return_value = {
            "data_uri": "data:image/png;base64,test_base64_data"
        }
        instance.visualize_quick_wins = AsyncMock()
        instance.visualize_quick_wins.return_value = {
            "data_uri": "data:image/png;base64,test_base64_data"
        }
        yield mock_viz

class TestVisualReportGenerator:
    """Tests for VisualReportGenerator."""

    @pytest.fixture
    def generator(self, mock_visualization):
        """Create a VisualReportGenerator for testing."""
        return VisualReportGenerator()

    def test_init(self, generator, mock_visualization):
        """Test initialization."""
        # Verify visualization was created with default settings
        mock_visualization.assert_called_once_with(
            visualizer_name='matplotlib',
            visualizer_config={}
        )
        assert generator.config == {}

    def test_init_with_custom_config(self, mock_visualization):
        """Test initialization with custom config."""
        config = {
            'visualizer_name': 'custom_visualizer',
            'visualizer_config': {'key': 'value'},
            'include_dashboard': False,
            'include_analyzer_details': False
        }
        generator = VisualReportGenerator(config)
        
        # Verify visualization was created with custom settings
        mock_visualization.assert_called_once_with(
            visualizer_name='custom_visualizer',
            visualizer_config={'key': 'value'}
        )
        assert generator.config == config

    def test_validate_data_valid(self, generator):
        """Test data validation with valid data."""
        # This should not raise an exception
        generator._validate_data(SAMPLE_RESULTS)

    def test_validate_data_invalid(self, generator):
        """Test data validation with invalid data."""
        # Test with non-dictionary data
        with pytest.raises(ValueError):
            generator._validate_data("not a dictionary")
        
        # Test without results key
        with pytest.raises(ValueError):
            generator._validate_data({"url": "https://example.com"})
        
        # Test with non-dictionary results
        with pytest.raises(ValueError):
            generator._validate_data({"results": "not a dictionary"})

    def test_calculate_average_score(self, generator):
        """Test average score calculation."""
        # Test with normal results
        avg_score = generator._calculate_average_score(SAMPLE_RESULTS["results"])
        assert avg_score == 80.0  # (75 + 85) / 2
        
        # Test with no scores
        no_scores = {"analyzer1": {}, "analyzer2": {}}
        assert generator._calculate_average_score(no_scores) == 0
        
        # Test with some scores missing
        mixed_scores = {
            "analyzer1": {"score": 90},
            "analyzer2": {}
        }
        assert generator._calculate_average_score(mixed_scores) == 90.0

    @pytest.mark.asyncio
    async def test_generate_charts(self, generator):
        """Test chart generation."""
        charts = await generator._generate_charts(SAMPLE_RESULTS)
        
        # Verify each chart type was generated
        assert "score_distribution" in charts
        assert "issue_severity" in charts
        assert "recommendation_priority" in charts
        assert "quick_wins" in charts
        
        # Verify visualization methods were called
        generator.visualization.visualize_score_distribution.assert_called_once_with(
            SAMPLE_RESULTS["results"]
        )
        generator.visualization.visualize_issue_severity.assert_called_once_with(
            SAMPLE_RESULTS["results"]
        )
        generator.visualization.visualize_recommendation_priority.assert_called_once_with(
            SAMPLE_RESULTS["results"]
        )
        generator.visualization.visualize_quick_wins.assert_called_once_with(
            SAMPLE_RESULTS["results"]
        )

    @pytest.mark.asyncio
    async def test_generate_report(self, generator):
        """Test report generation."""
        # Mock the template render method
        generator.template = MagicMock()
        generator.template.render.return_value = "<html>Test Report</html>"
        
        # Generate report
        report = await generator.generate_report(SAMPLE_RESULTS)
        
        # Verify report content
        assert report["html"] == "<html>Test Report</html>"
        assert "charts" in report
        assert report["timestamp"] == SAMPLE_RESULTS["timestamp"]
        
        # Verify template was rendered with the correct data
        _, kwargs = generator.template.render.call_args
        assert "data" in kwargs
        assert "charts" in kwargs
        assert kwargs["data"]["average_score"] == 80.0

    @pytest.mark.asyncio
    async def test_generate_report_adds_timestamp(self, generator):
        """Test that timestamp is added if not present."""
        # Mock the template render method
        generator.template = MagicMock()
        generator.template.render.return_value = "<html>Test Report</html>"
        
        # Remove timestamp from data
        data = SAMPLE_RESULTS.copy()
        del data["timestamp"]
        
        # Generate report
        with patch("time.strftime") as mock_strftime:
            mock_strftime.return_value = "2023-01-01 12:34:56"
            report = await generator.generate_report(data)
        
        # Verify timestamp was added
        assert report["timestamp"] == "2023-01-01 12:34:56"

    @pytest.mark.asyncio
    async def test_generate_report_handles_chart_errors(self, generator):
        """Test that report generation handles chart generation errors."""
        # Make one of the chart methods fail
        generator.visualization.visualize_score_distribution.side_effect = Exception("Test error")
        
        # Mock the template render method
        generator.template = MagicMock()
        generator.template.render.return_value = "<html>Test Report</html>"
        
        # Generate report (should not raise an exception)
        report = await generator.generate_report(SAMPLE_RESULTS)
        
        # Verify report contains error information for the failed chart
        assert "charts" in report
        assert "score_distribution" in report["charts"]
        assert "error" in report["charts"]["score_distribution"] 