"""
Tests for the error handling middleware and exception handlers.
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field, ValidationError

from summit_seo.web.api.core.error_handlers import (
    ErrorResponse,
    http_exception_handler,
    validation_exception_handler, 
    pydantic_validation_exception_handler,
    general_exception_handler
)

# Skip the configure_error_handlers function to avoid Settings import
@pytest.fixture
def test_app():
    """Create a test app with manually configured error handlers."""
    app = FastAPI()
    
    # Register exception handlers manually
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    # Add test endpoints
    @app.get("/test-http-exception")
    async def test_http_exception():
        """Test endpoint that raises an HTTPException."""
        raise HTTPException(
            status_code=404,
            detail="Test resource not found"
        )

    @app.get("/test-http-exception-with-code")
    async def test_http_exception_with_code():
        """Test endpoint that raises an HTTPException with error code."""
        raise HTTPException(
            status_code=400,
            detail={
                "code": "TEST_ERROR",
                "message": "Test error message",
                "details": {"test": "value"}
            }
        )

    @app.get("/test-validation-error")
    async def test_validation_error(request: Request):
        """Simulate a validation error."""
        raise ValidationError(
            [
                {
                    "loc": ["body", "name"],
                    "msg": "field required",
                    "type": "value_error.missing"
                }
            ],
            model=BaseModel
        )

    @app.get("/test-general-exception")
    async def test_general_exception():
        """Test endpoint that raises a general exception."""
        raise ValueError("Test general exception")
        
    return app

# Create a test client with the app fixture
@pytest.fixture
def client(test_app):
    return TestClient(test_app)

# Mock the error handling module's get_suggestion_for_error to avoid dependencies
@pytest.fixture(autouse=True)
def mock_suggestion_function(monkeypatch):
    """Mock get_suggestion_for_error to return an empty list."""
    def mock_get_suggestion(*args, **kwargs):
        return []
    
    monkeypatch.setattr(
        "summit_seo.web.api.core.error_handlers.get_suggestion_for_error", 
        mock_get_suggestion
    )

class TestErrorHandling:
    """Test cases for error handling middleware and exception handlers."""
    
    def test_http_exception(self, client):
        """Test handling of HTTPException."""
        response = client.get("/test-http-exception")
        
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "HTTP_404"
        assert "not found" in data["error"]["message"].lower()
        
    def test_http_exception_with_code(self, client):
        """Test handling of HTTPException with error code."""
        response = client.get("/test-http-exception-with-code")
        
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "TEST_ERROR"
        assert data["error"]["message"] == "Test error message"
        assert data["error"]["details"]["test"] == "value"
        
    def test_validation_error(self, client):
        """Test handling of validation error."""
        response = client.get("/test-validation-error")
        
        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "validation" in data["error"]["message"].lower()
        assert len(data["error"]["details"]["errors"]) == 1
        assert data["error"]["details"]["errors"][0]["type"] == "value_error.missing"
        
    def test_general_exception(self, client):
        """Test handling of general exception."""
        response = client.get("/test-general-exception")
        
        assert response.status_code == 500
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
        assert "unexpected error" in data["error"]["message"].lower()
        assert data["error"]["details"]["error_type"] == "ValueError"
        assert data["error"]["details"]["error"] == "Test general exception"
        
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