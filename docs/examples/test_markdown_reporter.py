import pytest
import asyncio
from typing import Dict, Any, List
from datetime import datetime

from summit_seo.reporter.base import BaseReporter, ReportResult, ReportMetadata
from summit_seo.reporter import ReporterFactory

# Import our custom reporter (assumed to be in a file called markdown_reporter.py)
from markdown_reporter import MarkdownReporter

# Register the reporter with the factory for testing
ReporterFactory.register('markdown', MarkdownReporter)

@pytest.fixture
def sample_data() -> Dict[str, Any]:
    """Fixture providing sample analysis data."""
    return {
        'url': 'https://example.com',
        'timestamp': '2023-04-15T14:30:00',
        'results': {
            'title': {
                'score': 85.5,
                'issues': [
                    'Title length (55 characters) is less than recommended (60-70 characters)',
                    'Title does not include main keyword'
                ],
                'warnings': [
                    'Title does not include brand name'
                ],
                'recommendations': [
                    'Increase title length to 60-70 characters',
                    'Include main keyword at the beginning of the title',
                    'Add brand name at the end of the title'
                ]
            },
            'meta': {
                'score': 72.0,
                'issues': [
                    'Meta description missing',
                    'Canonical URL not set'
                ],
                'warnings': [],
                'recommendations': [
                    'Add a meta description between 150-160 characters',
                    'Set canonical URL to avoid duplicate content issues'
                ]
            }
        }
    }

@pytest.fixture
def batch_data() -> List[Dict[str, Any]]:
    """Fixture providing sample batch analysis data."""
    return [
        {
            'url': 'https://example.com/home',
            'timestamp': '2023-04-15T14:30:00',
            'results': {
                'title': {'score': 85.5, 'issues': ['Title too short']},
                'meta': {'score': 72.0, 'issues': ['Meta description missing']}
            }
        },
        {
            'url': 'https://example.com/about',
            'timestamp': '2023-04-15T14:35:00',
            'results': {
                'title': {'score': 92.0, 'issues': []},
                'meta': {'score': 65.0, 'issues': ['Meta description too long']}
            }
        }
    ]

class TestMarkdownReporter:
    """Test suite for the MarkdownReporter class."""

    def test_initialization(self):
        """Test reporter initialization with different configurations."""
        # Test with default config
        reporter = MarkdownReporter()
        assert reporter.config['include_toc'] is True
        assert reporter.config['max_issues'] == 10
        assert reporter.config['heading_style'] == 'hash'

        # Test with custom config
        custom_config = {
            'include_toc': False,
            'max_issues': 5,
            'heading_style': 'underline'
        }
        reporter = MarkdownReporter(custom_config)
        assert reporter.config['include_toc'] is False
        assert reporter.config['max_issues'] == 5
        assert reporter.config['heading_style'] == 'underline'

    def test_validate_config(self):
        """Test configuration validation."""
        # Valid configuration
        reporter = MarkdownReporter({'include_toc': True, 'max_issues': 10})
        reporter.validate_config()  # Should not raise any errors

        # Invalid boolean
        with pytest.raises(ValueError):
            reporter = MarkdownReporter({'include_toc': 'yes'})
            reporter.validate_config()

        # Invalid max_issues
        with pytest.raises(ValueError):
            reporter = MarkdownReporter({'max_issues': -1})
            reporter.validate_config()

        # Invalid heading style
        with pytest.raises(ValueError):
            reporter = MarkdownReporter({'heading_style': 'invalid'})
            reporter.validate_config()

    @pytest.mark.asyncio
    async def test_generate_report(self, sample_data):
        """Test report generation."""
        reporter = MarkdownReporter()
        result = await reporter.generate_report(sample_data)

        # Verify result type
        assert isinstance(result, ReportResult)
        assert result.format == 'markdown'
        assert isinstance(result.metadata, ReportMetadata)

        # Verify content
        content = result.content
        assert "# SEO Analysis Report: https://example.com" in content
        assert "## Summary" in content
        assert "## Title Analysis" in content
        assert "## Meta Analysis" in content
        
        # Verify score is included
        assert "Overall Score: **78.8** / 100" in content
        
        # Verify table of contents (if enabled)
        assert "## Table of Contents" in content
        assert "1. [Summary](#summary)" in content

    @pytest.mark.asyncio
    async def test_generate_report_without_toc(self, sample_data):
        """Test report generation with TOC disabled."""
        reporter = MarkdownReporter({'include_toc': False})
        result = await reporter.generate_report(sample_data)
        
        # TOC should not be present
        assert "## Table of Contents" not in result.content
        assert "1. [Summary](#summary)" not in result.content

    @pytest.mark.asyncio
    async def test_generate_report_with_underline_style(self, sample_data):
        """Test report generation with underline heading style."""
        reporter = MarkdownReporter({'heading_style': 'underline'})
        result = await reporter.generate_report(sample_data)
        
        # Check underline style
        assert "Summary\n=======" in result.content
        assert "## Summary" not in result.content

    @pytest.mark.asyncio
    async def test_generate_batch_report(self, batch_data):
        """Test batch report generation."""
        reporter = MarkdownReporter()
        result = await reporter.generate_batch_report(batch_data)
        
        # Verify result type
        assert isinstance(result, ReportResult)
        assert result.format == 'markdown'
        
        # Verify content
        content = result.content
        assert "# SEO Batch Analysis Report" in content
        assert "Total sites analyzed: 2" in content
        assert "## Summary" in content
        assert "## example.com" in content
        
        # Verify batch summary
        assert "Sites Analyzed | 2" in content
        assert "Analyzer Performance" in content

    @pytest.mark.asyncio
    async def test_factory_integration(self, sample_data):
        """Test that the factory correctly creates our reporter."""
        factory = ReporterFactory()
        reporter = factory.create('markdown', {'max_issues': 5})
        
        # Verify correct reporter type
        assert isinstance(reporter, MarkdownReporter)
        assert reporter.config['max_issues'] == 5
        
        # Try generating a report through the factory
        result = await reporter.generate_report(sample_data)
        assert isinstance(result, ReportResult)
        assert "# SEO Analysis Report" in result.content

    def test_markdown_formatting(self, sample_data):
        """Test specific markdown formatting functionality."""
        reporter = MarkdownReporter()
        
        # Test summary section formatting
        summary = reporter._generate_summary_section(sample_data['results'])
        assert "## Summary" in summary
        assert "| Analyzer | Score | Issues | Warnings |" in summary
        assert "| Title | 85.5 |" in summary
        
        # Test analyzer section formatting
        analyzer_section = reporter._generate_analyzer_section(
            "title", sample_data['results']['title']
        )
        assert "## Title Analysis" in analyzer_section
        assert "Score: **85.5** / 100" in analyzer_section
        assert "### Issues" in analyzer_section
        assert "### Warnings" in analyzer_section
        assert "### Recommendations" in analyzer_section

if __name__ == "__main__":
    pytest.main(["-v", "test_markdown_reporter.py"]) 