"""Tests for the reports endpoints."""

import pytest
from typing import Dict

def test_list_reports(client):
    """Test listing reports for a project."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Use the token to access reports for project ID 1
    response = client.get(
        "/projects/1/reports", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "total" in data["data"]
    assert "items" in data["data"]

def test_list_reports_with_analysis_filter(client):
    """Test listing reports filtered by analysis ID."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Use the token to access reports for project ID 1 filtered by analysis ID 1
    response = client.get(
        "/projects/1/reports?analysis_id=1", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Check that all items are for the specified analysis
    if data["data"]["items"]:
        for item in data["data"]["items"]:
            assert item["analysis_id"] == 1

def test_create_report(client):
    """Test creating a new report."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Create a new report
    report_data = {
        "analysis_id": 1,
        "title": "Test Report",
        "description": "A test report",
        "format": "pdf",
        "settings": {
            "include_charts": True,
            "include_recommendations": True
        }
    }
    
    response = client.post(
        "/projects/1/reports", 
        json=report_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["title"] == "Test Report"
    assert data["data"]["format"] == "pdf"
    assert data["data"]["status"] == "pending"

def test_get_report_by_id(client):
    """Test getting a specific report by ID."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # First create a report to ensure we have one
    report_data = {
        "analysis_id": 1,
        "title": "Test Report for Get",
        "format": "pdf"
    }
    
    create_response = client.post(
        "/projects/1/reports", 
        json=report_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 201
    report_id = create_response.json()["data"]["id"]
    
    # Now get the report by ID
    response = client.get(
        f"/projects/1/reports/{report_id}", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["id"] == report_id
    assert data["data"]["title"] == "Test Report for Get"

def test_download_report(client):
    """Test downloading a report."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # First create a report
    report_data = {
        "analysis_id": 1,
        "title": "Test Report for Download",
        "format": "pdf"
    }
    
    create_response = client.post(
        "/projects/1/reports", 
        json=report_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 201
    report_id = create_response.json()["data"]["id"]
    
    # Try to download the report, but it should fail because it's not ready
    response = client.get(
        f"/projects/1/reports/{report_id}/download", 
        headers={"Authorization": f"Bearer {token}"}
    )
    # Since the report is newly created, it should be in "pending" status
    # and not ready for download
    assert response.status_code == 400

def test_get_reports_summary(client):
    """Test getting a summary of reports for a project."""
    # First login to get a token
    login_response = client.post(
        "/auth/login", 
        json={"email": "testuser@example.com", "password": "password"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    
    # Get the reports summary
    response = client.get(
        "/projects/1/reports/summary", 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Check that the summary fields are present
    summary = data["data"]
    assert "total_reports" in summary
    assert "completed_reports" in summary
    assert "failed_reports" in summary
    assert "pending_reports" in summary 