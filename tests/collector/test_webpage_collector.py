"""Tests for the webpage collector module."""

import pytest
import aiohttp
from typing import Dict, Any
from summit_seo.collector.webpage_collector import WebPageCollector
from summit_seo.collector.base import CollectionError

# Configuration Tests
def test_webpage_collector_initialization(collector_config):
    """Test webpage collector initialization with configuration."""
    collector = WebPageCollector(collector_config)
    
    # Test base configuration
    assert collector.requests_per_second == collector_config['requests_per_second']
    assert collector.timeout == collector_config['timeout']
    assert collector.max_retries == collector_config['max_retries']
    assert collector.retry_delay == collector_config['retry_delay']
    
    # Test webpage-specific configuration
    assert collector.follow_redirects == collector_config['follow_redirects']
    assert collector.max_redirects == collector_config['max_redirects']
    assert collector.proxy == collector_config['proxy']
    assert collector.cookies == collector_config['cookies']

def test_webpage_collector_default_config():
    """Test webpage collector initialization with default configuration."""
    collector = WebPageCollector()
    
    # Test default values
    assert collector.follow_redirects is True
    assert collector.max_redirects == 5
    assert collector.proxy is None
    assert isinstance(collector.cookies, dict)
    assert len(collector.cookies) == 0
    
    # Test default headers
    assert 'User-Agent' in collector.headers
    assert 'Accept' in collector.headers
    assert 'Accept-Language' in collector.headers
    assert 'Accept-Encoding' in collector.headers
    assert 'Connection' in collector.headers

def test_webpage_collector_custom_headers():
    """Test webpage collector with custom headers."""
    custom_headers = {
        'User-Agent': 'Custom Bot 1.0',
        'Custom-Header': 'Test Value'
    }
    collector = WebPageCollector({'headers': custom_headers})
    
    assert collector.headers['User-Agent'] == 'Custom Bot 1.0'
    assert collector.headers['Custom-Header'] == 'Test Value'
    assert 'Accept' in collector.headers
    assert 'Accept-Language' in collector.headers

# Collection Tests
@pytest.mark.asyncio
async def test_successful_collection(webpage_collector, test_urls, mock_session,
                                   mock_html_response):
    """Test successful webpage collection."""
    result = await webpage_collector.collect(test_urls['valid'])
    
    assert result.status_code == 200
    assert result.html_content == mock_html_response
    assert 'Content-Type' in result.headers
    assert result.metadata['title'] == 'Test Page'
    assert result.metadata['encoding'] == 'utf-8'
    assert isinstance(result.collection_time, float)

@pytest.mark.asyncio
async def test_redirect_handling(webpage_collector, mock_session, mock_response_factory):
    """Test handling of redirects."""
    # Mock a redirect response
    mock_session.response = mock_response_factory(
        status=301,
        content="Redirected content",
        headers={'Location': 'https://example.com/new'},
        history=[mock_response_factory(status=301)]
    )
    
    result = await webpage_collector.collect('https://example.com/old')
    assert result.metadata['is_redirect'] is True
    assert result.metadata['redirect_count'] == 1
    assert result.metadata['final_url'] == 'https://example.com/new'

@pytest.mark.asyncio
async def test_encoding_handling(webpage_collector, mock_session, mock_response_factory):
    """Test handling of different content encodings."""
    encodings = ['utf-8', 'iso-8859-1', 'windows-1252']
    test_content = "Test content with special chars: áéíóú"
    
    for encoding in encodings:
        mock_session.response = mock_response_factory(
            content=test_content,
            charset=encoding,
            headers={'Content-Type': f'text/html; charset={encoding}'}
        )
        
        result = await webpage_collector.collect('https://example.com')
        assert result.html_content == test_content
        assert result.metadata['encoding'] == encoding

@pytest.mark.asyncio
async def test_invalid_encoding_fallback(webpage_collector, mock_session, 
                                       mock_response_factory):
    """Test fallback behavior with invalid encoding."""
    mock_session.response = mock_response_factory(
        content="Test content",
        charset='invalid',
        headers={'Content-Type': 'text/html; charset=invalid'}
    )
    
    result = await webpage_collector.collect('https://example.com')
    assert len(result.html_content) > 0
    assert result.metadata['encoding'] == 'invalid'

# Error Handling Tests
@pytest.mark.asyncio
async def test_http_error_handling(webpage_collector, mock_session, mock_response_factory):
    """Test handling of HTTP errors."""
    error_cases = [
        (404, "Not Found"),
        (500, "Internal Server Error"),
        (403, "Forbidden"),
        (502, "Bad Gateway")
    ]
    
    for status, content in error_cases:
        mock_session.response = mock_response_factory(
            status=status,
            content=content,
            headers={'Content-Type': 'text/plain'}
        )
        
        result = await webpage_collector.collect('https://example.com')
        assert result.status_code == status
        assert content in result.html_content

@pytest.mark.asyncio
async def test_timeout_handling(webpage_collector, mock_session):
    """Test handling of timeout errors."""
    class TimeoutSession(mock_session):
        async def get(self, *args, **kwargs):
            raise asyncio.TimeoutError()
    
    # Replace mock session with timeout session
    webpage_collector._session_class = TimeoutSession
    
    with pytest.raises(CollectionError) as exc_info:
        await webpage_collector.collect('https://example.com')
    assert "timed out" in str(exc_info.value).lower()

@pytest.mark.asyncio
async def test_connection_error_handling(webpage_collector, mock_session):
    """Test handling of connection errors."""
    class ErrorSession(mock_session):
        async def get(self, *args, **kwargs):
            raise aiohttp.ClientError("Connection failed")
    
    webpage_collector._session_class = ErrorSession
    
    with pytest.raises(CollectionError) as exc_info:
        await webpage_collector.collect('https://example.com')
    assert "failed" in str(exc_info.value).lower()

# Metadata Extraction Tests
@pytest.mark.asyncio
async def test_metadata_extraction(webpage_collector, mock_session, mock_response_factory):
    """Test extraction of metadata from HTML content."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Metadata Test</title>
        <meta name="description" content="Test description">
        <meta name="keywords" content="test,metadata">
        <meta charset="utf-16">
    </head>
    <body>
        <h1>Test Content</h1>
        <p>Test paragraph</p>
    </body>
    </html>
    """
    
    mock_session.response = mock_response_factory(
        content=html_content,
        headers={'Content-Type': 'text/html; charset=utf-16'}
    )
    
    result = await webpage_collector.collect('https://example.com')
    assert result.metadata['title'] == 'Metadata Test'
    assert result.metadata['encoding'] == 'utf-16'
    assert isinstance(result.metadata['content_length'], int)
    assert result.metadata['content_type'] == 'text/html; charset=utf-16'

# Configuration Validation Tests
def test_webpage_collector_config_validation():
    """Test validation of webpage collector configuration."""
    invalid_configs = [
        {'max_redirects': -1},
        {'proxy': 123},  # Not a string
        {'cookies': 'invalid'},  # Not a dict
        {'headers': 'invalid'},  # Not a dict
        {'follow_redirects': 'invalid'}  # Not a boolean
    ]
    
    for config in invalid_configs:
        with pytest.raises(ValueError):
            collector = WebPageCollector(config)
            collector.validate_config()

# Resource Management Tests
@pytest.mark.asyncio
async def test_session_cleanup(webpage_collector, mock_session):
    """Test proper cleanup of aiohttp session."""
    class CleanupSession(mock_session):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.cleanup_called = False
        
        async def close(self):
            self.cleanup_called = True
    
    # Create a session and ensure it's cleaned up
    session = CleanupSession()
    async with session:
        pass
    assert session.cleanup_called

# Performance Tests
@pytest.mark.asyncio
async def test_concurrent_collection(webpage_collector, test_urls):
    """Test concurrent webpage collection."""
    urls = [test_urls['valid']] * 3
    tasks = [webpage_collector.collect(url) for url in urls]
    results = await asyncio.gather(*tasks)
    
    assert len(results) == 3
    assert all(r.status_code == 200 for r in results)
    assert all(isinstance(r.collection_time, float) for r in results) 