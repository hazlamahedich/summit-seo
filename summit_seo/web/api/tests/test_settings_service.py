"""
Tests for the Settings Service.
"""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch

from summit_seo.web.api.services import SettingScope
from summit_seo.web.api.services.settings_service import SettingsService

@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client."""
    mock_client = MagicMock()
    
    # Mock table method
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    
    # Mock query methods
    mock_table.eq.return_value = mock_table
    mock_table.order.return_value = mock_table
    mock_table.range.return_value = mock_table
    mock_table.update.return_value = mock_table
    mock_table.delete.return_value = mock_table
    mock_table.count.return_value = mock_table
    mock_table.or_.return_value = mock_table
    
    # Mock response
    mock_response = MagicMock()
    mock_response.data = []
    mock_response.count = 0
    
    return mock_client, mock_table, mock_response

@pytest.fixture
def settings_service(mock_supabase_client):
    """Create a settings service with a mock Supabase client."""
    mock_client, _, _ = mock_supabase_client
    service = SettingsService(mock_client)
    return service

class TestSettingsService:
    """Test cases for the SettingsService."""
    
    @pytest.mark.asyncio
    async def test_get_all_settings(self, settings_service, mock_supabase_client):
        """Test getting all settings."""
        mock_client, mock_table, mock_response = mock_supabase_client
        
        # Configure mock response
        mock_response.data = [{
            "id": "1",
            "key": "test.setting",
            "value": json.dumps("test-value"),
            "description": "Test setting description",
            "scope": SettingScope.SYSTEM,
            "scope_id": None,
            "created_at": "2023-01-01T00:00:00.000Z",
            "updated_at": "2023-01-01T00:00:00.000Z"
        }]
        mock_response.count = 1
        
        # Configure execute_query to return the mock response
        settings_service._execute_query = AsyncMock(return_value=mock_response)
        
        # Call the method
        result = await settings_service.get_all_settings()
        
        # Assertions
        assert len(result["data"]) == 1
        assert result["data"][0]["key"] == "test.setting"
        assert result["pagination"]["total"] == 1
        
        # Verify mock was called
        assert settings_service._execute_query.call_count == 2  # Once for count, once for data
    
    @pytest.mark.asyncio
    async def test_get_setting(self, settings_service, mock_supabase_client):
        """Test getting a single setting."""
        mock_client, mock_table, mock_response = mock_supabase_client
        
        # Configure mock response
        mock_response.data = [{
            "id": "1",
            "key": "test.setting",
            "value": json.dumps("test-value"),
            "description": "Test setting description",
            "scope": SettingScope.SYSTEM,
            "scope_id": None,
            "created_at": "2023-01-01T00:00:00.000Z",
            "updated_at": "2023-01-01T00:00:00.000Z"
        }]
        
        # Configure execute_query to return the mock response
        settings_service._execute_query = AsyncMock(return_value=mock_response)
        
        # Call the method
        result = await settings_service.get_setting("test.setting")
        
        # Assertions
        assert result["key"] == "test.setting"
        assert json.loads(result["value"]) == "test-value"
        
        # Verify mock was called
        settings_service._execute_query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_setting_not_found(self, settings_service, mock_supabase_client):
        """Test getting a non-existent setting."""
        mock_client, mock_table, mock_response = mock_supabase_client
        
        # Configure mock response
        mock_response.data = []
        
        # Configure execute_query to return the mock response
        settings_service._execute_query = AsyncMock(return_value=mock_response)
        
        # Call the method
        result = await settings_service.get_setting("nonexistent.setting")
        
        # Assertions
        assert result is None
        
        # Verify mock was called
        settings_service._execute_query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_existing_setting(self, settings_service, mock_supabase_client):
        """Test updating an existing setting."""
        mock_client, mock_table, mock_response = mock_supabase_client
        
        # Configure mock responses for get_setting and update
        existing_setting = {
            "id": "1",
            "key": "test.setting",
            "value": json.dumps("old-value"),
            "description": "Old description",
            "scope": SettingScope.SYSTEM,
            "scope_id": None,
            "created_at": "2023-01-01T00:00:00.000Z",
            "updated_at": "2023-01-01T00:00:00.000Z"
        }
        
        updated_setting = {
            "id": "1",
            "key": "test.setting",
            "value": json.dumps("new-value"),
            "description": "New description",
            "scope": SettingScope.SYSTEM,
            "scope_id": None,
            "created_at": "2023-01-01T00:00:00.000Z",
            "updated_at": "2023-01-02T00:00:00.000Z"
        }
        
        # Mock get_setting to return existing setting
        settings_service.get_setting = AsyncMock(return_value=existing_setting)
        
        # Configure execute_query for update
        update_response = MagicMock()
        update_response.data = [updated_setting]
        settings_service._execute_query = AsyncMock(return_value=update_response)
        
        # Call the method
        result = await settings_service.update_setting(
            key="test.setting",
            value="new-value",
            description="New description"
        )
        
        # Assertions
        assert result["key"] == "test.setting"
        assert json.loads(result["value"]) == "new-value"
        assert result["description"] == "New description"
        
        # Verify mocks were called
        settings_service.get_setting.assert_called_once_with(
            key="test.setting", 
            scope=SettingScope.SYSTEM, 
            scope_id=None
        )
        settings_service._execute_query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_new_setting(self, settings_service, mock_supabase_client):
        """Test creating a new setting."""
        mock_client, mock_table, mock_response = mock_supabase_client
        
        # Mock get_setting to return None (setting doesn't exist)
        settings_service.get_setting = AsyncMock(return_value=None)
        
        # Mock create method
        new_setting = {
            "id": "2",
            "key": "new.setting",
            "value": json.dumps("new-value"),
            "description": "New setting",
            "scope": SettingScope.SYSTEM,
            "scope_id": None,
            "created_at": "2023-01-01T00:00:00.000Z",
            "updated_at": "2023-01-01T00:00:00.000Z"
        }
        settings_service.create = AsyncMock(return_value=new_setting)
        
        # Call the method
        result = await settings_service.update_setting(
            key="new.setting",
            value="new-value",
            description="New setting"
        )
        
        # Assertions
        assert result["key"] == "new.setting"
        assert json.loads(result["value"]) == "new-value"
        
        # Verify mocks were called
        settings_service.get_setting.assert_called_once()
        settings_service.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_setting(self, settings_service, mock_supabase_client):
        """Test deleting a setting."""
        mock_client, mock_table, mock_response = mock_supabase_client
        
        # Configure mock response for get_setting
        existing_setting = {
            "id": "1",
            "key": "test.setting",
            "value": json.dumps("test-value"),
            "description": "Test setting description",
            "scope": SettingScope.SYSTEM,
            "scope_id": None,
            "created_at": "2023-01-01T00:00:00.000Z",
            "updated_at": "2023-01-01T00:00:00.000Z"
        }
        
        # Mock get_setting to return existing setting
        settings_service.get_setting = AsyncMock(return_value=existing_setting)
        
        # Configure execute_query for delete
        settings_service._execute_query = AsyncMock()
        
        # Call the method
        result = await settings_service.delete_setting("test.setting")
        
        # Assertions
        assert result is True
        
        # Verify mocks were called
        settings_service.get_setting.assert_called_once()
        settings_service._execute_query.assert_called_once() 