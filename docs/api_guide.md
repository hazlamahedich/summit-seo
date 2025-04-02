# Summit SEO API Guide

## Introduction

The Summit SEO API allows you to programmatically interact with the Summit SEO platform. This guide provides instructions on how to authenticate, make requests, and interpret responses.

## Authentication

The Summit SEO API uses JSON Web Tokens (JWT) for authentication. To authenticate your API requests:

1. Obtain an API token by logging in with your credentials
2. Include the token in the Authorization header of your requests

### Getting an API Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "your-email@example.com",
  "password": "your-password"
}
```

Response:

```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

### Refreshing an API Token

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Using the API Token

Include the token in your requests using the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## API Endpoints

### Projects

#### List Projects

```http
GET /api/v1/projects
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Response:

```json
{
  "status": "success",
  "data": [
    {
      "id": "1",
      "name": "My Website",
      "description": "My company website",
      "url": "https://example.com",
      "created_at": "2023-01-01T12:00:00Z",
      "updated_at": "2023-01-01T12:00:00Z"
    }
  ]
}
```

#### Get Project

```http
GET /api/v1/projects/{project_id}
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Create Project

```http
POST /api/v1/projects
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "New Project",
  "description": "Description of the project",
  "url": "https://example.com"
}
```

#### Update Project

```http
PUT /api/v1/projects/{project_id}
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "Updated Project Name",
  "description": "Updated description",
  "url": "https://example.com"
}
```

#### Delete Project

```http
DELETE /api/v1/projects/{project_id}
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Analyses

#### List Analyses

```http
GET /api/v1/projects/{project_id}/analyses
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Get Analysis

```http
GET /api/v1/analyses/{analysis_id}
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Create Analysis

```http
POST /api/v1/projects/{project_id}/analyses
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "settings": {
    "crawl_depth": 3,
    "analyze_js": true,
    "analyze_mobile": true,
    "analyze_security": true
  }
}
```

#### Get Analysis Status

```http
GET /api/v1/analyses/{analysis_id}/status
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Cancel Analysis

```http
POST /api/v1/analyses/{analysis_id}/cancel
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Reports

#### Generate Report

```http
POST /api/v1/analyses/{analysis_id}/reports
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "format": "pdf",
  "include_recommendations": true,
  "include_details": true
}
```

#### Get Report

```http
GET /api/v1/reports/{report_id}
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### List Reports

```http
GET /api/v1/projects/{project_id}/reports
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Users

#### Get Current User

```http
GET /api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Update User

```http
PUT /api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "full_name": "Updated Name",
  "email": "updated-email@example.com"
}
```

#### Change Password

```http
POST /api/v1/users/change-password
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "current_password": "current-password",
  "new_password": "new-password"
}
```

## Response Format

All API responses follow a consistent format:

```json
{
  "status": "success" | "error",
  "data": { ... } | null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message",
    "details": { ... }
  } | null
}
```

## Pagination

List endpoints support pagination using the following query parameters:

- `page`: Page number (default: 1)
- `page_size`: Number of items per page (default: 20, max: 100)

Example:

```http
GET /api/v1/projects?page=2&page_size=10
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Paginated responses include pagination information:

```json
{
  "status": "success",
  "data": [ ... ],
  "pagination": {
    "total": 45,
    "page": 2,
    "page_size": 10,
    "pages": 5
  }
}
```

## Rate Limiting

The API has rate limits to ensure fair usage:

- 100 requests per minute per IP address
- 1000 requests per hour per user

If you exceed the rate limit, you'll receive a 429 Too Many Requests status code.

## Error Codes

Common error codes you may encounter:

- `AUTHENTICATION_FAILED`: Invalid or expired token
- `PERMISSION_DENIED`: Insufficient permissions
- `RESOURCE_NOT_FOUND`: The requested resource doesn't exist
- `VALIDATION_ERROR`: Invalid request parameters
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `SERVER_ERROR`: Internal server error

## Webhooks

Summit SEO can send webhook notifications when certain events occur:

1. Go to your Profile Settings
2. Click "Webhooks"
3. Add a new webhook URL
4. Select the events you want to receive notifications for

Events include:

- `analysis.started`
- `analysis.completed`
- `analysis.failed`
- `report.generated`

## Code Examples

### Python

```python
import requests

API_URL = "https://api.summitseo.com"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Get all projects
response = requests.get(f"{API_URL}/api/v1/projects", headers=headers)
projects = response.json()["data"]

# Create a new analysis
analysis_data = {
    "settings": {
        "crawl_depth": 2,
        "analyze_js": True
    }
}
response = requests.post(
    f"{API_URL}/api/v1/projects/{project_id}/analyses",
    json=analysis_data,
    headers=headers
)
```

### JavaScript

```javascript
const apiUrl = 'https://api.summitseo.com';
const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';

// Get all projects
async function getProjects() {
  const response = await fetch(`${apiUrl}/api/v1/projects`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  const data = await response.json();
  return data.data;
}

// Create a new analysis
async function createAnalysis(projectId, settings) {
  const response = await fetch(`${apiUrl}/api/v1/projects/${projectId}/analyses`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ settings })
  });
  
  return await response.json();
}
```

## Additional Resources

- [API Reference](/api/v1/docs): Complete API reference
- [Postman Collection](https://github.com/summit-seo/api-postman): Postman collection with example requests
- [API Changelog](https://summitseo.com/api/changelog): Changes and updates to the API
- [GitHub Examples](https://github.com/summit-seo/api-examples): Example code in various languages 