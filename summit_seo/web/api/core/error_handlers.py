"""
Error handling utilities for the Summit SEO API.

This module provides centralized error handling for the API,
including middleware, exception handlers, and standardized error responses.
"""

from typing import Dict, Any, Optional, List, Union, Callable
import logging
import time
import traceback

from fastapi import Request, Response, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError

from summit_seo.error_handling import (
    ActionableSuggestion, 
    get_suggestion_for_error,
    SuggestionSeverity
)

# Configure logging
logger = logging.getLogger("summit-seo-api.errors")

# Error response model
class ErrorResponse:
    """Standard error response format."""
    
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


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling errors and logging requests.
    
    This middleware logs all requests and catches any unhandled exceptions,
    converting them into standardized error responses.
    """
    
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process each request through the middleware.
        
        Args:
            request: The incoming request
            call_next: Function to call the next middleware or route handler
            
        Returns:
            The response from the next middleware or route handler
        """
        start_time = time.time()
        
        # Get client IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # Process the request
        try:
            response = await call_next(request)
            
            # Log request details
            process_time = time.time() - start_time
            logger.info(
                f"Request: {request.method} {request.url.path} "
                f"Client: {client_ip} "
                f"Status: {response.status_code} "
                f"Time: {process_time:.3f}s"
            )
            
            # Add timing header to response
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                f"Unhandled exception: {request.method} {request.url.path} "
                f"Client: {client_ip} "
                f"Error: {str(e)} "
                f"Time: {process_time:.3f}s"
            )
            logger.exception(e)
            
            # Get suggestions for the error
            suggestions = get_suggestions_for_exception(e)
            
            # Create standardized error response
            error_response = ErrorResponse.create(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred",
                details={"error_type": type(e).__name__, "error": str(e)},
                suggestions=suggestions
            )
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=error_response
            )


# Exception handlers
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Custom exception handler for HTTPException.
    
    Args:
        request: The request that caused the exception
        exc: The raised HTTPException
        
    Returns:
        Standardized error response
    """
    # Extract error details from the exception
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        # Use the provided error details
        code = exc.detail.get("code", "UNKNOWN_ERROR")
        message = exc.detail.get("message", str(exc.detail))
        details = exc.detail.get("details", {})
    else:
        # Use the exception detail as the message
        code = f"HTTP_{exc.status_code}"
        message = str(exc.detail)
        details = {}
    
    # Create standardized error response
    error_response = ErrorResponse.create(
        status_code=exc.status_code,
        code=code,
        message=message,
        details=details
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Custom exception handler for validation errors.
    
    Args:
        request: The request that caused the exception
        exc: The raised validation exception
        
    Returns:
        Standardized error response with validation details
    """
    # Extract error details from the exception
    errors = []
    for error in exc.errors():
        error_detail = {
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        }
        errors.append(error_detail)
    
    # Create standardized error response
    error_response = ErrorResponse.create(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="VALIDATION_ERROR",
        message="Request validation failed",
        details={"errors": errors}
    )
    
    # Log validation errors
    logger.warning(
        f"Validation error: {request.method} {request.url.path} "
        f"Errors: {len(errors)}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )


async def pydantic_validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """
    Custom exception handler for Pydantic validation errors.
    
    Args:
        request: The request that caused the exception
        exc: The raised validation exception
        
    Returns:
        Standardized error response with validation details
    """
    # Convert to the same format as FastAPI validation errors
    errors = []
    for error in exc.errors():
        error_detail = {
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        }
        errors.append(error_detail)
    
    # Create standardized error response
    error_response = ErrorResponse.create(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="VALIDATION_ERROR",
        message="Data validation failed",
        details={"errors": errors}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Fallback handler for all other exceptions.
    
    Args:
        request: The request that caused the exception
        exc: The raised exception
        
    Returns:
        Standardized error response
    """
    # Log the error
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")
    logger.exception(exc)
    
    # Get suggestions for the error
    suggestions = get_suggestions_for_exception(exc)
    
    # Create standardized error response
    error_response = ErrorResponse.create(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred",
        details={"error_type": type(exc).__name__, "error": str(exc)},
        suggestions=suggestions
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response
    )


def get_suggestions_for_exception(exc: Exception) -> List[Dict[str, Any]]:
    """
    Get actionable suggestions for resolving an exception.
    
    Args:
        exc: The exception to get suggestions for
        
    Returns:
        List of suggestion dictionaries
    """
    try:
        # Get suggestions from the error handling module
        action_suggestions = get_suggestion_for_error(exc)
        
        # Convert to dict format for API response
        return [
            {
                "message": suggestion.message,
                "action": suggestion.action,
                "severity": suggestion.severity.value,
                "category": suggestion.category.value if suggestion.category else None
            }
            for suggestion in action_suggestions
        ]
    except Exception as e:
        # Don't let suggestion generation failure cause more problems
        logger.error(f"Error generating suggestions: {str(e)}")
        return []


def configure_error_handlers(app):
    """
    Configure all error handlers for a FastAPI application.
    
    Args:
        app: The FastAPI application to configure
    """
    # Add middleware
    app.add_middleware(ErrorHandlingMiddleware)
    
    # Register exception handlers
    app.exception_handler(HTTPException)(http_exception_handler)
    app.exception_handler(RequestValidationError)(validation_exception_handler)
    app.exception_handler(ValidationError)(pydantic_validation_exception_handler)
    app.exception_handler(Exception)(general_exception_handler) 