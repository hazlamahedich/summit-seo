"""Memory cache implementation."""

import asyncio
import fnmatch
import time
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union

from .base import BaseCache, CacheConfig, CacheError, CacheKeyError, CacheResult, CacheValueError, CacheKey

# Type variables for key and value
K = TypeVar('K')
V = TypeVar('V')

class CacheEntry:
    """Cache entry with metadata."""
    
    def __init__(self, key: Any, value: Any, ttl: int, timestamp: datetime):
        """Initialize a cache entry.
        
        Args:
            key: Cache key
            value: Cached value
            ttl: Time to live in seconds
            timestamp: Entry creation timestamp
        """
        self.key = key
        self.value = value
        self.ttl = ttl
        self.timestamp = timestamp
        self.last_accessed = timestamp
        self.access_count = 0
    
    def is_expired(self) -> bool:
        """Check if the entry has expired.
        
        Returns:
            True if expired, False otherwise
        """
        if self.ttl <= 0:  # TTL of 0 means no expiration
            return False
            
        expiration_time = self.timestamp.timestamp() + self.ttl
        return datetime.now().timestamp() > expiration_time
    
    def access(self) -> None:
        """Update entry access metadata."""
        self.last_accessed = datetime.now()
        self.access_count += 1


class MemoryCache(BaseCache[CacheKey, Any]):
    """In-memory cache implementation.
    
    This cache stores items in memory using an OrderedDict for efficient
    access and LRU (Least Recently Used) eviction policy.
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        """Initialize the memory cache.
        
        Args:
            config: Optional cache configuration
        """
        super().__init__(config)
        
        # Use an OrderedDict for efficient LRU implementation
        self._cache: Dict[str, Dict[CacheKey, CacheEntry]] = {}
        self._lock = asyncio.Lock()  # Lock for thread safety
        
        # Initialize namespace
        self._ensure_namespace(self.config.namespace)
    
    def _ensure_namespace(self, namespace: str) -> None:
        """Ensure a namespace exists in the cache.
        
        Args:
            namespace: Namespace to ensure exists
        """
        if namespace not in self._cache:
            self._cache[namespace] = OrderedDict()
    
    def _build_key(self, key: CacheKey, namespace: Optional[str] = None) -> Tuple[str, CacheKey]:
        """Build a full cache key with namespace.
        
        Args:
            key: The cache key
            namespace: Optional namespace (defaults to config namespace)
            
        Returns:
            Tuple of (namespace, key)
        """
        ns = namespace or self.config.namespace
        self._ensure_namespace(ns)
        return (ns, key)
    
    async def get(self, key: CacheKey) -> CacheResult[Any]:
        """Get a value from the cache.
        
        Args:
            key: The cache key to retrieve
            
        Returns:
            CacheResult containing the value and hit status
            
        Raises:
            CacheKeyError: If the key is invalid
        """
        if key is None:
            self._update_stats(miss=True)
            raise CacheKeyError("Cache key cannot be None")
        
        ns, cache_key = self._build_key(key)
        
        async with self._lock:
            if cache_key not in self._cache[ns]:
                self._update_stats(miss=True)
                return CacheResult(
                    value=None,
                    hit=False,
                    timestamp=datetime.now(),
                    ttl=self.config.ttl,
                    expired=False
                )
            
            entry = self._cache[ns][cache_key]
            
            # Check if entry has expired
            if entry.is_expired():
                # Remove expired entry
                del self._cache[ns][cache_key]
                self._update_stats(miss=True)
                return CacheResult(
                    value=None,
                    hit=False,
                    timestamp=entry.timestamp,
                    ttl=entry.ttl,
                    expired=True
                )
            
            # Update access metadata
            entry.access()
            
            # Move to end of OrderedDict for LRU tracking
            self._cache[ns].move_to_end(cache_key)
            
            self._update_stats(hit=True)
            return CacheResult(
                value=entry.value,
                hit=True,
                timestamp=entry.timestamp,
                ttl=entry.ttl,
                expired=False,
                metadata={
                    'access_count': entry.access_count,
                    'last_accessed': entry.last_accessed
                }
            )
    
    async def set(self, key: CacheKey, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache.
        
        Args:
            key: The cache key to set
            value: The value to cache
            ttl: Optional time to live in seconds (overrides config.ttl if provided)
            
        Raises:
            CacheKeyError: If the key is invalid
            CacheValueError: If the value is None
        """
        if key is None:
            self._update_stats(error=True)
            raise CacheKeyError("Cache key cannot be None")
        
        if value is None:
            self._update_stats(error=True)
            raise CacheValueError("Cache value cannot be None")
        
        ns, cache_key = self._build_key(key)
        ttl_value = ttl if ttl is not None else self.config.ttl
        
        async with self._lock:
            # Check if we need to evict items
            if len(self._cache[ns]) >= self.config.max_size and cache_key not in self._cache[ns]:
                self._evict_lru_item(ns)
            
            # Create new cache entry
            entry = CacheEntry(
                key=cache_key,
                value=value,
                ttl=ttl_value,
                timestamp=datetime.now()
            )
            
            # Store entry
            self._cache[ns][cache_key] = entry
            self._update_stats(set_op=True)
    
    def _evict_lru_item(self, namespace: str) -> bool:
        """Evict the least recently used item from the cache.
        
        Args:
            namespace: Namespace to evict from
            
        Returns:
            True if an item was evicted, False otherwise
        """
        if not self._cache[namespace]:
            return False
            
        # Get the first item (oldest) from the OrderedDict
        oldest_key, _ = next(iter(self._cache[namespace].items()))
        del self._cache[namespace][oldest_key]
        self._update_stats(eviction=True)
        return True
    
    async def invalidate(self, key: CacheKey) -> bool:
        """Invalidate a cache entry.
        
        Args:
            key: The cache key to invalidate
            
        Returns:
            True if the key was invalidated, False if it didn't exist
        """
        if key is None:
            raise CacheKeyError("Cache key cannot be None")
        
        ns, cache_key = self._build_key(key)
        
        async with self._lock:
            if cache_key in self._cache[ns]:
                del self._cache[ns][cache_key]
                return True
            return False
    
    async def invalidate_namespace(self, namespace: Optional[str] = None) -> int:
        """Invalidate all cache entries in a namespace.
        
        Args:
            namespace: The namespace to invalidate (defaults to config.namespace)
            
        Returns:
            Number of invalidated cache entries
        """
        ns = namespace or self.config.namespace
        
        async with self._lock:
            if ns in self._cache:
                count = len(self._cache[ns])
                self._cache[ns].clear()
                return count
            return 0
    
    async def clear(self) -> int:
        """Clear all cache entries in all namespaces.
        
        Returns:
            Number of cleared cache entries
        """
        async with self._lock:
            total_count = sum(len(entries) for entries in self._cache.values())
            self._cache.clear()
            self._ensure_namespace(self.config.namespace)
            return total_count
    
    async def get_keys(self, pattern: Optional[str] = None) -> List[CacheKey]:
        """Get all cache keys matching a pattern in the current namespace.
        
        Args:
            pattern: Optional pattern to match keys against
            
        Returns:
            List of matching cache keys
        """
        ns = self.config.namespace
        
        if ns not in self._cache:
            return []
        
        async with self._lock:
            if pattern is None:
                return list(self._cache[ns].keys())
            
            if isinstance(pattern, str):
                # Simple string pattern matching
                return [
                    key for key in self._cache[ns].keys()
                    if isinstance(key, str) and fnmatch.fnmatch(key, pattern)
                ]
            
            # For other types, just return all keys
            return list(self._cache[ns].keys())
    
    async def get_size(self) -> int:
        """Get the current size of the default namespace cache.
        
        Returns:
            Number of items in the cache
        """
        ns = self.config.namespace
        
        if ns not in self._cache:
            return 0
        
        return len(self._cache[ns])
    
    async def has_key(self, key: CacheKey) -> bool:
        """Check if a key exists in the cache.
        
        Args:
            key: The cache key to check
            
        Returns:
            True if the key exists and has not expired, False otherwise
        """
        if key is None:
            return False
        
        ns, cache_key = self._build_key(key)
        
        async with self._lock:
            if cache_key not in self._cache[ns]:
                return False
                
            entry = self._cache[ns][cache_key]
            if entry.is_expired():
                # Remove expired entry
                del self._cache[ns][cache_key]
                return False
                
            return True
    
    async def cleanup_expired(self) -> int:
        """Remove all expired entries from the cache.
        
        Returns:
            Number of removed entries
        """
        count = 0
        now = datetime.now().timestamp()
        
        async with self._lock:
            for ns in list(self._cache.keys()):
                to_remove = []
                
                for key, entry in self._cache[ns].items():
                    if entry.is_expired():
                        to_remove.append(key)
                
                for key in to_remove:
                    del self._cache[ns][key]
                    count += 1
        
        return count 