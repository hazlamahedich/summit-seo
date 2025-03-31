from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

# Import auth components
from .auth import User, get_current_user

# Import common models
from ..models.common import PaginatedResponse, StandardResponse

# Import project and user models
from ..models.project import Project
from ..models.user import User

# Import project schemas
from ..schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectList

# Import database
from ..core.database import get_db

# Router definition
router = APIRouter()

# Pydantic models
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    url: HttpUrl
    is_active: bool = True

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None

class ProjectSummary(BaseModel):
    overall_score: Optional[int] = None
    category_scores: Dict[str, int] = {}
    last_analyzed: Optional[datetime] = None
    trend: Optional[str] = None
    recommendations_count: int = 0

class Project(ProjectBase):
    id: str
    owner_id: int
    created_at: datetime
    updated_at: datetime
    last_analyzed: Optional[datetime] = None

class ProjectResponse(StandardResponse[Project]):
    data: Project

class ProjectListResponse(PaginatedResponse[Project]):
    data: List[Project]

class ProjectSummaryResponse(StandardResponse[ProjectSummary]):
    data: ProjectSummary

# Mock project database
fake_projects_db = {
    "1": {
        "id": "1",
        "name": "Example Project",
        "description": "An example project for demonstration",
        "url": "https://example.com",
        "is_active": True,
        "owner_id": 1,
        "created_at": datetime(2023, 1, 1, 12, 0, 0),
        "updated_at": datetime(2023, 1, 1, 12, 0, 0),
        "last_analyzed": datetime(2023, 1, 2, 12, 0, 0)
    }
}

# Mock project summary data
fake_project_summaries = {
    "1": {
        "overall_score": 76,
        "category_scores": {
            "SEO": 82,
            "Performance": 70,
            "Accessibility": 65,
            "Best Practices": 85,
            "Security": 78
        },
        "last_analyzed": datetime(2023, 1, 2, 12, 0, 0),
        "trend": "up",
        "recommendations_count": 12
    }
}

# Helper function to check project access
async def check_project_access(project_id: str, current_user: User):
    # Check if project exists
    if project_id not in fake_projects_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "PROJECT_NOT_FOUND",
                "message": f"Project with ID {project_id} not found",
                "details": {}
            }
        )
        
    project = fake_projects_db[project_id]
    
    # Check if user has access to project
    # Admin has access to all projects
    if current_user.role == "admin":
        return project
        
    # Project owner has access
    if project["owner_id"] == current_user.id:
        return project
        
    # In a real app, check for project members/collaborators
    
    # If none of the above, deny access
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "code": "PERMISSION_DENIED",
            "message": "You don't have access to this project",
            "details": {}
        }
    )

# Routes
@router.get("/", response_model=ProjectList)
async def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
) -> Any:
    """
    List all projects for the current user.
    """
    total = db.query(Project).filter(Project.owner_id == current_user.id).count()
    projects = db.query(Project).filter(Project.owner_id == current_user.id).offset(skip).limit(limit).all()
    return ProjectList(total=total, items=projects)

@router.post("/", response_model=ProjectResponse)
async def create_project(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_in: ProjectCreate
) -> Any:
    """
    Create a new project.
    """
    project = Project(
        **project_in.dict(),
        owner_id=current_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int
) -> Any:
    """
    Get a specific project by ID.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int,
    project_in: ProjectUpdate
) -> Any:
    """
    Update a project.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}")
async def delete_project(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int
) -> Any:
    """
    Delete a project.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"status": "success"}

@router.get("/{project_id}/summary", response_model=ProjectSummaryResponse)
async def get_project_summary(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get project summary with latest scores and statistics.
    """
    # Check project access
    await check_project_access(project_id, current_user)
    
    # Get project summary
    if project_id in fake_project_summaries:
        project_summary = fake_project_summaries[project_id]
    else:
        # Create empty summary for projects without analyses
        project_summary = {
            "overall_score": None,
            "category_scores": {},
            "last_analyzed": None,
            "trend": None,
            "recommendations_count": 0
        }
    
    return {
        "status": "success",
        "data": ProjectSummary(**project_summary),
        "meta": None
    } 