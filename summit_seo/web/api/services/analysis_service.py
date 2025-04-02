"""
Analysis service for database operations related to SEO analyses.
"""
from typing import Any, Dict, List, Optional, Tuple
import uuid
import time
from enum import Enum

from .base_service import BaseService
from .project_service import ProjectService

class AnalysisStatus(str, Enum):
    """Analysis status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class SeverityLevel(str, Enum):
    """Severity level enum for findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AnalysisService(BaseService):
    """
    Service for analysis-related database operations.
    """
    
    def __init__(self, use_rls_bypass: bool = False):
        """
        Initialize the analysis service.
        
        Args:
            use_rls_bypass: Whether to use admin client to bypass RLS
        """
        super().__init__("analysis", use_rls_bypass)
        self.project_service = ProjectService(use_rls_bypass)
    
    async def get_analyses_by_project(
        self, 
        project_id: str, 
        page: int = 1,
        page_size: int = 10,
        status: Optional[List[str]] = None,
        order_by: str = "-created_at"
    ) -> Dict[str, Any]:
        """
        Get analyses for a specific project.
        
        Args:
            project_id: UUID of the project
            page: Page number (1-indexed)
            page_size: Number of records per page
            status: List of statuses to filter by
            order_by: Column to order by (prefix with - for descending)
            
        Returns:
            Dictionary with data and pagination information
        """
        client = self.get_client()
        query = client.table(self.table_name).select("*").eq("project_id", project_id)
        
        # Apply status filter if provided
        if status and len(status) > 0:
            query = query.in_("status", status)
        
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
        count_query = client.table(self.table_name).select("count", count="exact").eq("project_id", project_id)
        
        if status and len(status) > 0:
            count_query = count_query.in_("status", status)
                
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
    
    async def create_analysis(
        self, 
        project_id: str,
        tenant_id: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new analysis.
        
        Args:
            project_id: UUID of the project
            tenant_id: UUID of the tenant
            config: Analysis configuration
            
        Returns:
            Created analysis data
        """
        analysis_data = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "tenant_id": tenant_id,
            "status": AnalysisStatus.PENDING.value,
            "config": config or {}
        }
        
        return await self.create(analysis_data)
    
    async def start_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """
        Start an analysis by updating its status and start time.
        
        Args:
            analysis_id: UUID of the analysis
            
        Returns:
            Updated analysis data
        """
        update_data = {
            "status": AnalysisStatus.RUNNING.value,
            "started_at": time.time()
        }
        
        return await self.update(analysis_id, update_data)
    
    async def complete_analysis(
        self, 
        analysis_id: str,
        score: float,
        results: Dict[str, Any],
        statistics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Complete an analysis by updating its status, score, and results.
        
        Args:
            analysis_id: UUID of the analysis
            score: Overall analysis score
            results: Analysis results by category
            statistics: Analysis statistics
            
        Returns:
            Updated analysis data
        """
        # Get the current analysis to update duration
        analysis = await self.get_by_id(analysis_id)
        
        if not analysis:
            raise Exception(f"Analysis with ID {analysis_id} not found")
        
        # Calculate duration
        started_at = analysis.get("started_at")
        duration = time.time() - started_at if started_at else 0
        
        # Extract issue counts from statistics
        issues_count = statistics.get("total_issues", 0)
        critical_issues_count = statistics.get("critical_issues", 0)
        high_issues_count = statistics.get("high_issues", 0)
        medium_issues_count = statistics.get("medium_issues", 0)
        low_issues_count = statistics.get("low_issues", 0)
        
        update_data = {
            "status": AnalysisStatus.COMPLETED.value,
            "score": score,
            "results": results,
            "completed_at": time.time(),
            "duration": duration,
            "issues_count": issues_count,
            "critical_issues_count": critical_issues_count,
            "high_issues_count": high_issues_count,
            "medium_issues_count": medium_issues_count,
            "low_issues_count": low_issues_count
        }
        
        # Update the project score as well
        project_id = analysis.get("project_id")
        if project_id:
            await self.project_service.update_project_score(
                project_id, 
                score,
                issues_count,
                critical_issues_count
            )
        
        return await self.update(analysis_id, update_data)
    
    async def fail_analysis(
        self, 
        analysis_id: str,
        error: str,
        error_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Mark an analysis as failed with error information.
        
        Args:
            analysis_id: UUID of the analysis
            error: Error message
            error_details: Detailed error information
            
        Returns:
            Updated analysis data
        """
        # Get the current analysis to update duration
        analysis = await self.get_by_id(analysis_id)
        
        if not analysis:
            raise Exception(f"Analysis with ID {analysis_id} not found")
        
        # Calculate duration
        started_at = analysis.get("started_at")
        duration = time.time() - started_at if started_at else 0
        
        update_data = {
            "status": AnalysisStatus.FAILED.value,
            "error": error,
            "error_details": error_details or {},
            "completed_at": time.time(),
            "duration": duration
        }
        
        return await self.update(analysis_id, update_data)
    
    async def cancel_analysis(self, analysis_id: str) -> Dict[str, Any]:
        """
        Cancel an analysis.
        
        Args:
            analysis_id: UUID of the analysis
            
        Returns:
            Updated analysis data
        """
        return await self.update(analysis_id, {"status": AnalysisStatus.CANCELLED.value})
    
    async def add_finding(
        self,
        analysis_id: str,
        severity: SeverityLevel,
        category: str,
        message: str,
        location: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        remediation: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a finding to an analysis.
        
        Args:
            analysis_id: UUID of the analysis
            severity: Severity level
            category: Finding category
            message: Finding message
            location: Location in the website
            details: Additional details
            remediation: Remediation steps
            
        Returns:
            Created finding data
        """
        client = self.get_client()
        
        finding_data = {
            "id": str(uuid.uuid4()),
            "analysis_id": analysis_id,
            "severity": severity.value if isinstance(severity, Enum) else severity,
            "category": category,
            "message": message,
            "location": location,
            "details": details or {},
            "remediation": remediation
        }
        
        # Get the tenant_id from the analysis
        analysis = await self.get_by_id(analysis_id)
        if analysis and "tenant_id" in analysis:
            finding_data["tenant_id"] = analysis["tenant_id"]
        
        response = client.table("finding").insert(finding_data).execute()
        
        if not response.data:
            raise Exception(f"Failed to add finding to analysis {analysis_id}")
        
        return response.data[0]
    
    async def add_recommendation(
        self,
        analysis_id: str,
        priority: str,
        type: str,
        title: str,
        description: str,
        implementation: Optional[str] = None,
        resources: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Add a recommendation to an analysis.
        
        Args:
            analysis_id: UUID of the analysis
            priority: Recommendation priority
            type: Recommendation type
            title: Recommendation title
            description: Recommendation description
            implementation: Implementation details
            resources: List of resources
            
        Returns:
            Created recommendation data
        """
        client = self.get_client()
        
        recommendation_data = {
            "id": str(uuid.uuid4()),
            "analysis_id": analysis_id,
            "priority": priority,
            "type": type,
            "title": title,
            "description": description,
            "implementation": implementation,
            "resources": resources or []
        }
        
        # Get the tenant_id from the analysis
        analysis = await self.get_by_id(analysis_id)
        if analysis and "tenant_id" in analysis:
            recommendation_data["tenant_id"] = analysis["tenant_id"]
        
        response = client.table("recommendation").insert(recommendation_data).execute()
        
        if not response.data:
            raise Exception(f"Failed to add recommendation to analysis {analysis_id}")
        
        return response.data[0]
    
    async def get_findings(
        self,
        analysis_id: str,
        severity: Optional[List[str]] = None,
        category: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        Get findings for an analysis.
        
        Args:
            analysis_id: UUID of the analysis
            severity: List of severity levels to filter by
            category: List of categories to filter by
            page: Page number (1-indexed)
            page_size: Number of records per page
            
        Returns:
            Dictionary with data and pagination information
        """
        client = self.get_client()
        query = client.table("finding").select("*").eq("analysis_id", analysis_id)
        
        # Apply severity filter if provided
        if severity and len(severity) > 0:
            query = query.in_("severity", severity)
        
        # Apply category filter if provided
        if category and len(category) > 0:
            query = query.in_("category", category)
        
        # Apply pagination
        start = (page - 1) * page_size
        query = query.range(start, start + page_size - 1)
        
        # Execute query
        response = query.execute()
        
        # Get total count for pagination
        count_query = client.table("finding").select("count", count="exact").eq("analysis_id", analysis_id)
        
        if severity and len(severity) > 0:
            count_query = count_query.in_("severity", severity)
            
        if category and len(category) > 0:
            count_query = count_query.in_("category", category)
                
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
    
    async def get_recommendations(
        self,
        analysis_id: str,
        priority: Optional[List[str]] = None,
        type: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """
        Get recommendations for an analysis.
        
        Args:
            analysis_id: UUID of the analysis
            priority: List of priority levels to filter by
            type: List of recommendation types to filter by
            page: Page number (1-indexed)
            page_size: Number of records per page
            
        Returns:
            Dictionary with data and pagination information
        """
        client = self.get_client()
        query = client.table("recommendation").select("*").eq("analysis_id", analysis_id)
        
        # Apply priority filter if provided
        if priority and len(priority) > 0:
            query = query.in_("priority", priority)
        
        # Apply type filter if provided
        if type and len(type) > 0:
            query = query.in_("type", type)
        
        # Apply pagination
        start = (page - 1) * page_size
        query = query.range(start, start + page_size - 1)
        
        # Execute query
        response = query.execute()
        
        # Get total count for pagination
        count_query = client.table("recommendation").select("count", count="exact").eq("analysis_id", analysis_id)
        
        if priority and len(priority) > 0:
            count_query = count_query.in_("priority", priority)
            
        if type and len(type) > 0:
            count_query = count_query.in_("type", type)
                
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
    
    async def create_analysis_with_llm(
        self, 
        project_id: str, 
        url: str, 
        analyzer_type: str, 
        config: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        enhance_with_llm: bool = True
    ) -> Dict[str, Any]:
        """Create a new analysis with LLM enhancements.
        
        Args:
            project_id: ID of the project
            url: URL to analyze
            analyzer_type: Type of analyzer to use
            config: Optional analyzer configuration
            user_id: Optional user ID (defaults to authenticated user)
            enhance_with_llm: Whether to enhance the analysis with LLM 
            
        Returns:
            Created analysis record
            
        Raises:
            AnalysisServiceError: If analysis creation fails
        """
        # First create a regular analysis
        analysis = await self.create_analysis(
            project_id=project_id,
            url=url,
            analyzer_type=analyzer_type,
            config=config,
            user_id=user_id
        )
        
        # If LLM enhancement is requested, update the config
        if enhance_with_llm:
            if config is None:
                config = {}
            
            # Set the LLM enhancement configuration
            config['enhance_recommendations'] = True
            
            # Update the analysis config
            try:
                analysis = await self.update_analysis(
                    analysis_id=analysis['id'],
                    data={'config': config},
                    user_id=user_id
                )
            except Exception as e:
                logger.error(f"Error updating analysis with LLM config: {str(e)}")
                # Continue with the analysis even if config update fails
        
        return analysis
        
    async def get_summary_with_natural_language(
        self,
        analysis_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get an analysis summary with natural language explanation.
        
        Args:
            analysis_id: ID of the analysis
            user_id: Optional user ID (defaults to authenticated user)
            
        Returns:
            Analysis summary with natural language explanation
            
        Raises:
            AnalysisServiceError: If retrieval fails
        """
        # Get the analysis result
        result = await self.get_analysis_result(analysis_id, user_id)
        
        # If there's no data, return as is
        if not result or 'data' not in result:
            return result
            
        try:
            # Import the explanation service
            from .explanation_service import get_explanation_service
            explanation_service = get_explanation_service()
            
            # Add natural language summary
            result_with_summary = await explanation_service.summarize_analysis_results(result)
            
            return result_with_summary
        except ImportError:
            logger.warning("Explanation service not available, returning standard result")
            return result
        except Exception as e:
            logger.error(f"Error generating natural language summary: {str(e)}")
            return result

# Singleton instance
_analysis_service_instance = None

def get_analysis_service(use_rls_bypass: bool = False) -> AnalysisService:
    """
    Get a singleton instance of the AnalysisService.
    
    Args:
        use_rls_bypass: Whether to use admin client to bypass RLS
        
    Returns:
        AnalysisService instance
    """
    global _analysis_service_instance
    if _analysis_service_instance is None or _analysis_service_instance.use_rls_bypass != use_rls_bypass:
        _analysis_service_instance = AnalysisService(use_rls_bypass)
    return _analysis_service_instance 