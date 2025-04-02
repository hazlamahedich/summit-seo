"""Router for LLM-specific endpoints.

This router provides endpoints for interacting with LLM capabilities,
including enhanced recommendations, explanations, and natural language summaries.
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel

from ..services.llm_service import get_llm_service, LLMServiceError
from ..services.recommendation_enhancer import get_recommendation_enhancer
from ..services.explanation_service import get_explanation_service
from ..core.auth import get_current_user

router = APIRouter(
    prefix="/llm",
    tags=["LLM"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


class ExplainIssueRequest(BaseModel):
    """Request model for explaining an SEO issue."""
    issue: str
    context: Optional[Dict[str, Any]] = None


class ExplainTermRequest(BaseModel):
    """Request model for explaining a technical term."""
    term: str


class EnhanceRecommendationRequest(BaseModel):
    """Request model for enhancing a recommendation."""
    title: str
    description: str
    severity: Optional[str] = "medium"
    priority: Optional[int] = 2
    

class LLMResponse(BaseModel):
    """Generic response model for LLM-generated content."""
    content: str


class ModelInfoResponse(BaseModel):
    """Response model for LLM model information."""
    available_models: Dict[str, List[str]]
    default_model: str
    fallback_models: List[str]


class BatchExplainIssuesRequest(BaseModel):
    """Request model for explaining multiple SEO issues."""
    issues: List[str]


@router.post("/explain/issue", response_model=LLMResponse)
async def explain_issue(
    request: ExplainIssueRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    explanation_service: Any = Depends(get_explanation_service)
):
    """Explain an SEO issue in natural language.
    
    Args:
        request: Issue and optional context
        
    Returns:
        Natural language explanation of the issue
    """
    try:
        explanation = await explanation_service.explain_issue(
            issue=request.issue,
            context=request.context
        )
        return LLMResponse(content=explanation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain/term", response_model=LLMResponse)
async def explain_term(
    request: ExplainTermRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    explanation_service: Any = Depends(get_explanation_service)
):
    """Explain a technical SEO term in simple language.
    
    Args:
        request: Term to explain
        
    Returns:
        Simple explanation of the term
    """
    try:
        explanation = await explanation_service.explain_technical_term(request.term)
        return LLMResponse(content=explanation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enhance/recommendation", response_model=Dict[str, Any])
async def enhance_recommendation(
    request: EnhanceRecommendationRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    recommendation_enhancer: Any = Depends(get_recommendation_enhancer)
):
    """Enhance a recommendation with LLM-generated content.
    
    Args:
        request: Basic recommendation information
        
    Returns:
        Enhanced recommendation with detailed explanation, steps, and impacts
    """
    try:
        from summit_seo.analyzer.recommendation import (
            RecommendationBuilder,
            RecommendationSeverity,
            RecommendationPriority
        )
        
        # Create a basic recommendation
        builder = RecommendationBuilder(request.title, request.description)
        
        # Add severity if provided
        if request.severity:
            builder.with_severity(request.severity)
            
        # Add priority if provided
        if request.priority is not None:
            builder.with_priority(request.priority)
            
        recommendation = builder.build()
        
        # Enhance the recommendation
        enhanced = await recommendation_enhancer.enhance_recommendation(recommendation)
        
        return enhanced.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize/analysis", response_model=Dict[str, Any])
async def summarize_analysis(
    results: Dict[str, Any] = Body(...),
    user: Dict[str, Any] = Depends(get_current_user),
    explanation_service: Any = Depends(get_explanation_service)
):
    """Generate a natural language summary of analysis results.
    
    Args:
        results: Analysis results data
        
    Returns:
        Original results plus natural language summary
    """
    try:
        results_with_summary = await explanation_service.summarize_analysis_results(results)
        return results_with_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain/score", response_model=LLMResponse)
async def explain_score(
    score_components: Dict[str, float] = Body(...),
    user: Dict[str, Any] = Depends(get_current_user),
    explanation_service: Any = Depends(get_explanation_service)
):
    """Generate an explanation of how the SEO score was calculated.
    
    Args:
        score_components: Dictionary of score components and their values
        
    Returns:
        Natural language explanation of the score breakdown
    """
    try:
        explanation = await explanation_service.explain_score_breakdown(score_components)
        return LLMResponse(content=explanation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=ModelInfoResponse)
async def get_available_models(
    user: Dict[str, Any] = Depends(get_current_user),
    llm_service: Any = Depends(get_llm_service)
):
    """Get information about available LLM models.
    
    Returns:
        Information about available models, default model, and fallback models
    """
    try:
        models = llm_service.list_available_models()
        return ModelInfoResponse(
            available_models=models,
            default_model=llm_service.default_model,
            fallback_models=llm_service.fallback_models
        )
    except LLMServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving models: {str(e)}")


@router.post("/explain/issues/batch", response_model=List[str])
async def batch_explain_issues(
    request: BatchExplainIssuesRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    explanation_service: Any = Depends(get_explanation_service)
):
    """Explain multiple SEO issues in natural language in batch.
    
    This endpoint processes multiple issues in a single request for improved efficiency.
    
    Args:
        request: List of issues to explain
        
    Returns:
        List of natural language explanations for each issue
    """
    try:
        explanations = await explanation_service.batch_explain_issues(request.issues)
        return explanations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 