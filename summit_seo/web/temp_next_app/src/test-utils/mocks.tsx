import React, { ReactNode } from 'react';
import { SupabaseClient } from '@supabase/supabase-js';

/**
 * Common mock data for tests
 */
export const mockUsers = [
  { 
    id: 'user-1', 
    email: 'test-user@example.com',
    created_at: '2023-01-01T00:00:00.000Z',
    last_sign_in_at: '2023-02-01T00:00:00.000Z',
  },
  { 
    id: 'user-2', 
    email: 'admin@example.com',
    created_at: '2023-01-02T00:00:00.000Z',
    last_sign_in_at: '2023-02-02T00:00:00.000Z',
  },
];

export const mockProjects = [
  {
    id: 'project-1',
    name: 'Example Website',
    url: 'https://example.com',
    created_at: '2023-03-01T00:00:00.000Z',
    user_id: 'user-1',
  },
  {
    id: 'project-2',
    name: 'Test Website',
    url: 'https://test.example.com',
    created_at: '2023-03-02T00:00:00.000Z',
    user_id: 'user-1',
  },
];

export const mockAnalyses = [
  {
    id: 'analysis-1',
    project_id: 'project-1',
    status: 'completed',
    score: 85,
    created_at: '2023-04-01T00:00:00.000Z',
    completed_at: '2023-04-01T00:10:00.000Z',
  },
  {
    id: 'analysis-2',
    project_id: 'project-1',
    status: 'in_progress',
    score: null,
    created_at: '2023-04-02T00:00:00.000Z',
    completed_at: null,
  },
];

/**
 * Mock Supabase client for testing
 */
export const createMockSupabaseClient = () => {
  const mockSupabase = {
    auth: {
      getUser: jest.fn().mockResolvedValue({ 
        data: { user: mockUsers[0] }, 
        error: null 
      }),
      signUp: jest.fn().mockResolvedValue({ 
        data: { user: mockUsers[0] },
        error: null 
      }),
      signInWithPassword: jest.fn().mockResolvedValue({ 
        data: { user: mockUsers[0] },
        error: null 
      }),
      signOut: jest.fn().mockResolvedValue({ error: null }),
      onAuthStateChange: jest.fn().mockImplementation((callback) => {
        // Simulate auth state change
        callback('SIGNED_IN', { user: mockUsers[0] });
        return { data: { subscription: { unsubscribe: jest.fn() } } };
      }),
    },
    from: jest.fn().mockImplementation((table) => ({
      select: jest.fn().mockReturnThis(),
      insert: jest.fn().mockReturnThis(),
      update: jest.fn().mockReturnThis(),
      delete: jest.fn().mockReturnThis(),
      eq: jest.fn().mockReturnThis(),
      match: jest.fn().mockReturnThis(),
      order: jest.fn().mockReturnThis(),
      limit: jest.fn().mockReturnThis(),
      single: jest.fn().mockReturnThis(),
      then: jest.fn().mockImplementation((callback) => {
        let data;
        let error = null;

        // Return appropriate mock data based on table
        if (table === 'projects') {
          data = { data: mockProjects, error: null };
        } else if (table === 'analyses') {
          data = { data: mockAnalyses, error: null };
        } else {
          data = { data: [], error: null };
        }

        return Promise.resolve(callback(data));
      }),
    })),
  } as unknown as SupabaseClient;

  return mockSupabase;
};

/**
 * Mock React Query provider for testing
 */
export const mockReactQuery = {
  useQuery: jest.fn().mockImplementation((queryKey, queryFn) => {
    return {
      data: null,
      isLoading: false,
      isError: false,
      error: null,
      refetch: jest.fn(),
    };
  }),
  useMutation: jest.fn().mockImplementation((mutationFn) => {
    return {
      mutate: jest.fn(),
      mutateAsync: jest.fn().mockResolvedValue({}),
      isLoading: false,
      isError: false,
      error: null,
    };
  }),
};

/**
 * Mock router for Next.js tests
 */
export const mockRouter = {
  push: jest.fn(),
  replace: jest.fn(),
  prefetch: jest.fn(),
  back: jest.fn(),
  pathname: '/',
  query: {},
  events: {
    on: jest.fn(),
    off: jest.fn(),
    emit: jest.fn(),
  },
};

/**
 * Utility for rendering with providers
 */
export const mockProviders = {
  wrapper: ({ children }: { children: ReactNode }) => {
    return children;
  },
};

/**
 * Helper to simulate media query matches
 */
export const mockMediaQuery = (matches: boolean) => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation(query => ({
      matches,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    })),
  });
};

/**
 * Helper to mock localStorage
 */
export const mockLocalStorage = () => {
  const localStorageMock = (() => {
    let store: Record<string, string> = {};
    return {
      getItem: jest.fn((key: string) => store[key] || null),
      setItem: jest.fn((key: string, value: string) => {
        store[key] = value.toString();
      }),
      removeItem: jest.fn((key: string) => {
        delete store[key];
      }),
      clear: jest.fn(() => {
        store = {};
      }),
    };
  })();

  Object.defineProperty(window, 'localStorage', {
    value: localStorageMock,
  });

  return localStorageMock;
}; 