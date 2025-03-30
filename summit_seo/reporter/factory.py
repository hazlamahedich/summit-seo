"""Reporter factory module for Summit SEO."""

from typing import Dict, Type, Any, Optional
from threading import Lock
from .base import BaseReporter

class ReporterFactoryError(Exception):
    """Base exception for reporter factory errors."""
    pass

class ReporterRegistrationError(ReporterFactoryError):
    """Exception raised when reporter registration fails."""
    pass

class ReporterNotFoundError(ReporterFactoryError):
    """Exception raised when a reporter is not found."""
    pass

class ReporterFactory:
    """Factory class for creating and managing reporters."""

    _registry: Dict[str, Type[BaseReporter]] = {}
    _lock = Lock()

    @classmethod
    def register(cls, name: str, reporter_class: Type[BaseReporter]) -> None:
        """Register a reporter class.
        
        Args:
            name: Name to register the reporter under.
            reporter_class: Reporter class to register.
        
        Raises:
            ReporterRegistrationError: If registration fails.
        """
        if not name:
            raise ReporterRegistrationError("Reporter name cannot be empty")
        
        if not isinstance(reporter_class, type):
            raise ReporterRegistrationError(
                f"Expected a class, got {type(reporter_class)}"
            )
        
        if not issubclass(reporter_class, BaseReporter):
            raise ReporterRegistrationError(
                f"{reporter_class.__name__} must inherit from BaseReporter"
            )
        
        with cls._lock:
            if name in cls._registry:
                raise ReporterRegistrationError(
                    f"Reporter '{name}' is already registered"
                )
            cls._registry[name] = reporter_class

    @classmethod
    def deregister(cls, name: str) -> None:
        """Remove a reporter from the registry.
        
        Args:
            name: Name of the reporter to remove.
        
        Raises:
            ReporterNotFoundError: If reporter is not found.
        """
        with cls._lock:
            if name not in cls._registry:
                raise ReporterNotFoundError(f"Reporter '{name}' not found")
            del cls._registry[name]

    @classmethod
    def get(cls, name: str) -> Type[BaseReporter]:
        """Get a reporter class by name.
        
        Args:
            name: Name of the reporter to get.
        
        Returns:
            The reporter class.
        
        Raises:
            ReporterNotFoundError: If reporter is not found.
        """
        with cls._lock:
            if name not in cls._registry:
                raise ReporterNotFoundError(f"Reporter '{name}' not found")
            return cls._registry[name]

    @classmethod
    def create(cls, name: str, config: Optional[Dict[str, Any]] = None) -> BaseReporter:
        """Create a new reporter instance.
        
        Args:
            name: Name of the reporter to create.
            config: Optional configuration for the reporter.
        
        Returns:
            A new reporter instance.
        
        Raises:
            ReporterNotFoundError: If reporter is not found.
            ReporterFactoryError: If reporter creation fails.
        """
        reporter_class = cls.get(name)
        try:
            return reporter_class(config)
        except Exception as e:
            raise ReporterFactoryError(
                f"Failed to create reporter '{name}': {str(e)}"
            ) from e

    @classmethod
    def get_registered_reporters(cls) -> Dict[str, Type[BaseReporter]]:
        """Get all registered reporters.
        
        Returns:
            Dictionary of registered reporter names and classes.
        """
        with cls._lock:
            return cls._registry.copy()

    @classmethod
    def clear_registry(cls) -> None:
        """Clear all registered reporters."""
        with cls._lock:
            cls._registry.clear() 