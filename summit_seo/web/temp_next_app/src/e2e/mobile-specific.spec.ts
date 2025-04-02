import { test, expect } from '@playwright/test';

/**
 * Mobile-specific test suite
 * Tests mobile interactions and gesture handling
 * Skip these tests on desktop browsers
 */
test.describe('Mobile interactions', () => {
  // Only run on mobile projects
  test.beforeEach(async ({ page, browserName }) => {
    // Skip these tests on desktop browsers
    test.skip(
      !['mobile-chrome', 'mobile-safari', 'tablet-safari'].includes(test.info().project.name),
      'This test is only for mobile browsers'
    );
    
    // Navigate to the home page
    await page.goto('/');
  });

  test('Mobile navigation menu works', async ({ page }) => {
    // Check that the hamburger menu is visible
    const menuButton = page.locator('button[aria-label="Toggle menu"]');
    await expect(menuButton).toBeVisible();
    
    // Click the hamburger menu
    await menuButton.click();
    
    // Check that the mobile navigation menu is visible
    const mobileNav = page.locator('nav[role="navigation"]');
    await expect(mobileNav).toBeVisible();
    
    // Verify navigation links are visible
    await expect(page.locator('text=Dashboard')).toBeVisible();
    await expect(page.locator('text=Projects')).toBeVisible();
    await expect(page.locator('text=Settings')).toBeVisible();
    
    // Click outside to close menu
    await page.locator('body').click({ position: { x: 10, y: 10 } });
    
    // Check that the mobile navigation is hidden
    await expect(mobileNav).toBeHidden();
  });

  test('Touch gestures work on carousel', async ({ page }) => {
    // Navigate to page with carousel
    await page.goto('/features');
    
    // Get the carousel element
    const carousel = page.locator('.carousel');
    await expect(carousel).toBeVisible();
    
    // Get initial active slide
    const initialActiveSlide = await page.locator('.carousel-slide.active').getAttribute('data-slide-index');
    
    // Perform swipe left gesture
    const carouselBox = await carousel.boundingBox();
    if (carouselBox) {
      // Swipe from right to left
      await page.mouse.move(
        carouselBox.x + carouselBox.width * 0.8,
        carouselBox.y + carouselBox.height * 0.5
      );
      await page.mouse.down();
      await page.mouse.move(
        carouselBox.x + carouselBox.width * 0.2,
        carouselBox.y + carouselBox.height * 0.5,
        { steps: 10 }
      );
      await page.mouse.up();
    }
    
    // Wait for the transition to complete
    await page.waitForTimeout(500);
    
    // Get new active slide
    const newActiveSlide = await page.locator('.carousel-slide.active').getAttribute('data-slide-index');
    
    // Check that the slide has changed
    expect(newActiveSlide).not.toEqual(initialActiveSlide);
    
    // Take screenshot of the carousel after swipe
    await page.screenshot({
      path: `screenshots/mobile-carousel-swipe-${test.info().project.name}.png`
    });
  });

  test('Pull-to-refresh functionality', async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/dashboard');
    
    // Simulate pull-to-refresh gesture
    const mainContent = page.locator('main');
    await expect(mainContent).toBeVisible();
    
    const mainBox = await mainContent.boundingBox();
    if (mainBox) {
      // Start from the top center and pull down
      await page.mouse.move(
        mainBox.x + mainBox.width * 0.5,
        mainBox.y + 10
      );
      await page.mouse.down();
      await page.mouse.move(
        mainBox.x + mainBox.width * 0.5,
        mainBox.y + 200,
        { steps: 10 }
      );
      
      // Hold for a moment
      await page.waitForTimeout(300);
      
      // Release
      await page.mouse.up();
    }
    
    // Check for loading indicator
    const loadingIndicator = page.locator('.loading-indicator');
    await expect(loadingIndicator).toBeVisible();
    
    // Wait for refresh to complete
    await page.waitForTimeout(1000);
    
    // Take screenshot after refresh
    await page.screenshot({
      path: `screenshots/mobile-pull-refresh-${test.info().project.name}.png`
    });
  });

  test('Pinch zoom on images', async ({ page }) => {
    // Navigate to page with images
    await page.goto('/gallery');
    
    // Find an image
    const image = page.locator('.zoomable-image').first();
    await expect(image).toBeVisible();
    
    // Get initial size
    const initialSize = await image.evaluate(node => {
      const { width, height } = node.getBoundingClientRect();
      return { width, height };
    });
    
    // Take screenshot before zoom
    await page.screenshot({
      path: `screenshots/mobile-image-before-zoom-${test.info().project.name}.png`
    });
    
    // Simulate pinch-to-zoom gesture (this is a simplified simulation)
    const imageBox = await image.boundingBox();
    if (imageBox) {
      // Center point of the image
      const centerX = imageBox.x + imageBox.width / 2;
      const centerY = imageBox.y + imageBox.height / 2;
      
      // Playwright doesn't directly support multi-touch, so we simulate with mouse
      await page.evaluate((centerX, centerY) => {
        // Create and dispatch custom event for pinch zoom
        const pinchEvent = new CustomEvent('pinchzoom', {
          detail: {
            scale: 2.0,
            centerX,
            centerY
          }
        });
        document.dispatchEvent(pinchEvent);
      }, centerX, centerY);
    }
    
    // Wait for zoom effect
    await page.waitForTimeout(500);
    
    // Take screenshot after zoom attempt
    await page.screenshot({
      path: `screenshots/mobile-image-after-zoom-${test.info().project.name}.png`
    });
  });
}); 