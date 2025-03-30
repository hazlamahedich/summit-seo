"""Tests for the collector factory module."""

import pytest
from typing import Dict, Any
from summit_seo.collector.base import BaseCollector
from summit_seo.collector.factory import CollectorFactory
from summit_seo.collector.webpage_collector import WebPageCollector

# Test Collector Classes
class TestCollector(BaseCollector):
    """Test collector for factory testing."""
    async def _collect_data(self, url: str) -> Dict[str, Any]:
        return {'html_content': '', 'status_code': 200, 'headers': {}, 'metadata': {}}

class AnotherTestCollector(BaseCollector):
    """Another test collector for factory testing."""
    async def _collect_data(self, url: str) -> Dict[str, Any]:
        return {'html_content': '', 'status_code': 200, 'headers': {}, 'metadata': {}}

# Registration Tests
def test_collector_registration(registered_collectors):
    """Test collector registration."""
    # Register a new collector
    CollectorFactory.register('test', TestCollector)
    
    # Verify registration
    assert 'test' in CollectorFactory.get_registered_collectors()
    assert CollectorFactory.get('test') == TestCollector

def test_duplicate_registration():
    """Test handling of duplicate collector registration."""
    CollectorFactory.register('unique', TestCollector)
    
    with pytest.raises(ValueError) as exc_info:
        CollectorFactory.register('unique', AnotherTestCollector)
    assert "already registered" in str(exc_info.value)

def test_invalid_registration():
    """Test registration with invalid collector classes."""
    invalid_cases = [
        ('invalid1', None),
        ('invalid2', object),
        ('invalid3', str),
        ('invalid4', dict),
        ('invalid5', type('DynamicClass', (), {}))
    ]
    
    for name, invalid_class in invalid_cases:
        with pytest.raises(TypeError):
            CollectorFactory.register(name, invalid_class)

def test_invalid_collector_names():
    """Test registration with invalid collector names."""
    invalid_names = [
        None,
        '',
        123,
        {},
        [],
        True
    ]
    
    for invalid_name in invalid_names:
        with pytest.raises(ValueError):
            CollectorFactory.register(invalid_name, TestCollector)

# Deregistration Tests
def test_collector_deregistration():
    """Test collector deregistration."""
    # Register and then deregister
    CollectorFactory.register('temp', TestCollector)
    assert 'temp' in CollectorFactory.get_registered_collectors()
    
    CollectorFactory.deregister('temp')
    assert 'temp' not in CollectorFactory.get_registered_collectors()

def test_deregister_nonexistent():
    """Test deregistration of non-existent collector."""
    with pytest.raises(KeyError) as exc_info:
        CollectorFactory.deregister('nonexistent')
    assert "No collector registered" in str(exc_info.value)

# Retrieval Tests
def test_get_registered_collector():
    """Test retrieval of registered collector."""
    CollectorFactory.register('test_get', TestCollector)
    collector_class = CollectorFactory.get('test_get')
    assert collector_class == TestCollector

def test_get_nonexistent_collector():
    """Test retrieval of non-existent collector."""
    with pytest.raises(KeyError) as exc_info:
        CollectorFactory.get('nonexistent')
    assert "No collector registered" in str(exc_info.value)

# Instance Creation Tests
def test_create_collector_instance():
    """Test creation of collector instances."""
    CollectorFactory.register('test_create', TestCollector)
    
    # Create with default config
    instance1 = CollectorFactory.create('test_create')
    assert isinstance(instance1, TestCollector)
    
    # Create with custom config
    config = {'timeout': 60, 'max_retries': 5}
    instance2 = CollectorFactory.create('test_create', config)
    assert isinstance(instance2, TestCollector)
    assert instance2.timeout == 60
    assert instance2.max_retries == 5

def test_create_with_invalid_config():
    """Test creation with invalid configuration."""
    CollectorFactory.register('test_invalid_config', TestCollector)
    
    invalid_configs = [
        {'timeout': -1},
        {'max_retries': -1},
        {'requests_per_second': 0}
    ]
    
    for config in invalid_configs:
        with pytest.raises(ValueError):
            instance = CollectorFactory.create('test_invalid_config', config)
            instance.validate_config()

# Registry Management Tests
def test_clear_registry():
    """Test clearing of collector registry."""
    # Register multiple collectors
    CollectorFactory.register('test1', TestCollector)
    CollectorFactory.register('test2', AnotherTestCollector)
    
    # Clear registry
    CollectorFactory.clear_registry()
    assert len(CollectorFactory.get_registered_collectors()) == 0

def test_registry_isolation():
    """Test isolation of collector registry."""
    # Register a collector
    CollectorFactory.register('test_isolation', TestCollector)
    
    # Get registry copy and modify it
    registry_copy = CollectorFactory.get_registered_collectors()
    registry_copy['new_collector'] = AnotherTestCollector
    
    # Verify original registry is unchanged
    assert 'new_collector' not in CollectorFactory.get_registered_collectors()

# Integration Tests
def test_factory_integration_with_webpage_collector():
    """Test factory integration with WebPageCollector."""
    # Register and create WebPageCollector
    CollectorFactory.register('webpage', WebPageCollector)
    
    config = {
        'timeout': 30,
        'max_retries': 3,
        'headers': {'User-Agent': 'Test Bot'}
    }
    
    collector = CollectorFactory.create('webpage', config)
    assert isinstance(collector, WebPageCollector)
    assert collector.timeout == config['timeout']
    assert collector.max_retries == config['max_retries']
    assert collector.headers['User-Agent'] == config['headers']['User-Agent']

# Error Cases Tests
def test_comprehensive_error_cases():
    """Test comprehensive error cases for factory operations."""
    error_cases = [
        # Registration errors
        lambda: CollectorFactory.register(None, TestCollector),
        lambda: CollectorFactory.register('', TestCollector),
        lambda: CollectorFactory.register('test', None),
        lambda: CollectorFactory.register('test', object),
        
        # Deregistration errors
        lambda: CollectorFactory.deregister('nonexistent'),
        lambda: CollectorFactory.deregister(''),
        
        # Retrieval errors
        lambda: CollectorFactory.get('nonexistent'),
        lambda: CollectorFactory.get(''),
        
        # Creation errors
        lambda: CollectorFactory.create('nonexistent'),
        lambda: CollectorFactory.create('')
    ]
    
    for error_case in error_cases:
        with pytest.raises((ValueError, TypeError, KeyError)):
            error_case()

# Thread Safety Tests
@pytest.mark.asyncio
async def test_concurrent_registration():
    """Test concurrent collector registration."""
    import asyncio
    
    async def register_collector(name: str, collector_class: type):
        await asyncio.sleep(0.1)  # Simulate work
        CollectorFactory.register(name, collector_class)
    
    # Try to register collectors concurrently
    tasks = [
        register_collector(f'concurrent_{i}', TestCollector)
        for i in range(5)
    ]
    
    await asyncio.gather(*tasks)
    
    # Verify all registrations succeeded
    registry = CollectorFactory.get_registered_collectors()
    assert all(f'concurrent_{i}' in registry for i in range(5)) 