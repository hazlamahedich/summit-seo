from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, HttpUrl

class ReportBase(BaseModel):
    project_id: int
    analysis_id: int
    title: str
    description: Optional[str] = None
    format: str = "pdf"  # pdf, html, json
    status: str = "pending"  # pending, generating, completed, failed
    error_message: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class ReportCreate(ReportBase):
    pass

class ReportUpdate(ReportBase):
    project_id: Optional[int] = None
    analysis_id: Optional[int] = None
    title: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class ReportInDBBase(ReportBase):
    id: int
    created_at: datetime
    updated_at: datetime
    generated_at: Optional[datetime] = None
    file_url: Optional[HttpUrl] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None

    class Config:
        orm_mode = True

class Report(ReportInDBBase):
    pass

class ReportResponse(ReportInDBBase):
    pass

class ReportList(BaseModel):
    total: int
    items: List[ReportResponse]

class ReportSummary(BaseModel):
    total_reports: int
    completed_reports: int
    failed_reports: int
    pending_reports: int
    average_generation_time: Optional[float] = None
    last_generated: Optional[datetime] = None
    most_common_format: Optional[str] = None 