"""
Supabase client configuration and utilities for the Summit SEO API.
"""
from typing import Any, Dict, Optional
from supabase import create_client, Client
from fastapi import Depends, HTTPException, status
from jose import JWTError

from .config import settings

def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance.
    
    Returns:
        Client: A configured Supabase client
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_supabase_admin_client() -> Client:
    """
    Create and return a Supabase client with service role key (bypasses RLS).
    
    Returns:
        Client: A Supabase client with admin privileges
    """
    if not settings.SUPABASE_SERVICE_KEY:
        raise ValueError("SUPABASE_SERVICE_KEY is not set")
    
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

async def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify a JWT token from Supabase Auth.
    
    Args:
        token: JWT token to verify
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If token is invalid
    """
    client = get_supabase_client()
    
    try:
        # Use Supabase's auth.getUser() to validate the token
        response = client.auth.get_user(token)
        return response.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(auth_token: str) -> Dict[str, Any]:
    """
    Get the current user based on the auth token.
    
    Args:
        auth_token: JWT token from Supabase
    
    Returns:
        Dict containing user details
    
    Raises:
        HTTPException: If user cannot be authenticated
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        user = await verify_token(auth_token)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception 