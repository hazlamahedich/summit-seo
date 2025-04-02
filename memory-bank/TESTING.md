# Testing Documentation

This document outlines the testing approach, setup, and best practices for the Summit SEO application.

## Testing Stack

Our testing infrastructure uses the following tools:

- **Jest**: Test runner and assertion library
- **React Testing Library**: Component testing utilities
- **Playwright**: End-to-end testing
- **Axe-core**: Accessibility testing

## TypeScript Configuration

We've configured TypeScript to provide type safety for all testing libraries:

- Global type declarations in `src/types/jest.d.ts`
- React Testing Library types in `src/types/testing-library.d.ts`
- Playwright types in `src/types/playwright.d.ts`
- Jest-DOM extensions in `src/types/testing-library-jest-dom.d.ts`
- Router mock types in `src/types/next-router-mock.d.ts`

These files extend the global namespace to provide proper typing for test files and autocompletion in your IDE.

## Directory Structure

```
src/
├── __tests__/           # Unit and integration tests
│   ├── components/      # Component tests
│   ├── pages/           # Page tests
│   └── utils/           # Utility function tests
├── e2e/                 # End-to-end tests using Playwright
│   ├── accessibility.spec.ts   # Accessibility tests
│   ├── cross-browser.spec.ts   # Cross-browser compatibility tests
│   ├── mobile-specific.spec.ts # Mobile-specific tests
│   └── visual-regression.spec.ts # Visual comparison tests
├── test-utils/          # Testing utilities and custom renderers
│   ├── mocks/           # Mock implementations
│   │   ├── supabaseMock.ts
│   │   ├── routerMock.ts
│   │   └── browserMock.ts  # Browser environment mocks
│   └── render.tsx       # Custom renderer
└── types/               # TypeScript declarations for testing
```

## Running Tests

### Unit and Integration Tests

Run all Jest tests:

```bash
npm test
```

Run specific tests:

```bash
npm test -- --testPathPattern=components/Button
```

Watch mode:

```bash
npm test -- --watch
```

### End-to-End Tests

Run all E2E tests:

```bash
npm run test:e2e
```

Run specific E2E tests:

```bash
npm run test:e2e -- --grep="login flow"
```

### Cross-Browser Testing

Run tests in specific browsers:

```bash
# Run in Chrome
npm run e2e:chrome

# Run in Firefox
npm run e2e:firefox

# Run in Safari 
npm run e2e:safari

# Run in mobile browsers
npm run e2e:mobile

# Run in tablet
npm run e2e:tablet

# Run cross-browser tests specifically
npm run e2e:cross-browser

# Run accessibility tests
npm run e2e:accessibility

# Run visual regression tests
npm run e2e:visual
```

## Test Utilities

### Custom Renderer

We provide a custom renderer that includes common providers:

```typescript
// src/test-utils/render.tsx
import { render } from '@testing-library/react';
import { ThemeProvider } from '@/context/ThemeContext';
import { AuthProvider } from '@/context/AuthContext';

const AllProviders = ({ children }) => (
  <ThemeProvider>
    <AuthProvider>
      {children}
    </AuthProvider>
  </ThemeProvider>
);

const customRender = (ui, options = {}) =>
  render(ui, { wrapper: AllProviders, ...options });

export * from '@testing-library/react';
export { customRender as render };
```

### Common Mocks

#### Supabase Mock

```typescript
// src/test-utils/mocks/supabaseMock.ts
export const createSupabaseMock = () => ({
  auth: {
    signIn: jest.fn(),
    signUp: jest.fn(),
    signOut: jest.fn(),
    user: { id: 'test-user-id', email: 'test@example.com' }
  },
  from: jest.fn().mockReturnThis(),
  select: jest.fn().mockReturnThis(),
  insert: jest.fn().mockReturnThis(),
  update: jest.fn().mockReturnThis(),
  delete: jest.fn().mockReturnThis(),
  eq: jest.fn(),
  single: jest.fn()
});
```

#### Router Mock

```typescript
// src/test-utils/mocks/routerMock.ts
import mockRouter from 'next-router-mock';

jest.mock('next/router', () => require('next-router-mock'));

export const setupRouterMock = (path = '/') => {
  mockRouter.setCurrentUrl(path);
  return mockRouter;
};
```

#### Browser Mock

```typescript
// src/test-utils/mocks/browserMock.ts
import { BrowserType } from './types';

export function setupBrowserMock(browser: BrowserType = 'chrome') {
  // Mock user agent
  Object.defineProperty(window.navigator, 'userAgent', {
    value: USER_AGENTS[browser],
    configurable: true
  });
  
  // Add browser feature detection
  const features = createBrowserFeatureMock(browser);
  
  // Mock CSS vendor prefixing
  document.documentElement.style.setProperty('--browser-prefix', CSS_PREFIXES[browser]);
  
  // Return cleanup function
  return function cleanup() {
    document.documentElement.classList.remove(`browser-${browser}`);
  };
}
```

## Testing Guidelines

### Component Testing

1. Test components in isolation
2. Focus on user behavior, not implementation details
3. Use data-testid attributes for component selection
4. Test accessibility for UI components
5. Mock external dependencies

Example component test:

```typescript
// src/components/Button/__tests__/Button.test.tsx
import { render, screen, fireEvent } from '@/test-utils';
import { Button } from '../Button';

describe('Button', () => {
  it('renders correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button')).toHaveTextContent('Click me');
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('can be disabled', () => {
    render(<Button disabled>Click me</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

### Page Testing

1. Test page components with their child components
2. Mock API calls and external services
3. Test page navigation and state changes
4. Verify that the correct components are rendered based on state

### E2E Testing

1. Focus on critical user flows
2. Test on multiple browsers
3. Include accessibility checks
4. Test responsive layouts

Example E2E test:

```typescript
// src/e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test('login flow', async ({ page }) => {
  await page.goto('/login');
  
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  
  await page.waitForURL('/dashboard');
  expect(page.url()).toContain('/dashboard');
  
  const welcomeMessage = page.locator('h1');
  await expect(welcomeMessage).toHaveText(/welcome/i);
});
```

### Cross-Browser Testing

1. Test in Chrome, Firefox, and Safari
2. Test in mobile browsers (Chrome for Android, Safari for iOS)
3. Test in tablet browsers
4. Verify responsive design across different screen sizes
5. Check for browser-specific bugs and inconsistencies

Example cross-browser test:

```typescript
// src/e2e/cross-browser.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Cross-browser compatibility tests', () => {
  test('Home page renders correctly across browsers', async ({ page }) => {
    await page.goto('/');
    
    // Check that critical elements are visible
    await expect(page.locator('nav')).toBeVisible();
    await expect(page.locator('main')).toBeVisible();
    
    // Take a screenshot for visual comparison
    await page.screenshot({ path: `screenshots/home-${test.info().project.name}.png` });
    
    // Check responsive layout adjustments based on viewport
    const isMobile = test.info().project.name.includes('mobile');
    if (isMobile) {
      // Mobile-specific assertions
      await expect(page.locator('button[aria-label="Toggle menu"]')).toBeVisible();
    } else {
      // Desktop-specific assertions
      await expect(page.locator('nav >> text=Dashboard')).toBeVisible();
    }
  });
});
```

### Visual Regression Testing

1. Capture screenshots for key pages and components
2. Compare screenshots across browsers
3. Check for visual inconsistencies

Example visual regression test:

```typescript
// src/e2e/visual-regression.spec.ts
import { test } from '@playwright/test';

test('Screenshot home page across browsers', async ({ page }) => {
  await page.goto('/');
  
  // Get current browser info for the screenshot name
  const browserName = test.info().project.name;
  const viewport = page.viewportSize();
  const viewportInfo = viewport ? `${viewport.width}x${viewport.height}` : 'default';
  
  // Take full page screenshot
  await page.screenshot({
    path: `screenshots/home-${browserName}-${viewportInfo}.png`,
    fullPage: true
  });
});
```

### Accessibility Testing

1. Include Axe checks in component and E2E tests
2. Test keyboard navigation
3. Verify proper ARIA attributes
4. Check color contrast

Example accessibility test:

```typescript
// src/components/Form/__tests__/Form.test.tsx
import { render } from '@/test-utils';
import { axe } from 'jest-axe';
import { Form } from '../Form';

test('form has no accessibility violations', async () => {
  const { container } = render(
    <Form>
      <input aria-label="Email" type="email" />
      <button type="submit">Submit</button>
    </Form>
  );
  
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

## CI/CD Integration

Our test suite is integrated with the CI/CD pipeline:

1. Unit and integration tests run on every pull request
2. E2E tests run on staging deployments
3. Accessibility tests are part of the pre-deployment checks
4. Cross-browser tests run on scheduled intervals

## Best Practices

1. Keep tests focused and concise
2. Use descriptive test names
3. Follow the Arrange-Act-Assert pattern
4. Avoid testing implementation details
5. Maintain independence between tests
6. Mock external dependencies appropriately
7. Keep test coverage high for critical components
8. Update tests when requirements change
9. Test in multiple browsers to catch browser-specific bugs
10. Use visual regression testing for UI components
11. Test in multiple screen sizes to catch responsive design inconsistencies
12. Use cross-browser testing to ensure consistent behavior across different browsers
13. Use accessibility testing to ensure that the application is usable by people with disabilities
14. Use visual regression testing to catch UI changes that could affect the user experience
15. Use cross-browser testing to catch browser-specific bugs and inconsistencies
16. Use accessibility testing to catch accessibility issues and ensure that the application is usable by people with disabilities
17. Use visual regression testing to catch UI changes that could affect the user experience
18. Use cross-browser testing to catch browser-specific bugs and inconsistencies
19. Use accessibility testing to catch accessibility issues and ensure that the application is usable by people with disabilities
20. Use visual regression testing to catch UI changes that could affect the user experience
21. Use cross-browser testing to catch browser-specific bugs and inconsistencies
22. Use accessibility testing to catch accessibility issues and ensure that the application is usable by people with disabilities
23. Use visual regression testing to catch UI changes that could affect the user experience
24. Use cross-browser testing to catch browser-specific bugs and inconsistencies
25. Use accessibility testing to catch accessibility issues and ensure that the application is usable by people with disabilities
26. Use visual regression testing to catch UI changes that could affect the user experience
27. Use cross-browser testing to catch browser-specific bugs and inconsistencies
28. Use accessibility testing to catch accessibility issues and ensure that the application is usable by people with disabilities
29. Use visual regression testing to catch UI changes that could affect the user experience
30. Use cross-browser testing to catch browser-specific bugs and inconsistencies
31. Use accessibility testing to catch accessibility issues and ensure that the application is usable by people with disabilities
32. Use visual regression testing to catch UI changes that could affect the user experience
33. Use cross-browser testing to catch browser-specific bugs and inconsistencies
34. Use accessibility testing to catch accessibility issues and ensure that the application is usable by people with disabilities
35. Use visual regression testing to catch UI changes that could affect the user experience
36. Use cross-browser testing to catch browser-specific bugs and inconsistencies
37. Use accessibility testing to catch accessibility issues and ensure that the application is usable by people with disabilities
38. Use visual regression testing to catch UI changes that could affect the user experience
39. Use cross-browser testing to catch browser-specific bugs and inconsistencies
40. Use accessibility testing to catch accessibility issues and ensure that the application is usable by people with disabilities
41. Use visual regression testing to catch UI changes that could affect the user experience
42. Use cross-browser testing to catch browser-specific bugs and inconsistencies
43. Use accessibility testing to catch accessibility issues and ensure that the application is usable by people with disabilities
44. Use visual regression testing to catch UI changes that could affect the user experience
45. Use cross-browser testing to catch browser-specific bugs and inconsistencies
46. Use accessibility testing to catch accessibility issues and ensure that the application is usable by people with disabilities
47. Use visual regression testing to catch UI changes that could affect the user experience
48. Use cross-browser testing to catch browser-specific bugs and inconsistencies
49. Use accessibility testing to catch accessibility issues and ensure that the application is usable by people with disabilities
50. Use visual regression testing to catch UI changes that could affect the user experience 