"""Tests for the ImageSEOAnalyzer class."""

import pytest
from bs4 import BeautifulSoup
from summit_seo.analyzer.image_analyzer import ImageSEOAnalyzer
from summit_seo.analyzer.base import AnalyzerError

@pytest.mark.analyzer
@pytest.mark.unit
class TestImageSEOAnalyzer:
    """Test suite for ImageSEOAnalyzer."""

    def test_initialization(self, image_analyzer_config):
        """Test analyzer initialization with config."""
        analyzer = ImageSEOAnalyzer(image_analyzer_config)
        assert analyzer.config == image_analyzer_config
        assert analyzer.config['min_alt_length'] == 5
        assert analyzer.config['max_alt_length'] == 125
        assert 'webp' in analyzer.config['allowed_formats']

    def test_initialization_default_config(self):
        """Test analyzer initialization with default config."""
        analyzer = ImageSEOAnalyzer()
        assert isinstance(analyzer.config, dict)
        assert 'min_alt_length' in analyzer.config
        assert 'max_alt_length' in analyzer.config
        assert 'allowed_formats' in analyzer.config

    def test_analyze_valid_html(self, sample_html):
        """Test analysis of valid HTML with images."""
        analyzer = ImageSEOAnalyzer()
        result = analyzer.analyze(sample_html)
        
        assert result.data['total_images'] == 3
        assert result.data['images_with_alt'] == 2
        assert result.data['images_with_dimensions'] == 1
        assert result.data['images_with_lazy_loading'] == 1
        
        assert len(result.issues) > 0  # Should have issue for missing alt text
        assert len(result.warnings) > 0  # Should have warning for missing dimensions
        assert len(result.recommendations) > 0

    def test_analyze_no_images(self):
        """Test analysis of HTML without images."""
        html = "<html><body><p>No images here</p></body></html>"
        analyzer = ImageSEOAnalyzer()
        result = analyzer.analyze(html)
        
        assert result.data['total_images'] == 0
        assert len(result.issues) == 0
        assert len(result.warnings) == 1  # Warning about no images
        assert len(result.recommendations) > 0

    def test_analyze_invalid_html(self):
        """Test handling of invalid HTML."""
        with pytest.raises(AnalyzerError):
            analyzer = ImageSEOAnalyzer()
            analyzer.analyze("Invalid HTML<<<")

    def test_analyze_missing_alt_text(self):
        """Test detection of missing alt text."""
        html = """
        <html><body>
            <img src="test.jpg">
            <img src="test2.jpg" alt="">
        </body></html>
        """
        analyzer = ImageSEOAnalyzer()
        result = analyzer.analyze(html)
        
        assert result.data['images_with_alt'] == 0
        assert 'missing alt text' in str(result.issues).lower()

    def test_analyze_alt_text_length(self):
        """Test validation of alt text length."""
        html = """
        <html><body>
            <img src="test.jpg" alt="too short">
            <img src="test2.jpg" alt="This is a very long alt text that exceeds the maximum length limit and provides too much unnecessary detail which is not recommended for SEO purposes">
        </body></html>
        """
        analyzer = ImageSEOAnalyzer({'min_alt_length': 15, 'max_alt_length': 100})
        result = analyzer.analyze(html)
        
        assert len(result.issues) > 0
        assert 'alt text too short' in str(result.issues).lower()
        assert 'alt text too long' in str(result.issues).lower()

    def test_analyze_image_dimensions(self):
        """Test validation of image dimensions."""
        html = """
        <html><body>
            <img src="test.jpg" alt="test" width="800" height="600">
            <img src="test2.jpg" alt="test2">
        </body></html>
        """
        analyzer = ImageSEOAnalyzer({'require_width_height': True})
        result = analyzer.analyze(html)
        
        assert result.data['images_with_dimensions'] == 1
        assert 'missing dimensions' in str(result.issues).lower()

    def test_analyze_lazy_loading(self):
        """Test validation of lazy loading."""
        html = """
        <html><body>
            <img src="test.jpg" alt="test" loading="lazy">
            <img src="test2.jpg" alt="test2">
        </body></html>
        """
        analyzer = ImageSEOAnalyzer({'require_lazy_loading': True})
        result = analyzer.analyze(html)
        
        assert result.data['images_with_lazy_loading'] == 1
        assert 'lazy loading' in str(result.recommendations).lower()

    def test_analyze_file_formats(self):
        """Test validation of image file formats."""
        html = """
        <html><body>
            <img src="test.jpg" alt="test">
            <img src="test.gif" alt="test">
            <img src="test.xyz" alt="test">
        </body></html>
        """
        analyzer = ImageSEOAnalyzer({'allowed_formats': ['jpg', 'png', 'webp']})
        result = analyzer.analyze(html)
        
        assert 'unsupported format' in str(result.issues).lower()
        assert len(result.recommendations) > 0

    def test_analyze_max_images(self):
        """Test validation of maximum images per page."""
        html = """
        <html><body>
            <img src="1.jpg" alt="1">
            <img src="2.jpg" alt="2">
            <img src="3.jpg" alt="3">
        </body></html>
        """
        analyzer = ImageSEOAnalyzer({'max_images_per_page': 2})
        result = analyzer.analyze(html)
        
        assert 'exceeds maximum' in str(result.issues).lower()
        assert len(result.recommendations) > 0

    def test_analyze_empty_content(self):
        """Test handling of empty content."""
        with pytest.raises(AnalyzerError):
            analyzer = ImageSEOAnalyzer()
            analyzer.analyze("")

    def test_analyze_none_content(self):
        """Test handling of None content."""
        with pytest.raises(AnalyzerError):
            analyzer = ImageSEOAnalyzer()
            analyzer.analyze(None) 