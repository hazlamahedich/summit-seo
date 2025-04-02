"""
Manual test script for error handlers without pytest dependencies.
"""
import os
import sys
import unittest
import asyncio
from unittest.mock import MagicMock, patch
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError, BaseModel, Field
from typing import List, Dict, Any

# Add the parent directory to the path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.insert(0, root_dir)

# Import the error handlers directly
from summit_seo.web.api.core.error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    pydantic_validation_exception_handler,
    general_exception_handler,
    get_suggestions_for_exception,
    ErrorResponse,
)

class TestModel(BaseModel):
    """Test model for validation errors."""
    name: str = Field(..., min_length=3)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    age: int = Field(..., gt=0, lt=150)

class AsyncTestCase(unittest.TestCase):
    """Base test case for async tests."""
    
    def run_async(self, coroutine):
        """Run a coroutine in the event loop."""
        return asyncio.run(coroutine)
    
    async def async_test_http_exception_handler(self):
        """Test handling HTTP exceptions."""
        exception = HTTPException(status_code=404, detail="Resource not found")
        
        # Call the handler
        response = await http_exception_handler(self.request_mock, exception)
        response_dict = response.body.decode()
        
        # Convert string response to dict for easier assertions
        import json
        response_dict = json.loads(response_dict)
        
        # Verify response structure
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_dict["status"], "error")
        self.assertEqual(response_dict["error"]["code"], "HTTP_404")
        self.assertEqual(response_dict["error"]["message"], "Resource not found")
        self.assertEqual(response_dict["error"]["status_code"], 404)
    
    async def async_test_http_exception_handler_with_code(self):
        """Test handling HTTP exceptions with custom error code."""
        exception = HTTPException(
            status_code=400, 
            detail={"code": "CUSTOM_ERROR", "message": "Bad request"}
        )
        
        # Call the handler
        response = await http_exception_handler(self.request_mock, exception)
        response_dict = response.body.decode()
        
        # Convert string response to dict for easier assertions
        import json
        response_dict = json.loads(response_dict)
        
        # Verify response structure
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_dict["status"], "error")
        self.assertEqual(response_dict["error"]["code"], "CUSTOM_ERROR")
        self.assertEqual(response_dict["error"]["message"], "Bad request")
        self.assertEqual(response_dict["error"]["status_code"], 400)
    
    async def async_test_pydantic_validation_exception_handler(self):
        """Test handling Pydantic validation exceptions."""
        # Create a validation error
        try:
            TestModel(name="t", email="invalid", age=200)
        except ValidationError as e:
            exception = e
        
        # Call the handler
        response = await pydantic_validation_exception_handler(self.request_mock, exception)
        response_dict = response.body.decode()
        
        # Convert string response to dict for easier assertions
        import json
        response_dict = json.loads(response_dict)
        
        # Verify response structure
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response_dict["status"], "error")
        self.assertEqual(response_dict["error"]["code"], "VALIDATION_ERROR")
        self.assertEqual(response_dict["error"]["message"], "Data validation failed")
        self.assertEqual(response_dict["error"]["status_code"], 422)
        self.assertTrue("details" in response_dict["error"])
        self.assertTrue("errors" in response_dict["error"]["details"])
        self.assertTrue(len(response_dict["error"]["details"]["errors"]) > 0)
        
        # Verify all validation errors are included
        error_fields = set()
        for error in response_dict["error"]["details"]["errors"]:
            if error["loc"]:
                error_fields.add(error["loc"][0])
        
        self.assertIn("name", error_fields)
        self.assertIn("email", error_fields)
        self.assertIn("age", error_fields)
    
    async def async_test_general_exception_handler(self):
        """Test handling unexpected exceptions."""
        exception = ValueError("Something went wrong")
        
        # Mock get_suggestions_for_exception function
        with patch(
            "summit_seo.web.api.core.error_handlers.get_suggestions_for_exception",
            return_value=[]
        ):
            # Call the handler
            response = await general_exception_handler(self.request_mock, exception)
            response_dict = response.body.decode()
            
            # Convert string response to dict for easier assertions
            import json
            response_dict = json.loads(response_dict)
            
            # Verify response structure
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response_dict["status"], "error")
            self.assertEqual(response_dict["error"]["code"], "INTERNAL_SERVER_ERROR")
            self.assertEqual(response_dict["error"]["message"], "An unexpected error occurred")
            self.assertEqual(response_dict["error"]["status_code"], 500)
            # Check for error details
            self.assertTrue("details" in response_dict["error"])
            self.assertEqual(response_dict["error"]["details"]["error_type"], "ValueError")
            self.assertEqual(response_dict["error"]["details"]["error"], "Something went wrong")

class TestErrorHandlers(AsyncTestCase):
    """Test cases for error handlers."""
    
    def setUp(self):
        """Set up test app and request mock."""
        self.app = FastAPI()
        self.request_mock = MagicMock()
        
        # Mock get_suggestion_for_error to avoid settings dependency
        self.suggestion_patch = patch(
            "summit_seo.web.api.core.error_handlers.get_suggestion_for_error",
            return_value=[],
        )
        self.mock_get_suggestion = self.suggestion_patch.start()
    
    def tearDown(self):
        """Tear down test dependencies."""
        self.suggestion_patch.stop()
    
    def test_http_exception_handler(self):
        """Test handling HTTP exceptions."""
        self.run_async(self.async_test_http_exception_handler())
    
    def test_http_exception_handler_with_code(self):
        """Test handling HTTP exceptions with custom error code."""
        self.run_async(self.async_test_http_exception_handler_with_code())
    
    def test_pydantic_validation_exception_handler(self):
        """Test handling Pydantic validation exceptions."""
        self.run_async(self.async_test_pydantic_validation_exception_handler())
    
    def test_general_exception_handler(self):
        """Test handling unexpected exceptions."""
        self.run_async(self.async_test_general_exception_handler())

if __name__ == "__main__":
    # Run the tests directly
    unittest.main() 