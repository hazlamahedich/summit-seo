"""
Direct tests of API endpoints with simplified mocking.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Directly create patchers to avoid settings validation issues
app_mock = MagicMock()
app_mock.API_V1_STR = "/api/v1"
app_mock.APP_NAME = "Summit SEO API Test"
app_mock.APP_DESCRIPTION = "Test API"
app_mock.APP_VERSION = "0.1.0"
app_mock.CORS_ORIGINS = ["*"]

# Patch at module level
with patch("summit_seo.web.api.core.config.settings", app_mock):
    with patch("summit_seo.web.api.app.app_settings", app_mock):
        # Now import the app with mocked settings
        from summit_seo.web.api.app import app

# Create test client
client = TestClient(app)

def test_health_endpoint():
    """Test the health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "description" in data
    assert "documentation" in data 