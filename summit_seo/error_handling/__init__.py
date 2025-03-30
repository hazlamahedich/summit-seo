"""Error handling utilities for Summit SEO.

This module provides enhanced error handling and reporting capabilities,
including actionable suggestions for resolving errors encountered during
SEO analysis operations.
"""

from .suggestions import (
    ActionableSuggestion,
    SuggestionSeverity,
    SuggestionCategory,
    ErrorWithSuggestions,
    SuggestionProvider,
    get_suggestion_for_error,
    register_suggestion_provider
)

from .reporting import (
    ErrorReporter,
    ConsoleErrorReporter,
    FileErrorReporter,
    ReportedError,
    ErrorContext
)

__all__ = [
    'ActionableSuggestion',
    'SuggestionSeverity',
    'SuggestionCategory',
    'ErrorWithSuggestions',
    'SuggestionProvider',
    'get_suggestion_for_error',
    'register_suggestion_provider',
    'ErrorReporter',
    'ConsoleErrorReporter',
    'FileErrorReporter',
    'ReportedError',
    'ErrorContext'
] 