"""
Tests for the Settings API endpoints.
"""
import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from summit_seo.web.api.main import app
from summit_seo.web.api.services import SettingScope

client = TestClient(app)

@pytest.mark.usefixtures("mock_supabase", "mock_verify_token")
class TestSettingsEndpoints:
    """Test cases for the settings endpoints."""
    
    def test_get_all_settings(self, mock_settings_service, mock_current_superuser):
        """Test listing all settings."""
        response = client.get(
            "/settings/",
            headers={"Authorization": f"Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["pagination"]["total"] == 1
        
        # Verify mock was called
        mock_settings_service.get_all_settings.assert_called_once()
    
    def test_get_setting(self, mock_settings_service, mock_current_superuser, test_settings_data):
        """Test getting a single setting."""
        response = client.get(
            "/settings/test.setting",
            headers={"Authorization": f"Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "test.setting"
        
        # Verify mock was called with correct arguments
        mock_settings_service.get_setting.assert_called_once_with(
            key="test.setting", 
            scope=SettingScope.SYSTEM, 
            scope_id=None
        )
    
    def test_create_setting(self, mock_settings_service, mock_current_superuser):
        """Test creating a new setting."""
        # Configure mock to return None (setting doesn't exist)
        mock_settings_service.get_setting.reset_mock()
        mock_settings_service.get_setting.return_value = None
        
        response = client.post(
            "/settings/",
            headers={"Authorization": f"Bearer test-token"},
            json={
                "key": "new.setting", 
                "value": "new-value",
                "description": "New setting description",
                "scope": SettingScope.SYSTEM
            }
        )
        
        assert response.status_code == 201
        mock_settings_service.get_setting.assert_called_once()
        mock_settings_service.update_setting.assert_called_once()
    
    def test_update_setting(self, mock_settings_service, mock_current_superuser, test_settings_data):
        """Test updating an existing setting."""
        # Reset and reconfigure mock
        mock_settings_service.get_setting.reset_mock()
        mock_settings_service.get_setting.return_value = test_settings_data
        
        response = client.put(
            "/settings/test.setting",
            headers={"Authorization": f"Bearer test-token"},
            json={
                "value": "updated-value",
                "description": "Updated description"
            }
        )
        
        assert response.status_code == 200
        mock_settings_service.get_setting.assert_called_once()
        mock_settings_service.update_setting.assert_called_once()
    
    def test_delete_setting(self, mock_settings_service, mock_current_superuser):
        """Test deleting a setting."""
        response = client.delete(
            "/settings/test.setting",
            headers={"Authorization": f"Bearer test-token"}
        )
        
        assert response.status_code == 204
        mock_settings_service.delete_setting.assert_called_once_with(
            key="test.setting", 
            scope=SettingScope.SYSTEM, 
            scope_id=None
        )
    
    def test_setting_not_found(self, mock_settings_service, mock_current_superuser):
        """Test getting a non-existent setting."""
        # Configure mock to return None
        mock_settings_service.get_setting.reset_mock()
        mock_settings_service.get_setting.return_value = None
        
        response = client.get(
            "/settings/nonexistent.setting",
            headers={"Authorization": f"Bearer test-token"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "SETTING_NOT_FOUND"
    
    def test_setting_exists_conflict(self, mock_settings_service, mock_current_superuser, test_settings_data):
        """Test creating a setting that already exists."""
        # Reset and reconfigure mock
        mock_settings_service.get_setting.reset_mock()
        mock_settings_service.get_setting.return_value = test_settings_data
        
        response = client.post(
            "/settings/",
            headers={"Authorization": f"Bearer test-token"},
            json={
                "key": "test.setting", 
                "value": "new-value",
                "description": "New setting description",
                "scope": SettingScope.SYSTEM
            }
        )
        
        assert response.status_code == 409
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "SETTING_EXISTS" 