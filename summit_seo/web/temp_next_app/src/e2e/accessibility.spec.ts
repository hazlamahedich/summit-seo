import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

/**
 * Accessibility testing suite
 * Tests application for accessibility compliance across browsers
 */
test.describe('Accessibility tests', () => {
  // Pages to test for accessibility
  const pagesToTest = [
    { name: 'home', path: '/' },
    { name: 'login', path: '/login' },
    { name: 'dashboard', path: '/dashboard' },
    { name: 'settings', path: '/settings' }
  ];
  
  // Test each page for accessibility
  for (const page of pagesToTest) {
    test(`Page ${page.name} should not have any automatically detectable accessibility issues`, async ({ page: playPage }) => {
      // Navigate to the page
      await playPage.goto(page.path);
      
      try {
        // Run the accessibility scan
        const accessibilityScanResults = await new AxeBuilder({ page: playPage }).analyze();
        
        // Output violations to help with debugging
        if (accessibilityScanResults.violations.length > 0) {
          console.log(`Accessibility violations on ${page.name}:`, 
            accessibilityScanResults.violations.map(v => ({
              id: v.id,
              impact: v.impact,
              description: v.description,
              nodes: v.nodes.map(n => n.html)
            }))
          );
        }
        
        // Assert no violations
        expect(accessibilityScanResults.violations).toEqual([]);
      } catch (error) {
        console.error(`Error running accessibility tests on ${page.name}:`, error);
        throw error;
      }
    });
  }
  
  test('Keyboard navigation works correctly', async ({ page }) => {
    // Go to home page
    await page.goto('/');
    
    // Test Tab navigation
    await page.keyboard.press('Tab');
    
    // Check if first focusable element is focused (usually skip to content link)
    const firstElementFocused = await page.evaluate(() => {
      const activeElement = document.activeElement;
      return activeElement ? 
        {
          tagName: activeElement.tagName.toLowerCase(),
          text: activeElement.textContent?.trim() || '',
          hasFocus: activeElement === document.activeElement
        } : null;
    });
    
    expect(firstElementFocused?.hasFocus).toBeTruthy();
    
    // Tab through important elements
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press('Tab');
      
      // Check if some element has focus after each Tab
      const elementHasFocus = await page.evaluate(() => {
        return document.activeElement !== document.body;
      });
      
      expect(elementHasFocus).toBeTruthy();
    }
    
    // Ensure we can navigate to important controls with keyboard
    await page.keyboard.press('Tab'); // Continue tabbing to reach common controls
    
    // Try to find and interact with a button using keyboard
    await page.keyboard.press('Enter');
    
    // Take a screenshot to see the result of keyboard interaction
    await page.screenshot({ 
      path: `screenshots/accessibility-keyboard-${test.info().project.name}.png` 
    });
  });
  
  test('Screen reader content is properly set', async ({ page }) => {
    // Go to home page
    await page.goto('/');
    
    // Check for common screen reader elements
    
    // Skip links should be present
    const skipLink = page.locator('a[href="#main-content"]');
    await expect(skipLink).toHaveCount(1);
    
    // Images should have alt text
    const imagesWithoutAlt = page.locator('img:not([alt]):not([role="presentation"])');
    await expect(imagesWithoutAlt).toHaveCount(0);
    
    // Buttons should have accessible names
    const buttonsWithoutName = page.locator('button:not([aria-label]):not(:has(text))');
    await expect(buttonsWithoutName).toHaveCount(0);
    
    // Forms should have labels
    const inputsWithoutLabels = page.locator('input:not([aria-label]):not([aria-labelledby]):not([type="hidden"])');
    await expect(inputsWithoutLabels).toHaveCount(0);
    
    // ARIA landmarks should be used appropriately
    const mainElement = page.locator('main');
    await expect(mainElement).toHaveCount(1);
    
    const navElement = page.locator('nav');
    await expect(navElement).toHaveCount(1);
    
    // Check for proper heading hierarchy
    const h1Elements = page.locator('h1');
    await expect(h1Elements).toHaveCount(1);
  });
  
  test('Color contrast meets accessibility standards', async ({ page }) => {
    // Go to home page
    await page.goto('/');
    
    // Check for color contrast issues using axe
    const contrastResults = await new AxeBuilder({ page })
      .withRules(['color-contrast'])
      .analyze();
    
    // Output any contrast issues
    if (contrastResults.violations.length > 0) {
      console.log('Color contrast issues:', 
        contrastResults.violations.map(v => ({
          id: v.id,
          impact: v.impact,
          description: v.description,
          nodes: v.nodes.map(n => n.html)
        }))
      );
    }
    
    // Assert no contrast violations
    expect(contrastResults.violations).toEqual([]);
    
    // Test with high contrast mode
    await page.evaluate(() => {
      document.documentElement.setAttribute('data-high-contrast', 'true');
    });
    
    // Take a screenshot with high contrast mode
    await page.screenshot({ 
      path: `screenshots/accessibility-high-contrast-${test.info().project.name}.png` 
    });
    
    // Run contrast check again in high contrast mode
    const highContrastResults = await new AxeBuilder({ page })
      .withRules(['color-contrast'])
      .analyze();
    
    expect(highContrastResults.violations).toEqual([]);
  });
  
  test('Reduced motion preference is respected', async ({ page }) => {
    // Go to page with animations
    await page.goto('/animation-demo');
    
    // Test with reduced motion preference
    await page.emulateMedia({ reducedMotion: 'reduce' });
    
    // Take a screenshot with reduced motion
    await page.screenshot({ 
      path: `screenshots/accessibility-reduced-motion-${test.info().project.name}.png` 
    });
    
    // Check if reduced motion class is applied
    const hasReducedMotionClass = await page.evaluate(() => {
      return document.documentElement.classList.contains('reduce-motion') ||
             document.documentElement.getAttribute('data-reduced-motion') === 'true';
    });
    
    expect(hasReducedMotionClass).toBeTruthy();
    
    // Try to trigger an animation and verify it's disabled or modified
    const animationButton = page.locator('button.animated-button').first();
    if (await animationButton.count() > 0) {
      await animationButton.click();
      
      // Check if animation is disabled or modified (this depends on your implementation)
      const animationDisabled = await page.evaluate(() => {
        const style = window.getComputedStyle(document.querySelector('.animated-button'));
        return style.animationDuration === '0s' || 
               style.animationName === 'none' ||
               document.documentElement.classList.contains('reduce-motion');
      });
      
      expect(animationDisabled).toBeTruthy();
    }
  });
}); 