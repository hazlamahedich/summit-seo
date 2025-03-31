from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session

# Import auth components
from .auth import User, get_current_user

# Import project access check
from .projects import check_project_access, fake_projects_db

# Import common models
from ..models.common import PaginatedResponse, StandardResponse

# Import database
from ..core.database import get_db

# Import analysis models
from ..models.analysis import Analysis
from ..models.project import Project

# Import analysis schemas
from ..schemas.analysis import (
    AnalysisCreate,
    AnalysisUpdate,
    AnalysisResponse,
    AnalysisList,
    AnalysisSummary
)

# Router definition
router = APIRouter()

# Pydantic models
class AnalysisCreate(BaseModel):
    analyzers: Optional[List[str]] = None
    depth: int = Field(1, ge=1, le=10, description="Crawl depth")
    max_urls: int = Field(100, ge=1, le=1000, description="Maximum URLs to analyze")
    custom_settings: Optional[Dict[str, Any]] = None

class AnalysisBase(BaseModel):
    id: str
    project_id: str
    status: str
    progress: int = 0
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: int
    analyzers: List[str]
    depth: int
    max_urls: int
    custom_settings: Dict[str, Any] = {}
    
class Analysis(AnalysisBase):
    urls_analyzed: int = 0
    total_urls: int = 0
    overall_score: Optional[int] = None
    
class AnalysisSchedule(BaseModel):
    frequency: Literal["daily", "weekly", "monthly"]
    time: str = Field(..., regex=r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$", description="Time in HH:MM format")
    day_of_week: Optional[int] = Field(None, ge=0, le=6, description="Day of week (0=Monday, 6=Sunday), required for weekly frequency")
    day_of_month: Optional[int] = Field(None, ge=1, le=31, description="Day of month, required for monthly frequency")
    is_active: bool = True

class AnalysisResult(BaseModel):
    overall_score: int
    category_scores: Dict[str, int]
    findings: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    
class AnalyzerResult(BaseModel):
    analyzer: str
    score: int
    findings: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]

class Recommendation(BaseModel):
    id: str
    title: str
    description: str
    priority: str
    impact: str
    effort: str
    url: str
    category: str
    analyzer: str

class AnalysisResponse(StandardResponse[Analysis]):
    data: Analysis
    
class AnalysisListResponse(PaginatedResponse[Analysis]):
    data: List[Analysis]

class AnalysisResultResponse(StandardResponse[AnalysisResult]):
    data: AnalysisResult
    
class AnalyzerResultResponse(StandardResponse[AnalyzerResult]):
    data: AnalyzerResult

class RecommendationsResponse(StandardResponse[List[Recommendation]]):
    data: List[Recommendation]

# Mock analyses database
fake_analyses_db = {
    "1": {
        "id": "1",
        "project_id": "1",
        "status": "completed",
        "progress": 100,
        "created_at": datetime(2023, 1, 2, 10, 0, 0),
        "started_at": datetime(2023, 1, 2, 10, 0, 0),
        "completed_at": datetime(2023, 1, 2, 10, 15, 0),
        "created_by": 1,
        "analyzers": ["seo", "performance", "accessibility", "best-practices", "security"],
        "depth": 2,
        "max_urls": 100,
        "custom_settings": {},
        "urls_analyzed": 35,
        "total_urls": 35,
        "overall_score": 76
    }
}

# Mock analysis results
fake_analysis_results = {
    "1": {
        "overall_score": 76,
        "category_scores": {
            "SEO": 82,
            "Performance": 70,
            "Accessibility": 65,
            "Best Practices": 85,
            "Security": 78
        },
        "findings": [
            {
                "id": "f1",
                "title": "Missing meta description",
                "description": "5 pages are missing meta descriptions",
                "severity": "medium",
                "category": "SEO",
                "analyzer": "seo",
                "affected_urls": ["https://example.com/page1", "https://example.com/page2"]
            },
            {
                "id": "f2",
                "title": "Images missing alt text",
                "description": "10 images are missing alt text",
                "severity": "high",
                "category": "Accessibility",
                "analyzer": "accessibility",
                "affected_urls": ["https://example.com/page3", "https://example.com/page4"]
            }
        ],
        "recommendations": [
            {
                "id": "r1",
                "title": "Add meta descriptions",
                "description": "Add descriptive meta descriptions to all pages",
                "priority": "high",
                "impact": "medium",
                "effort": "low",
                "url": "https://example.com/page1",
                "category": "SEO",
                "analyzer": "seo"
            },
            {
                "id": "r2",
                "title": "Add alt text to images",
                "description": "Add descriptive alt text to all images",
                "priority": "high",
                "impact": "high",
                "effort": "medium",
                "url": "https://example.com/page3",
                "category": "Accessibility",
                "analyzer": "accessibility"
            }
        ]
    }
}

# Mock analyzer results
fake_analyzer_results = {
    "1": {
        "seo": {
            "analyzer": "seo",
            "score": 82,
            "findings": [
                {
                    "id": "f1",
                    "title": "Missing meta description",
                    "description": "5 pages are missing meta descriptions",
                    "severity": "medium",
                    "category": "SEO",
                    "analyzer": "seo",
                    "affected_urls": ["https://example.com/page1", "https://example.com/page2"]
                }
            ],
            "recommendations": [
                {
                    "id": "r1",
                    "title": "Add meta descriptions",
                    "description": "Add descriptive meta descriptions to all pages",
                    "priority": "high",
                    "impact": "medium",
                    "effort": "low",
                    "url": "https://example.com/page1",
                    "category": "SEO",
                    "analyzer": "seo"
                }
            ]
        },
        "accessibility": {
            "analyzer": "accessibility",
            "score": 65,
            "findings": [
                {
                    "id": "f2",
                    "title": "Images missing alt text",
                    "description": "10 images are missing alt text",
                    "severity": "high",
                    "category": "Accessibility",
                    "analyzer": "accessibility",
                    "affected_urls": ["https://example.com/page3", "https://example.com/page4"]
                }
            ],
            "recommendations": [
                {
                    "id": "r2",
                    "title": "Add alt text to images",
                    "description": "Add descriptive alt text to all images",
                    "priority": "high",
                    "impact": "high",
                    "effort": "medium",
                    "url": "https://example.com/page3",
                    "category": "Accessibility",
                    "analyzer": "accessibility"
                }
            ]
        }
    }
}

# Helper function to check analysis access
async def check_analysis_access(project_id: str, analysis_id: str, current_user: User):
    # Check project access first
    await check_project_access(project_id, current_user)
    
    # Check if analysis exists
    if analysis_id not in fake_analyses_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "ANALYSIS_NOT_FOUND",
                "message": f"Analysis with ID {analysis_id} not found",
                "details": {}
            }
        )
        
    analysis = fake_analyses_db[analysis_id]
    
    # Check if analysis belongs to the project
    if analysis["project_id"] != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "ANALYSIS_NOT_FOUND",
                "message": f"Analysis with ID {analysis_id} not found in project {project_id}",
                "details": {}
            }
        )
        
    return analysis

# Routes
@router.get("/", response_model=AnalysisList)
async def list_analyses(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
) -> Any:
    """
    List all analyses for a specific project.
    """
    # Check project access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    total = db.query(Analysis).filter(Analysis.project_id == project_id).count()
    analyses = db.query(Analysis).filter(Analysis.project_id == project_id).offset(skip).limit(limit).all()
    return AnalysisList(total=total, items=analyses)

@router.post("/", response_model=AnalysisResponse)
async def create_analysis(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int,
    analysis_in: AnalysisCreate,
    background_tasks: BackgroundTasks
) -> Any:
    """
    Create a new analysis for a project.
    """
    # Check project access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    analysis = Analysis(
        **analysis_in.dict(),
        project_id=project_id
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    # Start analysis in background
    background_tasks.add_task(start_analysis, analysis.id)
    
    return analysis

@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int,
    analysis_id: int
) -> Any:
    """
    Get a specific analysis by ID.
    """
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.project_id == project_id
    ).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Check project access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return analysis

@router.get("/{analysis_id}/summary", response_model=AnalysisSummary)
async def get_analysis_summary(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int,
    analysis_id: int
) -> Any:
    """
    Get a summary of the analysis results.
    """
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.project_id == project_id
    ).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Check project access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Calculate summary statistics
    # This is a placeholder - implement actual calculation logic
    summary = AnalysisSummary(
        total_pages=0,
        analyzed_pages=0,
        total_findings=0,
        critical_findings=0,
        high_findings=0,
        medium_findings=0,
        low_findings=0,
        average_score=0.0,
        completion_percentage=0.0
    )
    
    return summary

async def start_analysis(analysis_id: int):
    """
    Background task to start the analysis process.
    """
    # This is a placeholder - implement actual analysis logic
    pass 