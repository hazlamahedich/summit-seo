from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import copy

# Import the auth router's components
from .auth import User, get_current_user, fake_users_db, get_password_hash

# Import pagination and response models (will create later)
from ..models.common import PaginatedResponse

# Router definition
router = APIRouter()

# Pydantic models
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    
class UserUpdateAdmin(UserUpdate):
    role: Optional[str] = None
    is_active: Optional[bool] = None
    
class UserResponse(User):
    pass
    
class UserListResponse(PaginatedResponse):
    data: List[UserResponse]

# Helper function to check admin role
async def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "PERMISSION_DENIED",
                "message": "Not enough permissions",
                "details": {"required_role": "admin"}
            }
        )
    return current_user

# Routes
@router.get("", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_admin)
):
    """
    List all users. Requires admin privileges.
    """
    users = []
    for username, user_data in fake_users_db.items():
        users.append(User(**user_data))
        
    # Apply pagination
    total = len(users)
    paginated_users = users[skip:skip + limit]
    
    return {
        "status": "success",
        "data": paginated_users,
        "meta": {
            "pagination": {
                "total": total,
                "page": skip // limit + 1 if limit else 1,
                "per_page": limit,
                "pages": (total + limit - 1) // limit if limit else 1
            }
        }
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user's information.
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's information.
    """
    # Get stored user data
    stored_user_data = fake_users_db[current_user.username]
    
    # Update user data with provided values
    if user_update.email is not None:
        stored_user_data["email"] = user_update.email
    if user_update.full_name is not None:
        stored_user_data["full_name"] = user_update.full_name
        
    # Return updated user
    return User(**stored_user_data)

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    current_user: User = Depends(get_current_admin)
):
    """
    Get user by ID. Requires admin privileges.
    """
    # Find user by ID
    for username, user_data in fake_users_db.items():
        if user_data["id"] == user_id:
            return User(**user_data)
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "code": "USER_NOT_FOUND",
            "message": f"User with ID {user_id} not found",
            "details": {}
        }
    )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdateAdmin,
    current_user: User = Depends(get_current_admin)
):
    """
    Update user by ID. Requires admin privileges.
    """
    # Find user by ID
    user_to_update = None
    username_to_update = None
    
    for username, user_data in fake_users_db.items():
        if user_data["id"] == user_id:
            user_to_update = user_data
            username_to_update = username
            break
            
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "USER_NOT_FOUND",
                "message": f"User with ID {user_id} not found",
                "details": {}
            }
        )
        
    # Update user data with provided values
    if user_update.email is not None:
        user_to_update["email"] = user_update.email
    if user_update.full_name is not None:
        user_to_update["full_name"] = user_update.full_name
    if user_update.role is not None:
        user_to_update["role"] = user_update.role
    if user_update.is_active is not None:
        user_to_update["is_active"] = user_update.is_active
        
    # Return updated user
    return User(**user_to_update)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin)
):
    """
    Delete user by ID. Requires admin privileges.
    """
    # Find user by ID
    user_to_delete = None
    username_to_delete = None
    
    for username, user_data in fake_users_db.items():
        if user_data["id"] == user_id:
            user_to_delete = user_data
            username_to_delete = username
            break
            
    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "USER_NOT_FOUND",
                "message": f"User with ID {user_id} not found",
                "details": {}
            }
        )
        
    # Check if user is trying to delete themselves
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_OPERATION",
                "message": "Cannot delete your own user account",
                "details": {}
            }
        )
        
    # Delete user
    del fake_users_db[username_to_delete]
    
    return None 