from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

# Import auth components
from .auth import User, get_current_user

# Import project access check
from .projects import check_project_access

# Import database
from ..core.database import get_db

# Import models
from ..models.report import Report
from ..models.project import Project
from ..models.analysis import Analysis

# Import schemas
from ..schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportList,
    ReportSummary
)

# Router definition
router = APIRouter()

# Helper function to check report access
async def check_report_access(project_id: int, report_id: int, current_user: User, db: Session):
    # Check project access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if report exists and belongs to project
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.project_id == project_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report

# Routes
@router.get("/", response_model=ReportList)
async def list_reports(
    project_id: int,
    analysis_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
) -> Any:
    """
    List all reports for a specific project and optionally filtered by analysis.
    """
    # Check project access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Build query
    query = db.query(Report).filter(Report.project_id == project_id)
    if analysis_id:
        query = query.filter(Report.analysis_id == analysis_id)
    
    total = query.count()
    reports = query.offset(skip).limit(limit).all()
    
    return ReportList(total=total, items=reports)

@router.post("/", response_model=ReportResponse)
async def create_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int,
    report_in: ReportCreate,
    background_tasks: BackgroundTasks
) -> Any:
    """
    Create a new report for a project.
    """
    # Check project access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if analysis exists
    analysis = db.query(Analysis).filter(
        Analysis.id == report_in.analysis_id,
        Analysis.project_id == project_id
    ).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    report = Report(
        **report_in.dict(),
        project_id=project_id
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # Start report generation in background
    background_tasks.add_task(generate_report, report.id)
    
    return report

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int,
    report_id: int
) -> Any:
    """
    Get a specific report by ID.
    """
    report = await check_report_access(project_id, report_id, current_user, db)
    return report

@router.get("/{report_id}/download")
async def download_report(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int,
    report_id: int
) -> Any:
    """
    Download a generated report file.
    """
    report = await check_report_access(project_id, report_id, current_user, db)
    
    if report.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Report is not ready for download"
        )
    
    if not report.file_url:
        raise HTTPException(
            status_code=404,
            detail="Report file not found"
        )
    
    # In a real implementation, you would:
    # 1. Generate a signed URL for the file
    # 2. Track the download
    # 3. Handle different file types appropriately
    
    return {
        "download_url": str(report.file_url),
        "file_type": report.file_type,
        "file_size": report.file_size
    }

@router.get("/summary", response_model=ReportSummary)
async def get_reports_summary(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get a summary of reports for a project.
    """
    # Check project access
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.owner_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get report statistics
    reports = db.query(Report).filter(Report.project_id == project_id).all()
    
    completed_reports = [r for r in reports if r.status == "completed"]
    failed_reports = [r for r in reports if r.status == "failed"]
    pending_reports = [r for r in reports if r.status in ["pending", "generating"]]
    
    # Calculate average generation time
    generation_times = []
    for report in completed_reports:
        if report.generated_at and report.created_at:
            generation_time = (report.generated_at - report.created_at).total_seconds()
            generation_times.append(generation_time)
    
    average_generation_time = sum(generation_times) / len(generation_times) if generation_times else None
    
    # Get most common format
    formats = [r.format for r in reports]
    most_common_format = max(set(formats), key=formats.count) if formats else None
    
    # Get last generated report
    last_generated = max(
        (r.generated_at for r in completed_reports),
        default=None
    )
    
    return ReportSummary(
        total_reports=len(reports),
        completed_reports=len(completed_reports),
        failed_reports=len(failed_reports),
        pending_reports=len(pending_reports),
        average_generation_time=average_generation_time,
        last_generated=last_generated,
        most_common_format=most_common_format
    )

async def generate_report(report_id: int):
    """
    Background task to generate the report.
    """
    # This is a placeholder - implement actual report generation logic
    # 1. Fetch analysis data
    # 2. Generate report in requested format
    # 3. Upload to storage
    # 4. Update report status and file details
    pass 