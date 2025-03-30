"""Tests for the BaseAnalyzer class."""

import pytest
from typing import Dict, Any
from bs4 import BeautifulSoup
from summit_seo.analyzer.base import BaseAnalyzer, AnalyzerError, AnalysisResult

class ConcreteAnalyzer(BaseAnalyzer):
    """Concrete implementation of BaseAnalyzer for testing."""
    
    def analyze(self, content: str) -> AnalysisResult:
        """Implement abstract method for testing."""
        if not content:
            raise AnalyzerError("Content cannot be empty")
            
        soup = self._parse_html(content)
        return AnalysisResult(
            data={'test_key': 'test_value'},
            score=1.0,
            issues=['Test issue'],
            warnings=['Test warning'],
            recommendations=['Test recommendation']
        )

@pytest.mark.analyzer
@pytest.mark.unit
class TestBaseAnalyzer:
    """Test suite for BaseAnalyzer."""

    def test_initialization(self, base_analyzer_config):
        """Test analyzer initialization with config."""
        analyzer = ConcreteAnalyzer(base_analyzer_config)
        assert analyzer.config == base_analyzer_config
        assert analyzer.config['base_url'] == 'https://example.com'

    def test_initialization_default_config(self):
        """Test analyzer initialization with default config."""
        analyzer = ConcreteAnalyzer()
        assert isinstance(analyzer.config, dict)
        assert analyzer.config == {}

    def test_parse_html_valid(self):
        """Test HTML parsing with valid content."""
        analyzer = ConcreteAnalyzer()
        html = "<html><body><p>Test</p></body></html>"
        soup = analyzer._parse_html(html)
        assert isinstance(soup, BeautifulSoup)
        assert soup.find('p').text == 'Test'

    def test_parse_html_invalid(self):
        """Test HTML parsing with invalid content."""
        analyzer = ConcreteAnalyzer()
        with pytest.raises(AnalyzerError):
            analyzer._parse_html("Invalid HTML<<<")

    def test_parse_html_empty(self):
        """Test HTML parsing with empty content."""
        analyzer = ConcreteAnalyzer()
        with pytest.raises(AnalyzerError):
            analyzer._parse_html("")

    def test_parse_html_none(self):
        """Test HTML parsing with None content."""
        analyzer = ConcreteAnalyzer()
        with pytest.raises(AnalyzerError):
            analyzer._parse_html(None)

    def test_analyze_method(self, sample_html):
        """Test analyze method implementation."""
        analyzer = ConcreteAnalyzer()
        result = analyzer.analyze(sample_html)
        
        assert isinstance(result, AnalysisResult)
        assert isinstance(result.data, dict)
        assert isinstance(result.score, float)
        assert isinstance(result.issues, list)
        assert isinstance(result.warnings, list)
        assert isinstance(result.recommendations, list)

    def test_analyze_empty_content(self):
        """Test analyze method with empty content."""
        analyzer = ConcreteAnalyzer()
        with pytest.raises(AnalyzerError):
            analyzer.analyze("")

    def test_analyze_none_content(self):
        """Test analyze method with None content."""
        analyzer = ConcreteAnalyzer()
        with pytest.raises(AnalyzerError):
            analyzer.analyze(None)

    def test_analysis_result_structure(self, sample_html):
        """Test structure of analysis result."""
        analyzer = ConcreteAnalyzer()
        result = analyzer.analyze(sample_html)
        
        assert 'test_key' in result.data
        assert result.score == 1.0
        assert len(result.issues) == 1
        assert len(result.warnings) == 1
        assert len(result.recommendations) == 1

    def test_config_immutability(self, base_analyzer_config):
        """Test that analyzer config cannot be modified after initialization."""
        analyzer = ConcreteAnalyzer(base_analyzer_config)
        original_config = analyzer.config.copy()
        
        # Try to modify config
        with pytest.raises(AttributeError):
            analyzer.config = {}
            
        # Verify config hasn't changed
        assert analyzer.config == original_config

    def test_config_deep_copy(self, base_analyzer_config):
        """Test that config modifications don't affect original."""
        original_config = base_analyzer_config.copy()
        analyzer = ConcreteAnalyzer(base_analyzer_config)
        
        # Modify original config
        base_analyzer_config['new_key'] = 'new_value'
        
        # Verify analyzer config hasn't changed
        assert 'new_key' not in analyzer.config
        assert analyzer.config == original_config 