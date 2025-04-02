"""
Manual test script for ErrorResponse without pytest dependencies.
"""
import os
import sys
import unittest

# Add the parent directory to the path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.insert(0, root_dir)

# Import directly from our module
from summit_seo.web.api.tests.utils.error_response import ErrorResponse

class TestErrorResponse(unittest.TestCase):
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
        
        self.assertEqual(response["status"], "error")
        self.assertEqual(response["error"]["code"], "FORBIDDEN")
        self.assertEqual(response["error"]["message"], "Access denied")
        self.assertEqual(response["error"]["status_code"], 403)
        self.assertEqual(response["error"]["details"]["reason"], "Insufficient permissions")
        self.assertEqual(response["error"]["suggestions"][0]["message"], "Request access from admin")
    
    def test_error_response_create_minimal(self):
        """Test creating a minimal error response."""
        response = ErrorResponse.create(
            status_code=404,
            code="NOT_FOUND",
            message="Resource not found"
        )
        
        self.assertEqual(response["status"], "error")
        self.assertEqual(response["error"]["code"], "NOT_FOUND")
        self.assertEqual(response["error"]["message"], "Resource not found")
        self.assertEqual(response["error"]["status_code"], 404)
        self.assertNotIn("details", response["error"])
        self.assertNotIn("suggestions", response["error"])
    
    def test_error_response_with_details(self):
        """Test error response with details but no suggestions."""
        response = ErrorResponse.create(
            status_code=400,
            code="VALIDATION_ERROR",
            message="Validation failed",
            details={"fields": ["name", "email"]}
        )
        
        self.assertEqual(response["status"], "error")
        self.assertEqual(response["error"]["code"], "VALIDATION_ERROR")
        self.assertEqual(response["error"]["message"], "Validation failed")
        self.assertEqual(response["error"]["status_code"], 400)
        self.assertEqual(response["error"]["details"]["fields"], ["name", "email"])
        self.assertNotIn("suggestions", response["error"])
    
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
        
        self.assertEqual(response["status"], "error")
        self.assertEqual(response["error"]["code"], "SERVER_ERROR")
        self.assertEqual(response["error"]["message"], "Internal server error")
        self.assertEqual(response["error"]["status_code"], 500)
        self.assertNotIn("details", response["error"])
        self.assertEqual(len(response["error"]["suggestions"]), 2)
        self.assertEqual(response["error"]["suggestions"][0]["message"], "Try again later")
        self.assertEqual(response["error"]["suggestions"][1]["message"], "Contact support")

if __name__ == "__main__":
    # Run the tests directly
    unittest.main() 