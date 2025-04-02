"""
Tests for the Settings service directly, without going through the FastAPI app.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import json

# Import the service directly rather than through the app
from summit_seo.web.api.services.settings import SettingsService, SettingScope, SettingNotFound, SettingAlreadyExists

@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client for testing."""
    mock_client = MagicMock()
    
    # Set up the from_ method
    from_mock = MagicMock()
    mock_client.from_ = MagicMock(return_value=from_mock)
    
    # Configure select method
    select_mock = MagicMock()
    from_mock.select = MagicMock(return_value=select_mock)
    
    # Configure eq, order, execute methods
    eq_mock = MagicMock()
    select_mock.eq = MagicMock(return_value=eq_mock)
    order_mock = MagicMock()
    eq_mock.order = MagicMock(return_value=order_mock)
    
    # Default empty response
    mock_response = MagicMock()
    mock_response.data = []
    order_mock.execute = AsyncMock(return_value=mock_response)
    
    # Configure insert and update methods
    from_mock.insert = MagicMock(return_value=MagicMock())
    from_mock.update = MagicMock(return_value=MagicMock())
    
    # Configure delete method
    from_mock.delete = MagicMock(return_value=MagicMock())
    
    return mock_client

@pytest.fixture
def settings_service(mock_supabase_client):
    """Create a SettingsService instance with a mock Supabase client."""
    return SettingsService(supabase_client=mock_supabase_client)

@pytest.fixture
def test_setting():
    """Sample setting for tests."""
    return {
        "id": "1",
        "key": "test.setting",
        "value": json.dumps("test-value"),  # JSON string
        "description": "Test setting description",
        "scope": SettingScope.SYSTEM,
        "scope_id": None,
        "created_at": "2023-01-01T00:00:00.000Z",
        "updated_at": "2023-01-01T00:00:00.000Z"
    }

class TestSettingsService:
    """Test cases for the SettingsService."""
    
    @pytest.mark.asyncio
    async def test_get_setting_found(self, settings_service, mock_supabase_client, test_setting):
        """Test getting a setting that exists."""
        # Configure the mock to return the test setting
        from_mock = mock_supabase_client.from_.return_value
        select_mock = from_mock.select.return_value
        eq_mock = select_mock.eq.return_value
        order_mock = eq_mock.order.return_value
        
        mock_response = MagicMock()
        mock_response.data = [test_setting]
        order_mock.execute.return_value = mock_response
        
        # Call the service
        result = await settings_service.get_setting(
            key="test.setting", 
            scope=SettingScope.SYSTEM,
            scope_id=None
        )
        
        # Verify the result
        assert result == test_setting
        
        # Verify the Supabase client was called correctly
        mock_supabase_client.from_.assert_called_once_with("settings")
        from_mock.select.assert_called_once_with("*")
        select_mock.eq.assert_called_once_with("key", "test.setting")
    
    @pytest.mark.asyncio
    async def test_get_setting_not_found(self, settings_service, mock_supabase_client):
        """Test getting a setting that doesn't exist."""
        # Configure the mock to return an empty result
        from_mock = mock_supabase_client.from_.return_value
        select_mock = from_mock.select.return_value
        eq_mock = select_mock.eq.return_value
        order_mock = eq_mock.order.return_value
        
        mock_response = MagicMock()
        mock_response.data = []
        order_mock.execute.return_value = mock_response
        
        # Call the service and expect it to return None
        result = await settings_service.get_setting(
            key="nonexistent.setting", 
            scope=SettingScope.SYSTEM,
            scope_id=None
        )
        
        # Verify the result
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_all_settings(self, settings_service, mock_supabase_client, test_setting):
        """Test getting all settings."""
        # Configure the mock to return the test setting
        from_mock = mock_supabase_client.from_.return_value
        select_mock = from_mock.select.return_value
        
        mock_response = MagicMock()
        mock_response.data = [test_setting]
        mock_response.count = 1
        select_mock.execute.return_value = mock_response
        
        # Call the service
        result = await settings_service.get_all_settings()
        
        # Verify the result
        assert result["data"] == [test_setting]
        assert result["pagination"]["total"] == 1
        
        # Verify the Supabase client was called correctly
        mock_supabase_client.from_.assert_called_once_with("settings")
        from_mock.select.assert_called_once_with("*")
    
    @pytest.mark.asyncio
    async def test_update_create_setting(self, settings_service, mock_supabase_client, test_setting):
        """Test creating a new setting."""
        # Configure the mock to return the test setting
        from_mock = mock_supabase_client.from_.return_value
        insert_mock = from_mock.insert.return_value
        
        mock_response = MagicMock()
        mock_response.data = [test_setting]
        insert_mock.execute.return_value = mock_response
        
        # Call the service
        setting_data = {
            "key": "test.setting",
            "value": "test-value",
            "description": "Test setting description",
            "scope": SettingScope.SYSTEM,
            "scope_id": None
        }
        
        result = await settings_service.update_setting(**setting_data)
        
        # Verify the result
        assert result["key"] == "test.setting"
        
        # Verify the Supabase client was called correctly
        mock_supabase_client.from_.assert_called_once_with("settings")
        from_mock.insert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_existing_setting(self, settings_service, mock_supabase_client, test_setting):
        """Test updating an existing setting."""
        # Configure the mock for get_setting
        from_mock = mock_supabase_client.from_.return_value
        select_mock = from_mock.select.return_value
        eq_mock = select_mock.eq.return_value
        order_mock = eq_mock.order.return_value
        
        mock_response_get = MagicMock()
        mock_response_get.data = [test_setting]
        order_mock.execute.return_value = mock_response_get
        
        # Configure the mock for the update
        update_mock = from_mock.update.return_value
        eq_update_mock = update_mock.eq.return_value
        
        updated_setting = test_setting.copy()
        updated_setting["value"] = json.dumps("updated-value")
        
        mock_response_update = MagicMock()
        mock_response_update.data = [updated_setting]
        eq_update_mock.execute.return_value = mock_response_update
        
        # Call the service
        result = await settings_service.update_setting(
            key="test.setting",
            value="updated-value",
            description="Updated description",
            scope=SettingScope.SYSTEM,
            scope_id=None
        )
        
        # Verify the result
        assert json.loads(result["value"]) == "updated-value"
        
        # Verify the Supabase client was called correctly
        assert mock_supabase_client.from_.call_count == 2  # Once for get, once for update
    
    @pytest.mark.asyncio
    async def test_delete_setting(self, settings_service, mock_supabase_client):
        """Test deleting a setting."""
        # Configure the mock
        from_mock = mock_supabase_client.from_.return_value
        delete_mock = from_mock.delete.return_value
        eq_mock = delete_mock.eq.return_value
        
        mock_response = MagicMock()
        mock_response.data = [{"id": "1"}]  # Deleted record
        eq_mock.execute.return_value = mock_response
        
        # Call the service
        result = await settings_service.delete_setting(
            key="test.setting",
            scope=SettingScope.SYSTEM,
            scope_id=None
        )
        
        # Verify the result
        assert result is True
        
        # Verify the Supabase client was called correctly
        mock_supabase_client.from_.assert_called_once_with("settings")
        from_mock.delete.assert_called_once()
        delete_mock.eq.assert_called_once_with("key", "test.setting") 