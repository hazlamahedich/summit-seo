"""Integration tests for the collector module."""

import pytest
import asyncio
from typing import Dict, Any, List
from summit_seo.collector.base import BaseCollector, CollectionResult
from summit_seo.collector.factory import CollectorFactory
from summit_seo.collector.webpage_collector import WebPageCollector

# Test Collectors
class ChainCollector(BaseCollector):
    """Collector that chains results from multiple collectors."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.collectors: List[BaseCollector] = []
        
    def add_collector(self, collector: BaseCollector):
        """Add a collector to the chain."""
        self.collectors.append(collector)
        
    async def _collect_data(self, url: str) -> Dict[str, Any]:
        results = []
        for collector in self.collectors:
            result = await collector.collect(url)
            results.append(result)
            
        # Combine results
        combined_content = "\n".join(r.html_content for r in results)
        combined_metadata = {
            f"{collector.name}_{key}": value
            for result, collector in zip(results, self.collectors)
            for key, value in result.metadata.items()
        }
        
        return {
            'html_content': combined_content,
            'status_code': results[0].status_code,
            'headers': results[0].headers,
            'metadata': combined_metadata
        }

class MetadataCollector(BaseCollector):
    """Collector that extracts metadata from other collector results."""
    
    async def _collect_data(self, url: str) -> Dict[str, Any]:
        return {
            'html_content': '',
            'status_code': 200,
            'headers': {},
            'metadata': {'url': url, 'type': 'metadata'}
        }

# Factory Integration Tests
@pytest.mark.asyncio
async def test_collector_chain_integration():
    """Test integration of multiple collectors through factory."""
    # Register collectors
    CollectorFactory.register('webpage', WebPageCollector)
    CollectorFactory.register('metadata', MetadataCollector)
    CollectorFactory.register('chain', ChainCollector)
    
    # Create collector instances
    webpage_collector = CollectorFactory.create('webpage')
    metadata_collector = CollectorFactory.create('metadata')
    chain_collector = CollectorFactory.create('chain')
    
    # Add collectors to chain
    chain_collector.add_collector(webpage_collector)
    chain_collector.add_collector(metadata_collector)
    
    # Test collection
    result = await chain_collector.collect('https://example.com')
    assert isinstance(result, CollectionResult)
    assert 'metadata_url' in result.metadata
    assert 'metadata_type' in result.metadata

# Configuration Inheritance Tests
@pytest.mark.asyncio
async def test_configuration_inheritance():
    """Test configuration inheritance between collectors."""
    base_config = {
        'timeout': 30,
        'max_retries': 3,
        'headers': {'User-Agent': 'Test Bot'}
    }
    
    # Create collectors with inherited config
    webpage_collector = WebPageCollector(base_config)
    metadata_collector = MetadataCollector(base_config)
    chain_collector = ChainCollector(base_config)
    
    # Verify config inheritance
    assert webpage_collector.timeout == base_config['timeout']
    assert metadata_collector.max_retries == base_config['max_retries']
    assert chain_collector.headers['User-Agent'] == base_config['headers']['User-Agent']

# Concurrent Operation Tests
@pytest.mark.asyncio
async def test_concurrent_collector_operations():
    """Test concurrent operations with multiple collectors."""
    collectors = [
        WebPageCollector(),
        MetadataCollector(),
        ChainCollector()
    ]
    
    urls = [
        'https://example.com',
        'https://example.org',
        'https://example.net'
    ]
    
    # Create collection tasks
    tasks = [
        collector.collect(url)
        for collector in collectors
        for url in urls
    ]
    
    # Run collections concurrently
    results = await asyncio.gather(*tasks)
    assert len(results) == len(collectors) * len(urls)
    assert all(isinstance(r, CollectionResult) for r in results)

# Error Propagation Tests
@pytest.mark.asyncio
async def test_error_propagation():
    """Test error propagation through collector chain."""
    class ErrorCollector(BaseCollector):
        async def _collect_data(self, url: str) -> Dict[str, Any]:
            raise ValueError("Test error")
    
    chain_collector = ChainCollector()
    chain_collector.add_collector(WebPageCollector())
    chain_collector.add_collector(ErrorCollector())
    
    with pytest.raises(ValueError):
        await chain_collector.collect('https://example.com')

# Resource Management Tests
@pytest.mark.asyncio
async def test_collector_resource_management():
    """Test resource management across collectors."""
    class ResourceCollector(BaseCollector):
        def __init__(self, config=None):
            super().__init__(config)
            self.resources = set()
        
        async def _collect_data(self, url: str) -> Dict[str, Any]:
            self.resources.add(url)
            return {
                'html_content': '',
                'status_code': 200,
                'headers': {},
                'metadata': {'resources': len(self.resources)}
            }
    
    collector = ResourceCollector()
    urls = ['https://example.com'] * 3
    
    # Collect same URL multiple times
    results = await asyncio.gather(*[collector.collect(url) for url in urls])
    assert len(collector.resources) == 1  # Should deduplicate resources

# Factory State Tests
def test_factory_state_isolation():
    """Test isolation of factory state between operations."""
    # Clear registry
    CollectorFactory.clear_registry()
    
    # Register collectors
    CollectorFactory.register('webpage', WebPageCollector)
    CollectorFactory.register('metadata', MetadataCollector)
    
    # Get initial state
    initial_registry = CollectorFactory.get_registered_collectors()
    
    # Modify registry
    CollectorFactory.register('chain', ChainCollector)
    
    # Verify state isolation
    assert len(initial_registry) == 2
    assert len(CollectorFactory.get_registered_collectors()) == 3

# Configuration Validation Tests
@pytest.mark.asyncio
async def test_integrated_config_validation():
    """Test configuration validation across collector chain."""
    invalid_configs = [
        {'timeout': -1},
        {'max_retries': -1},
        {'requests_per_second': 0}
    ]
    
    for config in invalid_configs:
        chain_collector = ChainCollector(config)
        chain_collector.add_collector(WebPageCollector(config))
        
        with pytest.raises(ValueError):
            chain_collector.validate_config()

# Result Aggregation Tests
@pytest.mark.asyncio
async def test_result_aggregation():
    """Test aggregation of results from multiple collectors."""
    class AggregatorCollector(BaseCollector):
        def __init__(self, config=None):
            super().__init__(config)
            self.results = []
        
        async def _collect_data(self, url: str) -> Dict[str, Any]:
            # Collect from multiple sources
            collectors = [WebPageCollector(), MetadataCollector()]
            results = await asyncio.gather(*[c.collect(url) for c in collectors])
            self.results.extend(results)
            
            return {
                'html_content': '',
                'status_code': 200,
                'headers': {},
                'metadata': {'total_results': len(self.results)}
            }
    
    collector = AggregatorCollector()
    result = await collector.collect('https://example.com')
    assert result.metadata['total_results'] == 2

# Performance Impact Tests
@pytest.mark.asyncio
async def test_collector_performance_impact():
    """Test performance impact of collector chain."""
    chain_collector = ChainCollector()
    collectors = [WebPageCollector(), MetadataCollector()]
    
    for collector in collectors:
        chain_collector.add_collector(collector)
    
    start_time = asyncio.get_event_loop().time()
    await chain_collector.collect('https://example.com')
    end_time = asyncio.get_event_loop().time()
    
    # Collection time should be reasonable
    assert end_time - start_time < 5.0  # Adjust threshold as needed 