"""
User service for database operations related to users.
"""
from typing import Any, Dict, List, Optional
import uuid

from .base_service import BaseService

class UserService(BaseService):
    """
    Service for user-related database operations.
    """
    
    def __init__(self, use_rls_bypass: bool = False):
        """
        Initialize the user service.
        
        Args:
            use_rls_bypass: Whether to use admin client to bypass RLS
        """
        super().__init__("user", use_rls_bypass)
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            User data or None if not found
        """
        client = self.get_client()
        response = client.table(self.table_name).select("*").eq("email", email.lower()).execute()
        
        if not response.data:
            return None
        
        return response.data[0]
    
    async def get_user_roles(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all roles for a user.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            List of role data
        """
        client = self.get_client()
        response = client.table("user_roles").select("role_id").eq("user_id", user_id).execute()
        
        if not response.data:
            return []
        
        # Get full role data
        role_ids = [item["role_id"] for item in response.data]
        roles_response = client.table("role").select("*").in_("id", role_ids).execute()
        
        return roles_response.data if roles_response.data else []
    
    async def get_user_tenants(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all tenants a user belongs to.
        
        Args:
            user_id: UUID of the user
            
        Returns:
            List of tenant data with role information
        """
        client = self.get_client()
        response = client.table("tenant_user").select("*").eq("user_id", user_id).execute()
        
        if not response.data:
            return []
        
        # Get full tenant data
        tenant_ids = [item["tenant_id"] for item in response.data]
        tenants_response = client.table("tenant").select("*").in_("id", tenant_ids).execute()
        
        # Merge tenant and tenant_user data
        if not tenants_response.data:
            return []
        
        result = []
        tenant_user_map = {item["tenant_id"]: item for item in response.data}
        
        for tenant in tenants_response.data:
            tenant_data = dict(tenant)
            tenant_user = tenant_user_map.get(tenant["id"])
            if tenant_user:
                tenant_data["role"] = tenant_user["role"]
                tenant_data["permissions"] = {
                    "can_create_projects": tenant_user["can_create_projects"],
                    "can_delete_projects": tenant_user["can_delete_projects"],
                    "can_manage_users": tenant_user["can_manage_users"]
                }
            result.append(tenant_data)
        
        return result
    
    async def add_user_to_tenant(
        self, 
        user_id: str, 
        tenant_id: str, 
        role: str = "member",
        permissions: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Add a user to a tenant with specified role and permissions.
        
        Args:
            user_id: UUID of the user
            tenant_id: UUID of the tenant
            role: User's role in the tenant
            permissions: Dictionary of permission flags
            
        Returns:
            Created tenant_user data
        """
        if permissions is None:
            permissions = {
                "can_create_projects": False,
                "can_delete_projects": False,
                "can_manage_users": False
            }
        
        tenant_user_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "tenant_id": tenant_id,
            "role": role,
            "can_create_projects": permissions.get("can_create_projects", False),
            "can_delete_projects": permissions.get("can_delete_projects", False),
            "can_manage_users": permissions.get("can_manage_users", False)
        }
        
        client = self.get_client()
        response = client.table("tenant_user").insert(tenant_user_data).execute()
        
        if not response.data:
            raise Exception(f"Failed to add user {user_id} to tenant {tenant_id}")
        
        return response.data[0]
    
    async def update_tenant_user(
        self, 
        user_id: str, 
        tenant_id: str, 
        role: Optional[str] = None,
        permissions: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Update a user's role and permissions in a tenant.
        
        Args:
            user_id: UUID of the user
            tenant_id: UUID of the tenant
            role: User's new role in the tenant
            permissions: Dictionary of permission flags to update
            
        Returns:
            Updated tenant_user data
        """
        update_data = {}
        
        if role is not None:
            update_data["role"] = role
        
        if permissions is not None:
            if "can_create_projects" in permissions:
                update_data["can_create_projects"] = permissions["can_create_projects"]
            if "can_delete_projects" in permissions:
                update_data["can_delete_projects"] = permissions["can_delete_projects"]
            if "can_manage_users" in permissions:
                update_data["can_manage_users"] = permissions["can_manage_users"]
        
        if not update_data:
            # Nothing to update
            return await self.get_tenant_user(user_id, tenant_id)
        
        client = self.get_client()
        response = client.table("tenant_user").update(update_data)\
            .eq("user_id", user_id)\
            .eq("tenant_id", tenant_id)\
            .execute()
        
        if not response.data:
            raise Exception(f"Failed to update user {user_id} in tenant {tenant_id}")
        
        return response.data[0]
    
    async def remove_user_from_tenant(self, user_id: str, tenant_id: str) -> bool:
        """
        Remove a user from a tenant.
        
        Args:
            user_id: UUID of the user
            tenant_id: UUID of the tenant
            
        Returns:
            True if successful
        """
        client = self.get_client()
        response = client.table("tenant_user").delete()\
            .eq("user_id", user_id)\
            .eq("tenant_id", tenant_id)\
            .execute()
        
        return len(response.data) > 0
    
    async def get_tenant_user(self, user_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a user's membership details for a specific tenant.
        
        Args:
            user_id: UUID of the user
            tenant_id: UUID of the tenant
            
        Returns:
            Tenant user data or None if not found
        """
        client = self.get_client()
        response = client.table("tenant_user").select("*")\
            .eq("user_id", user_id)\
            .eq("tenant_id", tenant_id)\
            .execute()
        
        if not response.data:
            return None
        
        return response.data[0]


# Singleton instance
_user_service_instance = None

def get_user_service(use_rls_bypass: bool = False) -> UserService:
    """
    Get a singleton instance of the UserService.
    
    Args:
        use_rls_bypass: Whether to use admin client to bypass RLS
        
    Returns:
        UserService instance
    """
    global _user_service_instance
    if _user_service_instance is None or _user_service_instance.use_rls_bypass != use_rls_bypass:
        _user_service_instance = UserService(use_rls_bypass)
    return _user_service_instance 