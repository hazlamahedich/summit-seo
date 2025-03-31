from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
from typing import Dict, Optional, Union, Any
import os
from uuid import uuid4
from sqlalchemy.orm import Session

from ..core import auth
from ..core.config import settings
from ..core.database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserResponse, Token

# Router definition
router = APIRouter()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "placeholder_secret_key_for_development")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Security utilities
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Token blocklist (in-memory for now, should be replaced with Redis in production)
token_blocklist = set()

# Pydantic models
class UserRegistration(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    
class UserLogin(BaseModel):
    username: str
    password: str
    
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None
    jti: Optional[str] = None

class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    
class RefreshToken(BaseModel):
    refresh_token: str

# Mock user database (replace with actual database implementation)
fake_users_db = {
    "johndoe": {
        "id": 1,
        "username": "johndoe",
        "email": "johndoe@example.com",
        "full_name": "John Doe",
        "hashed_password": pwd_context.hash("password123"),
        "role": "admin",
        "is_active": True
    }
}

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return User(**user_dict)
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, fake_users_db[username]["hashed_password"]):
        return False
    return user

def create_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    # Generate a unique token ID
    jti = str(uuid4())
    to_encode.update({"jti": jti})
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        
    to_encode.update({"exp": expire.timestamp()})
    to_encode.update({"iat": datetime.utcnow().timestamp()})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, jti

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "code": "AUTHENTICATION_FAILED",
            "message": "Could not validate credentials",
            "details": {"reason": "Invalid token"}
        },
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Check if token is in blocklist
        if token in token_blocklist:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "TOKEN_REVOKED",
                    "message": "Token has been revoked",
                    "details": {}
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
        # Check token expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "TOKEN_EXPIRED",
                    "message": "Token has expired",
                    "details": {}
                },
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        token_data = TokenData(**payload)
    except JWTError:
        raise credentials_exception
        
    user = get_user(username)
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "USER_INACTIVE",
                "message": "User account is inactive",
                "details": {}
            }
        )
        
    return user

# Routes
@router.post("/register", response_model=UserResponse)
async def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
) -> Any:
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    user = User(
        email=user_in.email,
        hashed_password=auth.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token_data: RefreshToken):
    """
    Use refresh token to get a new access token.
    """
    try:
        payload = jwt.decode(refresh_token_data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verify this is a refresh token
        if payload.get("token_type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_TOKEN_TYPE",
                    "message": "Not a refresh token",
                    "details": {}
                }
            )
            
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "TOKEN_EXPIRED",
                    "message": "Refresh token has expired",
                    "details": {}
                }
            )
            
        username = payload.get("sub")
        user = get_user(username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": "User not found",
                    "details": {}
                }
            )
            
        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token, _ = create_token(
            data={"sub": user.username, "role": user.role},
            expires_delta=access_token_expires
        )
        
        # Create new refresh token
        refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        new_refresh_token, _ = create_token(
            data={"sub": user.username, "role": user.role, "token_type": "refresh"},
            expires_delta=refresh_token_expires
        )
        
        # Add old refresh token to blocklist
        token_blocklist.add(refresh_token_data.refresh_token)
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid refresh token",
                "details": {}
            }
        )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(token: str = Depends(oauth2_scheme)):
    """
    Logout user by adding token to blocklist.
    """
    # Add token to blocklist
    token_blocklist.add(token)
    
    # In production, also invalidate refresh tokens
    
    return None

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(auth.get_current_active_user),
) -> Any:
    return current_user 