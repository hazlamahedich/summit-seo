"""Test fixtures for collector module."""

import pytest
import aiohttp
import asyncio
from typing import Dict, Any, Optional
from summit_seo.collector.base import BaseCollector, CollectionResult
from summit_seo.collector.factory import CollectorFactory
from summit_seo.collector.webpage_collector import WebPageCollector

class MockResponse:
    """Mock aiohttp response for testing."""
    
    def __init__(self, status: int, content: bytes, headers: Dict[str, str], 
                 charset: Optional[str] = None, history: Optional[list] = None,
                 url: str = "https://example.com"):
        self.status = status
        self._content = content
        self.headers = headers
        self.charset = charset
        self.history = history
        self._url = url

    async def read(self) -> bytes:
        return self._content

    @property
    def url(self):
        return self._url

class MockCollector(BaseCollector):
    """Mock collector for testing base functionality."""
    
    async def _collect_data(self, url: str) -> Dict[str, Any]:
        return {
            'html_content': '<html><body>Test content</body></html>',
            'status_code': 200,
            'headers': {'Content-Type': 'text/html'},
            'metadata': {'test': 'data'}
        }

@pytest.fixture
def mock_collector():
    """Fixture providing a mock collector instance."""
    return MockCollector()

@pytest.fixture
def collector_config():
    """Fixture providing test configuration for collectors."""
    return {
        'requests_per_second': 2.0,
        'timeout': 10.0,
        'max_retries': 3,
        'retry_delay': 1.0,
        'headers': {'Custom-Header': 'Test'},
        'verify_ssl': True,
        'follow_redirects': True,
        'max_redirects': 5,
        'proxy': None,
        'cookies': {'session': 'test'}
    }

@pytest.fixture
def mock_html_response():
    """Fixture providing mock HTML response content."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <meta charset="utf-8">
        <meta name="description" content="Test description">
    </head>
    <body>
        <h1>Test Content</h1>
        <p>This is a test page with some content.</p>
        <img src="test.jpg" alt="Test image">
        <a href="https://example.com">Test link</a>
    </body>
    </html>
    """

@pytest.fixture
def mock_response_factory():
    """Factory fixture for creating mock responses."""
    def create_response(status: int = 200, content: str = "", 
                       headers: Optional[Dict[str, str]] = None,
                       charset: str = "utf-8", history: Optional[list] = None,
                       url: str = "https://example.com") -> MockResponse:
        headers = headers or {'Content-Type': 'text/html; charset=utf-8'}
        return MockResponse(
            status=status,
            content=content.encode(charset),
            headers=headers,
            charset=charset,
            history=history,
            url=url
        )
    return create_response

@pytest.fixture
def mock_session(monkeypatch, mock_response_factory, mock_html_response):
    """Fixture providing a mock aiohttp ClientSession."""
    class MockClientSession:
        def __init__(self, *args, **kwargs):
            self.closed = False
            self.response = mock_response_factory(content=mock_html_response)
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            self.closed = True
        
        async def get(self, url: str, **kwargs):
            return self.response
        
        async def close(self):
            self.closed = True
    
    monkeypatch.setattr(aiohttp, "ClientSession", MockClientSession)
    return MockClientSession

@pytest.fixture
def webpage_collector(collector_config):
    """Fixture providing a configured WebPageCollector instance."""
    return WebPageCollector(collector_config)

@pytest.fixture
def registered_collectors():
    """Fixture providing registered test collectors."""
    # Clear existing registrations
    CollectorFactory.clear_registry()
    
    # Register test collectors
    collectors = {
        'mock': MockCollector,
        'webpage': WebPageCollector
    }
    
    for name, collector_class in collectors.items():
        CollectorFactory.register(name, collector_class)
    
    return collectors

@pytest.fixture
def test_urls():
    """Fixture providing test URLs."""
    return {
        'valid': 'https://example.com',
        'invalid': 'not-a-url',
        'redirect': 'https://example.com/redirect',
        'error': 'https://example.com/error',
        'timeout': 'https://example.com/timeout',
        'ssl_error': 'https://expired-cert.com',
        'rate_limit': 'https://rate-limited.com'
    }

@pytest.fixture
def error_responses(mock_response_factory):
    """Fixture providing various error responses."""
    return {
        'not_found': mock_response_factory(
            status=404,
            content="Not Found",
            headers={'Content-Type': 'text/plain'}
        ),
        'server_error': mock_response_factory(
            status=500,
            content="Internal Server Error",
            headers={'Content-Type': 'text/plain'}
        ),
        'redirect': mock_response_factory(
            status=301,
            content="Moved Permanently",
            headers={'Location': 'https://example.com/new'},
            history=[mock_response_factory(status=301)]
        ),
        'invalid_encoding': mock_response_factory(
            status=200,
            content="Invalid UTF-8 sequence",
            charset='invalid',
            headers={'Content-Type': 'text/html; charset=invalid'}
        )
    } 