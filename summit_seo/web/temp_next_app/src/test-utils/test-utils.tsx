import React, { ReactElement, ReactNode } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouterProvider } from 'next-router-mock/MemoryRouterProvider';

/**
 * Custom render function that includes common providers
 */
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  route?: string;
  initialEntries?: string[];
}

export function renderWithProviders(
  ui: ReactElement,
  {
    route = '/',
    initialEntries = ['/'],
    ...renderOptions
  }: CustomRenderOptions = {}
) {
  const AllProviders = ({ children }: { children: ReactNode }) => {
    return (
      <MemoryRouterProvider url={route} initialEntries={initialEntries}>
        {children}
      </MemoryRouterProvider>
    );
  };

  return {
    user: userEvent.setup(),
    ...render(ui, { wrapper: AllProviders, ...renderOptions }),
  };
}

/**
 * Helper to create a fake window resize event
 */
export function triggerResize(width: number, height: number) {
  window.innerWidth = width;
  window.innerHeight = height;
  window.dispatchEvent(new Event('resize'));
}

/**
 * Helper to wait for a specified time
 */
export function wait(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Helper to mock a successful fetch response
 */
export function mockFetchSuccess(data: any) {
  return jest.fn().mockImplementation(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve(data),
    })
  );
}

/**
 * Helper to mock a failed fetch response
 */
export function mockFetchFailure(error: string) {
  return jest.fn().mockImplementation(() =>
    Promise.resolve({
      ok: false,
      status: 400,
      statusText: error,
      json: () => Promise.resolve({ error }),
    })
  );
}

/**
 * Helper function to test async components
 */
export async function waitForComponentToRender(expectedText: string) {
  const element = await screen.findByText(expectedText);
  expect(element).toBeInTheDocument();
  return element;
}

/**
 * Helper to simulate an animation ending
 */
export function triggerAnimationEnd(element: HTMLElement) {
  const event = new Event('animationend', { bubbles: true });
  element.dispatchEvent(event);
}

/**
 * Helper to test file uploads in forms
 */
export function createMockFileList(files: File[]): FileList {
  return {
    ...files,
    item: (index: number) => files[index] || null,
    length: files.length,
    [Symbol.iterator]: function* () {
      for (let i = 0; i < this.length; i++) {
        yield this[i];
      }
    }
  } as unknown as FileList;
}

/**
 * Helper to create a mock file
 */
export function createMockFile(name: string, size: number, type: string): File {
  const file = new File([''], name, { type });
  Object.defineProperty(file, 'size', { value: size });
  return file;
}

/**
 * Helper to take a snapshot of certain elements
 */
export function takeSnapshot(element: HTMLElement) {
  const clone = element.cloneNode(true) as HTMLElement;
  // Remove any dynamic attributes that might cause false test failures
  const dynamicAttributes = ['id', 'style', 'data-testid'];
  dynamicAttributes.forEach(attr => {
    const elements = clone.querySelectorAll(`[${attr}]`);
    elements.forEach(el => el.removeAttribute(attr));
  });
  return clone.innerHTML;
} 