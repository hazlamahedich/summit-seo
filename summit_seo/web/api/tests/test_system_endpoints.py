"""Tests for the system endpoints."""

import pytest
from typing import Dict

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["status"] == "healthy"
    assert "timestamp" in data["data"]
    assert "version" in data["data"]
    assert "api_version" in data["data"]

def test_service_status(client):
    """Test the service status endpoint."""
    response = client.get("/system/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["status"] == "operational"
    assert "environment" in data["data"]
    assert "version" in data["data"]
    assert "api_version" in data["data"]
    assert "timestamp" in data["data"]
    assert "uptime" in data["data"]
    assert "load" in data["data"]
    assert "memory" in data["data"]
    assert "instance_id" in data["data"]

def test_system_info_without_auth(client):
    """Test that system info endpoint requires authentication."""
    response = client.get("/system/info")
    assert response.status_code == 401

def test_system_info_with_non_admin(client):
    """Test that system info endpoint requires admin privileges."""
    # First login as a regular user
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Try to access system info with a regular user token
    response = client.get(
        "/system/info", 
        headers={"Authorization": f"Bearer {token}"}
    )
    # Should be forbidden for regular users
    assert response.status_code == 403

def test_system_info_with_admin(client):
    """Test accessing system info with admin credentials."""
    # Login as an admin user
    login_response = client.post(
        "/auth/login", 
        json={"email": "admin@example.com", "password": "adminpassword"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Access system info with admin token
    response = client.get(
        "/system/info", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "system" in data["data"]
    assert "memory" in data["data"]
    assert "disk" in data["data"]
    assert "cpu" in data["data"]
    assert "app" in data["data"]
    assert "timestamp" in data["data"]

def test_restart_service_without_auth(client):
    """Test that restart service endpoint requires authentication."""
    response = client.post("/system/restart")
    assert response.status_code == 401

def test_restart_service_with_non_admin(client):
    """Test that restart service endpoint requires admin privileges."""
    # First login as a regular user
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Try to restart service with a regular user token
    response = client.post(
        "/system/restart", 
        headers={"Authorization": f"Bearer {token}"}
    )
    # Should be forbidden for regular users
    assert response.status_code == 403

def test_restart_service_with_admin(client):
    """Test restarting service with admin credentials."""
    # Login as an admin user
    login_response = client.post(
        "/auth/login", 
        json={"email": "admin@example.com", "password": "adminpassword"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Restart service with admin token
    response = client.post(
        "/system/restart", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["status"] == "restart_requested"
    assert "message" in data["data"]
    assert "estimated_completion" in data["data"]
    assert "request_id" in data["data"]

def test_system_config_without_auth(client):
    """Test that system config endpoint requires authentication."""
    response = client.get("/system/config")
    assert response.status_code == 401

def test_system_config_with_non_admin(client):
    """Test that system config endpoint requires admin privileges."""
    # First login as a regular user
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Try to access system config with a regular user token
    response = client.get(
        "/system/config", 
        headers={"Authorization": f"Bearer {token}"}
    )
    # Should be forbidden for regular users
    assert response.status_code == 403

def test_system_config_with_admin(client):
    """Test accessing system config with admin credentials."""
    # Login as an admin user
    login_response = client.post(
        "/auth/login", 
        json={"email": "admin@example.com", "password": "adminpassword"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Access system config with admin token
    response = client.get(
        "/system/config", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    # Config data structure will depend on your system implementation 