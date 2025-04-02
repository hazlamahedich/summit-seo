"""
Tests for the Projects API endpoints.
"""
import pytest
import uuid
from unittest.mock import MagicMock, AsyncMock, patch
import json
from fastapi.testclient import TestClient

from summit_seo.web.api.app import app

client = TestClient(app)

@pytest.fixture
def test_project_data():
    """Test project data."""
    return {
        "id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "name": "Test Project",
        "url": "https://example.com",
        "description": "Test project description",
        "created_at": "2023-01-01T00:00:00.000Z",
        "updated_at": "2023-01-01T00:00:00.000Z",
        "tags": ["test", "example"],
        "settings": {"analyzer_config": {"example": True}},
        "last_score": 85.5,
        "score_change": 2.5,
        "issues_count": 10,
        "critical_issues_count": 2,
        "icon_url": "https://example.com/icon.png",
        "is_active": True
    }

@pytest.fixture
def mock_project_service(monkeypatch, test_project_data):
    """Mock the project service for testing."""
    mock_service = MagicMock()
    
    # Setup common return values
    mock_service.get_projects_by_tenant = AsyncMock(
        return_value={
            "data": [test_project_data],
            "pagination": {
                "total": 1,
                "page": 1,
                "page_size": 10,
                "pages": 1
            }
        }
    )
    
    mock_service.get_project_with_access_check = AsyncMock(return_value=test_project_data)
    mock_service.create_project = AsyncMock(return_value=test_project_data)
    mock_service.update = AsyncMock(return_value=test_project_data)
    mock_service.get_by_id = AsyncMock(return_value=test_project_data)
    mock_service.delete = AsyncMock(return_value=True)
    mock_service.update_project_tags = AsyncMock(return_value=test_project_data)
    mock_service.update_project_settings = AsyncMock(return_value=test_project_data)
    
    def mock_get_project_service():
        return mock_service
    
    # Apply the mock
    monkeypatch.setattr(
        "summit_seo.web.api.routers.projects.get_project_service",
        mock_get_project_service
    )
    
    return mock_service

@pytest.mark.usefixtures("mock_supabase", "mock_verify_token", "mock_current_user")
class TestProjectsEndpoints:
    """Test cases for the Projects endpoints."""
    
    def test_list_projects(self, mock_project_service, test_project_data):
        """Test listing all projects."""
        response = client.get(
            "/api/v1/projects",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert len(data["data"]) == 1
        assert data["data"][0]["id"] == test_project_data["id"]
        
        # Verify service was called with correct parameters
        mock_project_service.get_projects_by_tenant.assert_awaited_once()
        
    def test_create_project(self, mock_project_service, test_project_data):
        """Test creating a new project."""
        project_data = {
            "name": "New Project",
            "url": "https://newproject.com",
            "description": "A brand new project",
            "tags": ["new", "project"],
            "settings": {"analyzer_config": {"new": True}}
        }
        
        response = client.post(
            "/api/v1/projects",
            headers={"Authorization": "Bearer test-token"},
            json=project_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == test_project_data["name"]  # Using the mock's return value
        
        # Verify service was called
        mock_project_service.create_project.assert_awaited_once()
        
    def test_get_project(self, mock_project_service, test_project_data):
        """Test getting a specific project."""
        response = client.get(
            f"/api/v1/projects/{test_project_data['id']}",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_project_data["id"]
        assert data["name"] == test_project_data["name"]
        
        # Verify service was called with correct parameters
        mock_project_service.get_project_with_access_check.assert_awaited_once_with(
            project_id=test_project_data["id"],
            user_id=pytest.match_param_dict["user_id"]
        )
        
    def test_get_project_not_found(self, mock_project_service):
        """Test getting a non-existent project."""
        # Make the service return None (not found)
        mock_project_service.get_project_with_access_check.return_value = None
        
        response = client.get(
            f"/api/v1/projects/{str(uuid.uuid4())}",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "code" in data["detail"]
        assert data["detail"]["code"] == "PROJECT_NOT_FOUND"
        
    def test_update_project(self, mock_project_service, test_project_data):
        """Test updating a project."""
        update_data = {
            "name": "Updated Project",
            "description": "Updated description",
            "tags": ["updated", "project"]
        }
        
        response = client.put(
            f"/api/v1/projects/{test_project_data['id']}",
            headers={"Authorization": "Bearer test-token"},
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_project_data["id"]
        
        # Verify service was called
        mock_project_service.get_project_with_access_check.assert_awaited_once()
        # Verify update was called if tags are provided
        if "tags" in update_data:
            mock_project_service.update_project_tags.assert_awaited_once_with(
                test_project_data["id"], update_data["tags"]
            )
        
    def test_delete_project(self, mock_project_service, test_project_data):
        """Test deleting a project."""
        response = client.delete(
            f"/api/v1/projects/{test_project_data['id']}",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify service was called
        mock_project_service.get_project_with_access_check.assert_awaited_once()
        mock_project_service.delete.assert_awaited_once_with(test_project_data["id"])
        
    def test_search_projects(self, mock_project_service, test_project_data):
        """Test searching for projects."""
        response = client.get(
            "/api/v1/projects?search=test&tags=test",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 1
        
        # Verify service was called with search parameter
        call_args = mock_project_service.get_projects_by_tenant.call_args[1]
        assert call_args["search"] == "test"
        assert call_args["tags"] == ["test"] 