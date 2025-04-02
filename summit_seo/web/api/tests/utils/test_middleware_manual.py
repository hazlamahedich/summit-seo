"""
Manual test script for ErrorHandlingMiddleware without pytest dependencies.
"""
import os
import sys
import unittest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

# Add the parent directory to the path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.insert(0, root_dir)

# Import middleware directly
from summit_seo.web.api.core.error_handlers import ErrorHandlingMiddleware

class AsyncTestCase(unittest.TestCase):
    """Base test case for async tests."""
    
    def run_async(self, coroutine):
        """Run a coroutine in the event loop."""
        return asyncio.run(coroutine)

class TestErrorHandlingMiddleware(AsyncTestCase):
    """Test cases for ErrorHandlingMiddleware."""
    
    def setUp(self):
        """Set up test dependencies."""
        self.app = FastAPI()
        # Initialize middleware with app
        self.middleware = ErrorHandlingMiddleware(self.app)
        
        # Create mocks
        self.request_mock = MagicMock()
        self.request_mock.method = "GET"
        self.request_mock.url = MagicMock()
        self.request_mock.url.path = "/test"
        self.request_mock.headers = {}
        self.request_mock.client = MagicMock()
        self.request_mock.client.host = "127.0.0.1"
        
        # Mock response
        self.response_mock = JSONResponse(content={"status": "success"})
        
        # Mock logging
        self.logger_patch = patch("summit_seo.web.api.core.error_handlers.logger")
        self.mock_logger = self.logger_patch.start()
        
        # Mock get_suggestions_for_exception
        self.suggestion_patch = patch(
            "summit_seo.web.api.core.error_handlers.get_suggestions_for_exception",
            return_value=[],
        )
        self.mock_get_suggestion = self.suggestion_patch.start()
    
    def tearDown(self):
        """Tear down test dependencies."""
        self.logger_patch.stop()
        self.suggestion_patch.stop()
    
    async def async_test_successful_request(self):
        """Test middleware handling successful request."""
        # Mock the call_next function
        async def mock_call_next(request):
            return self.response_mock
        
        # Process request through middleware
        response = await self.middleware.dispatch(self.request_mock, mock_call_next)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response, self.response_mock)
        self.assertTrue("X-Process-Time" in response.headers)
        self.mock_logger.info.assert_called_once()
    
    async def async_test_request_with_exception(self):
        """Test middleware handling request with exception."""
        # Mock the call_next function that raises an exception
        async def mock_call_next_with_error(request):
            raise ValueError("Test error")
        
        # Process request through middleware
        response = await self.middleware.dispatch(self.request_mock, mock_call_next_with_error)
        
        # Verify response
        self.assertEqual(response.status_code, 500)
        
        # Convert body to dict for easier assertions
        response_dict = response.body.decode()
        import json
        response_dict = json.loads(response_dict)
        
        # Verify error response structure
        self.assertEqual(response_dict["status"], "error")
        self.assertEqual(response_dict["error"]["code"], "INTERNAL_SERVER_ERROR")
        self.assertEqual(response_dict["error"]["message"], "An unexpected error occurred")
        self.assertEqual(response_dict["error"]["status_code"], 500)
        self.assertTrue("details" in response_dict["error"])
        self.assertEqual(response_dict["error"]["details"]["error_type"], "ValueError")
        self.assertEqual(response_dict["error"]["details"]["error"], "Test error")
        
        # Verify logging
        self.mock_logger.error.assert_called_once()
        self.mock_logger.exception.assert_called_once()
    
    async def async_test_request_with_forwarded_for(self):
        """Test middleware with X-Forwarded-For header."""
        # Set X-Forwarded-For header
        self.request_mock.headers = {"X-Forwarded-For": "10.0.0.1, 10.0.0.2"}
        
        # Mock the call_next function
        async def mock_call_next(request):
            return self.response_mock
        
        # Process request through middleware
        response = await self.middleware.dispatch(self.request_mock, mock_call_next)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response, self.response_mock)
        
        # Verify client IP is from X-Forwarded-For
        log_call_args = self.mock_logger.info.call_args[0][0]
        self.assertIn("Client: 10.0.0.1", log_call_args)
    
    def test_successful_request(self):
        """Test middleware handling successful request."""
        self.run_async(self.async_test_successful_request())
    
    def test_request_with_exception(self):
        """Test middleware handling request with exception."""
        self.run_async(self.async_test_request_with_exception())
    
    def test_request_with_forwarded_for(self):
        """Test middleware with X-Forwarded-For header."""
        self.run_async(self.async_test_request_with_forwarded_for())

if __name__ == "__main__":
    # Run the tests directly
    unittest.main() 