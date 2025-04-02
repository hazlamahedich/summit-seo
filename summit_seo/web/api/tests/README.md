# Summit SEO API Tests

This directory contains tests for the Summit SEO API. The tests cover various endpoints including authentication, users, projects, analyses, reports, and system endpoints.

## Test Structure

The tests are organized by endpoint type:

- `test_auth_endpoints.py`: Tests for authentication endpoints
- `test_users_endpoints.py`: Tests for user management endpoints
- `test_projects_endpoints.py`: Tests for project management endpoints
- `test_analyses_endpoints.py`: Tests for analysis endpoints
- `test_reports_endpoints.py`: Tests for report endpoints
- `test_system_endpoints.py`: Tests for system management endpoints

## Running the Tests

To run all API tests:

```bash
pytest web/api/tests/
```

To run tests for a specific endpoint:

```bash
pytest web/api/tests/test_auth_endpoints.py
```

To run with verbose output:

```bash
pytest -v web/api/tests/
```

## Configuration and Known Issues

The tests use a custom `conftest.py` file to mock dependencies like the database and Supabase client. This allows the tests to run without requiring actual connectivity to external services.

### Pydantic Settings Validation Issues

There are currently validation issues with the `Settings` class in the tests. The Pydantic validation complains about the `DATABASE_URL` configuration value. There are several possible workarounds:

1. Use environment variables for testing:
   ```bash
   export DATABASE_URL="postgresql://postgres:postgres@localhost/summit_seo_test"
   pytest web/api/tests/
   ```

2. Create a .env file in the project root with the required settings

3. Run tests with pytest-env plugin to set environment variables:
   ```bash
   pip install pytest-env
   # Add to pytest.ini:
   # [pytest]
   # env =
   #     DATABASE_URL=postgresql://postgres:postgres@localhost/summit_seo_test
   ```

4. Modify the Settings class to accept both `DATABASE_URL` and `SQLALCHEMY_DATABASE_URI`

## Test Coverage

The tests cover:

- Authentication (registration, login, logout, token refresh)
- User operations (profile retrieval, updates, password changes)
- Project management (creation, listing, retrieval, updates)
- Analysis operations (creation, status checking, results retrieval)
- Report generation and management
- System endpoints (health checks, status, configuration)

## Adding New Tests

When adding new tests:

1. Follow the existing patterns
2. Use the fixtures provided in `conftest.py`
3. Mock any new external dependencies
4. Ensure tests are isolated and don't depend on external state

## Test Fixtures

The test suite provides several useful fixtures:

- `client`: A FastAPI TestClient for making requests
- `test_user`: A sample user for testing
- `admin_user`: A sample admin user for testing
- `test_project`: A sample project for testing
- `test_analysis`: A sample analysis for testing
- `mock_supabase`: A mocked Supabase client
- `mock_response`: A generic mocked response 