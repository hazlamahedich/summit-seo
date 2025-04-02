"""
Project service for database operations related to projects.
"""
from typing import Any, Dict, List, Optional
import uuid

from .base_service import BaseService

class ProjectService(BaseService):
    """
    Service for project-related database operations.
    """
    
    def __init__(self, use_rls_bypass: bool = False):
        """
        Initialize the project service.
        
        Args:
            use_rls_bypass: Whether to use admin client to bypass RLS
        """
        super().__init__("project", use_rls_bypass)
    
    async def get_projects_by_tenant(
        self, 
        tenant_id: str, 
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        order_by: str = "-updated_at"
    ) -> Dict[str, Any]:
        """
        Get projects for a specific tenant.
        
        Args:
            tenant_id: UUID of the tenant
            page: Page number (1-indexed)
            page_size: Number of records per page
            search: Search term for project name or description
            tags: List of tags to filter by
            order_by: Column to order by (prefix with - for descending)
            
        Returns:
            Dictionary with data and pagination information
        """
        client = self.get_client()
        query = client.table(self.table_name).select("*").eq("tenant_id", tenant_id)
        
        # Apply search filter if provided
        if search:
            query = query.or_(f"name.ilike.%{search}%,description.ilike.%{search}%")
        
        # Apply tag filter if provided
        if tags and len(tags) > 0:
            # This is a simplified approach - for proper array contains operation,
            # you might need to use a PostgreSQL function or RPC
            for tag in tags:
                query = query.contains("tags", [tag])
        
        # Apply pagination
        start = (page - 1) * page_size
        query = query.range(start, start + page_size - 1)
        
        # Apply ordering
        if order_by:
            if order_by.startswith('-'):
                query = query.order(order_by[1:], desc=True)
            else:
                query = query.order(order_by)
        
        # Execute query
        response = query.execute()
        
        # Get total count for pagination
        count_query = client.table(self.table_name).select("count", count="exact").eq("tenant_id", tenant_id)
        
        if search:
            count_query = count_query.or_(f"name.ilike.%{search}%,description.ilike.%{search}%")
            
        if tags and len(tags) > 0:
            for tag in tags:
                count_query = count_query.contains("tags", [tag])
                
        count_response = count_query.execute()
        total = count_response.count if hasattr(count_response, 'count') else 0
        
        return {
            "data": response.data,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size
            }
        }
    
    async def get_project_with_access_check(self, project_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a project by ID with access check for the user.
        
        Args:
            project_id: UUID of the project
            user_id: UUID of the user
            
        Returns:
            Project data or None if not found or no access
        """
        # For projects, we rely on RLS to enforce access control
        # This method simply attempts to get the project - RLS will restrict access if needed
        client = self.get_client()
        response = client.table(self.table_name).select("*").eq("id", project_id).execute()
        
        if not response.data:
            return None
        
        return response.data[0]
    
    async def create_project(
        self, 
        tenant_id: str, 
        name: str,
        url: str,
        description: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        icon_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new project.
        
        Args:
            tenant_id: UUID of the tenant
            name: Project name
            url: Project URL
            description: Project description
            settings: Project settings
            tags: Project tags
            icon_url: Project icon URL
            
        Returns:
            Created project data
        """
        project_data = {
            "id": str(uuid.uuid4()),
            "tenant_id": tenant_id,
            "name": name,
            "url": url
        }
        
        if description is not None:
            project_data["description"] = description
        
        if settings is not None:
            project_data["settings"] = settings
        
        if tags is not None:
            project_data["tags"] = tags
        
        if icon_url is not None:
            project_data["icon_url"] = icon_url
        
        return await self.create(project_data)
    
    async def update_project_tags(self, project_id: str, tags: List[str]) -> Dict[str, Any]:
        """
        Update a project's tags.
        
        Args:
            project_id: UUID of the project
            tags: New list of tags
            
        Returns:
            Updated project data
        """
        return await self.update(project_id, {"tags": tags})
    
    async def update_project_settings(self, project_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a project's settings.
        
        Args:
            project_id: UUID of the project
            settings: New settings object
            
        Returns:
            Updated project data
        """
        return await self.update(project_id, {"settings": settings})
    
    async def update_project_score(
        self, 
        project_id: str, 
        score: float,
        issues_count: int = 0,
        critical_issues_count: int = 0
    ) -> Dict[str, Any]:
        """
        Update a project's score and issue counts.
        
        Args:
            project_id: UUID of the project
            score: New score value
            issues_count: Total number of issues
            critical_issues_count: Number of critical issues
            
        Returns:
            Updated project data
        """
        # First get current score to calculate change
        project = await self.get_by_id(project_id)
        
        if not project:
            raise Exception(f"Project with ID {project_id} not found")
        
        current_score = project.get("last_score")
        score_change = score - current_score if current_score is not None else 0
        
        update_data = {
            "last_score": score,
            "score_change": score_change,
            "issues_count": issues_count,
            "critical_issues_count": critical_issues_count
        }
        
        return await self.update(project_id, update_data)


# Singleton instance
_project_service_instance = None

def get_project_service(use_rls_bypass: bool = False) -> ProjectService:
    """
    Get a singleton instance of the ProjectService.
    
    Args:
        use_rls_bypass: Whether to use admin client to bypass RLS
        
    Returns:
        ProjectService instance
    """
    global _project_service_instance
    if _project_service_instance is None or _project_service_instance.use_rls_bypass != use_rls_bypass:
        _project_service_instance = ProjectService(use_rls_bypass)
    return _project_service_instance 