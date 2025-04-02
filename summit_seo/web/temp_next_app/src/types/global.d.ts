/// <reference types="@types/jest" />

// Extend the Jest namespace
declare namespace jest {
  interface Matchers<R> {
    toBeInTheDocument(): R;
    toHaveClass(className: string): R;
    toHaveAttribute(attr: string, value?: string): R;
    toBeDisabled(): R;
    toHaveValue(value: any): R;
    toBeVisible(options?: any): R;
    toHaveTextContent(text: string | RegExp): R;
  }
}

// Declare common types used in tests
interface Window {
  matchMedia(query: string): {
    matches: boolean;
    media: string;
    onchange: null;
    addListener: jest.Mock;
    removeListener: jest.Mock;
    addEventListener: jest.Mock;
    removeEventListener: jest.Mock;
    dispatchEvent: jest.Mock;
  };
}

// Declare types for external modules
declare module '@axe-core/playwright' {
  export default class AxeBuilder {
    constructor(options: { page: any });
    analyze(): Promise<{
      violations: Array<{
        id: string;
        impact: string;
        description: string;
        nodes: Array<{
          html: string;
          target: string[];
        }>;
      }>;
    }>;
  }
}

declare module 'next-router-mock/MemoryRouterProvider' {
  import React from 'react';
  
  interface MemoryRouterProviderProps {
    url?: string;
    initialEntries?: string[];
    children: React.ReactNode;
  }
  
  export const MemoryRouterProvider: React.FC<MemoryRouterProviderProps>;
}

// Extend existing modules
declare module 'framer-motion' {
  const motion: {
    div: React.FC<any>;
    span: React.FC<any>;
    [key: string]: React.FC<any>;
  };
} 