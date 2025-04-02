/**
 * Browser mock utilities for cross-browser testing
 * Provides functions to simulate different browser environments and behaviors
 */

/**
 * Browser types supported for mocking
 */
export type BrowserType = 'chrome' | 'firefox' | 'safari' | 'edge';

/**
 * Mock browser user agent strings for different browsers
 */
export const USER_AGENTS = {
  chrome: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
  firefox: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
  safari: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
  edge: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76',
  // Mobile browsers
  mobileChrome: 'Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36',
  mobileSafari: 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
  tabletSafari: 'Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
};

/**
 * CSS prefixes for different browsers
 */
export const CSS_PREFIXES = {
  chrome: '-webkit-',
  firefox: '-moz-',
  safari: '-webkit-',
  edge: '-webkit-'
};

/**
 * Feature support flags for different browsers
 */
export const FEATURE_SUPPORT = {
  chrome: {
    webp: true,
    webm: true,
    flexGap: true,
    gridLayout: true,
    webWorkers: true,
    webGL: true
  },
  firefox: {
    webp: true,
    webm: true,
    flexGap: true,
    gridLayout: true,
    webWorkers: true,
    webGL: true
  },
  safari: {
    webp: true,
    webm: false,
    flexGap: true,
    gridLayout: true,
    webWorkers: true,
    webGL: true
  },
  edge: {
    webp: true,
    webm: true,
    flexGap: true,
    gridLayout: true,
    webWorkers: true,
    webGL: true
  }
};

/**
 * Mock window.matchMedia for testing responsive design
 * @param matches Whether the media query matches
 * @returns A mock matchMedia function
 */
export function createMatchMediaMock(matches: boolean = false) {
  return function matchMediaMock(query: string) {
    return {
      matches,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn()
    };
  };
}

/**
 * Create a mock for browser feature detection
 * @param browser The browser to mock
 * @returns An object with feature detection properties
 */
export function createBrowserFeatureMock(browser: BrowserType = 'chrome') {
  const features = FEATURE_SUPPORT[browser];
  
  return {
    // Canvas support
    hasCanvasSupport: true,
    
    // WebP support
    hasWebPSupport: features.webp,
    
    // WebM support
    hasWebMSupport: features.webm,
    
    // CSS Grid support
    hasGridSupport: features.gridLayout,
    
    // Flex gap support
    hasFlexGapSupport: features.flexGap,
    
    // Web Workers support
    hasWebWorkersSupport: features.webWorkers,
    
    // WebGL support
    hasWebGLSupport: features.webGL,
    
    // Touch support (useful for mobile testing)
    hasTouchSupport: browser === 'safari',
    
    // Custom browser detection methods
    isChrome: browser === 'chrome',
    isFirefox: browser === 'firefox',
    isSafari: browser === 'safari',
    isEdge: browser === 'edge'
  };
}

/**
 * Set up browser mocks for testing
 * @param browser The browser to mock
 * @param viewport The viewport size to mock
 */
export function setupBrowserMock(
  browser: BrowserType = 'chrome',
  viewport: { width: number; height: number } = { width: 1280, height: 800 }
) {
  // Mock user agent
  Object.defineProperty(window.navigator, 'userAgent', {
    value: USER_AGENTS[browser],
    configurable: true
  });
  
  // Mock window dimensions
  Object.defineProperty(window, 'innerWidth', {
    value: viewport.width,
    configurable: true
  });
  
  Object.defineProperty(window, 'innerHeight', {
    value: viewport.height,
    configurable: true
  });
  
  // Mock matchMedia for responsive design testing
  window.matchMedia = createMatchMediaMock(viewport.width >= 768);
  
  // Add browser feature detection
  const features = createBrowserFeatureMock(browser);
  
  // Mock media capabilities check using global functions instead of direct property assignment
  const mockDecodingInfo = jest.fn().mockResolvedValue({
    supported: features.hasWebMSupport,
    smooth: true,
    powerEfficient: true
  });

  // Add feature detection methods to window
  (window as any).checkWebMSupport = () => features.hasWebMSupport;
  (window as any).checkWebPSupport = () => features.hasWebPSupport;
  
  // Mock CSS vendor prefixing
  document.documentElement.style.setProperty('--browser-prefix', CSS_PREFIXES[browser]);
  
  // Add browser class to document for CSS targeting
  document.documentElement.classList.add(`browser-${browser}`);
  
  // Return cleanup function
  return function cleanup() {
    document.documentElement.classList.remove(`browser-${browser}`);
    delete (window as any).checkWebMSupport;
    delete (window as any).checkWebPSupport;
  };
}

/**
 * Simulate browser-specific behavior in tests
 * @param callback Function that receives browser information
 */
export function withBrowserBehavior(
  callback: (browserInfo: { name: BrowserType; features: any }) => void
) {
  const browsers: BrowserType[] = ['chrome', 'firefox', 'safari', 'edge'];
  
  browsers.forEach(browser => {
    const cleanup = setupBrowserMock(browser);
    try {
      callback({
        name: browser,
        features: createBrowserFeatureMock(browser)
      });
    } finally {
      cleanup();
    }
  });
} 