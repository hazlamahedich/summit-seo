"""Factory module for creating analyzer instances."""

from typing import Dict, Type, Any, Optional, TypeVar, Generic

from .base import BaseAnalyzer, InputType, OutputType

T = TypeVar('T', bound=BaseAnalyzer)

class AnalyzerFactory(Generic[T]):
    """Factory class for creating and managing analyzer instances.
    
    This class implements the factory pattern for analyzer creation and provides
    a registration mechanism for different analyzer types.
    """

    _registry: Dict[str, Type[BaseAnalyzer]] = {}

    @classmethod
    def register(cls, name: str, analyzer_class: Type[T]) -> None:
        """Register a new analyzer class.
        
        Args:
            name: Name to register the analyzer under
            analyzer_class: Analyzer class to register
            
        Raises:
            ValueError: If name is already registered or class is invalid
        """
        if name in cls._registry:
            raise ValueError(f"Analyzer '{name}' is already registered")
        
        if not issubclass(analyzer_class, BaseAnalyzer):
            raise ValueError(
                f"Class {analyzer_class.__name__} must inherit from BaseAnalyzer"
            )
        
        cls._registry[name] = analyzer_class

    @classmethod
    def create(cls, name: str, config: Optional[Dict[str, Any]] = None) -> T:
        """Create an instance of a registered analyzer.
        
        Args:
            name: Name of the analyzer to create
            config: Optional configuration for the analyzer
            
        Returns:
            Instance of the requested analyzer
            
        Raises:
            ValueError: If analyzer name is not registered
        """
        if name not in cls._registry:
            raise ValueError(f"No analyzer registered with name '{name}'")
        
        analyzer_class = cls._registry[name]
        return analyzer_class(config)

    @classmethod
    def list_analyzers(cls) -> list[str]:
        """Get a list of all registered analyzer names.
        
        Returns:
            List of registered analyzer names
        """
        return list(cls._registry.keys())

    @classmethod
    def clear_registry(cls) -> None:
        """Clear all registered analyzers.
        
        This is primarily useful for testing.
        """
        cls._registry.clear() 