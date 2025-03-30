"""Module with common error suggestions for SEO analysis.

This module provides suggestion providers for common error types
encountered during SEO analysis. Each provider is specialized for
a specific category of errors and provides actionable suggestions
to help resolve the issues.
"""

from typing import List, Optional, Type, Union, Dict, Any
import re

from summit_seo.error_handling.suggestions import (
    SuggestionProvider,
    ActionableSuggestion,
    SuggestionSeverity,
    SuggestionCategory
)


class NetworkSuggestionProvider(SuggestionProvider):
    """Provides suggestions for network-related errors."""

    def _get_connection_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for connection errors."""
        suggestions = []
        
        suggestions.append(ActionableSuggestion(
            message="Network connection issue detected",
            steps=[
                "Check your internet connection",
                "Verify the server is accessible",
                "Ensure there are no firewall restrictions blocking access"
            ],
            severity=SuggestionSeverity.HIGH,
            category=SuggestionCategory.CONNECTION,
            estimated_fix_time="5-10 minutes"
        ))
        
        if "timeout" in error_text.lower() or "timed out" in error_text.lower():
            suggestions.append(ActionableSuggestion(
                message="Connection timeout detected",
                steps=[
                    "Check if the server is responding slowly",
                    "Consider increasing the connection timeout value",
                    "Try the request during a less busy time"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.CONNECTION,
                estimated_fix_time="2-5 minutes"
            ))
            
        return suggestions

    def _get_dns_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for DNS resolution errors."""
        return [
            ActionableSuggestion(
                message="DNS resolution error detected",
                steps=[
                    "Check if the domain name is correct",
                    "Verify DNS settings on your system",
                    "Try using an IP address directly if available"
                ],
                severity=SuggestionSeverity.HIGH,
                category=SuggestionCategory.CONNECTION,
                estimated_fix_time="10-15 minutes"
            )
        ]

    def _get_ssl_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for SSL/TLS errors."""
        return [
            ActionableSuggestion(
                message="SSL/TLS certificate issue detected",
                steps=[
                    "Verify the website's certificate is valid",
                    "Check your system's trusted certificate authorities",
                    "Update to a newer version of the SSL/TLS library"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.GENERAL,
                estimated_fix_time="15-20 minutes"
            )
        ]

    def _get_proxy_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for proxy-related errors."""
        return [
            ActionableSuggestion(
                message="Proxy connection error detected",
                steps=[
                    "Verify proxy settings",
                    "Check if the proxy server is operational",
                    "Ensure proxy authentication is correct if required"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.CONNECTION,
                estimated_fix_time="10-15 minutes"
            )
        ]
        
    def get_suggestions(self, error: Exception) -> List[ActionableSuggestion]:
        """Get suggestions for network-related errors.
        
        Args:
            error: The error to provide suggestions for
            
        Returns:
            A list of actionable suggestions
        """
        error_text = str(error)
        suggestions = []
        
        # Connection errors
        if isinstance(error, ConnectionError) or "connection" in error_text.lower() or "connect" in error_text.lower():
            suggestions.extend(self._get_connection_suggestions(error_text))
            
        # Timeout errors
        if isinstance(error, TimeoutError) or "timeout" in error_text.lower() or "timed out" in error_text.lower():
            suggestions.extend(self._get_connection_suggestions(error_text))
            
        # DNS errors
        if "dns" in error_text.lower() or "name" in error_text.lower() and "not" in error_text.lower() and "known" in error_text.lower():
            suggestions.extend(self._get_dns_suggestions(error_text))
            
        # SSL errors
        if "ssl" in error_text.lower() or "certificate" in error_text.lower() or "tls" in error_text.lower():
            suggestions.extend(self._get_ssl_suggestions(error_text))
            
        # Proxy errors
        if "proxy" in error_text.lower():
            suggestions.extend(self._get_proxy_suggestions(error_text))
            
        return suggestions


class ParsingErrorSuggestionProvider(SuggestionProvider):
    """Provides suggestions for parsing-related errors."""

    def _get_html_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for HTML parsing errors."""
        return [
            ActionableSuggestion(
                message="HTML parsing error detected",
                steps=[
                    "Check for malformed HTML in the page",
                    "Verify HTML validates using an HTML validator",
                    "Consider using a more lenient parser option if available"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.FORMAT,
                estimated_fix_time="15-20 minutes"
            )
        ]

    def _get_xml_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for XML parsing errors."""
        return [
            ActionableSuggestion(
                message="XML parsing error detected",
                steps=[
                    "Check for well-formedness of XML",
                    "Ensure all tags are properly closed",
                    "Validate XML against its schema if available"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.FORMAT,
                estimated_fix_time="10-15 minutes"
            )
        ]

    def _get_json_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for JSON parsing errors."""
        return [
            ActionableSuggestion(
                message="JSON parsing error detected",
                steps=[
                    "Check JSON syntax (brackets, commas, quotes)",
                    "Validate JSON using a JSON validator",
                    "Ensure the response is actually JSON and not HTML or text"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.FORMAT,
                estimated_fix_time="5-10 minutes"
            )
        ]

    def _get_selector_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for selector errors."""
        return [
            ActionableSuggestion(
                message="CSS selector error detected",
                steps=[
                    "Verify selector syntax",
                    "Check if the element exists in the document",
                    "Try simplifying the selector"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.FORMAT,
                estimated_fix_time="10-15 minutes"
            )
        ]

    def _get_encoding_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for encoding errors."""
        return [
            ActionableSuggestion(
                message="Text encoding error detected",
                steps=[
                    "Check the document's character encoding",
                    "Ensure the correct encoding is specified in parsing",
                    "Try using a more forgiving encoding (e.g., 'utf-8', 'latin-1')"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.FORMAT,
                estimated_fix_time="10-15 minutes"
            )
        ]
        
    def get_suggestions(self, error: Exception) -> List[ActionableSuggestion]:
        """Get suggestions for parsing-related errors.
        
        Args:
            error: The error to provide suggestions for
            
        Returns:
            A list of actionable suggestions
        """
        error_text = str(error).lower()
        suggestions = []
        
        # HTML parsing errors
        if "html" in error_text and ("parse" in error_text or "parsing" in error_text or "malformed" in error_text):
            suggestions.extend(self._get_html_suggestions(error_text))
            
        # XML parsing errors
        if "xml" in error_text and ("parse" in error_text or "parsing" in error_text or "syntax" in error_text):
            suggestions.extend(self._get_xml_suggestions(error_text))
            
        # JSON parsing errors
        if "json" in error_text or "jsondecode" in error_text:
            suggestions.extend(self._get_json_suggestions(error_text))
            
        # Selector errors
        if "selector" in error_text or "css selector" in error_text:
            suggestions.extend(self._get_selector_suggestions(error_text))
            
        # Encoding errors
        if isinstance(error, UnicodeError) or "encoding" in error_text or "decode" in error_text or "unicode" in error_text:
            suggestions.extend(self._get_encoding_suggestions(error_text))
            
        return suggestions


class AuthenticationSuggestionProvider(SuggestionProvider):
    """Provides suggestions for authentication-related errors."""

    def _get_auth_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for authentication errors."""
        return [
            ActionableSuggestion(
                message="Authentication error detected",
                steps=[
                    "Verify your credentials are correct",
                    "Check if your authentication method is supported",
                    "Ensure your account has the necessary permissions"
                ],
                severity=SuggestionSeverity.HIGH,
                category=SuggestionCategory.AUTHENTICATION,
                estimated_fix_time="5-10 minutes"
            )
        ]

    def _get_login_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for login errors."""
        return [
            ActionableSuggestion(
                message="Login error detected",
                steps=[
                    "Double-check username and password",
                    "Verify the login endpoint is correct",
                    "Check if account lockout policies are in effect"
                ],
                severity=SuggestionSeverity.HIGH,
                category=SuggestionCategory.AUTHENTICATION,
                estimated_fix_time="2-5 minutes"
            )
        ]

    def _get_token_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for token errors."""
        return [
            ActionableSuggestion(
                message="Token error detected",
                steps=[
                    "Refresh your access token",
                    "Check token expiration time",
                    "Verify the token has the required scopes or permissions"
                ],
                severity=SuggestionSeverity.HIGH,
                category=SuggestionCategory.AUTHENTICATION,
                estimated_fix_time="5-10 minutes"
            )
        ]

    def _get_permission_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for permission errors."""
        return [
            ActionableSuggestion(
                message="Permission error detected",
                steps=[
                    "Verify you have the required permissions",
                    "Check if you need elevated privileges",
                    "Contact the administrator for access rights"
                ],
                severity=SuggestionSeverity.HIGH,
                category=SuggestionCategory.PERMISSION,
                estimated_fix_time="20-30 minutes"
            )
        ]
        
    def get_suggestions(self, error: Exception) -> List[ActionableSuggestion]:
        """Get suggestions for authentication-related errors.
        
        Args:
            error: The error to provide suggestions for
            
        Returns:
            A list of actionable suggestions
        """
        error_text = str(error).lower()
        suggestions = []
        
        # Authentication errors
        if "authentication" in error_text or "auth" in error_text:
            suggestions.extend(self._get_auth_suggestions(error_text))
            
        # Login errors
        if "login" in error_text or "log in" in error_text:
            suggestions.extend(self._get_login_suggestions(error_text))
            
        # Token errors
        if "token" in error_text:
            suggestions.extend(self._get_token_suggestions(error_text))
            
        # Permission errors
        if "permission" in error_text or "access" in error_text and "denied" in error_text:
            suggestions.extend(self._get_permission_suggestions(error_text))
            
        return suggestions


class RateLimitSuggestionProvider(SuggestionProvider):
    """Provides suggestions for rate limit-related errors."""

    def _get_rate_limit_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for rate limit errors."""
        return [
            ActionableSuggestion(
                message="Rate limit exceeded",
                steps=[
                    "Reduce the request frequency",
                    "Implement request throttling in your code",
                    "Check the service's documentation for rate limits"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.USAGE,
                estimated_fix_time="20-30 minutes"
            )
        ]

    def _get_too_many_requests_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for too many requests errors."""
        return [
            ActionableSuggestion(
                message="Too many requests error (HTTP 429)",
                steps=[
                    "Wait before sending more requests",
                    "Add delay between requests",
                    "Implement exponential backoff strategy"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.USAGE,
                estimated_fix_time="15-20 minutes"
            )
        ]

    def _get_quota_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for quota exceeded errors."""
        return [
            ActionableSuggestion(
                message="API quota exceeded",
                steps=[
                    "Check your subscription plan limits",
                    "Wait until quota resets (often daily)",
                    "Consider upgrading your API plan"
                ],
                severity=SuggestionSeverity.HIGH,
                category=SuggestionCategory.USAGE,
                estimated_fix_time="30-60 minutes"
            )
        ]
        
    def get_suggestions(self, error: Exception) -> List[ActionableSuggestion]:
        """Get suggestions for rate limit-related errors.
        
        Args:
            error: The error to provide suggestions for
            
        Returns:
            A list of actionable suggestions
        """
        error_text = str(error).lower()
        suggestions = []
        
        # Rate limit errors
        if "rate limit" in error_text or "ratelimit" in error_text:
            suggestions.extend(self._get_rate_limit_suggestions(error_text))
            
        # Too many requests
        if "429" in error_text or "too many requests" in error_text:
            suggestions.extend(self._get_too_many_requests_suggestions(error_text))
            
        # Quota exceeded
        if "quota" in error_text:
            suggestions.extend(self._get_quota_suggestions(error_text))
            
        return suggestions


class ConfigurationErrorSuggestionProvider(SuggestionProvider):
    """Provides suggestions for configuration-related errors."""

    def _get_config_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for configuration errors."""
        return [
            ActionableSuggestion(
                message="Configuration error detected",
                steps=[
                    "Check configuration file syntax",
                    "Verify all required parameters are specified",
                    "Ensure configuration file is accessible"
                ],
                severity=SuggestionSeverity.HIGH,
                category=SuggestionCategory.CONFIGURATION,
                estimated_fix_time="10-15 minutes"
            )
        ]

    def _get_missing_setting_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for missing setting errors."""
        return [
            ActionableSuggestion(
                message="Missing required setting",
                steps=[
                    "Check for missing keys in configuration",
                    "Verify environment variables are set correctly",
                    "Consult documentation for required settings"
                ],
                severity=SuggestionSeverity.HIGH,
                category=SuggestionCategory.CONFIGURATION,
                estimated_fix_time="5-10 minutes"
            )
        ]

    def _get_format_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for format errors."""
        return [
            ActionableSuggestion(
                message="Invalid configuration format",
                steps=[
                    "Check for syntax errors in configuration file",
                    "Verify file is in the expected format (JSON, YAML, etc.)",
                    "Validate configuration against schema if available"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.CONFIGURATION,
                estimated_fix_time="10-15 minutes"
            )
        ]

    def _get_incompatible_setting_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for incompatible setting errors."""
        return [
            ActionableSuggestion(
                message="Incompatible configuration settings",
                steps=[
                    "Check for conflicting settings",
                    "Review documentation for compatible setting combinations",
                    "Use recommended setting templates if available"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.CONFIGURATION,
                estimated_fix_time="15-20 minutes"
            )
        ]
        
    def get_suggestions(self, error: Exception) -> List[ActionableSuggestion]:
        """Get suggestions for configuration-related errors.
        
        Args:
            error: The error to provide suggestions for
            
        Returns:
            A list of actionable suggestions
        """
        error_text = str(error).lower()
        suggestions = []
        
        # Configuration errors
        if "configuration" in error_text or "config" in error_text:
            suggestions.extend(self._get_config_suggestions(error_text))
            
        # Missing setting
        if "missing" in error_text and ("setting" in error_text or "parameter" in error_text):
            suggestions.extend(self._get_missing_setting_suggestions(error_text))
            
        # Format errors
        if "format" in error_text and "invalid" in error_text:
            suggestions.extend(self._get_format_suggestions(error_text))
            
        # Incompatible settings
        if "incompatible" in error_text or "conflict" in error_text:
            suggestions.extend(self._get_incompatible_setting_suggestions(error_text))
            
        return suggestions


class ResourceNotFoundSuggestionProvider(SuggestionProvider):
    """Provides suggestions for resource not found errors."""

    def _get_file_not_found_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for file not found errors."""
        return [
            ActionableSuggestion(
                message="File not found",
                steps=[
                    "Check if the file path is correct",
                    "Verify file permissions allow access",
                    "Ensure the file exists in the specified location"
                ],
                severity=SuggestionSeverity.HIGH,
                category=SuggestionCategory.SYSTEM,
                estimated_fix_time="5-10 minutes"
            )
        ]

    def _get_page_not_found_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for page not found errors."""
        return [
            ActionableSuggestion(
                message="Page not found (HTTP 404)",
                steps=[
                    "Verify the URL is correct",
                    "Check if the page has been moved or renamed",
                    "Ensure you have access to the requested resource"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.GENERAL,
                estimated_fix_time="10-15 minutes"
            )
        ]

    def _get_resource_not_found_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for resource not found errors."""
        return [
            ActionableSuggestion(
                message="Resource not found",
                steps=[
                    "Verify resource identifier is correct",
                    "Check if the resource still exists",
                    "Ensure you have permission to access the resource"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.GENERAL,
                estimated_fix_time="10-15 minutes"
            )
        ]

    def _get_element_not_found_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for element not found errors."""
        return [
            ActionableSuggestion(
                message="Element not found in document",
                steps=[
                    "Check if the selector is correct",
                    "Verify the element exists in the document",
                    "Consider using a wait mechanism if content is loaded dynamically"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.FORMAT,
                estimated_fix_time="15-20 minutes"
            )
        ]
        
    def get_suggestions(self, error: Exception) -> List[ActionableSuggestion]:
        """Get suggestions for resource not found errors.
        
        Args:
            error: The error to provide suggestions for
            
        Returns:
            A list of actionable suggestions
        """
        error_text = str(error).lower()
        suggestions = []
        
        # File not found
        if isinstance(error, FileNotFoundError) or "file not found" in error_text or "no such file" in error_text:
            suggestions.extend(self._get_file_not_found_suggestions(error_text))
            
        # Page not found
        if "404" in error_text or "page not found" in error_text:
            suggestions.extend(self._get_page_not_found_suggestions(error_text))
            
        # Resource not found
        if "resource not found" in error_text:
            suggestions.extend(self._get_resource_not_found_suggestions(error_text))
            
        # Element not found
        if "element not found" in error_text or "selector" in error_text and "not found" in error_text:
            suggestions.extend(self._get_element_not_found_suggestions(error_text))
            
        return suggestions


class AnalyzerErrorSuggestionProvider(SuggestionProvider):
    """Provides suggestions for analyzer-related errors."""

    def _get_analyzer_error_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for analyzer errors."""
        return [
            ActionableSuggestion(
                message="Analyzer error detected",
                steps=[
                    "Check analyzer configuration",
                    "Verify input data format meets analyzer requirements",
                    "Check for recent analyzer updates or known issues"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.GENERAL,
                estimated_fix_time="15-20 minutes"
            )
        ]

    def _get_analyzer_timeout_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for analyzer timeout errors."""
        return [
            ActionableSuggestion(
                message="Analyzer timeout detected",
                steps=[
                    "Consider increasing the analyzer timeout setting",
                    "Try analyzing a smaller dataset",
                    "Check if the analyzer is stuck in a loop"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.GENERAL,
                estimated_fix_time="10-15 minutes"
            )
        ]

    def _get_unsupported_feature_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for unsupported feature errors."""
        return [
            ActionableSuggestion(
                message="Unsupported analyzer feature",
                steps=[
                    "Check if the feature is available in your analyzer version",
                    "Consider using a different analyzer that supports this feature",
                    "Look for alternative approaches to achieve the same goal"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.GENERAL,
                estimated_fix_time="20-30 minutes"
            )
        ]

    def _get_initialization_error_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for initialization errors."""
        return [
            ActionableSuggestion(
                message="Analyzer initialization error",
                steps=[
                    "Check required dependencies are installed",
                    "Verify analyzer configuration is complete",
                    "Ensure environment is properly set up"
                ],
                severity=SuggestionSeverity.HIGH,
                category=SuggestionCategory.DEPENDENCY,
                estimated_fix_time="15-25 minutes"
            )
        ]
        
    def get_suggestions(self, error: Exception) -> List[ActionableSuggestion]:
        """Get suggestions for analyzer-related errors.
        
        Args:
            error: The error to provide suggestions for
            
        Returns:
            A list of actionable suggestions
        """
        error_text = str(error).lower()
        suggestions = []
        
        # Analyzer errors
        if "analyzer" in error_text and "error" in error_text:
            suggestions.extend(self._get_analyzer_error_suggestions(error_text))
            
        # Analyzer timeouts
        if "analyzer" in error_text and "timeout" in error_text:
            suggestions.extend(self._get_analyzer_timeout_suggestions(error_text))
        # Also check for "timed out" in the error message
        elif "analyzer" in error_text and "timed out" in error_text:
            suggestions.extend(self._get_analyzer_timeout_suggestions(error_text))
        # Check for timeout without explicitly mentioning analyzer
        elif any(analyzer_name in error_text and ("timeout" in error_text or "timed out" in error_text) 
                for analyzer_name in ["performanceanalyzer", "securityanalyzer", "contentanalyzer", "mobilenalyzer"]):
            suggestions.extend(self._get_analyzer_timeout_suggestions(error_text))
            
        # Unsupported feature
        if ("not support" in error_text or "unsupported" in error_text) and "feature" in error_text:
            suggestions.extend(self._get_unsupported_feature_suggestions(error_text))
            
        # Initialization errors
        if "initialize" in error_text or "initialization" in error_text:
            suggestions.extend(self._get_initialization_error_suggestions(error_text))
            
        return suggestions


class DataExtractionErrorSuggestionProvider(SuggestionProvider):
    """Provides suggestions for data extraction errors."""

    def _get_extraction_error_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for extraction errors."""
        return [
            ActionableSuggestion(
                message="Data extraction error",
                steps=[
                    "Verify extraction patterns or selectors",
                    "Check if the data structure has changed",
                    "Ensure the content exists in the document"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.DATA,
                estimated_fix_time="15-20 minutes"
            )
        ]

    def _get_empty_data_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for empty data errors."""
        return [
            ActionableSuggestion(
                message="No data found for extraction",
                steps=[
                    "Check if the source contains the expected data",
                    "Verify extraction pattern matches the data structure",
                    "Consider if the content is loaded dynamically"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.DATA,
                estimated_fix_time="10-15 minutes"
            )
        ]

    def _get_transformation_error_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for transformation errors."""
        return [
            ActionableSuggestion(
                message="Data transformation error",
                steps=[
                    "Check if the extracted data is in the expected format",
                    "Verify transformation logic handles edge cases",
                    "Add type checking or validation before transformation"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.DATA,
                estimated_fix_time="15-25 minutes"
            )
        ]

    def _get_schema_validation_suggestions(self, error_text: str) -> List[ActionableSuggestion]:
        """Get suggestions for schema validation errors."""
        return [
            ActionableSuggestion(
                message="Data schema validation error",
                steps=[
                    "Check if the data matches the expected schema",
                    "Verify all required fields are present",
                    "Ensure data types are correct"
                ],
                severity=SuggestionSeverity.MEDIUM,
                category=SuggestionCategory.DATA,
                estimated_fix_time="15-20 minutes"
            )
        ]
        
    def get_suggestions(self, error: Exception) -> List[ActionableSuggestion]:
        """Get suggestions for data extraction-related errors.
        
        Args:
            error: The error to provide suggestions for
            
        Returns:
            A list of actionable suggestions
        """
        error_text = str(error).lower()
        suggestions = []
        
        # Extraction errors
        if "extract" in error_text and "error" in error_text:
            suggestions.extend(self._get_extraction_error_suggestions(error_text))
            
        # Empty data
        if "no data" in error_text or "empty" in error_text:
            suggestions.extend(self._get_empty_data_suggestions(error_text))
            
        # Transformation errors
        if "transform" in error_text:
            suggestions.extend(self._get_transformation_error_suggestions(error_text))
            
        # Schema validation
        if "schema" in error_text or "validation" in error_text:
            suggestions.extend(self._get_schema_validation_suggestions(error_text))
            
        return suggestions 