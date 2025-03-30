"""Integration tests for analyzer factory functionality."""

import pytest
from typing import Dict, Any
from summit_seo.analyzer.factory import AnalyzerFactory
from summit_seo.analyzer.base import BaseAnalyzer, AnalysisResult

class MockAnalyzer(BaseAnalyzer):
    """Mock analyzer for testing factory integration."""
    
    def analyze(self, html_content: str) -> AnalysisResult:
        return AnalysisResult(
            score=1.0,
            data={'mock': 'data'},
            recommendations=['mock recommendation'],
            issues=[]
        )

@pytest.mark.integration
class TestAnalyzerFactoryIntegration:
    """Test suite for analyzer factory integration."""

    def test_factory_registration_lifecycle(self):
        """Test complete lifecycle of analyzer registration and management."""
        # Clear existing registrations
        AnalyzerFactory.clear_registry()
        
        # Register mock analyzer
        AnalyzerFactory.register('mock', MockAnalyzer)
        
        # Verify registration
        assert 'mock' in AnalyzerFactory.get_registered_analyzers()
        
        # Create instance and verify
        analyzer = AnalyzerFactory.get('mock')()
        assert isinstance(analyzer, MockAnalyzer)
        
        # Test deregistration
        AnalyzerFactory.deregister('mock')
        assert 'mock' not in AnalyzerFactory.get_registered_analyzers()

    def test_factory_configuration_inheritance(self, integration_configs):
        """Test configuration inheritance between analyzer instances."""
        AnalyzerFactory.register('mock', MockAnalyzer)
        
        # Create base configuration
        base_config = {'base_param': 'value'}
        
        # Create analyzer with base config
        analyzer1 = AnalyzerFactory.get('mock')(base_config)
        
        # Create analyzer with extended config
        extended_config = {**base_config, 'extra_param': 'extra'}
        analyzer2 = AnalyzerFactory.get('mock')(extended_config)
        
        # Verify configurations are isolated
        assert analyzer1.config != analyzer2.config
        assert 'extra_param' not in analyzer1.config
        assert 'extra_param' in analyzer2.config

    def test_factory_bulk_operations(self):
        """Test bulk operations with analyzer factory."""
        # Register multiple analyzers
        analyzers = {
            'mock1': MockAnalyzer,
            'mock2': MockAnalyzer,
            'mock3': MockAnalyzer
        }
        
        for name, cls in analyzers.items():
            AnalyzerFactory.register(name, cls)
        
        # Verify all registrations
        registered = AnalyzerFactory.get_registered_analyzers()
        assert all(name in registered for name in analyzers)
        
        # Bulk create analyzers
        instances = {
            name: AnalyzerFactory.get(name)()
            for name in analyzers
        }
        
        # Verify all instances
        assert all(isinstance(analyzer, MockAnalyzer) for analyzer in instances.values())
        
        # Bulk deregister
        for name in analyzers:
            AnalyzerFactory.deregister(name)
        
        # Verify all deregistered
        assert not any(name in AnalyzerFactory.get_registered_analyzers() for name in analyzers)

    def test_factory_error_handling(self):
        """Test error handling in factory operations."""
        # Test registration with invalid analyzer class
        with pytest.raises(TypeError):
            AnalyzerFactory.register('invalid', dict)
        
        # Test getting non-existent analyzer
        with pytest.raises(KeyError):
            AnalyzerFactory.get('non_existent')
        
        # Test deregistering non-existent analyzer
        with pytest.raises(KeyError):
            AnalyzerFactory.deregister('non_existent')
        
        # Test registering with invalid name
        with pytest.raises(ValueError):
            AnalyzerFactory.register('', MockAnalyzer)
        
        # Test registering same name twice
        AnalyzerFactory.register('mock', MockAnalyzer)
        with pytest.raises(ValueError):
            AnalyzerFactory.register('mock', MockAnalyzer)

    def test_factory_thread_safety(self):
        """Test thread safety of factory operations."""
        from concurrent.futures import ThreadPoolExecutor
        import threading
        
        def register_and_use(name: str) -> bool:
            try:
                AnalyzerFactory.register(f'{name}_{threading.get_ident()}', MockAnalyzer)
                analyzer = AnalyzerFactory.get(f'{name}_{threading.get_ident()}')()
                result = analyzer.analyze("<html></html>")
                return isinstance(result, AnalysisResult)
            except Exception:
                return False
        
        # Run concurrent operations
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(register_and_use, [f'mock{i}' for i in range(10)]))
        
        # Verify all operations succeeded
        assert all(results)

    def test_factory_configuration_validation(self):
        """Test configuration validation in factory-created instances."""
        AnalyzerFactory.register('mock', MockAnalyzer)
        
        invalid_configs = [
            None,  # None config
            [],  # List instead of dict
            {'weight': 1.5},  # Invalid weight value
            {'unknown': 'value'}  # Unknown parameter
        ]
        
        for config in invalid_configs:
            with pytest.raises(Exception):
                analyzer = AnalyzerFactory.get('mock')(config)
                analyzer.analyze("<html></html>")

    def test_factory_instance_isolation(self):
        """Test isolation between factory-created analyzer instances."""
        AnalyzerFactory.register('mock', MockAnalyzer)
        
        # Create multiple instances with different configs
        configs = [
            {'param': 'value1'},
            {'param': 'value2'},
            {'param': 'value3'}
        ]
        
        analyzers = [AnalyzerFactory.get('mock')(config) for config in configs]
        
        # Verify each instance has its own config
        for analyzer, config in zip(analyzers, configs):
            assert analyzer.config == config
            assert id(analyzer.config) != id(config)  # Config should be copied
            
        # Modify one instance's config
        analyzers[0].config['new_param'] = 'new_value'
        
        # Verify other instances are unaffected
        for analyzer in analyzers[1:]:
            assert 'new_param' not in analyzer.config 