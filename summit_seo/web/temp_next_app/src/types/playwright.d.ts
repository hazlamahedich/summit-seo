declare module '@playwright/test' {
  export const test: {
    describe(name: string, callback: () => void): void;
    (name: string, callback: (props: { page: Page }) => Promise<void>): void;
    only(name: string, callback: (props: { page: Page }) => Promise<void>): void;
    skip(name: string, callback: (props: { page: Page }) => Promise<void>): void;
    beforeEach(callback: (props: { page: Page }) => Promise<void>): void;
    afterEach(callback: (props: { page: Page }) => Promise<void>): void;
    beforeAll(callback: () => Promise<void>): void;
    afterAll(callback: () => Promise<void>): void;
  };

  export const expect: {
    (value: any): {
      toBe(expected: any): void;
      toEqual(expected: any): void;
      toContain(expected: any): void;
      toBeTruthy(): void;
      toBeFalsy(): void;
      toBeGreaterThan(expected: number): void;
      toBeVisible(options?: { timeout?: number }): Promise<void>;
      toHaveCount(count: number): Promise<void>;
      toHaveText(text: string | RegExp, options?: { timeout?: number }): Promise<void>;
      toHaveURL(url: string | RegExp, options?: { timeout?: number }): Promise<void>;
      toHaveValue(value: string): Promise<void>;
      toHaveAttribute(name: string, value: string): Promise<void>;
    };
  };

  export interface Page {
    goto(url: string): Promise<void>;
    getByText(text: string | RegExp): Locator;
    getByRole(role: string, options?: { name?: string | RegExp }): Locator;
    getByLabel(label: string | RegExp): Locator;
    getByTestId(testId: string): Locator;
    keyboard: {
      press(key: string): Promise<void>;
    };
    evaluateHandle(fn: () => any): Promise<ElementHandle>;
  }

  export interface Locator {
    click(): Promise<void>;
    fill(value: string): Promise<void>;
    check(): Promise<void>;
    uncheck(): Promise<void>;
    isVisible(): Promise<boolean>;
    textContent(): Promise<string | null>;
    getAttribute(name: string): Promise<string | null>;
    count(): Promise<number>;
  }

  export interface ElementHandle {
    getAttribute(name: string): Promise<string | null>;
    evaluate<T>(fn: (element: Element) => T): Promise<T>;
  }

  export interface PlaywrightTestConfig {
    testDir?: string;
    timeout?: number;
    fullyParallel?: boolean;
    forbidOnly?: boolean;
    retries?: number;
    workers?: number | undefined;
    reporter?: any[];
    use?: {
      baseURL?: string;
      trace?: string;
      video?: string;
      screenshot?: string;
    };
    projects?: Array<{
      name: string;
      use: any;
    }>;
    webServer?: {
      command: string;
      url: string;
      reuseExistingServer?: boolean;
      timeout?: number;
    };
  }

  export const devices: Record<string, any>;
} 