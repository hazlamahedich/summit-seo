"""Tests for the error suggestions module."""

import re
import pytest
from unittest.mock import patch, MagicMock

from summit_seo.error_handling.suggestions import (
    ActionableSuggestion,
    SuggestionSeverity,
    SuggestionCategory,
    ErrorWithSuggestions,
    get_suggestion_for_error,
    register_suggestion_provider,
    SuggestionProvider
)


class TestActionableSuggestion:
    """Tests for the ActionableSuggestion class."""
    
    def test_init_with_defaults(self):
        """Test initialization with default values."""
        suggestion = ActionableSuggestion(
            message="Test message",
            steps=["Step 1", "Step 2"]
        )
        
        assert suggestion.message == "Test message"
        assert suggestion.steps == ["Step 1", "Step 2"]
        assert suggestion.severity == SuggestionSeverity.MEDIUM
        assert suggestion.category == SuggestionCategory.GENERAL
        assert suggestion.code_example is None
        assert suggestion.documentation_url is None
        assert suggestion.requires_restart is False
        assert suggestion.requires_reinstall is False
        assert suggestion.estimated_fix_time is None
        assert suggestion.error_patterns == []
        assert suggestion.applies_to_exceptions == []
    
    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        suggestion = ActionableSuggestion(
            message="Custom message",
            steps=["Custom step"],
            severity=SuggestionSeverity.CRITICAL,
            category=SuggestionCategory.DEPENDENCY,
            code_example="Example code",
            documentation_url="https://example.com",
            requires_restart=True,
            requires_reinstall=True,
            estimated_fix_time="5 minutes",
            error_patterns=["error pattern"],
            applies_to_exceptions=[ValueError, TypeError]
        )
        
        assert suggestion.message == "Custom message"
        assert suggestion.steps == ["Custom step"]
        assert suggestion.severity == SuggestionSeverity.CRITICAL
        assert suggestion.category == SuggestionCategory.DEPENDENCY
        assert suggestion.code_example == "Example code"
        assert suggestion.documentation_url == "https://example.com"
        assert suggestion.requires_restart is True
        assert suggestion.requires_reinstall is True
        assert suggestion.estimated_fix_time == "5 minutes"
        assert suggestion.error_patterns == ["error pattern"]
        assert suggestion.applies_to_exceptions == [ValueError, TypeError]
    
    def test_matches_error_with_exception_type(self):
        """Test matching errors by exception type."""
        suggestion = ActionableSuggestion(
            message="Value error suggestion",
            steps=["Fix the value"],
            applies_to_exceptions=[ValueError]
        )
        
        value_error = ValueError("Invalid value")
        type_error = TypeError("Invalid type")
        
        assert suggestion.matches_error(value_error, str(value_error)) is True
        assert suggestion.matches_error(type_error, str(type_error)) is False
    
    def test_matches_error_with_pattern(self):
        """Test matching errors by error text pattern."""
        suggestion = ActionableSuggestion(
            message="Connection error suggestion",
            steps=["Check connection"],
            error_patterns=["timed out", "connection refused"]
        )
        
        timeout_error = Exception("Operation timed out")
        connection_error = Exception("Connection refused by host")
        other_error = Exception("Invalid operation")
        
        # The pattern "timed out" should be found in "Operation timed out"
        assert suggestion.matches_error(timeout_error, str(timeout_error)) is True
        # The pattern "connection refused" should be found in "Connection refused by host"
        assert suggestion.matches_error(connection_error, str(connection_error)) is True
        # No pattern match for "Invalid operation"
        assert suggestion.matches_error(other_error, str(other_error)) is False
    
    def test_matches_error_with_both_criteria(self):
        """Test matching errors with both exception type and pattern."""
        suggestion = ActionableSuggestion(
            message="Specific value error suggestion",
            steps=["Fix the specific value"],
            applies_to_exceptions=[ValueError],
            error_patterns=["invalid literal"]
        )
        
        matching_error = ValueError("invalid literal for int() with base 10: 'abc'")
        wrong_message = ValueError("Value is wrong")
        wrong_type = TypeError("invalid literal for int() with base 10: 'abc'")
        
        # Both criteria match: correct exception type and contains the pattern
        assert suggestion.matches_error(matching_error, str(matching_error)) is True
        # Wrong message: right exception type but doesn't contain the pattern
        assert suggestion.matches_error(wrong_message, str(wrong_message)) is False
        # Wrong type: wrong exception type but contains the pattern
        assert suggestion.matches_error(wrong_type, str(wrong_type)) is False


class TestErrorWithSuggestions:
    """Tests for the ErrorWithSuggestions class."""
    
    def test_init_with_defaults(self):
        """Test initialization with default values."""
        error = ErrorWithSuggestions("Test error")
        
        assert str(error) == "Test error"
        assert error.original_error is None
        assert error.suggestions == []
    
    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        original = ValueError("Original error")
        suggestions = [
            ActionableSuggestion(
                message="Suggestion 1",
                steps=["Step 1"]
            ),
            ActionableSuggestion(
                message="Suggestion 2",
                steps=["Step 2"]
            )
        ]
        
        error = ErrorWithSuggestions(
            "Enhanced error",
            original_error=original,
            suggestions=suggestions
        )
        
        assert "Enhanced error" in str(error)
        assert "Suggestion 1" in str(error)
        assert "Suggestion 2" in str(error)
        assert error.original_error == original
        assert error.suggestions == suggestions


class TestSuggestionProvider:
    """Tests for the SuggestionProvider class and related functions."""
    
    def test_register_suggestion_provider(self):
        """Test registering a suggestion provider function."""
        # Define a test provider
        def test_provider(error, error_text):
            return [
                ActionableSuggestion(
                    message="Test suggestion",
                    steps=["Test step"]
                )
            ]
        
        # Register it
        registered = register_suggestion_provider(test_provider)
        
        # Verify it was registered correctly and returned
        assert registered == test_provider
        
        # Try using it (directly test the result from the provider)
        error = ValueError("Test error")
        suggestions = test_provider(error, str(error))
        
        assert len(suggestions) == 1
        assert suggestions[0].message == "Test suggestion"
    
    def test_suggestion_provider_subclass_auto_registration(self):
        """Test that SuggestionProvider subclasses are auto-registered."""
        # Create a test provider class
        class TestProvider(SuggestionProvider):
            @classmethod
            def provide_suggestions(cls, error, error_text):
                return [
                    ActionableSuggestion(
                        message="Subclass suggestion",
                        steps=["Subclass step"]
                    )
                ]
        
        # No need to register manually, should be auto-registered
        
        # Create an error and get suggestions for it
        error = ValueError("Test error")
        suggestions = get_suggestion_for_error(error)
        
        # There should be at least one suggestion from our provider
        assert any(s.message == "Subclass suggestion" for s in suggestions)
    
    def test_get_suggestion_for_error(self):
        """Test getting suggestions for an error."""
        # Define and register a test provider
        @register_suggestion_provider
        def test_provider(error, error_text):
            if isinstance(error, ValueError):
                return [
                    ActionableSuggestion(
                        message="Value error suggestion",
                        steps=["Fix the value"]
                    )
                ]
            return []
        
        # Create errors and get suggestions
        value_error = ValueError("Invalid value")
        type_error = TypeError("Invalid type")
        
        value_suggestions = get_suggestion_for_error(value_error)
        type_suggestions = get_suggestion_for_error(type_error)
        
        # Check the results
        assert len(value_suggestions) >= 1
        assert any(s.message == "Value error suggestion" for s in value_suggestions)
        
        # Type error should have no suggestions from our provider
        assert not any(s.message == "Value error suggestion" for s in type_suggestions)
    
    def test_suggestion_provider_error_handling(self):
        """Test handling errors in suggestion providers."""
        # Define a provider that raises an exception
        @register_suggestion_provider
        def buggy_provider(error, error_text):
            raise RuntimeError("Provider bug")
        
        # Define a provider that works correctly
        @register_suggestion_provider
        def working_provider(error, error_text):
            return [
                ActionableSuggestion(
                    message="Working suggestion",
                    steps=["Working step"]
                )
            ]
        
        # Create an error and get suggestions
        with patch('summit_seo.error_handling.suggestions.logger') as mock_logger:
            error = ValueError("Test error")
            suggestions = get_suggestion_for_error(error)
            
            # The buggy provider should have logged a warning
            assert mock_logger.warning.called
            
            # But we should still get suggestions from the working provider
            assert any(s.message == "Working suggestion" for s in suggestions) 