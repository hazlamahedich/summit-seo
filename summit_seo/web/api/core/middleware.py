"""
Authentication middleware for FastAPI using Supabase.
"""
from typing import Callable, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .supabase import verify_token

class SupabaseAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling Supabase authentication.
    
    This middleware extracts the authorization token from headers
    and verifies it with Supabase. It attaches the user information
    to the request state for use in route handlers.
    """
    
    def __init__(
        self, 
        app: ASGIApp, 
        public_paths: Optional[list[str]] = None
    ):
        """
        Initialize the middleware.
        
        Args:
            app: The ASGI application
            public_paths: List of paths that don't require authentication
        """
        super().__init__(app)
        self.public_paths = public_paths or []
        
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        """
        Process each request through the middleware.
        
        Args:
            request: The incoming request
            call_next: Function to call the next middleware or route handler
            
        Returns:
            The response from the next middleware or route handler
        """
        # Skip authentication for public paths
        for path in self.public_paths:
            if request.url.path.startswith(path):
                return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            # Skip authentication if no token
            # The routes will handle authentication if needed
            return await call_next(request)
        
        token = auth_header.replace("Bearer ", "")
        
        try:
            # Verify token and get user information
            user = await verify_token(token)
            
            # Attach user to request state
            request.state.user = user
            request.state.authenticated = True
            
            # Continue processing the request
            return await call_next(request)
            
        except Exception as e:
            # Authentication failed
            # Don't return error here, let the route handlers handle it
            request.state.authenticated = False
            return await call_next(request) 