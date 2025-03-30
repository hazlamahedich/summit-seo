"""Test cases for processor factory functionality."""

import pytest
from typing import Dict, Any, List
import threading
import asyncio
from summit_seo.processor.base import BaseProcessor
from summit_seo.processor.factory import ProcessorFactory

class TestProcessor(BaseProcessor):
    """Test processor for factory testing."""
    
    def _get_required_fields(self) -> List[str]:
        return ['test']
    
    async def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {'processed': data}

class AnotherTestProcessor(BaseProcessor):
    """Another test processor for factory testing."""
    
    def _get_required_fields(self) -> List[str]:
        return ['another_test']
    
    async def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {'another_processed': data}

@pytest.fixture(autouse=True)
def clear_registry():
    """Clear the processor registry before and after each test."""
    ProcessorFactory.clear_registry()
    yield
    ProcessorFactory.clear_registry()

async def test_register_processor():
    """Test processor registration."""
    ProcessorFactory.register('test', TestProcessor)
    assert 'test' in ProcessorFactory.get_registered_processors()
    assert ProcessorFactory.get('test') == TestProcessor

async def test_register_invalid_name():
    """Test registration with invalid names."""
    invalid_names = ['', None, 123, [], {}]
    for name in invalid_names:
        with pytest.raises(ValueError):
            ProcessorFactory.register(name, TestProcessor)

async def test_register_invalid_processor():
    """Test registration with invalid processor classes."""
    invalid_processors = [
        None,
        'not a class',
        123,
        object,  # Not a BaseProcessor subclass
        type('InvalidProcessor', (), {})  # Dynamic class not inheriting BaseProcessor
    ]
    for processor in invalid_processors:
        with pytest.raises(TypeError):
            ProcessorFactory.register('test', processor)

async def test_register_duplicate():
    """Test registration of duplicate processor names."""
    ProcessorFactory.register('test', TestProcessor)
    with pytest.raises(ValueError):
        ProcessorFactory.register('test', AnotherTestProcessor)

async def test_deregister_processor():
    """Test processor deregistration."""
    ProcessorFactory.register('test', TestProcessor)
    ProcessorFactory.deregister('test')
    assert 'test' not in ProcessorFactory.get_registered_processors()

async def test_deregister_nonexistent():
    """Test deregistration of non-existent processor."""
    with pytest.raises(KeyError):
        ProcessorFactory.deregister('nonexistent')

async def test_get_processor():
    """Test getting registered processor."""
    ProcessorFactory.register('test', TestProcessor)
    processor_class = ProcessorFactory.get('test')
    assert processor_class == TestProcessor

async def test_get_nonexistent_processor():
    """Test getting non-existent processor."""
    with pytest.raises(KeyError):
        ProcessorFactory.get('nonexistent')

async def test_create_processor():
    """Test processor instance creation."""
    ProcessorFactory.register('test', TestProcessor)
    config = {'test_config': 'value'}
    processor = ProcessorFactory.create('test', config)
    
    assert isinstance(processor, TestProcessor)
    assert processor.config == config

async def test_create_processor_no_config():
    """Test processor creation without configuration."""
    ProcessorFactory.register('test', TestProcessor)
    processor = ProcessorFactory.create('test')
    
    assert isinstance(processor, TestProcessor)
    assert processor.config == {}

async def test_get_registered_processors():
    """Test getting registered processors."""
    ProcessorFactory.register('test1', TestProcessor)
    ProcessorFactory.register('test2', AnotherTestProcessor)
    
    registry = ProcessorFactory.get_registered_processors()
    assert len(registry) == 2
    assert registry['test1'] == TestProcessor
    assert registry['test2'] == AnotherTestProcessor

async def test_clear_registry():
    """Test clearing the processor registry."""
    ProcessorFactory.register('test1', TestProcessor)
    ProcessorFactory.register('test2', AnotherTestProcessor)
    
    ProcessorFactory.clear_registry()
    assert not ProcessorFactory.get_registered_processors()

async def test_thread_safety():
    """Test thread-safe registration and deregistration."""
    def register_processors():
        for i in range(100):
            try:
                ProcessorFactory.register(f'test{i}', TestProcessor)
            except ValueError:
                pass  # Ignore if already registered
    
    def deregister_processors():
        for i in range(100):
            try:
                ProcessorFactory.deregister(f'test{i}')
            except KeyError:
                pass  # Ignore if already deregistered
    
    threads = [
        threading.Thread(target=register_processors),
        threading.Thread(target=register_processors),
        threading.Thread(target=deregister_processors),
        threading.Thread(target=deregister_processors)
    ]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # No exceptions should have been raised

async def test_registry_isolation():
    """Test that registry modifications don't affect existing processors."""
    ProcessorFactory.register('test', TestProcessor)
    processor = ProcessorFactory.create('test')
    
    # Modify registry
    ProcessorFactory.clear_registry()
    ProcessorFactory.register('test', AnotherTestProcessor)
    
    # Original processor should maintain its type
    assert isinstance(processor, TestProcessor)
    
    # New processor should be of new type
    new_processor = ProcessorFactory.create('test')
    assert isinstance(new_processor, AnotherTestProcessor)

async def test_concurrent_access():
    """Test concurrent access to factory methods."""
    async def concurrent_operations():
        operations = [
            ProcessorFactory.register('test1', TestProcessor),
            ProcessorFactory.register('test2', AnotherTestProcessor),
            ProcessorFactory.create('test1'),
            ProcessorFactory.get('test2'),
            ProcessorFactory.deregister('test1'),
            ProcessorFactory.get_registered_processors()
        ]
        await asyncio.gather(*operations, return_exceptions=True)
    
    await concurrent_operations()
    # No exceptions should have been raised 