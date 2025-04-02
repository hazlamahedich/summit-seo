"""
Settings router for Summit SEO API.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator
import json

from ..core.deps import get_current_superuser, get_settings_service
from ..services import SettingScope

router = APIRouter()

class AppSettingBase(BaseModel):
    """
    Base model for application settings.
    """
    key: str = Field(..., description="Setting key")
    value: Any = Field(..., description="Setting value")
    description: Optional[str] = Field(None, description="Setting description")

class AppSetting(AppSettingBase):
    """
    Application setting model.
    """
    id: str = Field(..., description="Setting ID")
    scope: str = Field(..., description="Setting scope")
    scope_id: Optional[str] = Field(None, description="Scope ID for tenant/user settings")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

class AppSettingCreate(AppSettingBase):
    """
    Model for creating a new application setting.
    """
    scope: SettingScope = Field(default=SettingScope.SYSTEM, description="Setting scope")
    scope_id: Optional[str] = Field(None, description="Scope ID for tenant/user settings")
    
    @validator('scope_id')
    def validate_scope_id(cls, v, values):
        scope = values.get('scope')
        if scope in [SettingScope.TENANT, SettingScope.USER] and not v:
            raise ValueError(f"scope_id is required for scope {scope}")
        return v

class AppSettingUpdate(BaseModel):
    """
    Model for updating an application setting.
    """
    value: Any = Field(..., description="New setting value")
    description: Optional[str] = Field(None, description="Setting description")

class SettingsListResponseModel(BaseModel):
    """
    Response model for settings listing.
    """
    data: List[AppSetting]
    pagination: Dict[str, Any]

@router.get("/", response_model=SettingsListResponseModel)
async def get_all_settings(
    scope: Optional[SettingScope] = Query(None, description="Filter by setting scope"),
    scope_id: Optional[str] = Query(None, description="Scope ID for tenant/user settings"),
    search: Optional[str] = Query(None, description="Search term for key or description"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    order_by: str = Query("key", description="Field to order by"),
    current_user: Dict[str, Any] = Depends(get_current_superuser)
) -> Any:
    """
    Get all application settings.
    
    Only accessible by superusers.
    
    Filters:
    - scope: Filter by setting scope (system, tenant, user)
    - scope_id: ID of the scope entity (required for tenant and user scopes)
    - search: Search term for key or description
    
    Pagination:
    - page: Page number (1-indexed)
    - page_size: Number of items per page
    
    Sorting:
    - order_by: Field to sort by (prefix with - for descending)
    """
    settings_service = get_settings_service(use_rls_bypass=True)
    
    result = await settings_service.get_all_settings(
        scope=scope,
        scope_id=scope_id,
        page=page,
        page_size=page_size,
        search=search,
        order_by=order_by
    )
    
    return result

@router.post("/", response_model=AppSetting, status_code=status.HTTP_201_CREATED)
async def create_setting(
    setting: AppSettingCreate,
    current_user: Dict[str, Any] = Depends(get_current_superuser)
) -> Any:
    """
    Create a new application setting.
    
    Only accessible by superusers.
    """
    settings_service = get_settings_service(use_rls_bypass=True)
    
    # Check if setting already exists
    existing = await settings_service.get_setting(
        key=setting.key,
        scope=setting.scope,
        scope_id=setting.scope_id
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "SETTING_EXISTS",
                "message": f"Setting with key '{setting.key}' already exists for this scope",
                "details": {}
            }
        )
    
    # Create the setting
    result = await settings_service.update_setting(
        key=setting.key,
        value=setting.value,
        scope=setting.scope,
        scope_id=setting.scope_id,
        description=setting.description
    )
    
    return result

@router.get("/{key}", response_model=AppSetting)
async def get_setting(
    key: str = Path(..., description="Setting key"),
    scope: SettingScope = Query(SettingScope.SYSTEM, description="Setting scope"),
    scope_id: Optional[str] = Query(None, description="Scope ID for tenant/user settings"),
    current_user: Dict[str, Any] = Depends(get_current_superuser)
) -> Any:
    """
    Get a specific application setting by key.
    
    Only accessible by superusers.
    """
    settings_service = get_settings_service(use_rls_bypass=True)
    
    # Get the setting
    setting = await settings_service.get_setting(
        key=key,
        scope=scope,
        scope_id=scope_id
    )
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SETTING_NOT_FOUND",
                "message": f"Setting with key '{key}' not found for this scope",
                "details": {}
            }
        )
    
    return setting

@router.put("/{key}", response_model=AppSetting)
async def update_setting(
    key: str = Path(..., description="Setting key"),
    setting_update: AppSettingUpdate = None,
    scope: SettingScope = Query(SettingScope.SYSTEM, description="Setting scope"),
    scope_id: Optional[str] = Query(None, description="Scope ID for tenant/user settings"),
    current_user: Dict[str, Any] = Depends(get_current_superuser)
) -> Any:
    """
    Update a specific application setting by key.
    
    Only accessible by superusers.
    """
    settings_service = get_settings_service(use_rls_bypass=True)
    
    # Check if setting exists
    existing = await settings_service.get_setting(
        key=key,
        scope=scope,
        scope_id=scope_id
    )
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SETTING_NOT_FOUND",
                "message": f"Setting with key '{key}' not found for this scope",
                "details": {}
            }
        )
    
    # Update the setting
    result = await settings_service.update_setting(
        key=key,
        value=setting_update.value,
        scope=scope,
        scope_id=scope_id,
        description=setting_update.description if setting_update.description is not None else None
    )
    
    return result

@router.delete("/{key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_setting(
    key: str = Path(..., description="Setting key"),
    scope: SettingScope = Query(SettingScope.SYSTEM, description="Setting scope"),
    scope_id: Optional[str] = Query(None, description="Scope ID for tenant/user settings"),
    current_user: Dict[str, Any] = Depends(get_current_superuser)
) -> Any:
    """
    Delete a specific application setting by key.
    
    Only accessible by superusers.
    """
    settings_service = get_settings_service(use_rls_bypass=True)
    
    # Delete the setting
    deleted = await settings_service.delete_setting(
        key=key,
        scope=scope,
        scope_id=scope_id
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SETTING_NOT_FOUND",
                "message": f"Setting with key '{key}' not found for this scope",
                "details": {}
            }
        )
    
    return None 