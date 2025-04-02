"""
Tests for the LLM API endpoints.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import json
from fastapi.testclient import TestClient

# Import the app and necessary components
from summit_seo.web.api.app import app
from summit_seo.web.api.services import LLMServiceError

client = TestClient(app)

@pytest.fixture
def mock_llm_service(monkeypatch):
    """Mock the LLM service for testing."""
    mock_service = MagicMock()
    
    # Set up the list_available_models method
    mock_service.list_available_models.return_value = {
        "openai": ["gpt-3.5-turbo", "gpt-4"],
        "anthropic": ["claude-instant-1", "claude-2"],
        "ollama": ["llama3"]
    }
    mock_service.default_model = "gpt-3.5-turbo"
    mock_service.fallback_models = ["claude-instant-1"]
    
    # Set up mocked async methods
    mock_service.get_completion_async = AsyncMock()
    mock_service.get_completion_async.return_value = {
        "choices": [
            {
                "message": {
                    "content": "Mocked LLM response content",
                    "role": "assistant"
                }
            }
        ]
    }
    
    def mock_get_llm_service():
        return mock_service
    
    monkeypatch.setattr(
        "summit_seo.web.api.services.llm_service.get_llm_service",
        mock_get_llm_service
    )
    monkeypatch.setattr(
        "summit_seo.web.api.routers.llm.get_llm_service",
        mock_get_llm_service
    )
    
    return mock_service

@pytest.fixture
def mock_explanation_service(monkeypatch):
    """Mock the explanation service for testing."""
    mock_service = MagicMock()
    
    # Set up the necessary async methods
    mock_service.explain_issue = AsyncMock(return_value="This is an explanation of the SEO issue.")
    mock_service.explain_technical_term = AsyncMock(return_value="This is an explanation of the technical term.")
    mock_service.summarize_analysis_results = AsyncMock(
        return_value={"summary": "Summary of analysis", "original_data": {}}
    )
    mock_service.explain_score_breakdown = AsyncMock(
        return_value="Score breakdown explanation"
    )
    mock_service.batch_explain_issues = AsyncMock(
        return_value=["Explanation 1", "Explanation 2"]
    )
    
    def mock_get_explanation_service():
        return mock_service
    
    monkeypatch.setattr(
        "summit_seo.web.api.routers.llm.get_explanation_service",
        mock_get_explanation_service
    )
    
    return mock_service

@pytest.fixture
def mock_recommendation_enhancer(monkeypatch):
    """Mock the recommendation enhancer service for testing."""
    mock_service = MagicMock()
    
    # Mock the enhance_recommendation method
    enhanced_recommendation = MagicMock()
    enhanced_recommendation.to_dict.return_value = {
        "title": "Enhanced recommendation title",
        "description": "Enhanced description",
        "severity": "high",
        "priority": 1,
        "implementation_steps": ["Step 1", "Step 2"],
        "impact": "High impact on SEO performance"
    }
    
    mock_service.enhance_recommendation = AsyncMock(return_value=enhanced_recommendation)
    
    def mock_get_recommendation_enhancer():
        return mock_service
    
    monkeypatch.setattr(
        "summit_seo.web.api.routers.llm.get_recommendation_enhancer",
        mock_get_recommendation_enhancer
    )
    
    return mock_service

@pytest.mark.usefixtures("mock_supabase", "mock_verify_token", "mock_current_user")
class TestLLMEndpoints:
    """Test cases for the LLM endpoints."""
    
    def test_get_available_models(self, mock_llm_service):
        """Test getting available LLM models."""
        response = client.get(
            "/api/v1/llm/models",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "available_models" in data
        assert "default_model" in data
        assert "fallback_models" in data
        assert data["default_model"] == "gpt-3.5-turbo"
        assert "openai" in data["available_models"]
        assert "gpt-3.5-turbo" in data["available_models"]["openai"]
    
    def test_explain_issue(self, mock_explanation_service):
        """Test explaining an SEO issue."""
        response = client.post(
            "/api/v1/llm/explain/issue",
            headers={"Authorization": "Bearer test-token"},
            json={"issue": "Missing meta descriptions", "context": {"url": "https://example.com"}}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert data["content"] == "This is an explanation of the SEO issue."
        
        # Verify service was called with correct parameters
        mock_explanation_service.explain_issue.assert_called_once_with(
            issue="Missing meta descriptions",
            context={"url": "https://example.com"}
        )
    
    def test_explain_term(self, mock_explanation_service):
        """Test explaining a technical term."""
        response = client.post(
            "/api/v1/llm/explain/term",
            headers={"Authorization": "Bearer test-token"},
            json={"term": "Canonical URL"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert data["content"] == "This is an explanation of the technical term."
        
        # Verify service was called with correct parameters
        mock_explanation_service.explain_technical_term.assert_called_once_with("Canonical URL")
    
    def test_enhance_recommendation(self, mock_recommendation_enhancer):
        """Test enhancing a recommendation."""
        response = client.post(
            "/api/v1/llm/enhance/recommendation",
            headers={"Authorization": "Bearer test-token"},
            json={
                "title": "Add meta descriptions",
                "description": "Add missing meta descriptions to improve SEO",
                "severity": "medium",
                "priority": 2
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Enhanced recommendation title"
        assert data["severity"] == "high"
        assert "implementation_steps" in data
        assert len(data["implementation_steps"]) == 2
    
    def test_summarize_analysis(self, mock_explanation_service):
        """Test summarizing analysis results."""
        response = client.post(
            "/api/v1/llm/summarize/analysis",
            headers={"Authorization": "Bearer test-token"},
            json={"score": 85, "findings": ["Issue 1", "Issue 2"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert data["summary"] == "Summary of analysis"
    
    def test_explain_score(self, mock_explanation_service):
        """Test explaining a score breakdown."""
        response = client.post(
            "/api/v1/llm/explain/score",
            headers={"Authorization": "Bearer test-token"},
            json={"content": 0.8, "technical": 0.7, "security": 0.9}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert data["content"] == "Score breakdown explanation"
    
    def test_batch_explain_issues(self, mock_explanation_service):
        """Test batch explaining of SEO issues."""
        response = client.post(
            "/api/v1/llm/explain/issues/batch",
            headers={"Authorization": "Bearer test-token"},
            json={"issues": ["Missing alt text", "Slow page speed"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0] == "Explanation 1"
        assert data[1] == "Explanation 2"
        
        # Verify service was called with correct parameters
        mock_explanation_service.batch_explain_issues.assert_called_once_with(
            ["Missing alt text", "Slow page speed"]
        )
    
    def test_llm_service_error_handling(self, mock_llm_service):
        """Test error handling when LLM service fails."""
        # Make the service raise an error
        mock_llm_service.list_available_models.side_effect = LLMServiceError("Service unavailable")
        
        response = client.get(
            "/api/v1/llm/models",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Service unavailable" in data["detail"] 