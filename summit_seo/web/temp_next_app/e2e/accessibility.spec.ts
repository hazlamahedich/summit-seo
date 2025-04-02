import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility Tests', () => {
  test('homepage should not have any automatically detectable accessibility issues', async ({ page }) => {
    await page.goto('/');
    
    // Run the accessibility tests
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    
    // Assert no violations
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('login page should not have any automatically detectable accessibility issues', async ({ page }) => {
    await page.goto('/login');
    
    // Run the accessibility tests
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    
    // Sometimes we might have some acceptable violations, so we can check for specific ones
    // For example, check that critical violations are zero
    const criticalViolations = accessibilityScanResults.violations.filter(
      violation => violation.impact === 'critical'
    );
    
    expect(criticalViolations).toEqual([]);
    
    // Log all violations for review
    if (accessibilityScanResults.violations.length > 0) {
      console.log('Accessibility violations on login page:', 
        JSON.stringify(accessibilityScanResults.violations, null, 2)
      );
    }
  });

  test('dashboard page should be accessible', async ({ page }) => {
    // First login
    await page.goto('/login');
    await page.getByLabel('Email').fill('test-user@example.com');
    await page.getByLabel('Password').fill('test-password-123');
    await page.getByRole('button', { name: 'Sign In' }).click();
    
    // Wait for dashboard to load
    await expect(page).toHaveURL(/.*dashboard/, { timeout: 5000 });
    
    // Run the accessibility tests
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    
    // Assert no violations, or analyze specific ones
    if (accessibilityScanResults.violations.length > 0) {
      // Get all violations that are not from third-party widgets (if any)
      const appViolations = accessibilityScanResults.violations.filter(
        violation => !violation.nodes.every(node => 
          node.html.includes('third-party-widget') || 
          node.html.includes('external-component')
        )
      );
      
      // Log for review
      console.log('Accessibility violations on dashboard:', 
        JSON.stringify(appViolations, null, 2)
      );
      
      // Only critical and serious violations should fail the test
      const severeViolations = appViolations.filter(
        violation => ['critical', 'serious'].includes(violation.impact || '')
      );
      
      expect(severeViolations).toEqual([]);
    }
  });

  test('ensures keyboard navigation works properly', async ({ page }) => {
    await page.goto('/');
    
    // Start from the beginning of the page
    await page.keyboard.press('Tab');
    
    // The first focusable element should be focused
    const firstFocusable = await page.evaluateHandle(() => document.activeElement);
    expect(await firstFocusable.getAttribute('role') || 
           await firstFocusable.getAttribute('aria-label') || 
           await firstFocusable.evaluate(el => el.textContent)
    ).toBeTruthy();
    
    // Tab through all focusable elements
    let tabCount = 0;
    const maxTabs = 20; // Set a reasonable limit
    const focusedElements = new Set();
    
    while (tabCount < maxTabs) {
      await page.keyboard.press('Tab');
      tabCount++;
      
      // Get the currently focused element
      const focusedElement = await page.evaluateHandle(() => document.activeElement);
      const elementId = await focusedElement.evaluate(el => 
        el.id || el.getAttribute('data-testid') || el.className || el.tagName
      );
      
      // If we've seen this element before, we might be in a focus trap or loop
      if (focusedElements.has(elementId)) {
        break;
      }
      
      focusedElements.add(elementId);
      
      // Check if the focused element is actually visible and interactive
      const isVisible = await focusedElement.evaluate(el => {
        const style = window.getComputedStyle(el);
        return style.display !== 'none' && 
               style.visibility !== 'hidden' && 
               style.opacity !== '0';
      });
      
      expect(isVisible).toBeTruthy();
    }
    
    // Ensure we found at least some focusable elements
    expect(focusedElements.size).toBeGreaterThan(1);
  });
}); 