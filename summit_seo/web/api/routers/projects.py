from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from pydantic import BaseModel, HttpUrl, Field, UUID4
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

# Import auth components
from ..core.deps import get_current_user, get_project_service

# Import common models
from ..models.common import PaginatedResponse, StandardResponse

# Import project schemas
from ..schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectList

# Router definition
router = APIRouter()

# Pydantic models for requests and responses
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    url: HttpUrl
    is_active: bool = True

class ProjectCreateRequest(ProjectBase):
    """Request model for project creation"""
    tags: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None
    icon_url: Optional[str] = None

class ProjectUpdateRequest(BaseModel):
    """Request model for project update"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None
    icon_url: Optional[str] = None

class ProjectSummary(BaseModel):
    """Project summary model"""
    last_score: Optional[float] = None
    score_change: Optional[float] = None
    issues_count: int = 0
    critical_issues_count: int = 0
    last_analyzed: Optional[datetime] = None

class ProjectResponseModel(ProjectBase):
    """Response model for project data"""
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    tags: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None
    icon_url: Optional[str] = None
    last_score: Optional[float] = None
    score_change: Optional[float] = None

class ProjectListItem(ProjectResponseModel):
    """Item in project list response"""
    issues_count: int = 0
    critical_issues_count: int = 0

class ProjectListResponseModel(BaseModel):
    """Response model for project listing"""
    data: List[ProjectListItem]
    pagination: Dict[str, Any]

class ProjectSummaryResponse(StandardResponse):
    """Response model for project summary"""
    data: ProjectSummary

# Routes
@router.get("/", response_model=ProjectListResponseModel)
async def list_projects(
    tenant_id: Optional[str] = None,
    search: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    order_by: str = "-updated_at",
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    List all projects for the current user.
    
    Filters:
    - tenant_id: Filter by tenant ID
    - search: Search term for project name or description
    - tags: Filter by tags
    
    Pagination:
    - page: Page number (1-indexed)
    - page_size: Number of items per page
    
    Sorting:
    - order_by: Field to sort by (prefix with - for descending)
    """
    # Get user ID for filtering
    user_id = current_user.get("id")
    
    # Get projects service
    project_service = get_project_service()
    
    # Determine tenant_id if not provided
    if not tenant_id:
        # Use the first tenant the user belongs to
        # In a real application, we would have a selected tenant in the user's session
        # or require tenant_id as a parameter
        tenant_id = current_user.get("app_metadata", {}).get("tenant_id")
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "TENANT_REQUIRED",
                "message": "Tenant ID is required",
                "details": {}
            }
        )
    
    # List projects
    result = await project_service.get_projects_by_tenant(
        tenant_id=tenant_id,
        page=page,
        page_size=page_size,
        search=search,
        tags=tags,
        order_by=order_by
    )
    
    return result

@router.post("/", response_model=ProjectResponseModel)
async def create_project(
    project_in: ProjectCreateRequest,
    tenant_id: str = Query(..., description="Tenant ID"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Create a new project.
    """
    # Get projects service
    project_service = get_project_service()
    
    # Validate tenant access
    # In a real application, we would check if the user has access to the tenant
    # and has permission to create projects
    
    # Create project
    project = await project_service.create_project(
        tenant_id=tenant_id,
        name=project_in.name,
        url=str(project_in.url),
        description=project_in.description,
        settings=project_in.settings,
        tags=project_in.tags,
        icon_url=project_in.icon_url
    )
    
    return project

@router.get("/{project_id}", response_model=ProjectResponseModel)
async def get_project(
    project_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get a specific project by ID.
    """
    # Get projects service
    project_service = get_project_service()
    
    # Get user ID for access check
    user_id = current_user.get("id")
    
    # Get project with access check
    project = await project_service.get_project_with_access_check(
        project_id=project_id,
        user_id=user_id
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "PROJECT_NOT_FOUND",
                "message": f"Project with ID {project_id} not found or access denied",
                "details": {}
            }
        )
    
    return project

@router.put("/{project_id}", response_model=ProjectResponseModel)
async def update_project(
    project_id: str,
    project_in: ProjectUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Update a project.
    """
    # Get projects service
    project_service = get_project_service()
    
    # Get user ID for access check
    user_id = current_user.get("id")
    
    # Verify access to project
    project = await project_service.get_project_with_access_check(
        project_id=project_id,
        user_id=user_id
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "PROJECT_NOT_FOUND",
                "message": f"Project with ID {project_id} not found or access denied",
                "details": {}
            }
        )
    
    # Prepare update data
    update_data = {}
    
    if project_in.name is not None:
        update_data["name"] = project_in.name
    
    if project_in.description is not None:
        update_data["description"] = project_in.description
    
    if project_in.url is not None:
        update_data["url"] = str(project_in.url)
    
    if project_in.is_active is not None:
        update_data["is_active"] = project_in.is_active
    
    if project_in.icon_url is not None:
        update_data["icon_url"] = project_in.icon_url
    
    # Handle special fields separately
    if project_in.tags is not None:
        await project_service.update_project_tags(project_id, project_in.tags)
    
    if project_in.settings is not None:
        await project_service.update_project_settings(project_id, project_in.settings)
    
    # Update project with basic fields if there are any
    if update_data:
        project = await project_service.update(project_id, update_data)
    
    # Return the updated project
    return await project_service.get_by_id(project_id)

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Delete a project.
    """
    # Get projects service
    project_service = get_project_service()
    
    # Get user ID for access check
    user_id = current_user.get("id")
    
    # Verify access to project
    project = await project_service.get_project_with_access_check(
        project_id=project_id,
        user_id=user_id
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "PROJECT_NOT_FOUND",
                "message": f"Project with ID {project_id} not found or access denied",
                "details": {}
            }
        )
    
    # Delete project
    # In a real application, we might want to do a soft delete instead
    success = await project_service.delete(project_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "DELETE_FAILED",
                "message": "Failed to delete project",
                "details": {}
            }
        )
    
    return {"status": "success"}

@router.get("/{project_id}/summary", response_model=ProjectSummaryResponse)
async def get_project_summary(
    project_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get project summary with latest scores and statistics.
    """
    # Get projects service
    project_service = get_project_service()
    
    # Get user ID for access check
    user_id = current_user.get("id")
    
    # Verify access to project
    project = await project_service.get_project_with_access_check(
        project_id=project_id,
        user_id=user_id
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "PROJECT_NOT_FOUND",
                "message": f"Project with ID {project_id} not found or access denied",
                "details": {}
            }
        )
    
    # Extract summary data from project
    summary = ProjectSummary(
        last_score=project.get("last_score"),
        score_change=project.get("score_change"),
        issues_count=project.get("issues_count", 0),
        critical_issues_count=project.get("critical_issues_count", 0),
        last_analyzed=project.get("updated_at")  # Use updated_at as a proxy for last_analyzed
    )
    
    return {
        "status": "success",
        "data": summary
    } 