"""Minimal fixtures for API tests."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
from pathlib import Path
from datetime import datetime
from fastapi.testclient import TestClient
from summit_seo.web.api.app import app

# First, mock the Settings class before it's imported
# We need to patch it at the module level
sys.modules['summit_seo.web.api.core.config'] = MagicMock()
sys.modules['summit_seo.web.api.core.config'].settings = MagicMock()

# Setup settings attributes
test_settings = sys.modules['summit_seo.web.api.core.config'].settings
test_settings.API_V1_STR = "/api/v1"
test_settings.PROJECT_NAME = "Summit SEO API Test"
test_settings.BACKEND_CORS_ORIGINS = []
test_settings.POSTGRES_SERVER = "localhost"
test_settings.POSTGRES_USER = "postgres"
test_settings.POSTGRES_PASSWORD = "postgres"
test_settings.POSTGRES_DB = "summit_seo_test"
test_settings.SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/summit_seo_test"
test_settings.JWT_SECRET_KEY = "test_secret_key"
test_settings.JWT_ALGORITHM = "HS256"
test_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
test_settings.FIRST_SUPERUSER = "admin@example.com"
test_settings.FIRST_SUPERUSER_PASSWORD = "admin_test_password"
test_settings.SUPABASE_URL = "https://example.supabase.co"
test_settings.SUPABASE_KEY = "mock_key"
test_settings.SUPABASE_SERVICE_KEY = "mock_service_key"
test_settings.LITELLM_DEFAULT_MODEL = "gpt-3.5-turbo"
test_settings.LITELLM_DEFAULT_EMBEDDING_MODEL = "text-embedding-ada-002"
test_settings.LITELLM_FALLBACK_MODELS = ""
test_settings.LITELLM_ENABLE_COST_TRACKING = False
test_settings.LITELLM_MAX_BUDGET = 0.0
test_settings.LITELLM_ENABLE_CACHING = False
test_settings.LITELLM_CACHE_TYPE = "redis"
test_settings.LITELLM_CACHE_HOST = ""
test_settings.LITELLM_CACHE_PORT = 6379
test_settings.LITELLM_CACHE_PASSWORD = ""
test_settings.LITELLM_VERBOSE = False
test_settings.LITELLM_MODEL_CONFIG_PATH = ""
test_settings.OPENAI_API_KEY = ""
test_settings.ANTHROPIC_API_KEY = ""
test_settings.AZURE_API_KEY = ""
test_settings.COHERE_API_KEY = ""
test_settings.OPENROUTER_API_KEY = ""
test_settings.OLLAMA_BASE_URL = "http://localhost:11434"
test_settings.OLLAMA_MODELS = ""
test_settings.OLLAMA_ENABLE = False
test_settings.OPENROUTER_ENABLE = False
test_settings.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
test_settings.OPENROUTER_TIMEOUT = 60

# Path to the summit_seo package
package_path = str(Path(__file__).parent.parent.parent.parent.parent)
if package_path not in sys.path:
    sys.path.insert(0, package_path)

class TestSettings:
    """Test settings to substitute real settings to avoid validation errors"""
    API_V1_STR = "/api/v1"
    PROJECT_NAME = "Summit SEO API Test"
    BACKEND_CORS_ORIGINS = []
    POSTGRES_SERVER = "localhost"
    POSTGRES_USER = "postgres"
    POSTGRES_PASSWORD = "postgres"
    POSTGRES_DB = "summit_seo_test"
    DATABASE_URL = "postgresql://postgres:postgres@localhost/summit_seo_test"
    JWT_SECRET_KEY = "test_secret_key"
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    FIRST_SUPERUSER = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD = "admin_test_password"
    SUPABASE_URL = "https://example.supabase.co"
    SUPABASE_KEY = "mock_key"
    SUPABASE_SERVICE_KEY = "mock_service_key"
    
    # LLM settings
    LITELLM_DEFAULT_MODEL = "gpt-3.5-turbo"
    LITELLM_DEFAULT_EMBEDDING_MODEL = "text-embedding-ada-002"
    LITELLM_FALLBACK_MODELS = ""
    LITELLM_ENABLE_COST_TRACKING = False
    LITELLM_MAX_BUDGET = 0.0
    LITELLM_ENABLE_CACHING = False
    LITELLM_CACHE_TYPE = "redis"
    LITELLM_CACHE_HOST = ""
    LITELLM_CACHE_PORT = 6379
    LITELLM_CACHE_PASSWORD = ""
    LITELLM_VERBOSE = False
    LITELLM_MODEL_CONFIG_PATH = ""
    OPENAI_API_KEY = ""
    ANTHROPIC_API_KEY = ""
    AZURE_API_KEY = ""
    COHERE_API_KEY = ""
    OPENROUTER_API_KEY = ""
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODELS = ""
    OLLAMA_ENABLE = False
    OPENROUTER_ENABLE = False
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    OPENROUTER_TIMEOUT = 60

# Test data
@pytest.fixture
def test_user():
    """Test user data."""
    return {
        "email": "test@example.com",
        "password": "testpassword", 
        "is_active": True,
        "is_superuser": False,
        "full_name": "Test User",
    }

@pytest.fixture
def admin_user():
    """Admin user data."""
    return {
        "email": "admin@example.com",
        "password": "adminpassword",
        "is_active": True,
        "is_superuser": True,
        "full_name": "Admin User",
    }

@pytest.fixture
def test_project():
    """Test project data."""
    return {
        "id": "test-project-id",
        "name": "Test Project",
        "description": "Test project description",
        "url": "https://example.com",
        "created_at": "2023-01-01T00:00:00Z",
        "owner_id": "test-user-id",
    }

@pytest.fixture
def test_analysis():
    """Test analysis data."""
    return {
        "id": "test-analysis-id",
        "project_id": "test-project-id",
        "status": "completed",
        "results": {"score": 85, "recommendations": []},
        "created_at": "2023-01-01T00:00:00Z",
    }

@pytest.fixture
def mock_response():
    """Create a mock response object"""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"success": True}
    return response

@pytest.fixture
def mock_supabase():
    """Create a mock supabase client"""
    client = MagicMock()
    
    # Mock auth methods
    auth = MagicMock()
    auth.sign_in.return_value = {"user": {"id": "test-user-id"}, "session": {"access_token": "test-token"}}
    auth.sign_up.return_value = {"user": {"id": "new-user-id"}, "session": {"access_token": "new-token"}}
    client.auth = auth
    
    # Mock table queries
    table = MagicMock()
    table.select.return_value = table
    table.eq.return_value = table
    table.single.return_value = {"data": {"id": "test-item-id", "name": "Test Item"}}
    table.execute.return_value = {"data": [{"id": "test-item-id", "name": "Test Item"}]}
    client.table.return_value = table
    
    return client

@pytest.fixture
def client(mock_supabase):
    """Create a test client for the FastAPI app"""
    # Mock the Supabase client
    with patch('summit_seo.web.api.deps.create_supabase_client', return_value=mock_supabase):
        # Create test client with our app
        with TestClient(app) as client:
            yield client 