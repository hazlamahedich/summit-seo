"""Tests for the authentication endpoints."""

import pytest
from typing import Dict
import uuid

def test_register(client):
    """Test user registration."""
    # Create a unique email for this test to avoid conflicts
    unique_email = f"test-{uuid.uuid4()}@example.com"
    
    # Register a new user
    response = client.post(
        "/auth/register", 
        json={
            "email": unique_email,
            "password": "securepassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["email"] == unique_email
    assert data["data"]["full_name"] == "Test User"
    assert "id" in data["data"]
    
    # Try to register again with the same email, should fail
    response = client.post(
        "/auth/register", 
        json={
            "email": unique_email,
            "password": "securepassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 400

def test_login(client):
    """Test user login."""
    # Login with valid credentials
    response = client.post(
        "/auth/login", 
        json={
            "email": "testuser@example.com",
            "password": "password"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"
    
    # Login with invalid credentials
    response = client.post(
        "/auth/login", 
        json={
            "email": "testuser@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

def test_logout(client):
    """Test user logout."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={
            "email": "testuser@example.com",
            "password": "password"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Now logout with the token
    response = client.post(
        "/auth/logout", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204
    
    # Try to use the token after logout (should fail)
    response = client.get(
        "/users/me", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401

def test_refresh_token(client):
    """Test refreshing an access token."""
    # First login to get tokens
    login_response = client.post(
        "/auth/login", 
        json={
            "email": "testuser@example.com",
            "password": "password"
        }
    )
    assert login_response.status_code == 200
    refresh_token = login_response.json()["data"]["refresh_token"]
    
    # Now use the refresh token to get a new access token
    response = client.post(
        "/auth/refresh", 
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"
    
    # The new refresh token should be different
    assert data["data"]["refresh_token"] != refresh_token

def test_password_reset_request(client):
    """Test requesting a password reset."""
    # Request password reset for an existing email
    response = client.post(
        "/auth/password-reset-request", 
        json={"email": "testuser@example.com"}
    )
    assert response.status_code == 200
    
    # Request for non-existent email should still return 200
    # (for security reasons, to avoid leaking whether an email exists)
    response = client.post(
        "/auth/password-reset-request", 
        json={"email": "nonexistent@example.com"}
    )
    assert response.status_code == 200

def test_get_current_user(client):
    """Test getting the current user profile."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={
            "email": "testuser@example.com",
            "password": "password"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Use the token to get the user profile
    response = client.get(
        "/auth/me", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["email"] == "testuser@example.com"
    assert "id" in data["data"]
    assert "full_name" in data["data"]
    
    # Try without a token
    response = client.get("/auth/me")
    assert response.status_code == 401
    
    # Try with an invalid token
    response = client.get(
        "/auth/me", 
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401 