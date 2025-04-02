"""
Dependencies for FastAPI routes.
"""
from typing import Any, Dict, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

from .supabase import get_supabase_client, verify_token
from .config import settings
from ..services import UserService, ProjectService, AnalysisService, SettingsService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get the current authenticated user.
    
    Args:
        token: JWT token from authentication
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        user = await verify_token(token)
        if user is None:
            raise credentials_exception
        return user
    except Exception:
        raise credentials_exception

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get the current active user.
    
    Args:
        current_user: User information from get_current_user
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If user is not active
    """
    if not current_user.get("user_metadata", {}).get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_superuser(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get the current superuser.
    
    Args:
        current_user: User information from get_current_user
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.get("user_metadata", {}).get("is_superuser", False):
        raise HTTPException(
            status_code=400, 
            detail="The user doesn't have enough privileges"
        )
    return current_user

async def get_user_from_request(request: Request) -> Optional[Dict[str, Any]]:
    """
    Extract the authenticated user from the request state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dict containing user information or None if not authenticated
    """
    if hasattr(request.state, "authenticated") and request.state.authenticated:
        return request.state.user
    return None 

# Service dependencies
def get_user_service(use_rls_bypass: bool = False) -> UserService:
    """
    Get a UserService instance.
    
    Args:
        use_rls_bypass: Whether to bypass Row Level Security
        
    Returns:
        UserService instance
    """
    return UserService(use_rls_bypass)

def get_project_service(use_rls_bypass: bool = False) -> ProjectService:
    """
    Get a ProjectService instance.
    
    Args:
        use_rls_bypass: Whether to bypass Row Level Security
        
    Returns:
        ProjectService instance
    """
    return ProjectService(use_rls_bypass)

def get_analysis_service(use_rls_bypass: bool = False) -> AnalysisService:
    """
    Get an AnalysisService instance.
    
    Args:
        use_rls_bypass: Whether to bypass Row Level Security
        
    Returns:
        AnalysisService instance
    """
    return AnalysisService(use_rls_bypass)

def get_settings_service(use_rls_bypass: bool = False) -> SettingsService:
    """
    Get a SettingsService instance.
    
    Args:
        use_rls_bypass: Whether to bypass Row Level Security
        
    Returns:
        SettingsService instance
    """
    return SettingsService(use_rls_bypass) 