"""Tests for the analyses endpoints."""

import pytest
from typing import Dict

def test_list_analyses(client):
    """Test listing analyses for a project."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
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

def test_get_analysis_by_id(client):
    """Test getting a specific analysis by ID."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Use the token to access a specific analysis by ID
    response = client.get(
        "/projects/1/analyses/1", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["id"] == "1"
    assert data["data"]["project_id"] == "1"

def test_create_analysis(client):
    """Test creating a new analysis."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Use the token to create a new analysis
    response = client.post(
        "/projects/1/analyses", 
        json={"config": {"url": "https://example.com"}},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert "id" in data["data"]
    assert data["data"]["project_id"] == "1"
    assert data["data"]["status"] == "pending"

def test_get_analysis_results(client):
    """Test getting analysis results."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
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

def test_get_analysis_findings(client):
    """Test getting analysis findings."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Use the token to access findings for analysis ID 1 in project ID 1
    response = client.get(
        "/projects/1/analyses/1/findings", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert isinstance(data["data"], list)
    # Assuming there's at least one finding
    if data["data"]:
        assert "id" in data["data"][0]
        assert "analysis_id" in data["data"][0]
        assert "category" in data["data"][0]
        assert "message" in data["data"][0]

def test_cancel_analysis(client):
    """Test canceling an analysis."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # First create a new analysis to cancel
    create_response = client.post(
        "/projects/1/analyses", 
        json={"config": {"url": "https://example.com"}},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 201
    analysis_id = create_response.json()["data"]["id"]
    
    # Use the token to cancel the analysis
    response = client.post(
        f"/projects/1/analyses/{analysis_id}/cancel", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Verify the analysis was canceled
    check_response = client.get(
        f"/projects/1/analyses/{analysis_id}", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert check_response.status_code == 200
    check_data = check_response.json()
    assert check_data["data"]["status"] == "cancelled" 