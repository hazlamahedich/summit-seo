"""Tests for the users endpoints."""

import pytest
from typing import Dict

def test_get_current_user(client):
    """Test getting the current user."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Use the token to get current user
    response = client.get(
        "/users/me", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["email"] == "testuser@example.com"
    assert "id" in data["data"]
    assert "full_name" in data["data"]

def test_update_user(client):
    """Test updating a user."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Get the current user first to know what data to update
    me_response = client.get(
        "/users/me", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    user_data = me_response.json()["data"]
    
    # Update the user's display name
    new_display_name = f"Test User {user_data['id']}"
    update_data = {
        "display_name": new_display_name
    }
    
    # Use the token to update the user
    response = client.patch(
        "/users/me", 
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["display_name"] == new_display_name
    
    # Verify the update was saved by getting the user again
    me_response = client.get(
        "/users/me", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    user_data = me_response.json()["data"]
    assert user_data["display_name"] == new_display_name

def test_update_user_email(client):
    """Test updating a user's email."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Get the current user first
    me_response = client.get(
        "/users/me", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    user_data = me_response.json()["data"]
    
    # Update the user's email
    new_email = f"updated_{user_data['id']}@example.com"
    update_data = {
        "email": new_email
    }
    
    # Use the token to update the user's email
    response = client.patch(
        "/users/me", 
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["email"] == new_email
    
    # Verify the update was saved
    me_response = client.get(
        "/users/me", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    user_data = me_response.json()["data"]
    assert user_data["email"] == new_email

def test_unauthorized_access(client):
    """Test unauthorized access to user endpoints."""
    # Try to access user endpoint without token
    response = client.get("/users/me")
    assert response.status_code == 401
    
    # Try with invalid token
    response = client.get(
        "/users/me", 
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401

def test_change_password(client):
    """Test changing a user's password."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Change password
    response = client.post(
        "/users/me/change-password", 
        json={
            "current_password": "password",
            "new_password": "newpassword123"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Try logging in with the new password
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "newpassword123"}
    )
    assert login_response.status_code == 200
    
    # Reset the password back to original for other tests
    new_token = login_response.json()["data"]["access_token"]
    response = client.post(
        "/users/me/change-password", 
        json={
            "current_password": "newpassword123",
            "new_password": "password"
        },
        headers={"Authorization": f"Bearer {new_token}"}
    )
    assert response.status_code == 200 