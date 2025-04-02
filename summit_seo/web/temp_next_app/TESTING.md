# Summit SEO Testing Documentation

This document outlines the testing strategy for the Summit SEO frontend application.

## Overview

Our testing strategy follows a comprehensive approach with multiple levels of testing:

1. **Unit Testing** - For individual components and utilities
2. **Integration Testing** - For component interactions 
3. **End-to-End Testing** - For complete user flows
4. **Accessibility Testing** - To ensure the application is accessible to all users

## Testing Technologies

- **Jest** - Unit and integration test framework
- **React Testing Library** - Component testing
- **Playwright** - End-to-end testing and accessibility testing with Axe

## Running Tests

### Unit and Integration Tests

```bash
# Run all tests
npm test

# Run tests in watch mode (for development)
npm run test:watch

# Generate coverage report
npm run test:coverage
```

Test files are located alongside the components they test in `__tests__` directories.

### End-to-End Tests

```bash
# Run all E2E tests
npm run e2e

# Run E2E tests with UI mode for debugging
npm run e2e:ui

# Run E2E tests with debugging
npm run e2e:debug

# View the latest test report
npm run e2e:report
```

E2E test files are located in the `/e2e` directory.

## Test File Organization

- **Unit Tests**: Located in `__tests__` directories next to the components they test
- **E2E Tests**: Located in the `/e2e` directory
- **Test Utilities**: Shared utilities are in `src/test-utils`

## Testing Guidelines

### Component Testing

1. Test component rendering with default props
2. Test component rendering with various prop combinations
3. Test user interactions (clicks, keyboard navigation, form input)
4. Test state changes and conditional rendering
5. Mock external dependencies and context providers

### End-to-End Testing

1. Focus on critical user journeys (e.g., authentication, main features)
2. Test across multiple browsers (Chrome, Firefox, Safari)
3. Test both desktop and mobile viewports
4. Include accessibility checks with Axe
5. Test keyboard navigation

### Accessibility Testing

1. Automated testing with Axe
2. Keyboard navigation testing
3. Screen reader compatibility
4. Color contrast and readability

## Best Practices

1. Avoid testing implementation details
2. Prefer user-centric testing approaches
3. Write tests that resemble how users interact with the application
4. Maintain isolated tests with proper cleanup
5. Use meaningful test descriptions
6. Focus on behavior over implementation
7. Keep tests simple and maintainable

## Test Data

- Use mock data for component tests
- Create test data factories for consistent data generation
- Isolate test data between tests

## Continuous Integration

Tests are automatically run in CI/CD pipeline:
- Unit and integration tests run on every pull request
- E2E tests run on main branch changes and release branches
- Test failures block merges to protected branches

## Coverage Goals

We aim for:
- 80%+ code coverage for unit and integration tests
- Critical paths covered by E2E tests
- All components checked for accessibility compliance 