import pytest
from typing import Dict, Any
from summit_seo.analyzer import BaseAnalyzer, AnalyzerFactory, AnalysisResult, AnalysisError
from summit_seo.collector.base import CollectedData

# Mock analyzer for testing
class MockAnalyzer(BaseAnalyzer):
    async def analyze(self, data: CollectedData) -> AnalysisResult:
        self.validate_data(data)
        return AnalysisResult(
            score=0.5,
            details={"test": "value"},
            recommendations=["test recommendation"]
        )

# Test data
@pytest.fixture
def collected_data():
    return CollectedData(
        url="https://example.com",
        content="Test content",
        metadata={"title": "Test"}
    )

@pytest.fixture
def config():
    return {"test_config": "value"}

class TestBaseAnalyzer:
    def test_init(self):
        analyzer = MockAnalyzer()
        assert analyzer.config == {}
        
        analyzer_with_config = MockAnalyzer({"key": "value"})
        assert analyzer_with_config.config == {"key": "value"}
    
    def test_validate_data(self):
        analyzer = MockAnalyzer()
        
        # Should raise error for None data
        with pytest.raises(AnalysisError):
            analyzer.validate_data(None)
    
    def test_normalize_score(self):
        analyzer = MockAnalyzer()
        
        assert analyzer.normalize_score(0.5) == 0.5
        assert analyzer.normalize_score(1.5) == 1.0
        assert analyzer.normalize_score(-0.5) == 0.0

class TestAnalyzerFactory:
    def setup_method(self):
        AnalyzerFactory.clear_registry()
    
    def test_register(self):
        AnalyzerFactory.register("mock", MockAnalyzer)
        assert "mock" in AnalyzerFactory.list_analyzers()
        
        # Test duplicate registration
        with pytest.raises(ValueError):
            AnalyzerFactory.register("mock", MockAnalyzer)
        
        # Test invalid analyzer class
        class InvalidAnalyzer:
            pass
        
        with pytest.raises(ValueError):
            AnalyzerFactory.register("invalid", InvalidAnalyzer)
    
    def test_create(self):
        AnalyzerFactory.register("mock", MockAnalyzer)
        
        # Test creation without config
        analyzer = AnalyzerFactory.create("mock")
        assert isinstance(analyzer, MockAnalyzer)
        assert analyzer.config == {}
        
        # Test creation with config
        config = {"test": "value"}
        analyzer = AnalyzerFactory.create("mock", config)
        assert isinstance(analyzer, MockAnalyzer)
        assert analyzer.config == config
        
        # Test creation of unregistered analyzer
        with pytest.raises(ValueError):
            AnalyzerFactory.create("nonexistent")
    
    def test_list_analyzers(self):
        assert AnalyzerFactory.list_analyzers() == []
        
        AnalyzerFactory.register("mock1", MockAnalyzer)
        AnalyzerFactory.register("mock2", MockAnalyzer)
        
        analyzers = AnalyzerFactory.list_analyzers()
        assert len(analyzers) == 2
        assert "mock1" in analyzers
        assert "mock2" in analyzers 