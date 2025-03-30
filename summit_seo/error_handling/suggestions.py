"""Module providing actionable suggestions for error resolution.

This module defines the core classes and utilities for creating, managing
and providing actionable suggestions to help users resolve errors encountered
during SEO analysis operations.
"""

import enum
import inspect
import logging
import re
import traceback
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict, List, Optional, Type, Callable, Any, Union, Tuple, Set

logger = logging.getLogger(__name__)


class SuggestionSeverity(enum.Enum):
    """Severity levels for error suggestions."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SuggestionCategory(enum.Enum):
    """Categories for error suggestions."""
    CONFIGURATION = "configuration"
    CONNECTION = "connection"
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    DATA = "data"
    FORMAT = "format"
    COMPATIBILITY = "compatibility"
    DEPENDENCY = "dependency"
    SYSTEM = "system"
    USAGE = "usage"
    GENERAL = "general"


@dataclass
class ActionableSuggestion:
    """A specific, actionable suggestion to resolve an error."""
    
    # Core properties
    message: str
    steps: List[str]
    severity: SuggestionSeverity = SuggestionSeverity.MEDIUM
    category: SuggestionCategory = SuggestionCategory.GENERAL
    
    # Optional properties
    code_example: Optional[str] = None
    documentation_url: Optional[str] = None
    requires_restart: bool = False
    requires_reinstall: bool = False
    estimated_fix_time: Optional[str] = None  # e.g., "1-5 minutes", "about 10 minutes"
    
    # Related error information
    error_patterns: List[str] = field(default_factory=list)
    applies_to_exceptions: List[Type[Exception]] = field(default_factory=list)
    
    def matches_error(self, error: Exception, error_text: str) -> bool:
        """Check if this suggestion applies to the given error.
        
        Args:
            error: The exception object
            error_text: The stringified error message
            
        Returns:
            True if this suggestion applies to the error, False otherwise
        """
        # If no criteria are specified, always match
        if not self.applies_to_exceptions and not self.error_patterns:
            return True
            
        # Check if error is an instance of any of the specified exception types
        exception_match = False
        if self.applies_to_exceptions:
            exception_match = any(
                isinstance(error, exc_type) for exc_type in self.applies_to_exceptions
            )
        
        # Check if error message matches any of the specified patterns
        pattern_match = False
        if self.error_patterns:
            error_text_lower = error_text.lower()
            for pattern in self.error_patterns:
                pattern_lower = pattern.lower()
                if pattern_lower in error_text_lower:
                    pattern_match = True
                    break
        
        # If both criteria are specified, both must match
        if self.applies_to_exceptions and self.error_patterns:
            return exception_match and pattern_match
        
        # If only one criterion is specified, it must match
        return exception_match or pattern_match


class ErrorWithSuggestions(Exception):
    """Exception with actionable suggestions for resolution."""
    
    def __init__(
        self, 
        message: str, 
        original_error: Optional[Exception] = None,
        suggestions: List[ActionableSuggestion] = None
    ):
        """Initialize the exception with suggestions.
        
        Args:
            message: The error message
            original_error: The original exception that was caught
            suggestions: List of actionable suggestions for resolving the error
        """
        super().__init__(message)
        self.original_error = original_error
        self.suggestions = suggestions or []
        
    def __str__(self) -> str:
        """Return a string representation of the error with suggestions."""
        result = super().__str__()
        
        if self.suggestions:
            result += "\n\nSuggested actions:"
            for i, suggestion in enumerate(self.suggestions, 1):
                result += f"\n{i}. {suggestion.message}"
                
                if suggestion.documentation_url:
                    result += f"\n   For more information: {suggestion.documentation_url}"
        
        return result


# Registry for suggestion providers
_suggestion_providers: List[Callable[[Exception, str], List[ActionableSuggestion]]] = []


def register_suggestion_provider(provider: Callable[[Exception, str], List[ActionableSuggestion]]) -> Callable:
    """Register a function that provides suggestions for specific errors.
    
    Args:
        provider: A function that takes an exception and error text and returns suggestions
        
    Returns:
        The provider function for use as a decorator
    """
    _suggestion_providers.append(provider)
    return provider


@lru_cache(maxsize=128)
def get_suggestion_for_error(
    error: Exception, 
    include_traceback: bool = True
) -> List[ActionableSuggestion]:
    """Get actionable suggestions for resolving the given error.
    
    Args:
        error: The exception to find suggestions for
        include_traceback: Whether to include traceback information in error text
        
    Returns:
        A list of actionable suggestions for resolving the error
    """
    # Generate error text including traceback if requested
    if include_traceback and hasattr(error, '__traceback__'):
        error_text = ''.join(traceback.format_exception(
            type(error), error, error.__traceback__
        ))
    else:
        error_text = f"{type(error).__name__}: {str(error)}"
    
    # Collect suggestions from all registered providers
    all_suggestions = []
    for provider in _suggestion_providers:
        try:
            suggestions = provider(error, error_text)
            if suggestions:
                all_suggestions.extend(suggestions)
        except Exception as e:
            logger.warning(
                f"Error in suggestion provider {provider.__name__}: {str(e)}"
            )
    
    # Sort suggestions by severity
    severity_order = {
        SuggestionSeverity.CRITICAL: 0,
        SuggestionSeverity.HIGH: 1,
        SuggestionSeverity.MEDIUM: 2,
        SuggestionSeverity.LOW: 3,
        SuggestionSeverity.INFO: 4
    }
    
    all_suggestions.sort(key=lambda s: severity_order.get(s.severity, 999))
    
    return all_suggestions


class SuggestionProvider:
    """Base class for suggestion providers that can be registered with the system."""
    
    @classmethod
    def __init_subclass__(cls, **kwargs):
        """Automatically register subclasses as suggestion providers."""
        super().__init_subclass__(**kwargs)
        
        # Register the provide_suggestions method if it exists
        if hasattr(cls, 'provide_suggestions'):
            register_suggestion_provider(cls.provide_suggestions)
    
    @classmethod
    def provide_suggestions(
        cls, error: Exception, error_text: str
    ) -> List[ActionableSuggestion]:
        """Provide actionable suggestions for the given error.
        
        Args:
            error: The exception to find suggestions for
            error_text: The stringified error message including traceback
            
        Returns:
            A list of actionable suggestions for resolving the error
        """
        raise NotImplementedError(
            "Subclasses must implement provide_suggestions method"
        ) 