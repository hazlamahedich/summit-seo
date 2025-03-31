from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class AnalysisBase(BaseModel):
    project_id: int
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class AnalysisCreate(AnalysisBase):
    pass

class AnalysisUpdate(AnalysisBase):
    project_id: Optional[int] = None
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

class AnalysisInDBBase(AnalysisBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Analysis(AnalysisInDBBase):
    pass

class AnalysisResponse(AnalysisInDBBase):
    pass

class AnalysisList(BaseModel):
    total: int
    items: List[AnalysisResponse]

class AnalysisSummary(BaseModel):
    total_pages: int
    analyzed_pages: int
    total_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    average_score: float
    completion_percentage: float 