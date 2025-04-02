import pytest
from fastapi.testclient import TestClient
from summit_seo.web.api.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["healthy"] is True
    assert data["data"]["service"] == "summit-seo-api"

def test_root_redirect():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "API documentation" in data["message"]

def test_login_validation():
    """Test validation errors on login endpoint."""
    response = client.post("/auth/login", json={})
    assert response.status_code == 422
    data = response.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == "VALIDATION_ERROR"

def test_login_authentication():
    """Test successful login with test user."""
    response = client.post(
        "/auth/login", 
        json={"username": "testuser", "password": "password"}
    )
    # This should succeed because we have a mock user in the fake database
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"

def test_protected_endpoint_without_token():
    """Test accessing a protected endpoint without token."""
    response = client.get("/users/me")
    assert response.status_code == 401

def test_protected_endpoint_with_token():
    """Test accessing a protected endpoint with token."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"username": "testuser", "password": "password"}
    )
    token = login_response.json()["data"]["access_token"]
    
    # Use the token to access a protected endpoint
    response = client.get(
        "/users/me", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["username"] == "testuser"

def test_project_list():
    """Test listing projects endpoint."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"username": "testuser", "password": "password"}
    )
    token = login_response.json()["data"]["access_token"]
    
    # Use the token to access projects
    response = client.get(
        "/projects", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "pagination" in data["meta"]
    # We should have at least one project in our mock database
    assert len(data["data"]) > 0

def test_analysis_list():
    """Test listing analyses for a project."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"username": "testuser", "password": "password"}
    )
    token = login_response.json()["data"]["access_token"]
    
    # Use the token to access analyses for project ID 1
    response = client.get(
        "/projects/1/analyses", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "pagination" in data["meta"]
    # We should have at least one analysis in our mock database
    assert len(data["data"]) > 0

def test_analysis_results():
    """Test getting analysis results."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"username": "testuser", "password": "password"}
    )
    token = login_response.json()["data"]["access_token"]
    
    # Use the token to access results for analysis ID 1 in project ID 1
    response = client.get(
        "/projects/1/analyses/1/results", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "overall_score" in data["data"]
    assert "category_scores" in data["data"]
    assert "findings" in data["data"]
    assert "recommendations" in data["data"] 