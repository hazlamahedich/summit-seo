"""Test fixtures for processor testing."""

import pytest
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from summit_seo.processor.base import BaseProcessor, ProcessingResult

class MockProcessor(BaseProcessor):
    """Mock processor for testing base functionality."""
    
    def _get_required_fields(self) -> List[str]:
        return ['test_field']
    
    async def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {'processed_' + k: v for k, v in data.items()}

@pytest.fixture
def sample_html() -> str:
    """Sample HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <meta name="description" content="Test description">
        <meta property="og:title" content="OG Test Title">
    </head>
    <body>
        <!-- Test comment -->
        <h1>Main Heading</h1>
        <p>Test paragraph with <a href="/relative/link">relative link</a>.</p>
        <h2>Sub Heading</h2>
        <p>Another paragraph with <a href="https://absolute.link">absolute link</a>.</p>
        <img src="/test.jpg" alt="Test image">
        <img src="https://example.com/test.png" alt="External image">
        <script>console.log('test');</script>
        <style>.test { color: red; }</style>
    </body>
    </html>
    """

@pytest.fixture
def sample_html_with_issues() -> str:
    """Sample HTML content with various issues for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>  Poorly Formatted   Title  </title>
        <meta name="description" content="">
        <meta property="og:title" content="   ">
    </head>
    <body>
        <!-- Comment that should be removed -->
        <h1>  Multiple    Spaces  </h1>
        <p>
            Text with
            multiple lines and    spaces
        </p>
        <a href="javascript:void(0)">Invalid link</a>
        <img src="" alt="">
        <script>
            // Messy script
            console.log(   'test'   );
        </script>
        <style>
            /* Messy style */
            .test {
                color:    red;
            }
        </style>
    </body>
    </html>
    """

@pytest.fixture
def mock_processor() -> MockProcessor:
    """Create a mock processor instance."""
    return MockProcessor()

@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Sample processor configuration."""
    return {
        'batch_size': 10,
        'max_retries': 3,
        'parser': 'html.parser',
        'clean_whitespace': True,
        'normalize_urls': True,
        'remove_comments': True,
        'extract_metadata': True
    }

@pytest.fixture
def sample_data() -> Dict[str, Any]:
    """Sample data for processing."""
    return {
        'test_field': 'test_value',
        'html_content': '<p>Test content</p>',
        'url': 'https://example.com'
    }

@pytest.fixture
def sample_batch_data() -> List[Dict[str, Any]]:
    """Sample batch data for processing."""
    return [
        {
            'test_field': f'test_value_{i}',
            'html_content': f'<p>Test content {i}</p>',
            'url': f'https://example.com/page{i}'
        }
        for i in range(5)
    ]

@pytest.fixture
def expected_metadata_fields() -> List[str]:
    """Expected metadata fields in processing results."""
    return [
        'title',
        'meta_tags',
        'headings',
        'links',
        'images'
    ]

@pytest.fixture
def invalid_config_cases() -> List[Dict[str, Any]]:
    """Invalid configuration cases for testing."""
    return [
        {'batch_size': 0},
        {'batch_size': -1},
        {'batch_size': 'invalid'},
        {'max_retries': -1},
        {'max_retries': 'invalid'},
        {'parser': 'invalid_parser'},
        {'clean_whitespace': 'not_bool'},
        {'normalize_urls': 123},
        {'remove_comments': 'yes'},
        {'extract_metadata': 1}
    ]

@pytest.fixture
def invalid_html_cases() -> List[str]:
    """Invalid HTML cases for testing."""
    return [
        '',  # Empty string
        None,  # None value
        '<not>valid</html',  # Malformed HTML
        '<!-- comment only -->',  # Comment only
        'plain text',  # Plain text
        '<script>javascript only</script>'  # Script only
    ] 