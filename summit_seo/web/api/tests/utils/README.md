# Error Handling Test Utilities

This directory contains standalone test utilities for testing error handling functionality without depending on application settings or the pytest framework.

## Background

We encountered challenges with testing the error handling components due to settings validation issues. Specifically, the tests were failing with validation errors when importing modules that depend on the application settings.

## Solution

We created a set of standalone test utilities and scripts that:

1. Use Python's built-in `unittest` framework instead of pytest
2. Properly handle async functions using `asyncio`
3. Mock dependencies that would otherwise require settings validation
4. Run tests directly without relying on pytest fixtures or configuration

## Test Files

- `error_response.py`: Utility class for testing error responses
- `test_error_response_manual.py`: Tests for the ErrorResponse class
- `test_error_handlers_manual.py`: Tests for the exception handlers
- `test_middleware_manual.py`: Tests for the ErrorHandlingMiddleware
- `run_all_manual_tests.py`: Script to run all tests in a single test suite

## Running Tests

To run all tests, execute:

```
python web/api/tests/utils/run_all_manual_tests.py
```

To run individual test files:

```
python web/api/tests/utils/test_error_response_manual.py
python web/api/tests/utils/test_error_handlers_manual.py
python web/api/tests/utils/test_middleware_manual.py
```

## Test Coverage

The tests cover:

1. Error Response Structure
   - Basic error responses
   - Responses with details
   - Responses with suggestions
   - Minimal responses

2. Exception Handlers
   - HTTP exceptions
   - Validation exceptions
   - General exceptions

3. Middleware Functionality
   - Successfully handled requests
   - Error handling
   - Client IP detection

## Future Improvements

- Add these tests to the CI pipeline
- Expand test coverage to include more edge cases
- Consider integrating with pytest without the settings dependency 