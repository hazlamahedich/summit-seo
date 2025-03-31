# Summit SEO REST API

This is the RESTful API for the Summit SEO project, built with FastAPI.

## Structure

The API follows a modular structure:

```
summit_seo/web/api/
├── main.py              # Main FastAPI application
├── README.md            # This file
├── models/              # Pydantic models for the API
│   ├── __init__.py
│   └── common.py        # Common models like responses and pagination
├── routers/             # API routes organized by resource
│   ├── __init__.py
│   ├── auth.py          # Authentication routes
│   ├── users.py         # User management
│   ├── projects.py      # SEO project management
│   └── analyses.py      # Analysis operations
└── tests/               # API tests
    └── test_basic.py    # Basic API tests
```

## Features

- **Authentication**: JWT-based authentication with token refresh and revocation
- **User Management**: User creation, profile management, and admin operations
- **Project Management**: Create and manage SEO projects
- **Analyses**: Run SEO analyses on websites, view results and recommendations
- **Standardized Responses**: Consistent response format with proper error handling
- **Cross-Origin Resource Sharing (CORS)**: Configured for web client access
- **Request Logging**: Request ID tracking and timing

## API Routes

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get JWT token
- `POST /auth/refresh` - Refresh an access token
- `POST /auth/logout` - Logout and invalidate token

### Users

- `GET /users` - List all users (admin only)
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update current user profile
- `GET /users/{user_id}` - Get user by ID (admin only)
- `PUT /users/{user_id}` - Update user by ID (admin only)
- `DELETE /users/{user_id}` - Delete user by ID (admin only)

### Projects

- `GET /projects` - List all projects
- `POST /projects` - Create a new project
- `GET /projects/{project_id}` - Get project details
- `PUT /projects/{project_id}` - Update project
- `DELETE /projects/{project_id}` - Delete project
- `GET /projects/{project_id}/summary` - Get project summary

### Analyses

- `GET /projects/{project_id}/analyses` - List all analyses for a project
- `POST /projects/{project_id}/analyses` - Start a new analysis
- `GET /projects/{project_id}/analyses/{analysis_id}` - Get analysis details
- `DELETE /projects/{project_id}/analyses/{analysis_id}` - Delete analysis
- `GET /projects/{project_id}/analyses/latest` - Get latest analysis
- `GET /projects/{project_id}/analyses/{analysis_id}/results` - Get analysis results
- `GET /projects/{project_id}/analyses/{analysis_id}/results/{analyzer_type}` - Get specific analyzer results
- `GET /projects/{project_id}/analyses/{analysis_id}/recommendations` - Get prioritized recommendations
- `POST /projects/{project_id}/analyses/schedule` - Schedule recurring analysis

## Setup and Installation

1. Install dependencies:

```bash
pip install fastapi uvicorn pyjwt passlib
```

2. Run the API:

```bash
uvicorn summit_seo.web.api.main:app --reload
```

3. Access the API documentation:

Open your browser and navigate to: http://localhost:8000/docs

## Development

### Running Tests

```bash
pytest summit_seo/web/api/tests
```

### Adding a New Endpoint

1. Create or modify a router file in the `routers/` directory
2. Add models if needed in the `models/` directory
3. Include the router in `main.py` if it's a new router
4. Add tests for the new endpoint

## Authentication

The API uses JWT token-based authentication:

1. Obtain a token via the `/auth/login` endpoint
2. Include the token in the `Authorization` header:
   `Authorization: Bearer <your_token>`
3. For extended sessions, use the `/auth/refresh` endpoint to get a new token
4. Use `/auth/logout` to invalidate the token when done

## Response Format

All API responses follow a standardized format:

```json
{
  "status": "success",
  "data": { ... },
  "meta": { 
    "pagination": { ... }
  }
}
```

For errors:

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": { ... }
  }
}
```

## Next Steps

Future enhancements planned for the API:

- Database integration (replacing mock data)
- Rate limiting
- User roles and permissions refinement
- API versioning
- Export functionality for analysis results
- Webhook integration for analysis completion notifications 