# Summit SEO API Documentation

## Overview
The Summit SEO API provides a comprehensive set of endpoints for managing SEO analysis projects, running analyses, and generating reports. The API follows RESTful principles and uses JWT for authentication.

## Base URL
```
https://api.summitseo.com/v1
```

## Authentication
All API endpoints require authentication using JWT (JSON Web Tokens).

### Obtaining a Token
1. Send a POST request to `/auth/login` with your credentials:
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

2. The response will include your access token:
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
}
```

### Using the Token
Include the token in the Authorization header:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Common Response Format
All API responses follow this format:
```json
{
    "status": "success|error",
    "data": {
        // Response data
    },
    "meta": {
        // Additional metadata
    }
}
```

## Error Responses
The API uses standard HTTP status codes and provides detailed error information:

### 400 Bad Request
```json
{
    "status": "error",
    "error": {
        "code": "BAD_REQUEST",
        "message": "Invalid request parameters",
        "details": {
            "field": "error description"
        }
    }
}
```

### 401 Unauthorized
```json
{
    "status": "error",
    "error": {
        "code": "UNAUTHORIZED",
        "message": "Invalid or expired token"
    }
}
```

### 404 Not Found
```json
{
    "status": "error",
    "error": {
        "code": "NOT_FOUND",
        "message": "Resource not found"
    }
}
```

## Endpoints

### Authentication
#### POST /auth/login
Login to obtain access token.

**Request:**
```json
{
    "username": "string",
    "password": "string"
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "access_token": "string",
        "token_type": "bearer"
    }
}
```

### Projects
#### GET /projects
List all projects for the current user.

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 10, max: 100)

**Response:**
```json
{
    "status": "success",
    "data": {
        "total": 100,
        "items": [
            {
                "id": 1,
                "name": "Example Project",
                "description": "Project description",
                "created_at": "2024-03-20T10:00:00Z",
                "updated_at": "2024-03-20T10:00:00Z"
            }
        ]
    }
}
```

#### POST /projects
Create a new project.

**Request:**
```json
{
    "name": "string",
    "description": "string"
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "id": 1,
        "name": "string",
        "description": "string",
        "created_at": "2024-03-20T10:00:00Z",
        "updated_at": "2024-03-20T10:00:00Z"
    }
}
```

### Analyses
#### GET /projects/{project_id}/analyses
List all analyses for a project.

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 10, max: 100)

**Response:**
```json
{
    "status": "success",
    "data": {
        "total": 50,
        "items": [
            {
                "id": 1,
                "project_id": 1,
                "status": "completed",
                "started_at": "2024-03-20T10:00:00Z",
                "completed_at": "2024-03-20T10:01:00Z",
                "settings": {
                    "url": "https://example.com",
                    "analyze_js": true
                }
            }
        ]
    }
}
```

#### POST /projects/{project_id}/analyses
Create a new analysis.

**Request:**
```json
{
    "settings": {
        "url": "string",
        "analyze_js": boolean,
        "analyze_mobile": boolean,
        "analyze_security": boolean
    }
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "id": 1,
        "project_id": 1,
        "status": "pending",
        "created_at": "2024-03-20T10:00:00Z",
        "updated_at": "2024-03-20T10:00:00Z",
        "settings": {
            "url": "string",
            "analyze_js": true,
            "analyze_mobile": true,
            "analyze_security": true
        }
    }
}
```

### Reports
#### GET /projects/{project_id}/reports
List all reports for a project.

**Query Parameters:**
- `analysis_id`: Filter by analysis ID (optional)
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 10, max: 100)

**Response:**
```json
{
    "status": "success",
    "data": {
        "total": 25,
        "items": [
            {
                "id": 1,
                "project_id": 1,
                "analysis_id": 1,
                "title": "SEO Analysis Report",
                "format": "pdf",
                "status": "completed",
                "created_at": "2024-03-20T10:00:00Z",
                "generated_at": "2024-03-20T10:05:00Z",
                "file_url": "https://storage.summitseo.com/reports/1.pdf",
                "file_size": 1024000,
                "file_type": "application/pdf"
            }
        ]
    }
}
```

#### POST /projects/{project_id}/reports
Create a new report.

**Request:**
```json
{
    "analysis_id": 1,
    "title": "string",
    "description": "string",
    "format": "pdf|html|json",
    "settings": {
        "include_charts": true,
        "include_recommendations": true
    }
}
```

**Response:**
```json
{
    "status": "success",
    "data": {
        "id": 1,
        "project_id": 1,
        "analysis_id": 1,
        "title": "string",
        "description": "string",
        "format": "pdf",
        "status": "pending",
        "created_at": "2024-03-20T10:00:00Z",
        "updated_at": "2024-03-20T10:00:00Z",
        "settings": {
            "include_charts": true,
            "include_recommendations": true
        }
    }
}
```

#### GET /projects/{project_id}/reports/{report_id}/download
Download a generated report.

**Response:**
```json
{
    "status": "success",
    "data": {
        "download_url": "https://storage.summitseo.com/reports/1.pdf",
        "file_type": "application/pdf",
        "file_size": 1024000
    }
}
```

## Rate Limiting
The API implements rate limiting to ensure fair usage:
- 100 requests per minute per user
- 1000 requests per hour per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1616234400
```

## Versioning
The API is versioned through the URL path:
- Current version: v1
- Example: `https://api.summitseo.com/v1/projects`

## Webhooks
The API supports webhooks for asynchronous operations:

### Report Generation
When a report is generated, a POST request is sent to the configured webhook URL:

```json
{
    "event": "report.generated",
    "data": {
        "report_id": 1,
        "project_id": 1,
        "status": "completed",
        "file_url": "https://storage.summitseo.com/reports/1.pdf"
    },
    "timestamp": "2024-03-20T10:05:00Z"
}
```

## SDK Examples
The API provides official SDKs for popular programming languages:

### Python
```python
from summit_seo import SummitSEO

client = SummitSEO(api_key="your_api_key")

# Create a project
project = client.projects.create(
    name="My Website",
    description="SEO analysis for my website"
)

# Run an analysis
analysis = client.analyses.create(
    project_id=project.id,
    settings={
        "url": "https://example.com",
        "analyze_js": True
    }
)

# Generate a report
report = client.reports.create(
    project_id=project.id,
    analysis_id=analysis.id,
    title="SEO Report",
    format="pdf"
)
```

### JavaScript
```javascript
const { SummitSEO } = require('summit-seo');

const client = new SummitSEO({
    apiKey: 'your_api_key'
});

// Create a project
const project = await client.projects.create({
    name: 'My Website',
    description: 'SEO analysis for my website'
});

// Run an analysis
const analysis = await client.analyses.create({
    projectId: project.id,
    settings: {
        url: 'https://example.com',
        analyzeJs: true
    }
});

// Generate a report
const report = await client.reports.create({
    projectId: project.id,
    analysisId: analysis.id,
    title: 'SEO Report',
    format: 'pdf'
});
``` 