"""Factory module for creating and managing processors."""

from typing import Dict, Type, Any, Optional
from threading import Lock
from .base import BaseProcessor

class ProcessorFactory:
    """Factory class for managing processors."""
    
    _registry: Dict[str, Type[BaseProcessor]] = {}
    _lock = Lock()
    
    @classmethod
    def register(cls, name: str, processor_class: Type[BaseProcessor]) -> None:
        """Register a processor class.
        
        Args:
            name: Name to register the processor under.
            processor_class: Processor class to register.
            
        Raises:
            ValueError: If name is invalid or already registered.
            TypeError: If processor_class is not a BaseProcessor subclass.
        """
        # Validate name
        if not isinstance(name, str) or not name:
            raise ValueError("Processor name must be a non-empty string")
            
        # Validate processor class
        if not isinstance(processor_class, type):
            raise TypeError("Processor class must be a class type")
        if not issubclass(processor_class, BaseProcessor):
            raise TypeError("Processor class must inherit from BaseProcessor")
            
        with cls._lock:
            if name in cls._registry:
                raise ValueError(f"Processor '{name}' is already registered")
            cls._registry[name] = processor_class
    
    @classmethod
    def deregister(cls, name: str) -> None:
        """Remove a processor from the registry.
        
        Args:
            name: Name of the processor to remove.
            
        Raises:
            KeyError: If processor is not registered.
        """
        with cls._lock:
            if name not in cls._registry:
                raise KeyError(f"No processor registered as '{name}'")
            del cls._registry[name]
    
    @classmethod
    def get(cls, name: str) -> Type[BaseProcessor]:
        """Get a registered processor class.
        
        Args:
            name: Name of the processor to get.
            
        Returns:
            The registered processor class.
            
        Raises:
            KeyError: If processor is not registered.
        """
        with cls._lock:
            if name not in cls._registry:
                raise KeyError(f"No processor registered as '{name}'")
            return cls._registry[name]
    
    @classmethod
    def create(
        cls,
        name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> BaseProcessor:
        """Create a new processor instance.
        
        Args:
            name: Name of the processor to create.
            config: Optional configuration for the processor.
            
        Returns:
            New processor instance.
            
        Raises:
            KeyError: If processor is not registered.
        """
        processor_class = cls.get(name)
        return processor_class(config)
    
    @classmethod
    def get_registered_processors(cls) -> Dict[str, Type[BaseProcessor]]:
        """Get a copy of the processor registry.
        
        Returns:
            Dictionary mapping names to processor classes.
        """
        with cls._lock:
            return cls._registry.copy()
    
    @classmethod
    def clear_registry(cls) -> None:
        """Clear all registered processors."""
        with cls._lock:
            cls._registry.clear() 