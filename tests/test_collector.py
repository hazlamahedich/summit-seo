import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
from summit_seo.collector import (
    BaseCollector,
    CollectorFactory,
    CollectedData,
    CollectionError,
    RateLimiter
)

# Mock collector for testing
class MockCollector(BaseCollector):
    async def collect(self, url: str) -> CollectedData:
        await self.validate_url(url)
        await self.handle_rate_limit()
        return CollectedData(
            url=url,
            content="Test content",
            metadata={"test": "value"}
        )

@pytest.fixture
def config():
    return {"requests_per_second": 2.0}

class TestBaseCollector:
    def test_init(self):
        collector = MockCollector()
        assert collector.config == {}
        assert isinstance(collector.rate_limiter, RateLimiter)
        
        collector_with_config = MockCollector({"requests_per_second": 2.0})
        assert collector_with_config.config == {"requests_per_second": 2.0}
        assert collector_with_config.rate_limiter.min_interval == 0.5
    
    @pytest.mark.asyncio
    async def test_validate_url(self):
        collector = MockCollector()
        
        # Should raise error for empty URL
        with pytest.raises(CollectionError):
            await collector.validate_url("")
        
        # Should not raise error for valid URL
        await collector.validate_url("https://example.com")
    
    @pytest.mark.asyncio
    async def test_preprocess_url(self):
        collector = MockCollector()
        
        url = " https://example.com "
        processed = await collector.preprocess_url(url)
        assert processed == "https://example.com"
    
    @pytest.mark.asyncio
    async def test_collect(self):
        collector = MockCollector()
        
        data = await collector.collect("https://example.com")
        assert isinstance(data, CollectedData)
        assert data.url == "https://example.com"
        assert data.content == "Test content"
        assert data.metadata == {"test": "value"}
        assert isinstance(data.timestamp, datetime)

class TestCollectorFactory:
    def setup_method(self):
        CollectorFactory.clear_registry()
    
    def test_register(self):
        CollectorFactory.register("mock", MockCollector)
        assert "mock" in CollectorFactory.list_collectors()
        
        # Test duplicate registration
        with pytest.raises(ValueError):
            CollectorFactory.register("mock", MockCollector)
        
        # Test invalid collector class
        class InvalidCollector:
            pass
        
        with pytest.raises(ValueError):
            CollectorFactory.register("invalid", InvalidCollector)
    
    def test_create(self):
        CollectorFactory.register("mock", MockCollector)
        
        # Test creation without config
        collector = CollectorFactory.create("mock")
        assert isinstance(collector, MockCollector)
        assert collector.config == {}
        
        # Test creation with config
        config = {"requests_per_second": 2.0}
        collector = CollectorFactory.create("mock", config)
        assert isinstance(collector, MockCollector)
        assert collector.config == config
        
        # Test creation of unregistered collector
        with pytest.raises(ValueError):
            CollectorFactory.create("nonexistent")
    
    def test_list_collectors(self):
        assert CollectorFactory.list_collectors() == []
        
        CollectorFactory.register("mock1", MockCollector)
        CollectorFactory.register("mock2", MockCollector)
        
        collectors = CollectorFactory.list_collectors()
        assert len(collectors) == 2
        assert "mock1" in collectors
        assert "mock2" in collectors

class TestRateLimiter:
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        rate_limiter = RateLimiter(requests_per_second=2.0)  # 0.5s between requests
        
        # First request should not wait
        start = datetime.now()
        await rate_limiter.wait()
        elapsed = (datetime.now() - start).total_seconds()
        assert elapsed < 0.1  # Should be almost instant
        
        # Second request should wait
        start = datetime.now()
        await rate_limiter.wait()
        elapsed = (datetime.now() - start).total_seconds()
        assert 0.4 <= elapsed <= 0.6  # Should wait ~0.5s 