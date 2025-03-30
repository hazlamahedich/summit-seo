"""Integration test fixtures and configuration."""

import pytest
from typing import Dict, Any, List
from summit_seo.analyzer.factory import AnalyzerFactory
from summit_seo.analyzer.title_analyzer import TitleAnalyzer
from summit_seo.analyzer.meta_analyzer import MetaDescriptionAnalyzer
from summit_seo.analyzer.content_analyzer import ContentAnalyzer
from summit_seo.analyzer.image_analyzer import ImageSEOAnalyzer

@pytest.fixture(scope="session")
def complete_webpage() -> str:
    """Complete webpage HTML for integration testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Complete SEO Guide 2024: Best Practices & Strategy | Summit SEO</title>
        <meta name="description" content="Learn comprehensive SEO strategies for 2024. Our expert guide covers technical optimization, content strategy, and best practices to improve your website's search engine rankings.">
    </head>
    <body>
        <h1>Complete SEO Guide for 2024</h1>
        
        <h2>Technical SEO Fundamentals</h2>
        <p>Understanding technical SEO is crucial for website success. Focus on these key areas:</p>
        <ul>
            <li>Site structure and navigation</li>
            <li>Mobile responsiveness</li>
            <li>Page loading speed</li>
            <li>XML sitemaps</li>
        </ul>
        
        <h2>Content Optimization</h2>
        <p>Quality content remains the foundation of SEO success. Create valuable, informative content that serves user intent while maintaining optimal keyword density.</p>
        
        <img src="seo-diagram.jpg" alt="SEO optimization diagram showing key ranking factors" width="800" height="600">
        
        <h2>Link Building Strategies</h2>
        <p>Build authority through quality backlinks:</p>
        <ul>
            <li>Create linkable content</li>
            <li>Engage in guest posting</li>
            <li>Build industry relationships</li>
        </ul>
        
        <img src="link-building.webp" alt="Link building strategy flowchart" loading="lazy">
        
        <h3>Advanced Techniques</h3>
        <p>Implement these advanced SEO techniques to stay ahead of competition:</p>
        <ol>
            <li>Schema markup implementation</li>
            <li>Core Web Vitals optimization</li>
            <li>User experience enhancement</li>
        </ol>
    </body>
    </html>
    """

@pytest.fixture(scope="session")
def registered_analyzers() -> List[str]:
    """Register and return list of analyzer names."""
    AnalyzerFactory.clear_registry()
    
    analyzers = {
        'title': TitleAnalyzer,
        'meta': MetaDescriptionAnalyzer,
        'content': ContentAnalyzer,
        'image': ImageSEOAnalyzer
    }
    
    for name, analyzer_class in analyzers.items():
        AnalyzerFactory.register(name, analyzer_class)
    
    return list(analyzers.keys())

@pytest.fixture(scope="session")
def integration_configs() -> Dict[str, Dict[str, Any]]:
    """Configuration settings for integration testing."""
    return {
        'title': {
            'min_length': 30,
            'max_length': 60,
            'require_brand': True,
            'brand_separator': '|',
            'keyword_weight': 0.4,
            'length_weight': 0.3,
            'format_weight': 0.3
        },
        'meta': {
            'min_length': 120,
            'max_length': 160,
            'require_keywords': True,
            'keyword_weight': 0.4,
            'length_weight': 0.3,
            'content_weight': 0.3
        },
        'content': {
            'min_word_count': 300,
            'optimal_word_count': 1500,
            'max_keyword_density': 0.03,
            'readability_weight': 0.3,
            'structure_weight': 0.3,
            'keyword_weight': 0.4
        },
        'image': {
            'min_alt_length': 5,
            'max_alt_length': 125,
            'max_file_size_kb': 200,
            'allowed_formats': ['jpg', 'jpeg', 'png', 'webp', 'svg'],
            'require_lazy_loading': True,
            'require_width_height': True,
            'max_images_per_page': 50
        }
    }

@pytest.fixture(scope="session")
def expected_analysis_fields() -> Dict[str, List[str]]:
    """Expected fields in analysis results for each analyzer."""
    return {
        'title': ['title', 'length', 'has_brand', 'keyword_presence'],
        'meta': ['description', 'length', 'keyword_presence', 'content_quality'],
        'content': ['word_count', 'readability_score', 'keyword_density', 'structure_score'],
        'image': ['total_images', 'images_with_alt', 'images_with_dimensions', 'images_with_lazy_loading']
    } 