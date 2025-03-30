"""Tests for the TitleAnalyzer class."""

import pytest
import re
from summit_seo.analyzer.title_analyzer import TitleAnalyzer
from summit_seo.analyzer.base import AnalyzerError

@pytest.fixture
def enhanced_title_analyzer_config():
    """Return a sample configuration for TitleAnalyzer tests."""
    return {
        'min_length': 30,
        'max_length': 60,
        'brand_name': 'Summit SEO',
        'target_keywords': ['seo', 'best practices', 'guide'],
        'max_stop_words': 4,
        'ideal_keyword_position': 'beginning',
        'check_competitors': False,
    }

@pytest.mark.analyzer
@pytest.mark.unit
class TestTitleAnalyzer:
    """Test suite for TitleAnalyzer."""

    def test_initialization(self, title_analyzer_config):
        """Test analyzer initialization with config."""
        analyzer = TitleAnalyzer(title_analyzer_config)
        assert analyzer.config == title_analyzer_config
        assert analyzer.min_length == 30
        assert analyzer.max_length == 60

    def test_initialization_default_config(self):
        """Test analyzer initialization with default config."""
        analyzer = TitleAnalyzer()
        assert isinstance(analyzer.config, dict)
        assert analyzer.min_length == 30
        assert analyzer.max_length == 60
        assert analyzer.brand_name is None
        assert analyzer.target_keywords == []
        assert analyzer.max_stop_words == 4
        assert analyzer.ideal_keyword_position == 'beginning'

    def test_initialization_enhanced_config(self, enhanced_title_analyzer_config):
        """Test analyzer initialization with enhanced config."""
        analyzer = TitleAnalyzer(enhanced_title_analyzer_config)
        assert analyzer.brand_name == 'Summit SEO'
        assert 'seo' in analyzer.target_keywords
        assert 'best practices' in analyzer.target_keywords
        assert 'guide' in analyzer.target_keywords
        assert analyzer.max_stop_words == 4
        assert analyzer.ideal_keyword_position == 'beginning'
        assert analyzer.check_competitors is False

    def test_analyze_valid_title(self):
        """Test analysis of valid title."""
        html = """
        <html><head>
            <title>Best SEO Practices for 2024 | Summit SEO</title>
        </head></html>
        """
        analyzer = TitleAnalyzer()
        result = analyzer.analyze(html)
        
        assert result.data['title'] == 'Best SEO Practices for 2024 | Summit SEO'
        assert result.data['length'] > 0
        assert result.score > 0.5
        assert len(result.issues) == 0

    def test_analyze_missing_title(self):
        """Test analysis of HTML without title."""
        html = "<html><head></head></html>"
        analyzer = TitleAnalyzer()
        result = analyzer.analyze(html)
        
        assert result.data['title'] is None
        assert result.score == 0.0
        assert len(result.issues) > 0
        assert 'missing' in str(result.issues).lower()

    def test_analyze_empty_title(self):
        """Test analysis of empty title tag."""
        html = "<html><head><title></title></head></html>"
        analyzer = TitleAnalyzer()
        result = analyzer.analyze(html)
        
        assert result.data['title'] == ''
        assert result.score == 0.0
        assert len(result.issues) > 0
        assert 'missing' in str(result.issues).lower()

    def test_analyze_title_length(self):
        """Test validation of title length."""
        # Too short
        html_short = "<html><head><title>Short</title></head></html>"
        # Too long
        html_long = "<html><head><title>This is an extremely long title that exceeds the maximum length recommendation for SEO purposes and should trigger a length warning</title></head></html>"
        
        analyzer = TitleAnalyzer({'min_length': 30, 'max_length': 60})
        
        result_short = analyzer.analyze(html_short)
        assert any('below recommended minimum' in w for w in result_short.warnings)
        assert result_short.score < 0.5
        
        result_long = analyzer.analyze(html_long)
        assert any('exceeds recommended maximum' in w for w in result_long.warnings)
        assert result_long.score < 0.5
        assert result_long.data['is_likely_truncated'] is True

    def test_analyze_format_issues(self):
        """Test validation of title format."""
        html = "<html><head><title>ALL CAPS TITLE | Brand</title></head></html>"
        analyzer = TitleAnalyzer()
        result = analyzer.analyze(html)
        
        assert 'all uppercase' in str(result.warnings).lower()
        assert 'all_uppercase' in result.data['format_issues']
        assert 'Use title case or sentence case' in str(result.suggestions)

    def test_analyze_separator_issues(self):
        """Test validation of title separator usage."""
        html_trailing = "<html><head><title>SEO Title |</title></head></html>"
        html_leading = "<html><head><title>| SEO Title</title></head></html>"
        
        analyzer = TitleAnalyzer()
        
        trailing_result = analyzer.analyze(html_trailing)
        assert 'trailing separator' in str(trailing_result.warnings).lower()
        assert 'trailing_separator' in trailing_result.data['format_issues']
        
        leading_result = analyzer.analyze(html_leading)
        assert 'leading separator' in str(leading_result.warnings).lower()
        assert 'leading_separator' in leading_result.data['format_issues']

    def test_analyze_segments(self):
        """Test analysis of title segments."""
        html = "<html><head><title>SEO Guide | a | Summit SEO</title></head></html>"
        analyzer = TitleAnalyzer()
        result = analyzer.analyze(html)
        
        assert 'very short segments' in str(result.warnings).lower()
        assert len(result.data['segments']) == 3
        assert 'short_segments' in result.data['format_issues']

    def test_analyze_duplicate_words(self):
        """Test detection of duplicate words."""
        html = "<html><head><title>SEO SEO Guide for Guide Users</title></head></html>"
        analyzer = TitleAnalyzer()
        result = analyzer.analyze(html)
        
        assert 'duplicate words' in str(result.warnings).lower()
        assert 'seo' in result.data['duplicate_words']
        assert 'guide' in result.data['duplicate_words']
        assert 'duplicate_words' in result.data['format_issues']

    def test_analyze_special_characters(self):
        """Test handling of special characters in title."""
        html = "<html><head><title>SEO &amp; Digital Marketing | Brand</title></head></html>"
        analyzer = TitleAnalyzer()
        result = analyzer.analyze(html)
        
        assert result.data['title'] == 'SEO & Digital Marketing | Brand'
        assert len(result.issues) == 0

    def test_analyze_keywords(self):
        """Test keyword analysis functionality."""
        html = "<html><head><title>SEO Best Practices Guide 2024</title></head></html>"
        config = {
            'target_keywords': ['seo', 'best practices', 'guide'],
            'ideal_keyword_position': 'beginning'
        }
        analyzer = TitleAnalyzer(config)
        result = analyzer.analyze(html)
        
        assert 'seo' in result.data['found_keywords']
        assert 'best practices' in result.data['found_keywords']
        assert 'guide' in result.data['found_keywords']
        assert result.data['keyword_positions']['seo']['position'] == 'beginning'
        assert result.data['first_keyword'] == 'seo'
        assert result.data['keyword_density'] > 0

    def test_analyze_missing_keywords(self):
        """Test analysis when keywords are missing."""
        html = "<html><head><title>Digital Marketing Trends 2024</title></head></html>"
        config = {
            'target_keywords': ['seo', 'best practices', 'guide'],
            'ideal_keyword_position': 'beginning'
        }
        analyzer = TitleAnalyzer(config)
        result = analyzer.analyze(html)
        
        assert len(result.data['found_keywords']) == 0
        assert 'No target keywords found' in str(result.warnings)
        assert any('Include target keywords' in s for s in result.suggestions)

    def test_analyze_keyword_position(self):
        """Test analysis of keyword position."""
        html = "<html><head><title>Digital Marketing | SEO Guide</title></head></html>"
        config = {
            'target_keywords': ['seo', 'guide'],
            'ideal_keyword_position': 'beginning'
        }
        analyzer = TitleAnalyzer(config)
        result = analyzer.analyze(html)
        
        assert result.data['keyword_positions']['seo']['position'] == 'end'
        assert any('not in the ideal position' in w for w in result.warnings)
        assert any('Move primary keyword' in s for s in result.suggestions)

    def test_analyze_brand_presence(self):
        """Test detection of brand in title."""
        html = "<html><head><title>SEO Best Practices | Summit SEO</title></head></html>"
        config = {
            'brand_name': 'Summit SEO'
        }
        analyzer = TitleAnalyzer(config)
        result = analyzer.analyze(html)
        
        assert result.data['brand_present'] is True
        assert result.data['brand_position'] == 'end'
        assert len([s for s in result.suggestions if 'brand name' in s.lower()]) == 0

    def test_analyze_missing_brand(self):
        """Test analysis when brand is missing."""
        html = "<html><head><title>SEO Best Practices Guide</title></head></html>"
        config = {
            'brand_name': 'Summit SEO'
        }
        analyzer = TitleAnalyzer(config)
        result = analyzer.analyze(html)
        
        assert result.data['brand_present'] is False
        assert result.data['brand_position'] is None
        assert any('adding your brand name' in s for s in result.suggestions)

    def test_analyze_brand_position(self):
        """Test analysis of brand position."""
        html = "<html><head><title>Summit SEO | Best Practices Guide</title></head></html>"
        config = {
            'brand_name': 'Summit SEO'
        }
        analyzer = TitleAnalyzer(config)
        result = analyzer.analyze(html)
        
        assert result.data['brand_present'] is True
        assert result.data['brand_position'] == 'beginning'
        assert any('moving your brand name to the end' in s for s in result.suggestions)

    def test_analyze_stop_words(self):
        """Test analysis of stop words in title."""
        html = "<html><head><title>The Best SEO Practices for the Modern and Effective Marketing</title></head></html>"
        config = {
            'max_stop_words': 3
        }
        analyzer = TitleAnalyzer(config)
        result = analyzer.analyze(html)
        
        assert len(result.data['stop_words_found']) > 3
        assert 'the' in result.data['stop_words_found']
        assert 'for' in result.data['stop_words_found']
        assert 'and' in result.data['stop_words_found']
        assert any('more than the recommended maximum' in w for w in result.warnings)
        assert any('Reduce the number of stop words' in s for s in result.suggestions)

    def test_analyze_power_words(self):
        """Test analysis of power words in title."""
        html = "<html><head><title>Best Ultimate Guide for Effective SEO</title></head></html>"
        analyzer = TitleAnalyzer()
        result = analyzer.analyze(html)
        
        assert 'best' in result.data['power_words_found']
        assert 'ultimate' in result.data['power_words_found']
        assert 'effective' in result.data['power_words_found']
        assert result.data['power_word_count'] == 3
        assert result.data['power_word_ratio'] > 0

    def test_analyze_no_power_words(self):
        """Test analysis when no power words are present."""
        html = "<html><head><title>SEO Information Document 2024</title></head></html>"
        analyzer = TitleAnalyzer()
        result = analyzer.analyze(html)
        
        assert len(result.data['power_words_found']) == 0
        assert result.data['power_word_count'] == 0
        assert any('adding power words' in s for s in result.suggestions)

    def test_serp_preview(self):
        """Test SERP preview generation."""
        # Short title that won't be truncated
        html_short = "<html><head><title>SEO Guide 2024</title></head></html>"
        # Long title that will be truncated
        html_long = "<html><head><title>This is an extremely long title that will definitely be truncated in search engine results pages</title></head></html>"
        
        analyzer = TitleAnalyzer()
        
        short_result = analyzer.analyze(html_short)
        assert short_result.data['serp_preview']['display_title'] == 'SEO Guide 2024'
        assert short_result.data['serp_preview']['is_truncated'] is False
        
        long_result = analyzer.analyze(html_long)
        assert len(long_result.data['serp_preview']['display_title']) < len(long_result.data['title'])
        assert long_result.data['serp_preview']['display_title'].endswith('...')
        assert long_result.data['serp_preview']['is_truncated'] is True

    def test_analyze_invalid_html(self):
        """Test handling of invalid HTML."""
        with pytest.raises(AnalyzerError):
            analyzer = TitleAnalyzer()
            analyzer.analyze("Invalid HTML<<<")

    def test_analyze_none_content(self):
        """Test handling of None content."""
        with pytest.raises(AnalyzerError):
            analyzer = TitleAnalyzer()
            analyzer.analyze(None)

    def test_score_calculation(self):
        """Test title score calculation with enhanced analyzer."""
        html_perfect = """
        <html><head>
            <title>Best SEO Practices Guide for Beginners | Summit SEO</title>
        </head></html>
        """
        html_issues = """
        <html><head>
            <title>SHORT</title>
        </head></html>
        """
        
        config = {
            'brand_name': 'Summit SEO',
            'target_keywords': ['seo', 'best practices', 'guide'],
            'ideal_keyword_position': 'beginning'
        }
        analyzer = TitleAnalyzer(config)
        
        perfect_result = analyzer.analyze(html_perfect)
        assert perfect_result.score > 0.8  # High score for good title
        
        issues_result = analyzer.analyze(html_issues)
        assert issues_result.score < 0.5  # Low score for problematic title 