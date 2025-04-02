from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, BackgroundTasks
from pydantic import BaseModel, Field, UUID4
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, timedelta
import uuid
from enum import Enum

# Import auth components
from ..core.deps import get_current_user, get_project_service, get_analysis_service

# Import common models
from ..models.common import PaginatedResponse, StandardResponse

# Import services
from ..services.analysis_service import AnalysisStatus, SeverityLevel

# Router definition
router = APIRouter()

# Pydantic models for requests and responses
class AnalysisCreateRequest(BaseModel):
    """Request model for creating an analysis"""
    analyzers: Optional[List[str]] = None
    depth: int = Field(1, ge=1, le=10, description="Crawl depth")
    max_urls: int = Field(100, ge=1, le=1000, description="Maximum URLs to analyze")
    custom_settings: Optional[Dict[str, Any]] = None

class AnalysisUpdateRequest(BaseModel):
    """Request model for updating an analysis"""
    status: Optional[str] = None
    analyzers: Optional[List[str]] = None
    depth: Optional[int] = Field(None, ge=1, le=10)
    max_urls: Optional[int] = Field(None, ge=1, le=1000)
    custom_settings: Optional[Dict[str, Any]] = None

class FindingResponse(BaseModel):
    """Response model for findings"""
    id: str
    analysis_id: str
    tenant_id: str
    severity: str
    category: str
    message: str
    location: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    remediation: Optional[str] = None
    created_at: datetime

class RecommendationResponse(BaseModel):
    """Response model for recommendations"""
    id: str
    analysis_id: str
    tenant_id: str
    priority: str
    type: str
    title: str
    description: str
    implementation: Optional[str] = None
    resources: Optional[List[Dict[str, str]]] = None
    created_at: datetime

class AnalysisResponseModel(BaseModel):
    """Response model for analysis"""
    id: str
    tenant_id: str
    project_id: str
    status: str
    config: Dict[str, Any]
    score: Optional[float] = None
    results: Optional[Dict[str, Any]] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    duration: Optional[float] = None
    error: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    analyzer_versions: Optional[Dict[str, str]] = None
    issues_count: Optional[int] = None
    critical_issues_count: Optional[int] = None
    high_issues_count: Optional[int] = None
    medium_issues_count: Optional[int] = None
    low_issues_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime

class AnalysisListItem(BaseModel):
    """Item in analysis list"""
    id: str
    tenant_id: str
    project_id: str
    status: str
    score: Optional[float] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    duration: Optional[float] = None
    issues_count: Optional[int] = None
    critical_issues_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime

class AnalysisListResponseModel(BaseModel):
    """Response model for analysis listing"""
    data: List[AnalysisListItem]
    pagination: Dict[str, Any]

class AnalysisSummaryModel(BaseModel):
    """Model for analysis summary"""
    total_pages: int = 0
    analyzed_pages: int = 0
    total_findings: int = 0
    critical_findings: int = 0
    high_findings: int = 0
    medium_findings: int = 0
    low_findings: int = 0
    average_score: float = 0.0
    completion_percentage: float = 0.0

class AnalysisSummaryResponse(StandardResponse):
    """Response model for analysis summary"""
    data: AnalysisSummaryModel

class FindingsListResponseModel(BaseModel):
    """Response model for findings listing"""
    data: List[FindingResponse]
    pagination: Dict[str, Any]

class RecommendationsListResponseModel(BaseModel):
    """Response model for recommendations listing"""
    data: List[RecommendationResponse]
    pagination: Dict[str, Any]

# Routes
@router.get("/", response_model=AnalysisListResponseModel)
async def list_analyses(
    project_id: str = Path(..., description="Project ID"),
    status: Optional[List[str]] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    order_by: str = Query("-created_at", description="Order by field"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    List all analyses for a specific project.
    
    Filters:
    - status: Filter by analysis status (pending, running, completed, failed, cancelled)
    
    Pagination:
    - page: Page number (1-indexed)
    - page_size: Number of items per page
    
    Sorting:
    - order_by: Field to sort by (prefix with - for descending)
    """
    # Get user ID for filtering
    user_id = current_user.get("id")
    
    # Get services
    project_service = get_project_service()
    analysis_service = get_analysis_service()
    
    # Verify access to project first
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
    
    # Get analyses for project
    result = await analysis_service.get_analyses_by_project(
        project_id=project_id,
        page=page,
        page_size=page_size,
        status=status,
        order_by=order_by
    )
    
    return result

@router.post("/", response_model=AnalysisResponseModel)
async def create_analysis(
    analysis_in: AnalysisCreateRequest,
    project_id: str = Path(..., description="Project ID"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """
    Create a new analysis for a project.
    """
    # Get user ID for access check
    user_id = current_user.get("id")
    
    # Get services
    project_service = get_project_service()
    analysis_service = get_analysis_service()
    
    # Verify access to project first
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
    
    # Prepare analysis configuration
    config = {
        "analyzers": analysis_in.analyzers,
        "depth": analysis_in.depth,
        "max_urls": analysis_in.max_urls,
    }
    
    if analysis_in.custom_settings:
        config["custom_settings"] = analysis_in.custom_settings
    
    # Create analysis
    analysis = await analysis_service.create_analysis(
        project_id=project_id,
        tenant_id=project["tenant_id"],
        config=config
    )
    
    # Start analysis in background
    background_tasks.add_task(start_analysis, analysis["id"], analysis_service)
    
    return analysis

@router.get("/{analysis_id}", response_model=AnalysisResponseModel)
async def get_analysis(
    analysis_id: str,
    project_id: str = Path(..., description="Project ID"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get a specific analysis by ID.
    """
    # Get user ID for access check
    user_id = current_user.get("id")
    
    # Get services
    project_service = get_project_service()
    analysis_service = get_analysis_service()
    
    # Verify access to project first
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
    
    # Get analysis
    analysis = await analysis_service.get_by_id(analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "ANALYSIS_NOT_FOUND",
                "message": f"Analysis with ID {analysis_id} not found",
                "details": {}
            }
        )
    
    # Verify analysis belongs to project
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

@router.get("/{analysis_id}/summary", response_model=AnalysisSummaryResponse)
async def get_analysis_summary(
    analysis_id: str,
    project_id: str = Path(..., description="Project ID"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get a summary of the analysis results.
    """
    # Get user ID for access check
    user_id = current_user.get("id")
    
    # Get services
    project_service = get_project_service()
    analysis_service = get_analysis_service()
    
    # Verify access to project first
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
    
    # Get analysis
    analysis = await analysis_service.get_by_id(analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "ANALYSIS_NOT_FOUND",
                "message": f"Analysis with ID {analysis_id} not found",
                "details": {}
            }
        )
    
    # Verify analysis belongs to project
    if analysis["project_id"] != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "ANALYSIS_NOT_FOUND",
                "message": f"Analysis with ID {analysis_id} not found in project {project_id}",
                "details": {}
            }
        )
    
    # Calculate summary statistics
    # This is a placeholder - in a real implementation, you would extract this from the analysis results
    completion_percentage = 0.0
    if analysis["status"] == AnalysisStatus.COMPLETED.value:
        completion_percentage = 100.0
    elif analysis["status"] == AnalysisStatus.RUNNING.value and analysis.get("started_at"):
        # Estimate completion based on time elapsed
        # This is just a simple example - real implementation would be more sophisticated
        started_time = analysis["started_at"]
        elapsed = datetime.utcnow().timestamp() - started_time
        # Assume a typical analysis takes 2 minutes
        completion_percentage = min(95.0, (elapsed / 120.0) * 100.0)
    
    summary = AnalysisSummaryModel(
        total_pages=analysis.get("config", {}).get("max_urls", 0),
        analyzed_pages=analysis.get("issues_count", 0),  # This is a proxy, not accurate
        total_findings=analysis.get("issues_count", 0),
        critical_findings=analysis.get("critical_issues_count", 0),
        high_findings=analysis.get("high_issues_count", 0),
        medium_findings=analysis.get("medium_issues_count", 0),
        low_findings=analysis.get("low_issues_count", 0),
        average_score=analysis.get("score", 0.0),
        completion_percentage=completion_percentage
    )
    
    return {
        "status": "success",
        "data": summary
    }

@router.get("/{analysis_id}/findings", response_model=FindingsListResponseModel)
async def get_analysis_findings(
    analysis_id: str,
    project_id: str = Path(..., description="Project ID"),
    severity: Optional[List[str]] = Query(None, description="Filter by severity"),
    category: Optional[List[str]] = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get findings for an analysis.
    
    Filters:
    - severity: Filter by severity level (critical, high, medium, low, info)
    - category: Filter by finding category
    
    Pagination:
    - page: Page number (1-indexed)
    - page_size: Number of items per page
    """
    # Get user ID for access check
    user_id = current_user.get("id")
    
    # Get services
    project_service = get_project_service()
    analysis_service = get_analysis_service()
    
    # Verify access to project first
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
    
    # Get analysis
    analysis = await analysis_service.get_by_id(analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "ANALYSIS_NOT_FOUND",
                "message": f"Analysis with ID {analysis_id} not found",
                "details": {}
            }
        )
    
    # Verify analysis belongs to project
    if analysis["project_id"] != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "ANALYSIS_NOT_FOUND",
                "message": f"Analysis with ID {analysis_id} not found in project {project_id}",
                "details": {}
            }
        )
    
    # Get findings
    findings = await analysis_service.get_findings(
        analysis_id=analysis_id,
        severity=severity,
        category=category,
        page=page,
        page_size=page_size
    )
    
    return findings

@router.get("/{analysis_id}/recommendations", response_model=RecommendationsListResponseModel)
async def get_analysis_recommendations(
    analysis_id: str,
    project_id: str = Path(..., description="Project ID"),
    priority: Optional[List[str]] = Query(None, description="Filter by priority"),
    type: Optional[List[str]] = Query(None, description="Filter by type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get recommendations for an analysis.
    
    Filters:
    - priority: Filter by priority level
    - type: Filter by recommendation type
    
    Pagination:
    - page: Page number (1-indexed)
    - page_size: Number of items per page
    """
    # Get user ID for access check
    user_id = current_user.get("id")
    
    # Get services
    project_service = get_project_service()
    analysis_service = get_analysis_service()
    
    # Verify access to project first
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
    
    # Get analysis
    analysis = await analysis_service.get_by_id(analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "ANALYSIS_NOT_FOUND",
                "message": f"Analysis with ID {analysis_id} not found",
                "details": {}
            }
        )
    
    # Verify analysis belongs to project
    if analysis["project_id"] != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "ANALYSIS_NOT_FOUND",
                "message": f"Analysis with ID {analysis_id} not found in project {project_id}",
                "details": {}
            }
        )
    
    # Get recommendations
    recommendations = await analysis_service.get_recommendations(
        analysis_id=analysis_id,
        priority=priority,
        type=type,
        page=page,
        page_size=page_size
    )
    
    return recommendations

@router.post("/{analysis_id}/cancel")
async def cancel_analysis(
    analysis_id: str,
    project_id: str = Path(..., description="Project ID"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Cancel an analysis in progress.
    """
    # Get user ID for access check
    user_id = current_user.get("id")
    
    # Get services
    project_service = get_project_service()
    analysis_service = get_analysis_service()
    
    # Verify access to project first
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
    
    # Get analysis
    analysis = await analysis_service.get_by_id(analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "ANALYSIS_NOT_FOUND",
                "message": f"Analysis with ID {analysis_id} not found",
                "details": {}
            }
        )
    
    # Verify analysis belongs to project
    if analysis["project_id"] != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "ANALYSIS_NOT_FOUND",
                "message": f"Analysis with ID {analysis_id} not found in project {project_id}",
                "details": {}
            }
        )
    
    # Check if analysis can be cancelled
    if analysis["status"] not in [AnalysisStatus.PENDING.value, AnalysisStatus.RUNNING.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_OPERATION",
                "message": f"Cannot cancel analysis with status {analysis['status']}",
                "details": {}
            }
        )
    
    # Cancel analysis
    await analysis_service.cancel_analysis(analysis_id)
    
    return {
        "status": "success",
        "message": "Analysis cancelled successfully"
    }

# Background task for starting analysis
async def start_analysis(analysis_id: str, analysis_service):
    """Start an analysis in the background."""
    try:
        # Update analysis status to running
        await analysis_service.start_analysis(analysis_id)
        
        # In a real implementation, you would:
        # 1. Run the actual analysis
        # 2. Update the analysis with results
        # 3. Create findings and recommendations
        # 4. Update the status to completed
        
        # For now, just simulate a delay and then complete it
        # In a real implementation, this would be a more complex process
        # and would likely involve a task queue or worker service
        
        # Simulate analysis - this would be replaced with actual analysis logic
        # Ideally, start_analysis would be called by a separate worker process
        # or a task queue system like Celery or RQ
        
        # For demo purposes, we're using a fake completion after a delay
        # This is not how a real implementation would work
        # In a real system, this would be handled by a background worker
        import asyncio
        await asyncio.sleep(5)
        
        # Complete analysis with fake results
        await analysis_service.complete_analysis(
            analysis_id=analysis_id,
            score=85.5,
            results={
                "seo": {"score": 90},
                "performance": {"score": 85},
                "accessibility": {"score": 82},
                "security": {"score": 88}
            },
            statistics={
                "total_issues": 12,
                "critical_issues": 1,
                "high_issues": 3,
                "medium_issues": 5,
                "low_issues": 3
            }
        )
        
        # Add some sample findings and recommendations
        # In a real implementation, these would be generated based on actual analysis
        
        # Sample finding
        await analysis_service.add_finding(
            analysis_id=analysis_id,
            severity=SeverityLevel.HIGH,
            category="security",
            message="Missing HTTPS implementation",
            location="https://example.com",
            details={"pages_affected": 1},
            remediation="Implement HTTPS for all pages"
        )
        
        # Sample recommendation
        await analysis_service.add_recommendation(
            analysis_id=analysis_id,
            priority="high",
            type="security",
            title="Implement HTTPS",
            description="The website should use HTTPS to secure user connections",
            implementation="Configure SSL certificates and redirect HTTP to HTTPS",
            resources=[{"title": "SSL Guide", "url": "https://example.com/ssl-guide"}]
        )
    
    except Exception as e:
        # Log the error
        print(f"Error starting analysis {analysis_id}: {e}")
        
        # Update analysis status to failed
        try:
            await analysis_service.fail_analysis(
                analysis_id=analysis_id,
                error=str(e),
                error_details={"traceback": str(e)}
            )
        except Exception as update_error:
            # Log the error if we can't update the analysis
            print(f"Error updating analysis {analysis_id} status: {update_error}")

@router.post("/{project_id}/analyses/enhanced", response_model=Dict[str, Any])
async def create_enhanced_analysis(
    project_id: str,
    data: AnalysisCreate,
    user: Dict[str, Any] = Depends(get_current_user),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """Create a new analysis with LLM enhancements.
    
    Args:
        project_id: ID of the project
        data: Analysis creation data
        
    Returns:
        Created analysis record
    """
    try:
        analysis = await analysis_service.create_analysis_with_llm(
            project_id=project_id,
            url=data.url,
            analyzer_type=data.analyzer_type,
            config=data.config,
            user_id=user.get("id"),
            enhance_with_llm=True
        )
        return analysis
    except AnalysisServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create enhanced analysis: {str(e)}")

@router.get("/{project_id}/analyses/{analysis_id}/summary/natural-language", response_model=Dict[str, Any])
async def get_analysis_summary_with_natural_language(
    project_id: str,
    analysis_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """Get an analysis summary with natural language explanation.
    
    Args:
        project_id: ID of the project
        analysis_id: ID of the analysis
        
    Returns:
        Analysis summary with natural language explanation
    """
    try:
        # Verify the analysis belongs to the project
        await analysis_service.verify_analysis_ownership(
            analysis_id=analysis_id,
            project_id=project_id,
            user_id=user.get("id")
        )
        
        # Get the summary with natural language
        summary = await analysis_service.get_summary_with_natural_language(
            analysis_id=analysis_id,
            user_id=user.get("id")
        )
        return summary
    except AnalysisServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get analysis summary with natural language: {str(e)}"
        ) 