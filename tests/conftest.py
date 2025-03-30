"""Test fixtures and configuration."""

import pytest
from typing import Dict, Any
from bs4 import BeautifulSoup

@pytest.fixture
def sample_html() -> str:
    """Sample HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <meta name="description" content="A test page for SEO analysis">
    </head>
    <body>
        <h1>Welcome to Test Page</h1>
        <h2>About Section</h2>
        <p>This is a test paragraph with a <a href="/internal-link">internal link</a>
        and an <a href="https://external.com">external link</a>.</p>
        
        <img src="/test-image.jpg" alt="A test image" width="800" height="600">
        <img src="https://example.com/image.png" alt="Example image" loading="lazy">
        <img src="no-alt-image.webp">
        
        <h2>Another Section</h2>
        <p>More test content here.</p>
    </body>
    </html>
    """

@pytest.fixture
def sample_html_soup(sample_html: str) -> BeautifulSoup:
    """BeautifulSoup object for sample HTML."""
    return BeautifulSoup(sample_html, 'html.parser')

@pytest.fixture
def base_analyzer_config() -> Dict[str, Any]:
    """Base configuration for analyzer testing."""
    return {
        'base_url': 'https://example.com',
        'min_length': 10,
        'max_length': 60
    }

@pytest.fixture
def image_analyzer_config() -> Dict[str, Any]:
    """Configuration for image analyzer testing."""
    return {
        'base_url': 'https://example.com',
        'min_alt_length': 5,
        'max_alt_length': 125,
        'max_file_size_kb': 200,
        'allowed_formats': ['jpg', 'jpeg', 'png', 'webp', 'svg'],
        'require_lazy_loading': True,
        'require_width_height': True,
        'max_images_per_page': 50
    }

@pytest.fixture
def link_analyzer_config() -> Dict[str, Any]:
    """Configuration for link analyzer testing."""
    return {
        'base_url': 'https://example.com',
        'min_anchor_length': 3,
        'max_anchor_length': 60,
        'max_links_per_page': 100,
        'nofollow_external': True,
        'check_fragments': True,
        'allowed_schemes': ['http', 'https']
    }

@pytest.fixture
def heading_analyzer_config() -> Dict[str, Any]:
    """Configuration for heading structure analyzer testing."""
    return {
        'max_heading_length': 60,
        'min_heading_length': 10,
        'max_heading_depth': 6,
        'require_h1': True,
        'allow_multiple_h1': False
    }

@pytest.fixture
def content_analyzer_config() -> Dict[str, Any]:
    """Configuration for content analyzer testing."""
    return {
        'min_word_count': 300,
        'optimal_word_count': 1500,
        'max_keyword_density': 0.03,
        'readability_weight': 0.3,
        'structure_weight': 0.3,
        'keyword_weight': 0.4
    }

@pytest.fixture
def meta_analyzer_config() -> Dict[str, Any]:
    """Configuration for meta description analyzer testing."""
    return {
        'min_length': 120,
        'max_length': 160,
        'require_keywords': True,
        'keyword_weight': 0.4,
        'length_weight': 0.3,
        'content_weight': 0.3
    }

@pytest.fixture
def title_analyzer_config() -> Dict[str, Any]:
    """Configuration for title analyzer testing."""
    return {
        'min_length': 30,
        'max_length': 60,
        'require_brand': True,
        'brand_separator': '|',
        'keyword_weight': 0.4,
        'length_weight': 0.3,
        'format_weight': 0.3
    } 