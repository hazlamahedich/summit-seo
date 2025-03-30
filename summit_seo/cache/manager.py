"""Cache manager module for coordinating cache operations."""

import logging
import asyncio
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union, Callable, Awaitable

from .base import BaseCache, CacheConfig, CacheError, CacheResult, CacheKey
from .factory import CacheFactory
from .memory_cache import MemoryCache
from .file_cache import FileCache

# Type variables
K = TypeVar('K')
V = TypeVar('V')

# Setup logging
logger = logging.getLogger(__name__)

class CacheManager:
    """Manages caching operations across the application.
    
    This class provides a simplified interface for cache operations
    and coordinates caching across different modules.
    """
    
    def __init__(self):
        """Initialize the cache manager."""
        self._initialized = False
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the cache system.
        
        Args:
            config: Optional configuration dictionary for caches
        """
        if self._initialized:
            return
        
        # Register cache types
        CacheFactory.register('memory', MemoryCache)
        CacheFactory.register('file', FileCache)
        
        # Create default configurations
        memory_config = CacheConfig(
            ttl=3600,               # 1 hour
            max_size=10000,         # Max 10,000 items
            namespace="default",
            enable_stats=True,
            invalidate_on_error=False
        )
        
        file_config = CacheConfig(
            ttl=86400,              # 24 hours
            max_size=100000,        # Max 100,000 items
            namespace="default",
            enable_stats=True,
            invalidate_on_error=False,
            persistent=True
        )
        
        # Apply custom configurations if provided
        if config:
            if 'memory' in config:
                self._update_config(memory_config, config['memory'])
            
            if 'file' in config:
                self._update_config(file_config, config['file'])
        
        # Create cache instances
        CacheFactory.create('memory', memory_config)
        CacheFactory.create('file', file_config)
        
        # Create specialized cache namespaces with custom TTL values
        self._create_specialized_caches()
        
        self._initialized = True
        
        logger.info("Cache manager initialized")
    
    def _update_config(self, base_config: CacheConfig, updates: Dict[str, Any]) -> None:
        """Update a base config with custom values.
        
        Args:
            base_config: Base configuration to update
            updates: Dictionary of updates to apply
        """
        for key, value in updates.items():
            if hasattr(base_config, key):
                setattr(base_config, key, value)
    
    def _create_specialized_caches(self) -> None:
        """Create specialized cache namespaces with custom TTL values."""
        # Short-lived caches
        short_config = CacheConfig(
            ttl=300,                # 5 minutes
            max_size=1000,
            namespace="short_term",
            enable_stats=True
        )
        
        # Medium-lived caches
        medium_config = CacheConfig(
            ttl=3600,               # 1 hour
            max_size=5000,
            namespace="medium_term",
            enable_stats=True
        )
        
        # Long-lived caches
        long_config = CacheConfig(
            ttl=86400,              # 24 hours
            max_size=10000,
            namespace="long_term",
            enable_stats=True
        )
        
        # Create memory caches with different TTLs
        short_mem_config = CacheConfig(**vars(short_config))
        medium_mem_config = CacheConfig(**vars(medium_config))
        long_mem_config = CacheConfig(**vars(long_config))
        
        # Create file caches with different TTLs
        short_file_config = CacheConfig(**vars(short_config))
        medium_file_config = CacheConfig(**vars(medium_config))
        long_file_config = CacheConfig(**vars(long_config))
        
        # Add names to configs for instance identification
        short_mem_config.name = "memory_short"
        medium_mem_config.name = "memory_medium"
        long_mem_config.name = "memory_long"
        short_file_config.name = "file_short"
        medium_file_config.name = "file_medium"
        long_file_config.name = "file_long"
        
        # Create cache instances
        CacheFactory.create('memory', short_mem_config)
        CacheFactory.create('memory', medium_mem_config)
        CacheFactory.create('memory', long_mem_config)
        CacheFactory.create('file', short_file_config)
        CacheFactory.create('file', medium_file_config)
        CacheFactory.create('file', long_file_config)
    
    def get_cache(self, cache_type: str, name: Optional[str] = None) -> BaseCache:
        """Get a cache instance.
        
        Args:
            cache_type: Type of cache ('memory' or 'file')
            name: Optional instance name ('short', 'medium', 'long', or None for default)
            
        Returns:
            Cache instance
            
        Raises:
            ValueError: If cache type or name is invalid
        """
        if not self._initialized:
            self.initialize()
        
        if cache_type not in ('memory', 'file'):
            raise ValueError(f"Invalid cache type: {cache_type}")
        
        if name is None:
            return CacheFactory.get_instance(cache_type)
        
        if name not in ('short', 'medium', 'long'):
            raise ValueError(f"Invalid cache name: {name}")
        
        cache_key = f"{cache_type}_{name}"
        cache = CacheFactory.get_instance(cache_key)
        
        if cache is None:
            raise ValueError(f"Cache not found: {cache_key}")
        
        return cache
    
    async def get(self, key: CacheKey, cache_type: str = 'memory', 
                 name: Optional[str] = None) -> CacheResult:
        """Get a value from the cache.
        
        Args:
            key: Cache key
            cache_type: Type of cache ('memory' or 'file')
            name: Optional instance name
            
        Returns:
            CacheResult containing the value and hit status
        """
        cache = self.get_cache(cache_type, name)
        return await cache.get(key)
    
    async def set(self, key: CacheKey, value: Any, ttl: Optional[int] = None,
                 cache_type: str = 'memory', name: Optional[str] = None) -> None:
        """Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional time to live
            cache_type: Type of cache ('memory' or 'file')
            name: Optional instance name
        """
        cache = self.get_cache(cache_type, name)
        await cache.set(key, value, ttl)
    
    async def invalidate(self, key: CacheKey, cache_type: Optional[str] = None,
                        name: Optional[str] = None) -> None:
        """Invalidate a cache entry, optionally across multiple caches.
        
        Args:
            key: Cache key
            cache_type: Optional type of cache (if None, invalidate in all types)
            name: Optional instance name (if None, invalidate in all instances)
        """
        if cache_type is not None:
            # Invalidate in specific cache type
            cache = self.get_cache(cache_type, name)
            await cache.invalidate(key)
        else:
            # Invalidate in all cache types
            if name is not None:
                # Invalidate in specific instance of all cache types
                for type_name in ('memory', 'file'):
                    try:
                        cache = self.get_cache(type_name, name)
                        await cache.invalidate(key)
                    except ValueError:
                        pass
            else:
                # Invalidate in all instances of all cache types
                for instance in CacheFactory._instances.values():
                    await instance.invalidate(key)
    
    async def clear_all(self) -> Dict[str, int]:
        """Clear all caches.
        
        Returns:
            Dictionary mapping cache names to number of cleared items
        """
        return await CacheFactory.clear_all_caches()
    
    async def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all caches.
        
        Returns:
            Dictionary mapping cache names to statistics
        """
        stats = {}
        
        for name, instance in CacheFactory._instances.items():
            stats[name] = instance.get_stats()
        
        return stats
    
    async def cleanup(self) -> Dict[str, int]:
        """Clean up expired entries in all caches.
        
        Returns:
            Dictionary mapping cache names to number of removed entries
        """
        results = {}
        
        for name, instance in CacheFactory._instances.items():
            if hasattr(instance, 'cleanup_expired'):
                count = await instance.cleanup_expired()
                results[name] = count
        
        return results
    
    async def get_or_compute(self, key: CacheKey, compute_func: Callable[[], Awaitable[V]],
                            ttl: Optional[int] = None, cache_type: str = 'memory',
                            name: Optional[str] = None) -> V:
        """Get a value from cache or compute if not found.
        
        Args:
            key: Cache key
            compute_func: Async function to compute the value if not in cache
            ttl: Optional time to live
            cache_type: Type of cache ('memory' or 'file')
            name: Optional instance name
            
        Returns:
            The cached or computed value
        """
        cache = self.get_cache(cache_type, name)
        result = await cache.get_or_set(key, compute_func, ttl)
        return result.value


# Singleton instance
cache_manager = CacheManager() 