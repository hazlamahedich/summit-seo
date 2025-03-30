"""Tests for the memory cache implementation."""

import pytest
import asyncio
from datetime import datetime, timedelta

from summit_seo.cache.base import CacheConfig
from summit_seo.cache.memory_cache import MemoryCache

@pytest.fixture
def memory_cache():
    """Create a memory cache instance for testing."""
    return MemoryCache(CacheConfig(
        ttl=10,  # 10 seconds for testing
        max_size=10,
        namespace="test"
    ))

@pytest.mark.asyncio
async def test_memory_cache_set_get(memory_cache):
    """Test setting and getting values from memory cache."""
    # Set a value
    await memory_cache.set("test_key", "test_value")
    
    # Get the value
    result = await memory_cache.get("test_key")
    
    # Verify result
    assert result.hit is True
    assert result.value == "test_value"
    assert result.expired is False
    assert result.metadata.get("access_count") == 1

@pytest.mark.asyncio
async def test_memory_cache_get_nonexistent(memory_cache):
    """Test getting a nonexistent key from memory cache."""
    result = await memory_cache.get("nonexistent_key")
    
    # Verify result
    assert result.hit is False
    assert result.value is None
    assert result.expired is False

@pytest.mark.asyncio
async def test_memory_cache_expiration(memory_cache):
    """Test cache entry expiration."""
    # Set a value with custom TTL of 1 second
    await memory_cache.set("expiring_key", "expiring_value", ttl=1)
    
    # Get the value immediately - should be a hit
    result1 = await memory_cache.get("expiring_key")
    assert result1.hit is True
    assert result1.value == "expiring_value"
    
    # Wait for the entry to expire
    await asyncio.sleep(1.1)
    
    # Get the value again - should be a miss
    result2 = await memory_cache.get("expiring_key")
    assert result2.hit is False
    assert result2.value is None
    assert result2.expired is True

@pytest.mark.asyncio
async def test_memory_cache_invalidate(memory_cache):
    """Test invalidating a cache entry."""
    # Set a value
    await memory_cache.set("to_invalidate", "test_value")
    
    # Verify it's there
    result1 = await memory_cache.get("to_invalidate")
    assert result1.hit is True
    
    # Invalidate the key
    invalidated = await memory_cache.invalidate("to_invalidate")
    assert invalidated is True
    
    # Verify it's gone
    result2 = await memory_cache.get("to_invalidate")
    assert result2.hit is False
    
    # Try to invalidate again - should return False
    invalidated2 = await memory_cache.invalidate("to_invalidate")
    assert invalidated2 is False

@pytest.mark.asyncio
async def test_memory_cache_clear(memory_cache):
    """Test clearing all cache entries."""
    # Set multiple values
    await memory_cache.set("key1", "value1")
    await memory_cache.set("key2", "value2")
    await memory_cache.set("key3", "value3")
    
    # Verify cache size
    size = await memory_cache.get_size()
    assert size == 3
    
    # Clear the cache
    cleared_count = await memory_cache.clear()
    assert cleared_count == 3
    
    # Verify cache is empty
    size = await memory_cache.get_size()
    assert size == 0

@pytest.mark.asyncio
async def test_memory_cache_get_keys(memory_cache):
    """Test getting all cache keys."""
    # Set multiple values
    await memory_cache.set("key1", "value1")
    await memory_cache.set("key2", "value2")
    await memory_cache.set("key3", "value3")
    
    # Get all keys
    keys = await memory_cache.get_keys()
    assert sorted(keys) == ["key1", "key2", "key3"]
    
    # Get keys with pattern
    keys_with_1 = await memory_cache.get_keys("*1")
    assert keys_with_1 == ["key1"]

@pytest.mark.asyncio
async def test_memory_cache_max_size(memory_cache):
    """Test cache respects max_size limit."""
    # Configure a small cache
    small_cache = MemoryCache(CacheConfig(
        ttl=10,
        max_size=3,
        namespace="small"
    ))
    
    # Fill the cache
    await small_cache.set("key1", "value1")
    await small_cache.set("key2", "value2")
    await small_cache.set("key3", "value3")
    
    # Verify cache size
    size = await small_cache.get_size()
    assert size == 3
    
    # Add one more entry - should evict the oldest
    await small_cache.set("key4", "value4")
    
    # Verify cache size hasn't changed
    size = await small_cache.get_size()
    assert size == 3
    
    # Verify the oldest entry was evicted
    result = await small_cache.get("key1")
    assert result.hit is False

@pytest.mark.asyncio
async def test_memory_cache_namespaces():
    """Test cache namespaces are isolated."""
    cache1 = MemoryCache(CacheConfig(namespace="ns1"))
    cache2 = MemoryCache(CacheConfig(namespace="ns2"))
    
    # Set same key in different namespaces
    await cache1.set("shared_key", "value1")
    await cache2.set("shared_key", "value2")
    
    # Get values from each namespace
    result1 = await cache1.get("shared_key")
    result2 = await cache2.get("shared_key")
    
    # Verify values are namespace-specific
    assert result1.value == "value1"
    assert result2.value == "value2"
    
    # Clear one namespace
    await cache1.clear()
    
    # Verify only that namespace was cleared
    result1 = await cache1.get("shared_key")
    result2 = await cache2.get("shared_key")
    assert result1.hit is False
    assert result2.hit is True

@pytest.mark.asyncio
async def test_memory_cache_get_or_set(memory_cache):
    """Test get_or_set functionality."""
    # Create a function that returns a value
    async def get_value():
        return "computed_value"
    
    # Get a value using get_or_set (should compute)
    result1 = await memory_cache.get_or_set("computed_key", get_value)
    assert result1.value == "computed_value"
    assert result1.hit is False
    
    # Get the value again (should hit cache)
    result2 = await memory_cache.get("computed_key")
    assert result2.value == "computed_value"
    assert result2.hit is True

@pytest.mark.asyncio
async def test_memory_cache_stats(memory_cache):
    """Test cache statistics tracking."""
    # Perform some operations
    await memory_cache.set("key1", "value1")
    
    # Hit
    await memory_cache.get("key1")
    
    # Miss
    await memory_cache.get("nonexistent")
    
    # Get stats
    stats = memory_cache.get_stats()
    
    # Verify basic stats
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["sets"] == 1 