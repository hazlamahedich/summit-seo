import { test, expect } from '@playwright/test';

/**
 * Visual regression test suite
 * Captures screenshots across different browsers and viewports for visual comparison
 */
test.describe('Visual regression tests', () => {
  
  // Pages to capture for visual regression testing
  const pagesToTest = [
    { name: 'home', path: '/' },
    { name: 'login', path: '/login' },
    { name: 'dashboard', path: '/dashboard' },
    { name: 'projects', path: '/projects' },
    { name: 'settings', path: '/settings' }
  ];
  
  // Test each page in different viewports
  for (const page of pagesToTest) {
    test(`Screenshot ${page.name} page across browsers`, async ({ page: playPage }) => {
      // Navigate to the page
      await playPage.goto(page.path, { waitUntil: 'networkidle' });
      
      // Get current browser and viewport info for the screenshot name
      const browserName = test.info().project.name;
      const viewport = playPage.viewportSize();
      const viewportInfo = viewport ? `${viewport.width}x${viewport.height}` : 'default';
      
      // Create screenshots directory if it doesn't exist
      await playPage.evaluate(() => {
        if (!window.fs) {
          return;
        }
        if (!window.fs.existsSync('./screenshots')) {
          window.fs.mkdirSync('./screenshots', { recursive: true });
        }
      });
      
      // Take full page screenshot
      await playPage.screenshot({
        path: `screenshots/${page.name}-${browserName}-${viewportInfo}.png`,
        fullPage: true
      });
      
      // Desktop specific tests for pages that require login
      if (!page.path.includes('login') && !page.path.includes('/')) {
        // We would normally be logged in here for the dashboard, projects, etc.
        // For test purposes, we check if we are redirected to login
        const currentUrl = new URL(playPage.url());
        expect(currentUrl.pathname).toContain('login');
      }
    });
  }
  
  // Test theme variations (light/dark mode)
  test('Theme variations across browsers', async ({ page }) => {
    // Navigate to home page
    await page.goto('/');
    
    // Get browser and viewport info
    const browserName = test.info().project.name;
    const viewport = page.viewportSize();
    const viewportInfo = viewport ? `${viewport.width}x${viewport.height}` : 'default';
    
    // Test light theme
    await page.evaluate(() => {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
    });
    
    await page.screenshot({
      path: `screenshots/theme-light-${browserName}-${viewportInfo}.png`,
      fullPage: true
    });
    
    // Test dark theme
    await page.evaluate(() => {
      document.documentElement.classList.remove('light');
      document.documentElement.classList.add('dark');
    });
    
    await page.screenshot({
      path: `screenshots/theme-dark-${browserName}-${viewportInfo}.png`,
      fullPage: true
    });
  });
  
  // Test responsive design breakpoints
  test('Responsive design breakpoints', async ({ page }) => {
    // Navigate to home page
    await page.goto('/');
    
    // Get browser info
    const browserName = test.info().project.name;
    
    // Common breakpoints to test
    const breakpoints = [
      { name: 'xs', width: 320, height: 568 },
      { name: 'sm', width: 640, height: 800 },
      { name: 'md', width: 768, height: 1024 },
      { name: 'lg', width: 1024, height: 768 },
      { name: 'xl', width: 1280, height: 800 },
      { name: '2xl', width: 1536, height: 864 }
    ];
    
    // Test each breakpoint
    for (const bp of breakpoints) {
      await page.setViewportSize({ width: bp.width, height: bp.height });
      
      // Wait for any responsive adjustments to take effect
      await page.waitForTimeout(500);
      
      // Take screenshot at this breakpoint
      await page.screenshot({
        path: `screenshots/responsive-${bp.name}-${bp.width}x${bp.height}-${browserName}.png`,
        fullPage: true
      });
    }
  });
  
  // Test animation frames
  test('Animation key frames', async ({ page }) => {
    // Navigate to animation demo page
    await page.goto('/animation-demo');
    
    // Get browser info
    const browserName = test.info().project.name;
    
    // Capture button hover animation
    const button = page.locator('button.animated-button').first();
    
    // Before hover
    await page.screenshot({
      path: `screenshots/animation-before-hover-${browserName}.png`
    });
    
    // Hover state
    await button.hover();
    await page.waitForTimeout(500); // Wait for hover animation
    
    await page.screenshot({
      path: `screenshots/animation-hover-${browserName}.png`
    });
    
    // Click animation
    await button.click();
    await page.waitForTimeout(100); // Capture during animation
    
    await page.screenshot({
      path: `screenshots/animation-click-${browserName}.png`
    });
  });
}); 