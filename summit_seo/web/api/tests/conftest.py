"""
Pytest fixtures for API tests.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import os
from typing import List
from fastapi.testclient import TestClient
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Generator

# Mock environment variables needed by Settings class
@pytest.fixture(scope="session", autouse=True)
def mock_env_vars():
    """Set up mock environment variables for testing."""
    # Load from .env file if it exists
    env_file = os.path.join(os.path.dirname(__file__), "../.env")
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key] = value
    
    # Make sure essential variables are set
    os.environ.setdefault("POSTGRES_SERVER", "localhost")
    os.environ.setdefault("POSTGRES_USER", "postgres")
    os.environ.setdefault("POSTGRES_PASSWORD", "postgres")
    os.environ.setdefault("POSTGRES_DB", "summit_seo_test")
    os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key")
    os.environ.setdefault("FIRST_SUPERUSER", "admin@example.com")
    os.environ.setdefault("FIRST_SUPERUSER_PASSWORD", "admin_test_password")
    os.environ.setdefault("SUPABASE_URL", "https://gqbihjuxgutbxsqfhxnd.supabase.co")
    os.environ.setdefault("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdxYmloanV4Z3V0YnhzcWZoeG5kIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMyOTkyMjksImV4cCI6MjA1ODg3NTIyOX0.J1GSo3XMV_BV3iTPrtJ2gtSS5dB-Ng6zkXZU_PDXjGI")
    os.environ.setdefault("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdxYmloanV4Z3V0YnhzcWZoeG5kIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MzI5OTIyOSwiZXhwIjoyMDU4ODc1MjI5fQ.HXF3lTXkfC0mvS4fhixco7UNGLaQ1gK_9DJzc0dVvQ4")

@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    """Mock the settings object to avoid validation errors"""
    mock_settings = MagicMock()
    
    # Add required attributes
    mock_settings.API_V1_STR = "/api/v1"
    mock_settings.PROJECT_NAME = "Summit SEO API Test"
    mock_settings.BACKEND_CORS_ORIGINS = []
    mock_settings.POSTGRES_SERVER = "localhost"
    mock_settings.POSTGRES_USER = "postgres"
    mock_settings.POSTGRES_PASSWORD = "postgres"
    mock_settings.POSTGRES_DB = "summit_seo_test"
    mock_settings.SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/summit_seo_test"
    mock_settings.JWT_SECRET_KEY = "test_secret_key"
    mock_settings.JWT_ALGORITHM = "HS256"
    mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    mock_settings.FIRST_SUPERUSER = "admin@example.com"
    mock_settings.FIRST_SUPERUSER_PASSWORD = "admin_test_password"
    mock_settings.SUPABASE_URL = "https://gqbihjuxgutbxsqfhxnd.supabase.co"
    mock_settings.SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdxYmloanV4Z3V0YnhzcWZoeG5kIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMyOTkyMjksImV4cCI6MjA1ODg3NTIyOX0.J1GSo3XMV_BV3iTPrtJ2gtSS5dB-Ng6zkXZU_PDXjGI"
    mock_settings.SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdxYmloanV4Z3V0YnhzcWZoeG5kIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0MzI5OTIyOSwiZXhwIjoyMDU4ODc1MjI5fQ.HXF3lTXkfC0mvS4fhixco7UNGLaQ1gK_9DJzc0dVvQ4"
    
    # Add LLM settings with default values
    mock_settings.LITELLM_DEFAULT_MODEL = "gpt-3.5-turbo"
    mock_settings.LITELLM_DEFAULT_EMBEDDING_MODEL = "text-embedding-ada-002"
    mock_settings.LITELLM_FALLBACK_MODELS = ""
    mock_settings.LITELLM_ENABLE_COST_TRACKING = False
    mock_settings.LITELLM_MAX_BUDGET = 0.0
    mock_settings.LITELLM_ENABLE_CACHING = False
    mock_settings.LITELLM_CACHE_TYPE = "redis"
    mock_settings.LITELLM_CACHE_HOST = ""
    mock_settings.LITELLM_CACHE_PORT = 6379
    mock_settings.LITELLM_CACHE_PASSWORD = ""
    mock_settings.LITELLM_VERBOSE = False
    mock_settings.LITELLM_MODEL_CONFIG_PATH = ""
    mock_settings.OPENAI_API_KEY = ""
    mock_settings.ANTHROPIC_API_KEY = ""
    mock_settings.AZURE_API_KEY = ""
    mock_settings.COHERE_API_KEY = ""
    mock_settings.OPENROUTER_API_KEY = ""
    mock_settings.OLLAMA_BASE_URL = "http://localhost:11434"
    mock_settings.OLLAMA_MODELS = ""
    mock_settings.OLLAMA_ENABLE = False
    mock_settings.OPENROUTER_ENABLE = False
    mock_settings.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    mock_settings.OPENROUTER_TIMEOUT = 60
    
    # Apply the mock to the settings module
    monkeypatch.setattr("summit_seo.web.api.core.config.settings", mock_settings)
    
    return mock_settings

@pytest.fixture(autouse=True)
def mock_supabase(monkeypatch):
    """
    Mock the Supabase client for all tests.
    
    This fixture is automatically used for all tests in the session.
    """
    # Create a mock Supabase client
    mock_client = MagicMock()
    
    # Mock auth methods
    mock_client.auth = MagicMock()
    mock_client.auth.get_user = MagicMock()
    mock_client.auth.get_user.return_value.user = {
        "id": "test-user-id",
        "email": "testuser@example.com",
        "user_metadata": {
            "is_superuser": True,
            "is_active": True
        }
    }
    
    # Mock database methods
    mock_client.table = MagicMock(return_value=MagicMock())
    mock_client.from_ = MagicMock(return_value=MagicMock())
    
    # Set up response patterns for common operations
    mock_response = MagicMock()
    mock_response.data = []
    mock_response.count = 0
    
    # Create a mock function for query execution
    def mock_execute(query):
        return mock_response
    
    # Apply patches
    monkeypatch.setattr("supabase.create_client", lambda *args, **kwargs: mock_client)
    monkeypatch.setattr("summit_seo.web.api.core.supabase.create_client", lambda *args, **kwargs: mock_client)
    
    return mock_client

@pytest.fixture
def mock_verify_token(monkeypatch):
    """
    Mock the verify_token function in the supabase module.
    """
    user_data = {
        "id": "test-user-id",
        "email": "testuser@example.com",
        "user_metadata": {
            "is_superuser": True,
            "is_active": True
        }
    }
    
    async def mock_verify(*args, **kwargs):
        return user_data
    
    monkeypatch.setattr("summit_seo.web.api.core.supabase.verify_token", mock_verify)
    return user_data

@pytest.fixture
def mock_oauth(monkeypatch):
    """
    Mock the OAuth2PasswordBearer dependency.
    """
    def mock_oauth(*args, **kwargs):
        return "test-token"
    
    monkeypatch.setattr("fastapi.security.OAuth2PasswordBearer.__call__", mock_oauth)
    return "test-token"

@pytest.fixture
def mock_current_user(monkeypatch):
    """
    Mock the get_current_user dependency.
    """
    user_data = {
        "id": "test-user-id",
        "email": "testuser@example.com",
        "user_metadata": {
            "is_active": True
        }
    }
    
    async def mock_get_current_user(*args, **kwargs):
        return user_data
    
    monkeypatch.setattr("summit_seo.web.api.core.deps.get_current_user", mock_get_current_user)
    return user_data

@pytest.fixture
def mock_current_superuser(monkeypatch):
    """
    Mock the get_current_superuser dependency.
    """
    user_data = {
        "id": "test-user-id",
        "email": "testuser@example.com",
        "user_metadata": {
            "is_superuser": True,
            "is_active": True
        }
    }
    
    async def mock_get_superuser(*args, **kwargs):
        return user_data
    
    monkeypatch.setattr("summit_seo.web.api.core.deps.get_current_superuser", mock_get_superuser)
    return user_data

@pytest.fixture
def test_settings_data():
    """
    Mock settings data for tests.
    """
    return {
        "id": "1",
        "key": "test.setting",
        "value": "\"test-value\"",  # JSON string
        "description": "Test setting description",
        "scope": "system",
        "scope_id": None,
        "created_at": "2023-01-01T00:00:00.000Z",
        "updated_at": "2023-01-01T00:00:00.000Z"
    }

@pytest.fixture
def mock_settings_service(monkeypatch, test_settings_data):
    """
    Mock the settings service for testing.
    """
    mock_service = MagicMock()
    
    # Configure the mock with appropriate return values
    async def mock_get_all_settings(*args, **kwargs):
        return {
            "data": [test_settings_data],
            "pagination": {
                "total": 1,
                "page": 1,
                "pages": 1,
                "page_size": 50
            }
        }
    
    async def mock_get_setting(*args, **kwargs):
        return test_settings_data
    
    async def mock_update_setting(*args, **kwargs):
        return test_settings_data
    
    async def mock_delete_setting(*args, **kwargs):
        return True
    
    mock_service.get_all_settings = mock_get_all_settings
    mock_service.get_setting = mock_get_setting
    mock_service.update_setting = mock_update_setting
    mock_service.delete_setting = mock_delete_setting
    
    def mock_get_settings_service(*args, **kwargs):
        return mock_service
    
    monkeypatch.setattr("summit_seo.web.api.core.deps.get_settings_service", mock_get_settings_service)
    return mock_service

# Define test data
@pytest.fixture
def test_user():
    """Test user data."""
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "email": "testuser@example.com",
        "password": "password",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False
    }

@pytest.fixture
def admin_user():
    """Admin user data."""
    return {
        "id": "223e4567-e89b-12d3-a456-426614174001",
        "email": "admin@example.com",
        "password": "adminpassword",
        "full_name": "Admin User",
        "is_active": True,
        "is_superuser": True
    }

@pytest.fixture
def test_project():
    """Test project data."""
    return {
        "id": "1",
        "name": "Test Project",
        "description": "A test project",
        "url": "https://example.com",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "owner_id": "123e4567-e89b-12d3-a456-426614174000"
    }

@pytest.fixture
def test_analysis():
    """Test analysis data."""
    return {
        "id": "1",
        "project_id": "1",
        "status": "completed",
        "overall_score": 85,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "settings": {
            "url": "https://example.com",
            "analyze_js": True,
            "analyze_mobile": True,
            "analyze_security": True
        },
        "results": {
            "overall_score": 85,
            "category_scores": {
                "seo": 90,
                "performance": 80,
                "security": 85,
                "accessibility": 75
            }
        }
    }

@pytest.fixture
def test_report():
    """Test report data."""
    return {
        "id": "1",
        "project_id": "1",
        "analysis_id": "1",
        "title": "Test Report",
        "description": "A test report",
        "format": "pdf",
        "status": "completed",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "generated_at": datetime.now().isoformat(),
        "file_url": "https://storage.example.com/reports/1.pdf",
        "file_size": 1024000,
        "file_type": "application/pdf"
    }

# Mock Supabase client
class MockSupabaseClient:
    """Mock Supabase client for testing."""
    
    def __init__(self, test_user, admin_user):
        self.test_user = test_user
        self.admin_user = admin_user
        self.auth = MagicMock()
        self.table = MagicMock()
        
        # Setup auth methods
        self.auth.sign_up = MagicMock(return_value=MagicMock(
            user=MagicMock(
                id=test_user["id"],
                email=test_user["email"],
                user_metadata={"full_name": test_user["full_name"], "is_active": True}
            )
        ))
        
        self.auth.sign_in_with_password = MagicMock(side_effect=self._handle_sign_in)
        self.auth.sign_out = MagicMock(return_value=None)
        
    def _handle_sign_in(self, credentials):
        """Handle sign in based on credentials."""
        if (credentials["email"] == self.test_user["email"] and 
            credentials["password"] == self.test_user["password"]):
            return MagicMock(
                session=MagicMock(
                    access_token="test_access_token",
                    refresh_token="test_refresh_token"
                ),
                user=MagicMock(
                    id=self.test_user["id"],
                    email=self.test_user["email"],
                    user_metadata={"full_name": self.test_user["full_name"], "is_active": True}
                )
            )
        elif (credentials["email"] == self.admin_user["email"] and 
              credentials["password"] == self.admin_user["password"]):
            return MagicMock(
                session=MagicMock(
                    access_token="admin_access_token",
                    refresh_token="admin_refresh_token"
                ),
                user=MagicMock(
                    id=self.admin_user["id"],
                    email=self.admin_user["email"],
                    user_metadata={"full_name": self.admin_user["full_name"], "is_active": True, "is_superuser": True}
                )
            )
        else:
            raise Exception("Invalid email or password")
            
    def from_(self, table_name):
        """Mock from method."""
        self.current_table = table_name
        return self
        
    def select(self, *args):
        """Mock select method."""
        return self
        
    def eq(self, column, value):
        """Mock eq method."""
        return self
        
    def execute(self):
        """Mock execute method based on current table."""
        if self.current_table == "projects":
            return MagicMock(data=[{"id": "1", "name": "Test Project"}])
        elif self.current_table == "analyses":
            return MagicMock(data=[{"id": "1", "project_id": "1", "status": "completed"}])
        elif self.current_table == "reports":
            return MagicMock(data=[{"id": "1", "project_id": "1", "analysis_id": "1", "title": "Test Report"}])
        return MagicMock(data=[])

# Create test app with mocked dependencies
@pytest.fixture
def client(test_user, admin_user, test_project, test_analysis, test_report):
    """Create test client with mocked dependencies."""
    # Create mock supabase client
    mock_supabase_client = MockSupabaseClient(test_user, admin_user)
    
    # Mock functions that use supabase client
    with patch("summit_seo.web.api.core.supabase.get_supabase_client", return_value=mock_supabase_client), \
         patch("summit_seo.web.api.core.supabase.get_current_user") as mock_get_current_user, \
         patch("summit_seo.web.api.core.supabase.verify_token") as mock_verify_token:
        
        # Setup get_current_user mock
        def get_current_user_side_effect(token=None):
            if token == "test_access_token":
                user = MagicMock(
                    id=test_user["id"],
                    email=test_user["email"],
                    user_metadata={"full_name": test_user["full_name"], "is_active": True}
                )
                return user
            elif token == "admin_access_token":
                user = MagicMock(
                    id=admin_user["id"],
                    email=admin_user["email"],
                    user_metadata={"full_name": admin_user["full_name"], "is_active": True, "is_superuser": True}
                )
                return user
            else:
                raise Exception("Invalid token")
        
        mock_get_current_user.side_effect = get_current_user_side_effect
        mock_verify_token.side_effect = get_current_user_side_effect
        
        # Override config settings
        with patch("summit_seo.web.api.core.config.Settings"):
            # Import app here to use mocked dependencies
            from summit_seo.web.api.app import app
            
            # Create test client
            test_client = TestClient(app)
            
            yield test_client 