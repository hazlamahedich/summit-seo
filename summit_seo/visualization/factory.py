"""Factory for visualization components."""

from typing import Dict, Any, Optional, Type, ClassVar

from .base import BaseVisualizer


class VisualizationFactory:
    """Factory for creating visualization components."""

    _registry: ClassVar[Dict[str, Type[BaseVisualizer]]] = {}

    @classmethod
    def register(cls, name: str, visualizer_class: Type[BaseVisualizer]) -> None:
        """Register a visualizer class with the factory.
        
        Args:
            name: Name to register the visualizer with.
            visualizer_class: The visualizer class to register.
            
        Raises:
            ValueError: If name is already registered or class doesn't inherit from BaseVisualizer.
        """
        if name in cls._registry:
            raise ValueError(f"Visualizer {name} is already registered")
            
        if not issubclass(visualizer_class, BaseVisualizer):
            raise ValueError(f"Class {visualizer_class.__name__} must inherit from BaseVisualizer")
            
        cls._registry[name] = visualizer_class
    
    @classmethod
    def create(cls, name: str, config: Optional[Dict[str, Any]] = None) -> BaseVisualizer:
        """Create a visualizer instance.
        
        Args:
            name: Name of the registered visualizer.
            config: Optional configuration dictionary.
            
        Returns:
            Instance of the requested visualizer.
            
        Raises:
            ValueError: If visualizer name is not registered.
        """
        if name not in cls._registry:
            raise ValueError(f"Visualizer {name} is not registered")
            
        visualizer_class = cls._registry[name]
        return visualizer_class(config)
    
    @classmethod
    def get_registered_visualizers(cls) -> Dict[str, Type[BaseVisualizer]]:
        """Get all registered visualizers.
        
        Returns:
            Dictionary of registered visualizer names and classes.
        """
        return cls._registry.copy() 