"""Tests for the MetaDescriptionAnalyzer class."""

import pytest
from summit_seo.analyzer.meta_analyzer import MetaDescriptionAnalyzer
from summit_seo.analyzer.base import AnalyzerError

@pytest.mark.analyzer
@pytest.mark.unit
class TestMetaDescriptionAnalyzer:
    """Test suite for MetaDescriptionAnalyzer."""

    def test_initialization(self, meta_analyzer_config):
        """Test analyzer initialization with config."""
        analyzer = MetaDescriptionAnalyzer(meta_analyzer_config)
        assert analyzer.config == meta_analyzer_config
        assert analyzer.config['min_length'] == 120
        assert analyzer.config['max_length'] == 160
        assert analyzer.config['require_keywords'] is True
        assert analyzer.config['keyword_weight'] == 0.4

    def test_initialization_default_config(self):
        """Test analyzer initialization with default config."""
        analyzer = MetaDescriptionAnalyzer()
        assert isinstance(analyzer.config, dict)
        assert 'min_length' in analyzer.config
        assert 'max_length' in analyzer.config
        assert 'require_keywords' in analyzer.config
        assert 'keyword_weight' in analyzer.config

    def test_analyze_valid_description(self):
        """Test analysis of valid meta description."""
        html = """
        <html><head>
            <meta name="description" content="Learn comprehensive SEO strategies and best practices for 2024. Our guide covers everything from technical optimization to content strategy, helping you improve your website's search engine rankings.">
        </head></html>
        """
        analyzer = MetaDescriptionAnalyzer()
        result = analyzer.analyze(html)
        
        assert result.data['description'] is not None
        assert result.data['length'] > 0
        assert result.score > 0.5
        assert len(result.issues) == 0

    def test_analyze_missing_description(self):
        """Test analysis of HTML without meta description."""
        html = "<html><head></head></html>"
        analyzer = MetaDescriptionAnalyzer()
        result = analyzer.analyze(html)
        
        assert result.data['description'] is None
        assert result.score == 0.0
        assert len(result.issues) > 0
        assert 'missing meta description' in str(result.issues).lower()

    def test_analyze_empty_description(self):
        """Test analysis of empty meta description."""
        html = """
        <html><head>
            <meta name="description" content="">
        </head></html>
        """
        analyzer = MetaDescriptionAnalyzer()
        result = analyzer.analyze(html)
        
        assert result.data['description'] == ''
        assert result.score == 0.0
        assert len(result.issues) > 0
        assert 'empty meta description' in str(result.issues).lower()

    def test_analyze_description_length(self):
        """Test validation of description length."""
        # Too short
        html_short = """
        <html><head>
            <meta name="description" content="Short description">
        </head></html>
        """
        # Too long
        html_long = """
        <html><head>
            <meta name="description" content="This is an extremely long meta description that exceeds the maximum length recommendation for SEO purposes. It contains too many characters and should trigger a length warning because search engines will truncate this text in search results, making it less effective for users.">
        </head></html>
        """
        
        analyzer = MetaDescriptionAnalyzer({'min_length': 120, 'max_length': 160})
        
        result_short = analyzer.analyze(html_short)
        assert 'too short' in str(result_short.issues).lower()
        assert result_short.score < 0.5
        
        result_long = analyzer.analyze(html_long)
        assert 'too long' in str(result_long.issues).lower()
        assert result_long.score < 0.5

    def test_analyze_keyword_presence(self):
        """Test validation of keyword presence."""
        html = """
        <html><head>
            <meta name="description" content="A generic description without any relevant keywords or specific information about the content.">
        </head></html>
        """
        analyzer = MetaDescriptionAnalyzer({'require_keywords': True})
        result = analyzer.analyze(html)
        
        assert 'missing keywords' in str(result.issues).lower()
        assert len(result.recommendations) > 0

    def test_analyze_content_quality(self):
        """Test validation of description content quality."""
        html = """
        <html><head>
            <meta name="description" content="Click here! Best website ever! Amazing content! Must see! Check it out now! Don't miss out!">
        </head></html>
        """
        analyzer = MetaDescriptionAnalyzer()
        result = analyzer.analyze(html)
        
        assert 'clickbait language' in str(result.issues).lower()
        assert 'improve content quality' in str(result.recommendations).lower()

    def test_analyze_multiple_descriptions(self):
        """Test handling of multiple meta descriptions."""
        html = """
        <html><head>
            <meta name="description" content="First description">
            <meta name="description" content="Second description">
        </head></html>
        """
        analyzer = MetaDescriptionAnalyzer()
        result = analyzer.analyze(html)
        
        assert 'multiple meta descriptions' in str(result.issues).lower()
        assert len(result.recommendations) > 0

    def test_analyze_special_characters(self):
        """Test handling of special characters in description."""
        html = """
        <html><head>
            <meta name="description" content="SEO &amp; Digital Marketing strategies for 2024. Learn about technical SEO, content optimization &amp; more.">
        </head></html>
        """
        analyzer = MetaDescriptionAnalyzer()
        result = analyzer.analyze(html)
        
        assert '&' in result.data['description']
        assert len(result.issues) == 0

    def test_analyze_invalid_html(self):
        """Test handling of invalid HTML."""
        with pytest.raises(AnalyzerError):
            analyzer = MetaDescriptionAnalyzer()
            analyzer.analyze("Invalid HTML<<<")

    def test_analyze_none_content(self):
        """Test handling of None content."""
        with pytest.raises(AnalyzerError):
            analyzer = MetaDescriptionAnalyzer()
            analyzer.analyze(None)

    def test_score_calculation(self):
        """Test description score calculation."""
        html_perfect = """
        <html><head>
            <meta name="description" content="Learn comprehensive SEO strategies for 2024. Our expert guide covers technical optimization, content strategy, and best practices to improve your website's search engine rankings and visibility.">
        </head></html>
        """
        html_issues = """
        <html><head>
            <meta name="description" content="Short text">
        </head></html>
        """
        
        analyzer = MetaDescriptionAnalyzer()
        
        perfect_result = analyzer.analyze(html_perfect)
        assert perfect_result.score > 0.8  # High score for good description
        
        issues_result = analyzer.analyze(html_issues)
        assert issues_result.score < 0.5  # Low score for problematic description

    def test_analyze_duplicate_content(self):
        """Test detection of duplicate content with title."""
        html = """
        <html><head>
            <title>Comprehensive SEO Guide for 2024</title>
            <meta name="description" content="Comprehensive SEO Guide for 2024">
        </head></html>
        """
        analyzer = MetaDescriptionAnalyzer()
        result = analyzer.analyze(html)
        
        assert 'duplicate of title' in str(result.issues).lower()
        assert 'unique description' in str(result.recommendations).lower()

    def test_analyze_call_to_action(self):
        """Test validation of call to action presence."""
        html = """
        <html><head>
            <meta name="description" content="A complete guide to SEO best practices and strategies. Improve your website's visibility and rankings.">
        </head></html>
        """
        analyzer = MetaDescriptionAnalyzer()
        result = analyzer.analyze(html)
        
        assert result.data['has_call_to_action'] is True
        assert len(result.issues) == 0 