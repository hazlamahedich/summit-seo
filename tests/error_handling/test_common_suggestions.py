"""Tests for the common suggestion providers."""

import re
from unittest.mock import patch, MagicMock

import pytest

from summit_seo.error_handling.common_suggestions import (
    NetworkSuggestionProvider,
    ParsingErrorSuggestionProvider,
    AuthenticationSuggestionProvider,
    RateLimitSuggestionProvider,
    ConfigurationErrorSuggestionProvider,
    ResourceNotFoundSuggestionProvider,
    AnalyzerErrorSuggestionProvider,
    DataExtractionErrorSuggestionProvider
)
from summit_seo.error_handling.suggestions import (
    ActionableSuggestion,
    SuggestionSeverity,
    SuggestionCategory
)


class TestNetworkSuggestionProvider:
    """Tests for the NetworkSuggestionProvider class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.provider = NetworkSuggestionProvider()
    
    def test_get_suggestions_connection_error(self):
        """Test suggestions for connection errors."""
        # Connection refused error
        error = ConnectionError("Connection refused")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("connection" in s.message.lower() for s in suggestions)
        assert any("Check your internet connection" in step for s in suggestions for step in s.steps)
        
        # Connection timeout error
        error = TimeoutError("Connection timed out")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("timeout" in s.message.lower() for s in suggestions)
    
    def test_get_suggestions_dns_error(self):
        """Test suggestions for DNS-related errors."""
        # Name resolution error
        error = Exception("Name or service not known")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("dns" in s.message.lower() for s in suggestions)
        assert any("Check if the domain name is correct" in step for s in suggestions for step in s.steps)
    
    def test_get_suggestions_timeout_error(self):
        """Test suggestions for timeout errors."""
        # Request timeout
        error = Exception("Request timed out after 30 seconds")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("timeout" in s.message.lower() for s in suggestions)
        assert any("increasing" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_ssl_error(self):
        """Test suggestions for SSL/TLS errors."""
        # SSL certificate error
        error = Exception("SSL certificate verification failed")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("ssl" in s.message.lower() or "certificate" in s.message.lower() for s in suggestions)
        assert any("certificate" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_proxy_error(self):
        """Test suggestions for proxy-related errors."""
        # Proxy configuration error
        error = Exception("Failed to establish a connection through proxy")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("proxy" in s.message.lower() for s in suggestions)
        assert any("proxy" in step.lower() for s in suggestions for step in s.steps)
    
    def test_non_matching_error(self):
        """Test behavior with non-matching error."""
        # Error not related to network issues
        error = ValueError("Invalid value")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) == 0


class TestParsingErrorSuggestionProvider:
    """Tests for the ParsingErrorSuggestionProvider class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.provider = ParsingErrorSuggestionProvider()
    
    def test_get_suggestions_html_error(self):
        """Test suggestions for HTML parsing errors."""
        # HTML parser error
        error = Exception("Error parsing HTML: malformed tag")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("html" in s.message.lower() for s in suggestions)
        assert any("malformed html" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_xml_error(self):
        """Test suggestions for XML parsing errors."""
        # XML parser error
        error = Exception("XML syntax error: mismatched tag")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("xml" in s.message.lower() for s in suggestions)
        assert any("xml" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_json_error(self):
        """Test suggestions for JSON parsing errors."""
        # JSON parser error
        error = Exception("JSONDecodeError: Expecting property name")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("json" in s.message.lower() for s in suggestions)
        assert any("json validator" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_selector_error(self):
        """Test suggestions for CSS selector errors."""
        # CSS selector error
        error = Exception("Invalid CSS selector: syntax error")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("selector" in s.message.lower() for s in suggestions)
        assert any("selector" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_encoding_error(self):
        """Test suggestions for encoding errors."""
        # Encoding error
        error = UnicodeDecodeError("utf-8", b"invalid", 0, 1, "invalid sequence")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("encoding" in s.message.lower() for s in suggestions)
        assert any("encoding" in step.lower() for s in suggestions for step in s.steps)
    
    def test_non_matching_error(self):
        """Test behavior with non-matching error."""
        # Error not related to parsing issues
        error = ValueError("Invalid value")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) == 0


class TestAuthenticationSuggestionProvider:
    """Tests for the AuthenticationSuggestionProvider class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.provider = AuthenticationSuggestionProvider()
    
    def test_get_suggestions_auth_error(self):
        """Test suggestions for authentication errors."""
        # Authentication failure
        error = Exception("Authentication failed: invalid credentials")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("authentication" in s.message.lower() for s in suggestions)
        assert any("credentials" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_login_error(self):
        """Test suggestions for login errors."""
        # Login failure
        error = Exception("Login failed: incorrect username or password")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("login" in s.message.lower() for s in suggestions)
        assert any("password" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_token_error(self):
        """Test suggestions for token errors."""
        # Token expiration
        error = Exception("Access token expired")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("token" in s.message.lower() for s in suggestions)
        assert any("refresh" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_permission_error(self):
        """Test suggestions for permission errors."""
        # Permission denied
        error = Exception("Permission denied: insufficient access rights")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("permission" in s.message.lower() for s in suggestions)
        assert any("permission" in step.lower() for s in suggestions for step in s.steps)
    
    def test_non_matching_error(self):
        """Test behavior with non-matching error."""
        # Error not related to authentication issues
        error = ValueError("Invalid value")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) == 0


class TestRateLimitSuggestionProvider:
    """Tests for the RateLimitSuggestionProvider class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.provider = RateLimitSuggestionProvider()
    
    def test_get_suggestions_rate_limit_error(self):
        """Test suggestions for rate limit errors."""
        # Rate limit exceeded
        error = Exception("Rate limit exceeded: too many requests")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("rate limit" in s.message.lower() for s in suggestions)
        assert any("throttling" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_too_many_requests(self):
        """Test suggestions for too many requests errors."""
        # Too many requests
        error = Exception("429 Too Many Requests")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("request" in s.message.lower() for s in suggestions)
        assert any("delay" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_quota_exceeded(self):
        """Test suggestions for quota exceeded errors."""
        # Quota exceeded
        error = Exception("API quota exceeded for today")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("quota" in s.message.lower() for s in suggestions)
        assert any("quota" in step.lower() for s in suggestions for step in s.steps)
    
    def test_non_matching_error(self):
        """Test behavior with non-matching error."""
        # Error not related to rate limiting issues
        error = ValueError("Invalid value")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) == 0


class TestConfigurationErrorSuggestionProvider:
    """Tests for the ConfigurationErrorSuggestionProvider class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.provider = ConfigurationErrorSuggestionProvider()
    
    def test_get_suggestions_config_error(self):
        """Test suggestions for configuration errors."""
        # Configuration error
        error = Exception("Configuration error: missing required parameter")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("configuration" in s.message.lower() for s in suggestions)
        assert any("parameter" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_missing_setting(self):
        """Test suggestions for missing setting errors."""
        # Missing setting
        error = Exception("Missing required setting: API_KEY")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("setting" in s.message.lower() for s in suggestions)
        assert any("environment variable" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_invalid_format(self):
        """Test suggestions for invalid format errors."""
        # Invalid format
        error = Exception("Invalid configuration format in config.json")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("format" in s.message.lower() for s in suggestions)
        assert any("format" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_incompatible_setting(self):
        """Test suggestions for incompatible setting errors."""
        # Incompatible settings
        error = Exception("Incompatible settings: cannot use feature X with feature Y")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("incompatible" in s.message.lower() for s in suggestions)
        assert any("compatible" in step.lower() for s in suggestions for step in s.steps)
    
    def test_non_matching_error(self):
        """Test behavior with non-matching error."""
        # Error not related to configuration issues
        error = ValueError("Invalid value")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) == 0


class TestResourceNotFoundSuggestionProvider:
    """Tests for the ResourceNotFoundSuggestionProvider class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.provider = ResourceNotFoundSuggestionProvider()
    
    def test_get_suggestions_file_not_found(self):
        """Test suggestions for file not found errors."""
        # File not found
        error = FileNotFoundError("No such file or directory: 'config.json'")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("file" in s.message.lower() for s in suggestions)
        assert any("path" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_page_not_found(self):
        """Test suggestions for page not found errors."""
        # Page not found
        error = Exception("404 Page Not Found")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("page" in s.message.lower() for s in suggestions)
        assert any("url" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_resource_not_found(self):
        """Test suggestions for resource not found errors."""
        # Resource not found
        error = Exception("Resource not found: user_id=123")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("resource" in s.message.lower() for s in suggestions)
        assert any("exist" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_element_not_found(self):
        """Test suggestions for element not found errors."""
        # Element not found
        error = Exception("Element not found: selector='#main-content'")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("element" in s.message.lower() for s in suggestions)
        assert any("selector" in step.lower() for s in suggestions for step in s.steps)
    
    def test_non_matching_error(self):
        """Test behavior with non-matching error."""
        # Error not related to resource not found issues
        error = ValueError("Invalid value")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) == 0


class TestAnalyzerErrorSuggestionProvider:
    """Tests for the AnalyzerErrorSuggestionProvider class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.provider = AnalyzerErrorSuggestionProvider()
    
    def test_get_suggestions_analyzer_error(self):
        """Test suggestions for analyzer errors."""
        # Analyzer error
        error = Exception("Error in SecurityAnalyzer: failed to check HTTPS")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("analyzer" in s.message.lower() for s in suggestions)
        assert any("analyzer" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_analyzer_timeout(self):
        """Test suggestions for analyzer timeout errors."""
        # Analyzer timeout
        error = Exception("PerformanceAnalyzer timed out after 60 seconds")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("timeout" in s.message.lower() for s in suggestions)
        assert any("timeout" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_unsupported_feature(self):
        """Test suggestions for unsupported feature errors."""
        # Unsupported feature
        error = Exception("MobileAnalyzer does not support this feature")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("support" in s.message.lower() for s in suggestions)
        assert any("feature" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_initialization_error(self):
        """Test suggestions for analyzer initialization errors."""
        # Initialization error
        error = Exception("Failed to initialize ContentAnalyzer: missing dependency")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("initialization" in s.message.lower() for s in suggestions)
        assert any("dependencies" in step.lower() for s in suggestions for step in s.steps)
    
    def test_non_matching_error(self):
        """Test behavior with non-matching error."""
        # Error not related to analyzer issues
        error = ValueError("Invalid value")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) == 0


class TestDataExtractionErrorSuggestionProvider:
    """Tests for the DataExtractionErrorSuggestionProvider class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.provider = DataExtractionErrorSuggestionProvider()
    
    def test_get_suggestions_extraction_error(self):
        """Test suggestions for data extraction errors."""
        # Data extraction error
        error = Exception("Error extracting data: invalid selector")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("extraction" in s.message.lower() for s in suggestions)
        assert any("selector" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_empty_data(self):
        """Test suggestions for empty data errors."""
        # Empty data
        error = Exception("No data found for extraction pattern")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("data" in s.message.lower() for s in suggestions)
        assert any("pattern" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_transformation_error(self):
        """Test suggestions for data transformation errors."""
        # Transformation error
        error = Exception("Failed to transform extracted data: type conversion error")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("transform" in s.message.lower() for s in suggestions)
        assert any("type" in step.lower() for s in suggestions for step in s.steps)
    
    def test_get_suggestions_schema_validation_error(self):
        """Test suggestions for schema validation errors."""
        # Schema validation error
        error = Exception("Extracted data failed schema validation")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) > 0
        assert any("schema" in s.message.lower() or "validation" in s.message.lower() for s in suggestions)
        assert any("schema" in step.lower() for s in suggestions for step in s.steps)
    
    def test_non_matching_error(self):
        """Test behavior with non-matching error."""
        # Error not related to data extraction issues
        error = ValueError("Invalid value")
        suggestions = self.provider.get_suggestions(error)
        
        assert len(suggestions) == 0 