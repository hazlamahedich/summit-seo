from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Optional, Any
from datetime import datetime

# Import Supabase utilities
from ..core.supabase import get_supabase_client, get_current_user
from ..schemas.user import UserCreate, UserResponse, Token

# Router definition
router = APIRouter()

# Pydantic models
class UserRegistration(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
class RefreshToken(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    password: str = Field(..., min_length=8)

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserRegistration) -> Any:
    """
    Register a new user using Supabase Auth.
    """
    client = get_supabase_client()
    
    try:
        # Register user with Supabase
        response = client.auth.sign_up({
            "email": user_in.email,
            "password": user_in.password,
            "options": {
                "data": {
                    "full_name": user_in.full_name,
                    "is_active": True,
                }
            }
        })
        
        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )
            
        # Return user information
        return {
            "id": response.user.id,
            "email": response.user.email,
            "full_name": response.user.user_metadata.get("full_name"),
            "is_active": response.user.user_metadata.get("is_active", True),
            "is_superuser": False
        }
    except Exception as e:
        # Handle specific error cases
        error_msg = str(e)
        
        if "already registered" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this email already exists in the system."
            )
        
        # Generic error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {error_msg}"
        )

@router.post("/login", response_model=TokenResponse)
async def login(form_data: UserLogin) -> Any:
    """
    Login with Supabase Auth and get access token.
    """
    client = get_supabase_client()
    
    try:
        # Authenticate with Supabase
        response = client.auth.sign_in_with_password({
            "email": form_data.email,
            "password": form_data.password
        })
        
        if response.session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
            
        # Return tokens
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        # Handle authentication failure
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(refresh_token_data: RefreshToken) -> Any:
    """
    Refresh access token using refresh token.
    """
    client = get_supabase_client()
    
    try:
        # Refresh token with Supabase
        response = client.auth.refresh_session(refresh_token_data.refresh_token)
        
        if response.session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
            
        # Return new tokens
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        # Handle refresh failure
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(authorization: Optional[str] = Header(None)) -> None:
    """
    Logout user and invalidate token.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
        
    token = authorization.replace("Bearer ", "")
    client = get_supabase_client()
    
    try:
        # Sign out with Supabase
        client.auth.sign_out()
        return None
    except Exception as e:
        # Handle sign out failure
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.post("/password-reset-request", status_code=status.HTTP_204_NO_CONTENT)
async def request_password_reset(request_data: PasswordResetRequest) -> None:
    """
    Request a password reset email.
    """
    client = get_supabase_client()
    
    try:
        # Request password reset with Supabase
        client.auth.reset_password_email(request_data.email)
        return None
    except Exception as e:
        # Always return success to prevent email enumeration
        return None

@router.get("/me", response_model=UserResponse)
async def read_users_me(authorization: Optional[str] = Header(None)) -> Any:
    """
    Get current user profile.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
        
    token = authorization.replace("Bearer ", "")
    
    try:
        # Get user from token
        user = await get_current_user(token)
        
        # Return user profile
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.user_metadata.get("full_name"),
            "is_active": user.user_metadata.get("is_active", True),
            "is_superuser": user.user_metadata.get("is_superuser", False)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        ) 