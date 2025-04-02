"""
Tests for the Project Service.
"""
import pytest
import uuid
from unittest.mock import MagicMock, AsyncMock, patch

from summit_seo.web.api.services.project_service import ProjectService

@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client."""
    mock_client = MagicMock()
    
    # Mock table method
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    
    # Mock query methods
    mock_table.select = MagicMock(return_value=mock_table)
    mock_table.eq = MagicMock(return_value=mock_table)
    mock_table.or_ = MagicMock(return_value=mock_table)
    mock_table.contains = MagicMock(return_value=mock_table)
    mock_table.range = MagicMock(return_value=mock_table)
    mock_table.order = MagicMock(return_value=mock_table)
    mock_table.update = MagicMock(return_value=mock_table)
    mock_table.delete = MagicMock(return_value=mock_table)
    mock_table.insert = MagicMock(return_value=mock_table)
    mock_table.count = MagicMock(return_value=mock_table)
    
    # Mock response
    mock_response = MagicMock()
    mock_response.data = []
    mock_response.count = 0
    mock_table.execute = AsyncMock(return_value=mock_response)
    
    return mock_client, mock_table, mock_response

@pytest.fixture
def project_service(mock_supabase_client):
    """Create a project service with a mock Supabase client."""
    mock_client, _, _ = mock_supabase_client
    
    # Mock the get_supabase_client function to return our mock
    with patch('summit_seo.web.api.services.base_service.get_supabase_client', return_value=mock_client):
        with patch('summit_seo.web.api.services.base_service.get_supabase_admin_client', return_value=mock_client):
            service = ProjectService()
            return service

@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
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

class TestProjectService:
    """Test cases for the ProjectService."""
    
    async def test_get_projects_by_tenant(self, project_service, mock_supabase_client, sample_project_data):
        """Test getting projects by tenant ID."""
        _, _, mock_response = mock_supabase_client
        
        # Configure the mock response
        mock_response.data = [sample_project_data]
        mock_response.count = 1
        
        # Call the method
        result = await project_service.get_projects_by_tenant(
            tenant_id=sample_project_data["tenant_id"],
            page=1,
            page_size=10,
            search="test",
            tags=["test"]
        )
        
        # Verify the result
        assert result["data"] == [sample_project_data]
        assert result["pagination"]["total"] == 1
        assert result["pagination"]["page"] == 1
        assert result["pagination"]["page_size"] == 10
    
    async def test_get_project_with_access_check(self, project_service, mock_supabase_client, sample_project_data):
        """Test getting a project with access check."""
        _, _, mock_response = mock_supabase_client
        
        # Configure the mock response
        mock_response.data = [sample_project_data]
        
        # Call the method
        result = await project_service.get_project_with_access_check(
            project_id=sample_project_data["id"],
            user_id=str(uuid.uuid4())
        )
        
        # Verify the result
        assert result == sample_project_data
    
    async def test_get_project_with_access_check_not_found(self, project_service, mock_supabase_client):
        """Test getting a project with access check when not found."""
        _, _, mock_response = mock_supabase_client
        
        # Configure the mock response to return no data
        mock_response.data = []
        
        # Call the method
        result = await project_service.get_project_with_access_check(
            project_id=str(uuid.uuid4()),
            user_id=str(uuid.uuid4())
        )
        
        # Verify the result
        assert result is None
    
    async def test_create_project(self, project_service, mock_supabase_client, sample_project_data):
        """Test creating a project."""
        _, _, mock_response = mock_supabase_client
        
        # Configure the mock response
        mock_response.data = [sample_project_data]
        
        # Mock the create method
        project_service.create = AsyncMock(return_value=sample_project_data)
        
        # Call the method
        result = await project_service.create_project(
            tenant_id=sample_project_data["tenant_id"],
            name=sample_project_data["name"],
            url=sample_project_data["url"],
            description=sample_project_data["description"],
            settings=sample_project_data["settings"],
            tags=sample_project_data["tags"],
            icon_url=sample_project_data["icon_url"]
        )
        
        # Verify the result
        assert result == sample_project_data
        # Verify the create method was called
        project_service.create.assert_called_once()
    
    async def test_update_project_tags(self, project_service, mock_supabase_client, sample_project_data):
        """Test updating project tags."""
        # Mock the update method
        project_service.update = AsyncMock(return_value=sample_project_data)
        
        # Call the method
        result = await project_service.update_project_tags(
            project_id=sample_project_data["id"],
            tags=["updated", "tags"]
        )
        
        # Verify the result
        assert result == sample_project_data
        # Verify the update method was called with the correct parameters
        project_service.update.assert_called_once_with(
            sample_project_data["id"],
            {"tags": ["updated", "tags"]}
        )
    
    async def test_update_project_settings(self, project_service, mock_supabase_client, sample_project_data):
        """Test updating project settings."""
        # Mock the update method
        project_service.update = AsyncMock(return_value=sample_project_data)
        
        # New settings
        new_settings = {"analyzer_config": {"updated": True}}
        
        # Call the method
        result = await project_service.update_project_settings(
            project_id=sample_project_data["id"],
            settings=new_settings
        )
        
        # Verify the result
        assert result == sample_project_data
        # Verify the update method was called with the correct parameters
        project_service.update.assert_called_once_with(
            sample_project_data["id"],
            {"settings": new_settings}
        )
    
    async def test_update_project_score(self, project_service, mock_supabase_client, sample_project_data):
        """Test updating project score."""
        _, _, mock_response = mock_supabase_client
        
        # Configure the mock response for get_by_id
        mock_response.data = [sample_project_data]
        
        # Mock the get_by_id and update methods
        project_service.get_by_id = AsyncMock(return_value=sample_project_data)
        project_service.update = AsyncMock(return_value=sample_project_data)
        
        # New score values
        new_score = 90.0
        issues_count = 8
        critical_issues_count = 1
        
        # Call the method
        result = await project_service.update_project_score(
            project_id=sample_project_data["id"],
            score=new_score,
            issues_count=issues_count,
            critical_issues_count=critical_issues_count
        )
        
        # Verify the result
        assert result == sample_project_data
        
        # Verify the update method was called with the correct parameters
        project_service.update.assert_called_once_with(
            sample_project_data["id"],
            {
                "last_score": new_score,
                "score_change": new_score - sample_project_data["last_score"],
                "issues_count": issues_count,
                "critical_issues_count": critical_issues_count
            }
        ) 