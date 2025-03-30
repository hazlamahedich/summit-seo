"""Factory for creating progress tracking instances."""

from typing import Dict, Type, Any, Optional
from summit_seo.progress.base import ProgressTracker


class ProgressFactory:
    """Factory for creating progress tracker instances.
    
    This class provides a way to register and create different
    progress tracker implementations.
    """
    
    _registry: Dict[str, Type[ProgressTracker]] = {}
    
    @classmethod
    def register(cls, name: str, tracker_class: Type[ProgressTracker]) -> None:
        """Register a progress tracker implementation.
        
        Args:
            name: Name to register the tracker under.
            tracker_class: The tracker class to register.
        """
        if not issubclass(tracker_class, ProgressTracker):
            raise TypeError(f"Class {tracker_class.__name__} is not a subclass of ProgressTracker")
        
        cls._registry[name] = tracker_class
    
    @classmethod
    def create(cls, tracker_type: str, **kwargs: Any) -> ProgressTracker:
        """Create a progress tracker instance.
        
        Args:
            tracker_type: Type of the tracker implementation to create.
            **kwargs: Additional arguments to pass to the tracker constructor.
            
        Returns:
            A new instance of the requested progress tracker.
            
        Raises:
            KeyError: If no tracker is registered under the given name.
        """
        if tracker_type not in cls._registry:
            raise KeyError(f"No progress tracker registered under name: {tracker_type}")
        
        tracker_class = cls._registry[tracker_type]
        return tracker_class(**kwargs)
    
    @classmethod
    def list_available(cls) -> Dict[str, Type[ProgressTracker]]:
        """List all available progress tracker implementations.
        
        Returns:
            Dictionary mapping names to tracker classes.
        """
        return cls._registry.copy()
    
    @classmethod
    def get_default(cls, **kwargs: Any) -> ProgressTracker:
        """Get the default progress tracker implementation.
        
        Args:
            **kwargs: Additional arguments to pass to the tracker constructor.
            
        Returns:
            A new instance of the default progress tracker.
            
        Raises:
            KeyError: If no default tracker is registered.
        """
        # Use "simple" as the default if available
        if "simple" in cls._registry:
            return cls.create("simple", **kwargs)
        
        # Otherwise, use the first registered tracker
        if not cls._registry:
            raise KeyError("No progress trackers registered")
        
        first_key = next(iter(cls._registry))
        return cls.create(first_key, **kwargs) 