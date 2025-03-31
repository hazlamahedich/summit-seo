"""
Project and analysis models.
"""
import enum
from typing import Dict, Any, List
from sqlalchemy import Column, String, ForeignKey, Integer, Float, JSON, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .base import TenantModel


class AnalysisStatus(enum.Enum):
    """Analysis status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Project(TenantModel):
    """Project model for organizing website analyses."""
    
    # Basic project information
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(512), nullable=False)
    
    # Project configuration
    settings = Column(JSONB, nullable=True, default={})
    
    # Tags for organization
    tags = Column(JSONB, nullable=True, default=[])
    
    # Favicon or project icon
    icon_url = Column(String(255), nullable=True)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="project", cascade="all, delete-orphan")
    
    # Metrics and statistics calculated from analyses
    last_score = Column(Float, nullable=True)
    score_change = Column(Float, nullable=True)
    issues_count = Column(Integer, nullable=True, default=0)
    critical_issues_count = Column(Integer, nullable=True, default=0)
    
    __table_args__ = (
        # Additional table arguments can be added here
    )


class Analysis(TenantModel):
    """Analysis model for storing SEO analysis results."""
    
    # Status of this analysis
    status = Column(Enum(AnalysisStatus), nullable=False, default=AnalysisStatus.PENDING)
    
    # Project relationship
    project_id = Column(UUID(as_uuid=True), ForeignKey('project.id'), nullable=False)
    project = relationship("Project", back_populates="analyses")
    
    # Analysis configuration used for this run
    config = Column(JSONB, nullable=True)
    
    # Overall score (0-100)
    score = Column(Float, nullable=True)
    
    # Analysis results by category
    results = Column(JSONB, nullable=True)
    
    # Timestamps
    started_at = Column(Float, nullable=True)  # Unix timestamp
    completed_at = Column(Float, nullable=True)  # Unix timestamp
    
    # Duration in seconds
    duration = Column(Float, nullable=True)
    
    # Error information if analysis failed
    error = Column(Text, nullable=True)
    error_details = Column(JSONB, nullable=True)
    
    # Analyzer versions used for this analysis
    analyzer_versions = Column(JSONB, nullable=True)
    
    # Relationships
    findings = relationship("Finding", back_populates="analysis", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="analysis", cascade="all, delete-orphan")
    
    # Statistics
    issues_count = Column(Integer, nullable=True, default=0)
    critical_issues_count = Column(Integer, nullable=True, default=0)
    high_issues_count = Column(Integer, nullable=True, default=0)
    medium_issues_count = Column(Integer, nullable=True, default=0)
    low_issues_count = Column(Integer, nullable=True, default=0)


class SeverityLevel(enum.Enum):
    """Severity level enum for findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Finding(TenantModel):
    """Model for individual findings from an analysis."""
    
    # Analysis relationship
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analysis.id'), nullable=False)
    analysis = relationship("Analysis", back_populates="findings")
    
    # Finding details
    analyzer = Column(String(100), nullable=False)  # The analyzer that generated this finding
    category = Column(String(100), nullable=False)  # Category of the finding (e.g., "security", "performance")
    rule_id = Column(String(100), nullable=False)  # Unique identifier for the rule that was checked
    
    # Finding information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(Enum(SeverityLevel), nullable=False)
    
    # Locations in the code/site where the finding was detected
    locations = Column(JSONB, nullable=True)
    
    # Additional data specific to this finding
    metadata = Column(JSONB, nullable=True)
    
    # Recommendations for fixing this issue
    recommendations = relationship("Recommendation", back_populates="finding", cascade="all, delete-orphan")


class RecommendationType(enum.Enum):
    """Recommendation type enum."""
    BEST_PRACTICE = "best_practice"
    QUICK_WIN = "quick_win"
    TECHNICAL = "technical"
    CONTENT = "content"
    SECURITY = "security"
    PERFORMANCE = "performance"


class RecommendationPriority(enum.Enum):
    """Recommendation priority enum."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Recommendation(TenantModel):
    """Model for recommendations to improve SEO."""
    
    # Analysis relationship
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analysis.id'), nullable=False)
    analysis = relationship("Analysis", back_populates="recommendations")
    
    # Finding relationship (optional - some recommendations might not be tied to a specific finding)
    finding_id = Column(UUID(as_uuid=True), ForeignKey('finding.id'), nullable=True)
    finding = relationship("Finding", back_populates="recommendations")
    
    # Recommendation details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Implementation difficulty (1-10, 10 being most difficult)
    difficulty = Column(Integer, nullable=True)
    
    # Expected impact (1-10, 10 being highest impact)
    impact = Column(Integer, nullable=True)
    
    # Priority (calculated from difficulty and impact)
    priority = Column(Enum(RecommendationPriority), nullable=False)
    
    # Type of recommendation
    type = Column(Enum(RecommendationType), nullable=False)
    
    # Implementation instructions
    implementation = Column(Text, nullable=True)
    
    # Code snippets or examples
    code_examples = Column(JSONB, nullable=True)
    
    # Resources and references
    resources = Column(JSONB, nullable=True)
    
    # Estimated implementation time (in minutes)
    estimated_time = Column(Integer, nullable=True) 