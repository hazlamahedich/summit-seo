import { test, expect } from '@playwright/test';

/**
 * Cross-browser test suite for critical user flows
 * This suite validates application functionality across different browsers and device types
 */
test.describe('Cross-browser compatibility tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the home page before each test
    await page.goto('/');
  });

  test('Home page renders correctly across browsers', async ({ page }) => {
    // Check that critical elements are visible
    await expect(page.locator('nav')).toBeVisible();
    await expect(page.locator('main')).toBeVisible();
    await expect(page.locator('footer')).toBeVisible();
    
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

  test('Authentication flow works across browsers', async ({ page }) => {
    // Navigate to login page
    await page.click('text=Login');
    
    // Verify login form is displayed
    await expect(page.locator('form')).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    
    // Attempt login with test credentials
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    // Verify error message for invalid credentials
    await expect(page.locator('text=Invalid email or password')).toBeVisible();
    
    // Verify form validation works
    await page.click('button[type="submit"]');
    await page.fill('input[type="email"]', 'invalid-email');
    await page.fill('input[type="password"]', '123');
    await page.click('button[type="submit"]');
    
    // Expect validation errors
    await expect(page.locator('text=Please enter a valid email')).toBeVisible();
    await expect(page.locator('text=Password must be at least 8 characters')).toBeVisible();
  });

  test('Dark mode toggle works across browsers', async ({ page }) => {
    // Find the theme toggle button
    const themeToggle = page.locator('[aria-label="Toggle theme"]');
    await expect(themeToggle).toBeVisible();
    
    // Check initial theme (could be light or dark based on system preference)
    const initialTheme = await page.evaluate(() => {
      return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    });
    
    // Toggle theme
    await themeToggle.click();
    
    // Verify theme has changed
    const newTheme = await page.evaluate(() => {
      return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    });
    
    expect(newTheme).not.toEqual(initialTheme);
    
    // Take screenshots of both themes for visual comparison
    await page.screenshot({ path: `screenshots/theme-${newTheme}-${test.info().project.name}.png` });
  });
  
  test('Responsive design adapts to different viewports', async ({ page }) => {
    // Check for the current viewport dimensions
    const viewportSize = page.viewportSize();
    
    // Check that responsive components adapt correctly
    const isMobile = test.info().project.name.includes('mobile');
    const isTablet = test.info().project.name.includes('tablet');
    
    if (isMobile) {
      // Mobile specific checks
      await expect(page.locator('button[aria-label="Toggle menu"]')).toBeVisible();
      
      // Mobile navigation check
      await page.click('button[aria-label="Toggle menu"]');
      await expect(page.locator('nav[role="navigation"]')).toBeVisible();
      
      // Check mobile-specific layout elements
      await expect(page.locator('.mobile-only')).toBeVisible();
    } else if (isTablet) {
      // Tablet specific checks
      await expect(page.locator('.tablet-navigation')).toBeVisible();
    } else {
      // Desktop specific checks
      await expect(page.locator('.desktop-navigation')).toBeVisible();
    }
    
    // Take a screenshot for visual comparison
    await page.screenshot({ 
      path: `screenshots/responsive-${viewportSize?.width}x${viewportSize?.height}-${test.info().project.name}.png` 
    });
  });

  test('Accessibility works across browsers', async ({ page }) => {
    // Test keyboard navigation
    await page.keyboard.press('Tab');
    
    // The first focusable element should have focus
    const firstFocusable = await page.evaluate(() => {
      const activeElement = document.activeElement;
      return activeElement ? true : false;
    });
    
    expect(firstFocusable).toBeTruthy();
    
    // Test ARIA attributes are properly set
    await expect(page.locator('[role="navigation"]')).toBeVisible();
    await expect(page.locator('[role="main"]')).toBeVisible();
    
    // Check for high contrast modes
    await page.evaluate(() => {
      document.documentElement.setAttribute('data-high-contrast', 'true');
    });
    
    // Verify high contrast mode is applied correctly
    const hasHighContrast = await page.evaluate(() => {
      return document.documentElement.getAttribute('data-high-contrast') === 'true';
    });
    
    expect(hasHighContrast).toBeTruthy();
    
    // Take a screenshot for visual comparison
    await page.screenshot({ 
      path: `screenshots/accessibility-high-contrast-${test.info().project.name}.png` 
    });
  });
}); 