"""
Tests for settings using fully mocked imports.
"""
import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch

# Define enums we need without importing
class SettingScope:
    SYSTEM = "system"
    PROJECT = "project"
    USER = "user"

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
    
    # Configure execute method directly on select_mock
    select_mock.execute = AsyncMock(return_value=mock_response)
    
    # Configure insert and update methods
    insert_mock = MagicMock()
    from_mock.insert = MagicMock(return_value=insert_mock)
    insert_mock.execute = AsyncMock(return_value=mock_response)
    
    update_mock = MagicMock()
    from_mock.update = MagicMock(return_value=update_mock)
    eq_update_mock = MagicMock()
    update_mock.eq = MagicMock(return_value=eq_update_mock)
    eq_update_mock.execute = AsyncMock(return_value=mock_response)
    
    # Configure delete method
    delete_mock = MagicMock()
    from_mock.delete = MagicMock(return_value=delete_mock)
    eq_delete_mock = MagicMock()
    delete_mock.eq = MagicMock(return_value=eq_delete_mock)
    eq_delete_mock.eq = MagicMock(return_value=eq_delete_mock)  # For chained eq() calls
    is_delete_mock = MagicMock()
    eq_delete_mock.is_ = MagicMock(return_value=is_delete_mock)
    is_delete_mock.execute = AsyncMock(return_value=mock_response)
    
    return mock_client

# Mock the settings service
class MockSettingsService:
    """Mock implementation of the SettingsService."""
    
    def __init__(self, supabase_client):
        self.client = supabase_client
        self.table_name = "settings"
    
    async def get_setting(self, key, scope=SettingScope.SYSTEM, scope_id=None):
        """Get a setting by key, scope, and scope_id."""
        query = (
            self.client.from_(self.table_name)
            .select("*")
            .eq("key", key)
            .eq("scope", scope)
        )
        
        if scope_id is not None:
            query = query.eq("scope_id", scope_id)
        else:
            query = query.is_("scope_id", "null")
            
        response = await query.order("created_at", desc=True).execute()
        
        if not response.data:
            return None
            
        return response.data[0]
    
    async def get_all_settings(self, scope=None, scope_id=None, page=1, page_size=50):
        """Get all settings, optionally filtered by scope and scope_id."""
        query = self.client.from_(self.table_name).select("*")
        
        if scope:
            query = query.eq("scope", scope)
            
        if scope_id is not None:
            query = query.eq("scope_id", scope_id)
            
        response = await query.execute()
        
        # Calculate pagination
        total = len(response.data)
        total_pages = (total + page_size - 1) // page_size if total > 0 else 1
        
        # Apply pagination (simple implementation)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_data = response.data[start:end]
        
        return {
            "data": paginated_data,
            "pagination": {
                "total": total,
                "page": page,
                "pages": total_pages,
                "page_size": page_size
            }
        }
    
    async def update_setting(self, key, value, description=None, scope=SettingScope.SYSTEM, scope_id=None):
        """Create or update a setting."""
        # Check if the setting exists
        existing = await self.get_setting(key, scope, scope_id)
        
        # Prepare the data
        setting_data = {
            "key": key,
            "value": json.dumps(value),
            "scope": scope
        }
        
        if scope_id is not None:
            setting_data["scope_id"] = scope_id
            
        if description is not None:
            setting_data["description"] = description
            
        if existing:
            # Update existing setting
            response = await (
                self.client.from_(self.table_name)
                .update(setting_data)
                .eq("id", existing["id"])
                .execute()
            )
        else:
            # Create new setting
            response = await (
                self.client.from_(self.table_name)
                .insert(setting_data)
                .execute()
            )
            
        return response.data[0] if response.data else None
    
    async def delete_setting(self, key, scope=SettingScope.SYSTEM, scope_id=None):
        """Delete a setting by key, scope, and scope_id."""
        query = (
            self.client.from_(self.table_name)
            .delete()
            .eq("key", key)
            .eq("scope", scope)
        )
        
        if scope_id is not None:
            query = query.eq("scope_id", scope_id)
        else:
            query = query.is_("scope_id", "null")
            
        response = await query.execute()
        
        return len(response.data) > 0

@pytest.fixture
def settings_service(mock_supabase_client):
    """Create a MockSettingsService instance with a mock Supabase client."""
    return MockSettingsService(supabase_client=mock_supabase_client)

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

class TestMockedSettingsService:
    """Test cases for the mocked SettingsService."""
    
    @pytest.mark.asyncio
    async def test_get_setting_found(self, settings_service, mock_supabase_client, test_setting):
        """Test getting a setting that exists."""
        # Get all the mocks we need to configure
        from_mock = mock_supabase_client.from_.return_value
        select_mock = from_mock.select.return_value
        eq_mock = select_mock.eq.return_value
        eq_mock2 = MagicMock()
        eq_mock.eq.return_value = eq_mock2
        is_mock = MagicMock()
        eq_mock2.is_.return_value = is_mock
        order_mock = MagicMock()
        is_mock.order.return_value = order_mock
        
        # Set up response with test data
        mock_response = MagicMock()
        mock_response.data = [test_setting]
        
        # Make sure execute() is an AsyncMock that returns our response
        order_mock.execute = AsyncMock(return_value=mock_response)
        
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
        # Get all the mocks we need to configure
        from_mock = mock_supabase_client.from_.return_value
        select_mock = from_mock.select.return_value
        eq_mock = select_mock.eq.return_value
        eq_mock2 = MagicMock()
        eq_mock.eq.return_value = eq_mock2
        is_mock = MagicMock()
        eq_mock2.is_.return_value = is_mock
        order_mock = MagicMock()
        is_mock.order.return_value = order_mock
        
        # Set up empty response
        mock_response = MagicMock()
        mock_response.data = []
        
        # Make sure execute() is an AsyncMock that returns our response
        order_mock.execute = AsyncMock(return_value=mock_response)
        
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
        # Get all the mocks we need to configure
        from_mock = mock_supabase_client.from_.return_value
        select_mock = from_mock.select.return_value
        
        # Set up response with test data
        mock_response = MagicMock()
        mock_response.data = [test_setting]
        mock_response.count = 1
        
        # Make sure execute() is an AsyncMock that returns our response
        select_mock.execute = AsyncMock(return_value=mock_response)
        
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
        # Mock for get_setting (returns None to indicate the setting doesn't exist)
        from_mock = mock_supabase_client.from_.return_value
        select_mock = from_mock.select.return_value
        eq_mock = select_mock.eq.return_value
        eq_mock2 = MagicMock()
        eq_mock.eq.return_value = eq_mock2
        is_mock = MagicMock()
        eq_mock2.is_.return_value = is_mock
        order_mock = MagicMock()
        is_mock.order.return_value = order_mock
        
        get_response = MagicMock()
        get_response.data = []
        order_mock.execute = AsyncMock(return_value=get_response)
        
        # Mock for insert
        insert_mock = MagicMock()
        from_mock.insert.return_value = insert_mock
        
        # Set up response with created setting
        insert_response = MagicMock()
        insert_response.data = [test_setting]
        insert_mock.execute = AsyncMock(return_value=insert_response)
        
        # Call the service
        result = await settings_service.update_setting(
            key="test.setting", 
            value="test-value",
            description="Test setting description",
            scope=SettingScope.SYSTEM,
            scope_id=None
        )
        
        # Verify the result
        assert result == test_setting
        
        # Verify the insert was called
        from_mock.insert.assert_called_once()
        insert_mock.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_existing_setting(self, settings_service, mock_supabase_client, test_setting):
        """Test updating an existing setting."""
        # Mock for get_setting (returns the test setting to indicate it exists)
        from_mock = mock_supabase_client.from_.return_value
        select_mock = from_mock.select.return_value
        eq_mock = select_mock.eq.return_value
        eq_mock2 = MagicMock()
        eq_mock.eq.return_value = eq_mock2
        is_mock = MagicMock()
        eq_mock2.is_.return_value = is_mock
        order_mock = MagicMock()
        is_mock.order.return_value = order_mock
        
        get_response = MagicMock()
        get_response.data = [test_setting]
        order_mock.execute = AsyncMock(return_value=get_response)
        
        # Mock for update
        update_mock = MagicMock()
        from_mock.update.return_value = update_mock
        update_eq_mock = MagicMock()
        update_mock.eq.return_value = update_eq_mock
        
        # Set up response with updated setting
        updated_setting = test_setting.copy()
        updated_setting["value"] = json.dumps("updated-value")
        
        update_response = MagicMock()
        update_response.data = [updated_setting]
        update_eq_mock.execute = AsyncMock(return_value=update_response)
        
        # Call the service
        result = await settings_service.update_setting(
            key="test.setting",
            value="updated-value",
            description="Updated description",
            scope=SettingScope.SYSTEM,
            scope_id=None
        )
        
        # Verify the result
        assert result == updated_setting
        
        # Verify the update was called
        from_mock.update.assert_called_once()
        update_eq_mock.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_setting(self, settings_service, mock_supabase_client):
        """Test deleting a setting."""
        # Set up mocks for the delete operation
        from_mock = mock_supabase_client.from_.return_value
        delete_mock = MagicMock()
        from_mock.delete.return_value = delete_mock
        eq_mock = MagicMock()
        delete_mock.eq.return_value = eq_mock
        eq_mock2 = MagicMock()
        eq_mock.eq.return_value = eq_mock2
        is_mock = MagicMock()
        eq_mock2.is_.return_value = is_mock
        
        # Set up response with deleted record
        delete_response = MagicMock()
        delete_response.data = [{"id": "1"}]  # Deleted record
        is_mock.execute = AsyncMock(return_value=delete_response)
        
        # Call the service
        result = await settings_service.delete_setting(
            key="test.setting",
            scope=SettingScope.SYSTEM,
            scope_id=None
        )
        
        # Verify the result
        assert result is True
        
        # Verify the delete was called correctly
        mock_supabase_client.from_.assert_called_once_with("settings")
        from_mock.delete.assert_called_once()
        delete_mock.eq.assert_called_once_with("key", "test.setting") 