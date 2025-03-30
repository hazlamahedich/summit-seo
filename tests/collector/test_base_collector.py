"""Tests for the base collector module."""

import pytest
import asyncio
from typing import Dict, Any
from summit_seo.collector.base import (
    BaseCollector,
    CollectorError,
    RateLimitError,
    CollectionResult
)

# Configuration Tests
def test_collector_initialization(mock_collector, collector_config):
    """Test collector initialization with configuration."""
    collector = mock_collector.__class__(collector_config)
    assert collector.requests_per_second == collector_config['requests_per_second']
    assert collector.timeout == collector_config['timeout']
    assert collector.max_retries == collector_config['max_retries']
    assert collector.retry_delay == collector_config['retry_delay']
    assert collector.headers == collector_config['headers']
    assert collector.verify_ssl == collector_config['verify_ssl']

def test_collector_default_config(mock_collector):
    """Test collector initialization with default configuration."""
    collector = mock_collector.__class__()
    assert collector.requests_per_second == 2.0
    assert collector.timeout == 30.0
    assert collector.max_retries == 3
    assert collector.retry_delay == 1.0
    assert isinstance(collector.headers, dict)
    assert collector.verify_ssl is True

def test_collector_invalid_config():
    """Test collector initialization with invalid configuration."""
    invalid_configs = [
        {'requests_per_second': 0},
        {'requests_per_second': -1},
        {'timeout': 0},
        {'timeout': -1},
        {'max_retries': -1},
        {'retry_delay': -1}
    ]
    
    for config in invalid_configs:
        with pytest.raises(ValueError):
            mock = MockCollector(config)
            mock.validate_config()

# URL Validation Tests
@pytest.mark.asyncio
async def test_valid_url_collection(mock_collector, test_urls):
    """Test collection with valid URL."""
    result = await mock_collector.collect(test_urls['valid'])
    assert isinstance(result, CollectionResult)
    assert result.url == test_urls['valid']
    assert result.status_code == 200
    assert isinstance(result.headers, dict)
    assert isinstance(result.metadata, dict)

@pytest.mark.asyncio
async def test_invalid_url_collection(mock_collector, test_urls):
    """Test collection with invalid URL."""
    with pytest.raises(CollectorError) as exc_info:
        await mock_collector.collect(test_urls['invalid'])
    assert "Invalid URL format" in str(exc_info.value)

# Rate Limiting Tests
@pytest.mark.asyncio
async def test_rate_limiting(mock_collector):
    """Test rate limiting functionality."""
    collector = mock_collector.__class__({'requests_per_second': 2.0})
    start_time = asyncio.get_event_loop().time()
    
    # Make multiple requests
    for _ in range(3):
        await collector.collect('https://example.com')
    
    end_time = asyncio.get_event_loop().time()
    # Should take at least 1 second due to rate limiting
    assert end_time - start_time >= 1.0

@pytest.mark.asyncio
async def test_rate_limit_burst(mock_collector):
    """Test rate limiting under burst conditions."""
    collector = mock_collector.__class__({'requests_per_second': 1.0})
    
    # Try to make requests faster than allowed
    tasks = [
        collector.collect('https://example.com')
        for _ in range(3)
    ]
    
    start_time = asyncio.get_event_loop().time()
    await asyncio.gather(*tasks)
    end_time = asyncio.get_event_loop().time()
    
    # Should take at least 2 seconds for 3 requests at 1 req/sec
    assert end_time - start_time >= 2.0

# Retry Mechanism Tests
class RetryTestCollector(BaseCollector):
    def __init__(self, config=None, fail_count=2):
        super().__init__(config)
        self.attempts = 0
        self.fail_count = fail_count
    
    async def _collect_data(self, url: str) -> Dict[str, Any]:
        self.attempts += 1
        if self.attempts <= self.fail_count:
            raise CollectorError("Simulated failure")
        return {
            'html_content': 'Success',
            'status_code': 200,
            'headers': {},
            'metadata': {'attempts': self.attempts}
        }

@pytest.mark.asyncio
async def test_retry_mechanism():
    """Test retry mechanism with temporary failures."""
    collector = RetryTestCollector({'max_retries': 3, 'retry_delay': 0.1})
    result = await collector.collect('https://example.com')
    assert result.html_content == 'Success'
    assert result.metadata['attempts'] == 3

@pytest.mark.asyncio
async def test_retry_exhaustion():
    """Test retry mechanism when all retries are exhausted."""
    collector = RetryTestCollector(
        {'max_retries': 2, 'retry_delay': 0.1},
        fail_count=3
    )
    with pytest.raises(CollectionError) as exc_info:
        await collector.collect('https://example.com')
    assert "Collection failed after 2 attempts" in str(exc_info.value)

# Error Handling Tests
@pytest.mark.asyncio
async def test_collection_error_handling(mock_collector):
    """Test handling of various collection errors."""
    error_cases = [
        (None, TypeError),
        ("", CollectorError),
        ("http://", CollectorError),
        ("ftp://example.com", CollectorError)
    ]
    
    for url, expected_error in error_cases:
        with pytest.raises(expected_error):
            await mock_collector.collect(url)

# Result Type Tests
@pytest.mark.asyncio
async def test_collection_result_attributes(mock_collector, test_urls):
    """Test CollectionResult attributes."""
    result = await mock_collector.collect(test_urls['valid'])
    assert hasattr(result, 'url')
    assert hasattr(result, 'html_content')
    assert hasattr(result, 'status_code')
    assert hasattr(result, 'headers')
    assert hasattr(result, 'collection_time')
    assert hasattr(result, 'metadata')

# Collector Name Tests
def test_collector_name(mock_collector):
    """Test collector name property."""
    assert mock_collector.name == "MockCollector"

# Configuration Validation Tests
def test_config_validation_comprehensive(mock_collector):
    """Test comprehensive configuration validation."""
    invalid_configs = [
        {'requests_per_second': 'invalid'},
        {'timeout': 'invalid'},
        {'max_retries': 'invalid'},
        {'retry_delay': 'invalid'},
        {'headers': 'invalid'},
        {'verify_ssl': 'invalid'}
    ]
    
    for config in invalid_configs:
        with pytest.raises((ValueError, TypeError)):
            collector = mock_collector.__class__(config)
            collector.validate_config()

# Async Context Tests
@pytest.mark.asyncio
async def test_concurrent_collection(mock_collector, test_urls):
    """Test concurrent collection requests."""
    urls = [test_urls['valid']] * 3
    tasks = [mock_collector.collect(url) for url in urls]
    results = await asyncio.gather(*tasks)
    
    assert len(results) == 3
    assert all(isinstance(r, CollectionResult) for r in results)
    assert all(r.status_code == 200 for r in results)

class MockCollector(BaseCollector):
    """Mock collector for testing."""
    async def _collect_data(self, url: str) -> Dict[str, Any]:
        return {
            'html_content': '<html><body>Test content</body></html>',
            'status_code': 200,
            'headers': {'Content-Type': 'text/html'},
            'metadata': {'test': 'data'}
        } 