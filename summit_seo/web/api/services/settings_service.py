"""
Settings service for managing application settings in Supabase.

This service provides functionality to manage system-wide settings
in a multi-tenant environment, with appropriate access controls.
"""
from typing import Dict, List, Any, Optional
import json
from enum import Enum

from .base_service import BaseService


class SettingScope(str, Enum):
    """Scope of a setting."""
    SYSTEM = "system"  # System-wide settings
    TENANT = "tenant"  # Tenant-specific settings
    USER = "user"  # User-specific settings


class SettingsService(BaseService):
    """Service for managing application settings."""
    
    def __init__(self, supabase):
        """Initialize the settings service."""
        super().__init__(supabase, "settings")
        
    async def get_all_settings(
        self,
        scope: Optional[SettingScope] = None,
        scope_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        search: Optional[str] = None,
        order_by: str = "key"
    ) -> Dict[str, Any]:
        """
        Get all settings, optionally filtered by scope.
        
        Args:
            scope: Optional scope filter (system, tenant, user)
            scope_id: ID of the scope entity (required for tenant and user scopes)
            page: Page number for pagination
            page_size: Number of items per page
            search: Optional search term for key or description
            order_by: Field to order by
            
        Returns:
            Dictionary with settings and pagination information
        """
        query = self.table()
        
        # Apply scope filters
        if scope:
            query = query.eq("scope", scope)
            
            if scope in [SettingScope.TENANT, SettingScope.USER] and scope_id:
                query = query.eq("scope_id", scope_id)
                
        # Apply search filter
        if search:
            query = query.or_(f"key.ilike.%{search}%,description.ilike.%{search}%")
            
        # Calculate pagination
        offset = (page - 1) * page_size
        
        # Get total count
        count_query = query.count()
        count_data = await self._execute_query(count_query)
        total = count_data.count
        
        # Apply ordering and pagination
        if order_by.startswith("-"):
            order_field = order_by[1:]
            query = query.order(order_field, desc=True)
        else:
            query = query.order(order_by)
            
        query = query.range(offset, offset + page_size - 1)
        
        # Execute query
        data = await self._execute_query(query)
        
        # Calculate pagination metadata
        pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        return {
            "data": data.data,
            "pagination": {
                "total": total,
                "page": page,
                "pages": pages,
                "page_size": page_size
            }
        }
    
    async def get_setting(
        self,
        key: str,
        scope: Optional[SettingScope] = SettingScope.SYSTEM,
        scope_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific setting by key and scope.
        
        Args:
            key: Setting key
            scope: Setting scope
            scope_id: ID of the scope entity (required for tenant and user scopes)
            
        Returns:
            Setting if found, None otherwise
        """
        query = self.table().eq("key", key).eq("scope", scope)
        
        if scope in [SettingScope.TENANT, SettingScope.USER] and scope_id:
            query = query.eq("scope_id", scope_id)
            
        data = await self._execute_query(query)
        
        if not data.data:
            return None
            
        return data.data[0]
    
    async def update_setting(
        self,
        key: str,
        value: Any,
        scope: SettingScope = SettingScope.SYSTEM,
        scope_id: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update or create a setting.
        
        Args:
            key: Setting key
            value: Setting value (will be stored as JSON)
            scope: Setting scope
            scope_id: ID of the scope entity (required for tenant and user scopes)
            description: Optional setting description
            
        Returns:
            Updated or created setting
        """
        # First check if the setting exists
        existing = await self.get_setting(key, scope, scope_id)
        
        # Convert value to JSON string for storage
        value_json = json.dumps(value)
        
        if existing:
            # Update existing setting
            query = self.table().eq("id", existing["id"]).update({
                "value": value_json
            })
            
            if description is not None:
                query = query.update({"description": description})
                
            data = await self._execute_query(query)
            return data.data[0]
        else:
            # Create new setting
            setting_data = {
                "key": key,
                "value": value_json,
                "scope": scope,
            }
            
            if scope in [SettingScope.TENANT, SettingScope.USER] and scope_id:
                setting_data["scope_id"] = scope_id
                
            if description is not None:
                setting_data["description"] = description
                
            data = await self.create(setting_data)
            return data
    
    async def delete_setting(
        self,
        key: str,
        scope: SettingScope = SettingScope.SYSTEM,
        scope_id: Optional[str] = None
    ) -> bool:
        """
        Delete a setting.
        
        Args:
            key: Setting key
            scope: Setting scope
            scope_id: ID of the scope entity (required for tenant and user scopes)
            
        Returns:
            True if deleted, False if not found
        """
        # First check if the setting exists
        existing = await self.get_setting(key, scope, scope_id)
        
        if not existing:
            return False
            
        # Delete the setting
        query = self.table().eq("id", existing["id"]).delete()
        await self._execute_query(query)
        
        return True
    
    async def get_setting_value(
        self,
        key: str,
        default_value: Any = None,
        scope: SettingScope = SettingScope.SYSTEM,
        scope_id: Optional[str] = None
    ) -> Any:
        """
        Get a setting value, with fallback to default if not found.
        
        Args:
            key: Setting key
            default_value: Default value if setting not found
            scope: Setting scope
            scope_id: ID of the scope entity (required for tenant and user scopes)
            
        Returns:
            Setting value or default value
        """
        setting = await self.get_setting(key, scope, scope_id)
        
        if not setting:
            return default_value
            
        try:
            # Parse the JSON value
            return json.loads(setting["value"])
        except:
            # If parsing fails, return the raw value
            return setting["value"]
    
    async def get_settings_by_prefix(
        self,
        prefix: str,
        scope: SettingScope = SettingScope.SYSTEM,
        scope_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all settings with keys starting with a specific prefix.
        
        Args:
            prefix: Key prefix to filter by
            scope: Setting scope
            scope_id: ID of the scope entity (required for tenant and user scopes)
            
        Returns:
            Dictionary of settings with the prefix removed from keys
        """
        query = self.table().eq("scope", scope).like("key", f"{prefix}%")
        
        if scope in [SettingScope.TENANT, SettingScope.USER] and scope_id:
            query = query.eq("scope_id", scope_id)
            
        data = await self._execute_query(query)
        
        # Convert to dictionary with prefix removed
        result = {}
        prefix_len = len(prefix)
        
        for setting in data.data:
            key = setting["key"][prefix_len:] if setting["key"].startswith(prefix) else setting["key"]
            try:
                # Parse the JSON value
                result[key] = json.loads(setting["value"])
            except:
                # If parsing fails, use the raw value
                result[key] = setting["value"]
                
        return result 

# Singleton instance
_settings_service_instance = None

def get_settings_service(use_rls_bypass: bool = False) -> SettingsService:
    """
    Get a singleton instance of the SettingsService.
    
    Args:
        use_rls_bypass: Whether to use admin client to bypass RLS
        
    Returns:
        SettingsService instance
    """
    global _settings_service_instance
    if _settings_service_instance is None:
        from ..core.supabase import get_supabase_client, get_supabase_admin_client
        supabase = get_supabase_admin_client() if use_rls_bypass else get_supabase_client()
        _settings_service_instance = SettingsService(supabase)
    return _settings_service_instance 