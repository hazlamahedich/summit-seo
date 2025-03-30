"""Factory module for creating cache instances."""

from typing import Dict, Type, Any, Optional, TypeVar

from .base import BaseCache, CacheConfig

T = TypeVar('T', bound=BaseCache)

class CacheFactory:
    """Factory class for creating and managing cache instances.
    
    This class implements the factory pattern for cache creation and provides
    a registration mechanism for different cache types.
    """

    _registry: Dict[str, Type[BaseCache]] = {}
    _instances: Dict[str, BaseCache] = {}

    @classmethod
    def register(cls, name: str, cache_class: Type[T]) -> None:
        """Register a new cache class.
        
        Args:
            name: Name to register the cache under
            cache_class: Cache class to register
            
        Raises:
            ValueError: If name is already registered or class is invalid
        """
        if name in cls._registry:
            raise ValueError(f"Cache '{name}' is already registered")
        
        if not issubclass(cache_class, BaseCache):
            raise ValueError(
                f"Class {cache_class.__name__} must inherit from BaseCache"
            )
        
        cls._registry[name] = cache_class

    @classmethod
    def create(cls, name: str, config: Optional[CacheConfig] = None) -> T:
        """Create or retrieve a cache instance.
        
        Args:
            name: Name of the cache to create
            config: Optional configuration for the cache
            
        Returns:
            Instance of the requested cache
            
        Raises:
            ValueError: If cache name is not registered
        """
        if name not in cls._registry:
            raise ValueError(f"No cache registered with name '{name}'")
        
        # If config includes a cache_key, use it for instance lookup
        cache_key = config.name if hasattr(config, 'name') and config.name else name
        
        # Return existing instance if available
        if cache_key in cls._instances:
            return cls._instances[cache_key]
        
        # Create new instance
        cache_class = cls._registry[name]
        instance = cache_class(config)
        
        # Cache instance for future use
        cls._instances[cache_key] = instance
        
        return instance

    @classmethod
    def get_instance(cls, name: str) -> Optional[BaseCache]:
        """Get an existing cache instance.
        
        Args:
            name: Name of the cache instance to retrieve
            
        Returns:
            Cache instance or None if not found
        """
        return cls._instances.get(name)

    @classmethod
    def get_registered_caches(cls) -> Dict[str, Type[BaseCache]]:
        """Get all registered cache types.
        
        Returns:
            Dictionary mapping cache names to cache classes
        """
        return cls._registry.copy()

    @classmethod
    def clear_registry(cls) -> None:
        """Clear all registered caches.
        
        This is primarily useful for testing.
        """
        cls._registry.clear()
        
    @classmethod
    def clear_instances(cls) -> None:
        """Clear all cache instances.
        
        This is primarily useful for testing or for freeing resources.
        """
        cls._instances.clear()
        
    @classmethod
    async def clear_all_caches(cls) -> Dict[str, int]:
        """Clear the contents of all cache instances.
        
        Returns:
            Dictionary mapping cache names to number of cleared items
        """
        results = {}
        
        for name, instance in cls._instances.items():
            count = await instance.clear()
            results[name] = count
            
        return results 