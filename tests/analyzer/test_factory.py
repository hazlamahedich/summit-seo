"""Tests for the AnalyzerFactory class."""

import pytest
from typing import Dict, Any
from summit_seo.analyzer.base import BaseAnalyzer, AnalysisResult, AnalyzerError
from summit_seo.analyzer.factory import AnalyzerFactory

class TestAnalyzer(BaseAnalyzer):
    """Test analyzer implementation."""
    
    def analyze(self, content: str) -> AnalysisResult:
        """Implement abstract method for testing."""
        return AnalysisResult(
            data={'test': True},
            score=1.0,
            issues=[],
            warnings=[],
            recommendations=[]
        )

class AnotherTestAnalyzer(BaseAnalyzer):
    """Another test analyzer implementation."""
    
    def analyze(self, content: str) -> AnalysisResult:
        """Implement abstract method for testing."""
        return AnalysisResult(
            data={'another_test': True},
            score=1.0,
            issues=[],
            warnings=[],
            recommendations=[]
        )

@pytest.mark.analyzer
@pytest.mark.unit
class TestAnalyzerFactory:
    """Test suite for AnalyzerFactory."""

    def setup_method(self):
        """Set up test environment before each test."""
        AnalyzerFactory.clear_registry()

    def test_registration(self):
        """Test analyzer registration."""
        AnalyzerFactory.register('test', TestAnalyzer)
        assert 'test' in AnalyzerFactory.list_analyzers()

    def test_duplicate_registration(self):
        """Test handling of duplicate registration."""
        AnalyzerFactory.register('test', TestAnalyzer)
        with pytest.raises(ValueError):
            AnalyzerFactory.register('test', TestAnalyzer)

    def test_invalid_analyzer_registration(self):
        """Test registration of invalid analyzer class."""
        class InvalidAnalyzer:
            pass

        with pytest.raises(TypeError):
            AnalyzerFactory.register('invalid', InvalidAnalyzer)

    def test_create_analyzer(self):
        """Test analyzer creation."""
        AnalyzerFactory.register('test', TestAnalyzer)
        analyzer = AnalyzerFactory.create('test')
        assert isinstance(analyzer, TestAnalyzer)

    def test_create_analyzer_with_config(self, base_analyzer_config):
        """Test analyzer creation with configuration."""
        AnalyzerFactory.register('test', TestAnalyzer)
        analyzer = AnalyzerFactory.create('test', base_analyzer_config)
        assert analyzer.config == base_analyzer_config

    def test_create_nonexistent_analyzer(self):
        """Test creation of non-registered analyzer."""
        with pytest.raises(KeyError):
            AnalyzerFactory.create('nonexistent')

    def test_list_analyzers(self):
        """Test listing registered analyzers."""
        AnalyzerFactory.register('test1', TestAnalyzer)
        AnalyzerFactory.register('test2', AnotherTestAnalyzer)
        
        analyzers = AnalyzerFactory.list_analyzers()
        assert 'test1' in analyzers
        assert 'test2' in analyzers
        assert len(analyzers) == 2

    def test_clear_registry(self):
        """Test clearing analyzer registry."""
        AnalyzerFactory.register('test', TestAnalyzer)
        assert len(AnalyzerFactory.list_analyzers()) > 0
        
        AnalyzerFactory.clear_registry()
        assert len(AnalyzerFactory.list_analyzers()) == 0

    def test_type_safety(self):
        """Test type safety of factory methods."""
        AnalyzerFactory.register('test', TestAnalyzer)
        analyzer = AnalyzerFactory.create('test')
        
        # Test return type annotations
        assert isinstance(analyzer, BaseAnalyzer)
        
        # Test method type hints
        result = analyzer.analyze("<html></html>")
        assert isinstance(result, AnalysisResult)

    def test_registration_name_validation(self):
        """Test validation of analyzer names during registration."""
        with pytest.raises(ValueError):
            AnalyzerFactory.register('', TestAnalyzer)
            
        with pytest.raises(ValueError):
            AnalyzerFactory.register(None, TestAnalyzer)

    def test_analyzer_inheritance(self):
        """Test that only BaseAnalyzer subclasses can be registered."""
        class NotAnAnalyzer:
            def analyze(self, content: str):
                pass

        with pytest.raises(TypeError):
            AnalyzerFactory.register('invalid', NotAnAnalyzer)

    def test_config_propagation(self):
        """Test that configuration is properly propagated to created analyzers."""
        config = {'test_key': 'test_value'}
        AnalyzerFactory.register('test', TestAnalyzer)
        
        analyzer = AnalyzerFactory.create('test', config)
        assert analyzer.config == config
        assert analyzer.config['test_key'] == 'test_value' 