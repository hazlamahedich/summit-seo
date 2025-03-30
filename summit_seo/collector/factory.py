"""Factory module for creating collectors."""

from typing import Dict, Type, Optional, Any
from .base import BaseCollector

class CollectorFactory:
    """Factory class for managing and creating collectors."""
    
    _registry: Dict[str, Type[BaseCollector]] = {}

    @classmethod
    def register(cls, name: str, collector_class: Type[BaseCollector]) -> None:
        """Register a collector class.
        
        Args:
            name: Name to register the collector under
            collector_class: The collector class to register
            
        Raises:
            TypeError: If collector_class is not a subclass of BaseCollector
            ValueError: If name is invalid or already registered
        """
        # Validate collector class
        if not isinstance(collector_class, type) or not issubclass(collector_class, BaseCollector):
            raise TypeError("Collector class must be a subclass of BaseCollector")
        
        # Validate name
        if not name or not isinstance(name, str):
            raise ValueError("Collector name must be a non-empty string")
        
        # Check for existing registration
        if name in cls._registry:
            raise ValueError(f"Collector '{name}' is already registered")
        
        cls._registry[name] = collector_class

    @classmethod
    def deregister(cls, name: str) -> None:
        """Remove a collector from the registry.
        
        Args:
            name: Name of the collector to deregister
            
        Raises:
            KeyError: If collector is not registered
        """
        if name not in cls._registry:
            raise KeyError(f"No collector registered with name '{name}'")
        
        del cls._registry[name]

    @classmethod
    def get(cls, name: str) -> Type[BaseCollector]:
        """Get a collector class by name.
        
        Args:
            name: Name of the collector to get
            
        Returns:
            The collector class
            
        Raises:
            KeyError: If collector is not registered
        """
        if name not in cls._registry:
            raise KeyError(f"No collector registered with name '{name}'")
        
        return cls._registry[name]

    @classmethod
    def create(cls, name: str, config: Optional[Dict[str, Any]] = None) -> BaseCollector:
        """Create a new collector instance.
        
        Args:
            name: Name of the collector to create
            config: Optional configuration for the collector
            
        Returns:
            A new collector instance
            
        Raises:
            KeyError: If collector is not registered
        """
        collector_class = cls.get(name)
        return collector_class(config)

    @classmethod
    def get_registered_collectors(cls) -> Dict[str, Type[BaseCollector]]:
        """Get all registered collectors.
        
        Returns:
            Dictionary mapping collector names to their classes
        """
        return cls._registry.copy()

    @classmethod
    def clear_registry(cls) -> None:
        """Clear all registered collectors."""
        cls._registry.clear() 