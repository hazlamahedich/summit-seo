"""
Tests for the error response utilities.
"""
import pytest

# Import from our test utils module
from summit_seo.web.api.tests.utils.error_response import ErrorResponse

class TestErrorResponse:
    """Test cases for error response utilities."""
    
    def test_error_response_create(self):
        """Test the ErrorResponse.create method."""
        response = ErrorResponse.create(
            status_code=403,
            code="FORBIDDEN",
            message="Access denied",
            details={"reason": "Insufficient permissions"},
            suggestions=[{"message": "Request access from admin", "severity": "high"}]
        )
        
        assert response["status"] == "error"
        assert response["error"]["code"] == "FORBIDDEN"
        assert response["error"]["message"] == "Access denied"
        assert response["error"]["status_code"] == 403
        assert response["error"]["details"]["reason"] == "Insufficient permissions"
        assert response["error"]["suggestions"][0]["message"] == "Request access from admin"
    
    def test_error_response_create_minimal(self):
        """Test creating a minimal error response."""
        response = ErrorResponse.create(
            status_code=404,
            code="NOT_FOUND",
            message="Resource not found"
        )
        
        assert response["status"] == "error"
        assert response["error"]["code"] == "NOT_FOUND"
        assert response["error"]["message"] == "Resource not found"
        assert response["error"]["status_code"] == 404
        assert "details" not in response["error"]
        assert "suggestions" not in response["error"]
    
    def test_error_response_with_details(self):
        """Test error response with details but no suggestions."""
        response = ErrorResponse.create(
            status_code=400,
            code="VALIDATION_ERROR",
            message="Validation failed",
            details={"fields": ["name", "email"]}
        )
        
        assert response["status"] == "error"
        assert response["error"]["code"] == "VALIDATION_ERROR"
        assert response["error"]["message"] == "Validation failed"
        assert response["error"]["status_code"] == 400
        assert response["error"]["details"]["fields"] == ["name", "email"]
        assert "suggestions" not in response["error"]
    
    def test_error_response_with_suggestions(self):
        """Test error response with suggestions but no details."""
        response = ErrorResponse.create(
            status_code=500,
            code="SERVER_ERROR",
            message="Internal server error",
            suggestions=[
                {"message": "Try again later", "severity": "medium"},
                {"message": "Contact support", "severity": "high"}
            ]
        )
        
        assert response["status"] == "error"
        assert response["error"]["code"] == "SERVER_ERROR"
        assert response["error"]["message"] == "Internal server error"
        assert response["error"]["status_code"] == 500
        assert "details" not in response["error"]
        assert len(response["error"]["suggestions"]) == 2
        assert response["error"]["suggestions"][0]["message"] == "Try again later"
        assert response["error"]["suggestions"][1]["message"] == "Contact support" 