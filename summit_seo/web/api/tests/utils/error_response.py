"""
Error response utilities for testing.
"""
from typing import Dict, Any, Optional, List

class ErrorResponse:
    """Standard error response format for testing."""
    
    @staticmethod
    def create(
        status_code: int, 
        code: str, 
        message: str, 
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized error response.
        
        Args:
            status_code: HTTP status code
            code: Error code for programmatic handling
            message: Human-readable error message
            details: Additional error details
            suggestions: Actionable suggestions for resolving the error
            
        Returns:
            Standardized error response dictionary
        """
        response = {
            "status": "error",
            "error": {
                "code": code,
                "message": message,
                "status_code": status_code
            }
        }
        
        if details:
            response["error"]["details"] = details
            
        if suggestions:
            response["error"]["suggestions"] = suggestions
            
        return response 