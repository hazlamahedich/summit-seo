"""Base cache module for caching functionality."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Generic, Optional, TypeVar, Union, List, Tuple

# Type variable for cache key and value
K = TypeVar('K')
V = TypeVar('V')

# Cache key type alias
CacheKey = Union[str, Tuple[str, ...]]

@dataclass
class CacheConfig:
    """Configuration for cache behavior."""
    ttl: int = 3600  # Time to live in seconds (default: 1 hour)
    max_size: int = 1000  # Maximum number of items in cache
    invalidate_on_error: bool = False  # Whether to invalidate cache on errors
    namespace: str = "default"  # Namespace for the cache
    enable_stats: bool = True  # Whether to track cache statistics
    persistent: bool = False  # Whether the cache should persist between runs

@dataclass
class CacheResult(Generic[V]):
    """Result of a cache operation."""
    value: Optional[V]
    hit: bool  # True if the result was found in cache, False otherwise
    timestamp: datetime
    ttl: int  # Time to live in seconds
    expired: bool = False  # True if the cache entry has expired
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize metadata if None."""
        if self.metadata is None:
            self.metadata = {}


class CacheError(Exception):
    """Base exception for cache errors."""
    pass


class CacheKeyError(CacheError):
    """Exception raised when a cache key is invalid or not found."""
    pass


class CacheValueError(CacheError):
    """Exception raised when a cache value is invalid."""
    pass


class CacheConfigError(CacheError):
    """Exception raised when cache configuration is invalid."""
    pass


class BaseCache(ABC, Generic[K, V]):
    """Abstract base class for cache implementations.
    
    This class defines the interface that all cache implementations must implement.
    It provides methods for getting, setting, and invalidating cached values,
    as well as cache statistics.
    """

    def __init__(self, config: Optional[CacheConfig] = None):
        """Initialize the cache with configuration.
        
        Args:
            config: Optional configuration for the cache behavior
        """
        self.config = config or CacheConfig()
        self._validate_config()
        
        # Cache statistics
        self._hits = 0
        self._misses = 0
        self._sets = 0
        self._evictions = 0
        self._errors = 0
        self._start_time = datetime.now()

    def _validate_config(self) -> None:
        """Validate cache configuration.
        
        Raises:
            CacheConfigError: If configuration is invalid
        """
        if self.config.ttl < 0:
            raise CacheConfigError("TTL cannot be negative")
        
        if self.config.max_size < 1:
            raise CacheConfigError("Max size must be at least 1")

    @abstractmethod
    async def get(self, key: K) -> CacheResult[V]:
        """Get a value from the cache.
        
        Args:
            key: The cache key to retrieve
            
        Returns:
            CacheResult containing the value and hit status
            
        Raises:
            CacheKeyError: If the key is invalid
        """
        pass

    @abstractmethod
    async def set(self, key: K, value: V, ttl: Optional[int] = None) -> None:
        """Set a value in the cache.
        
        Args:
            key: The cache key to set
            value: The value to cache
            ttl: Optional time to live in seconds (overrides config.ttl if provided)
            
        Raises:
            CacheKeyError: If the key is invalid
            CacheValueError: If the value is invalid
        """
        pass

    @abstractmethod
    async def invalidate(self, key: K) -> bool:
        """Invalidate a cache entry.
        
        Args:
            key: The cache key to invalidate
            
        Returns:
            True if the key was invalidated, False if it didn't exist
        """
        pass

    @abstractmethod
    async def invalidate_namespace(self, namespace: Optional[str] = None) -> int:
        """Invalidate all cache entries in a namespace.
        
        Args:
            namespace: The namespace to invalidate (defaults to config.namespace)
            
        Returns:
            Number of invalidated cache entries
        """
        pass

    @abstractmethod
    async def clear(self) -> int:
        """Clear all cache entries.
        
        Returns:
            Number of cleared cache entries
        """
        pass

    @abstractmethod
    async def get_keys(self, pattern: Optional[str] = None) -> List[K]:
        """Get all cache keys matching a pattern.
        
        Args:
            pattern: Optional pattern to match keys against
            
        Returns:
            List of matching cache keys
        """
        pass

    @abstractmethod
    async def get_size(self) -> int:
        """Get the current size of the cache.
        
        Returns:
            Number of items in the cache
        """
        pass

    async def get_or_set(self, key: K, getter_func, ttl: Optional[int] = None) -> CacheResult[V]:
        """Get a value from the cache or set it if not found.
        
        Args:
            key: The cache key
            getter_func: Async function to call if key is not in cache
            ttl: Optional time to live in seconds
            
        Returns:
            CacheResult containing the value and hit status
            
        Raises:
            CacheError: If cache operation fails
        """
        result = await self.get(key)
        
        if not result.hit or result.expired:
            try:
                value = await getter_func()
                await self.set(key, value, ttl)
                
                return CacheResult(
                    value=value,
                    hit=False,
                    timestamp=datetime.now(),
                    ttl=ttl or self.config.ttl,
                    expired=False,
                    metadata={'source': 'getter_func'}
                )
            except Exception as e:
                self._errors += 1
                if self.config.invalidate_on_error:
                    await self.invalidate(key)
                raise CacheError(f"Failed to get or set cache value: {str(e)}")
        
        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary containing cache statistics
        """
        if not self.config.enable_stats:
            return {'stats_enabled': False}
        
        total_operations = self._hits + self._misses
        hit_ratio = self._hits / total_operations if total_operations > 0 else 0
        
        uptime = datetime.now() - self._start_time
        uptime_seconds = uptime.total_seconds()
        
        return {
            'hits': self._hits,
            'misses': self._misses,
            'sets': self._sets,
            'evictions': self._evictions,
            'errors': self._errors,
            'hit_ratio': hit_ratio,
            'uptime_seconds': uptime_seconds,
            'operations_per_second': total_operations / uptime_seconds if uptime_seconds > 0 else 0
        }

    def _update_stats(self, hit: bool = False, miss: bool = False, 
                      set_op: bool = False, eviction: bool = False, 
                      error: bool = False) -> None:
        """Update cache statistics.
        
        Args:
            hit: Whether a cache hit occurred
            miss: Whether a cache miss occurred
            set_op: Whether a cache set operation occurred
            eviction: Whether a cache eviction occurred
            error: Whether a cache error occurred
        """
        if not self.config.enable_stats:
            return
            
        if hit:
            self._hits += 1
        if miss:
            self._misses += 1
        if set_op:
            self._sets += 1
        if eviction:
            self._evictions += 1
        if error:
            self._errors += 1

    @abstractmethod
    async def has_key(self, key: K) -> bool:
        """Check if a key exists in the cache.
        
        Args:
            key: The cache key to check
            
        Returns:
            True if the key exists, False otherwise
        """
        pass

    @property
    def name(self) -> str:
        """Get the name of the cache implementation."""
        return self.__class__.__name__ 