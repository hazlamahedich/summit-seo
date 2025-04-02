import React from 'react';
import { render, screen } from '@testing-library/react';
import { AuthStatus } from '../../ui/auth-status';
import { useAuth } from '@/providers/auth-provider';
import { useRouter } from 'next/navigation';

// Mock the useAuth hook
jest.mock('@/providers/auth-provider', () => ({
  useAuth: jest.fn(),
}));

// Mock the useRouter hook
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

describe('AuthStatus Component', () => {
  const mockRouter = {
    push: jest.fn(),
  };

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
  });

  test('shows loading state when auth is loading', () => {
    (useAuth as jest.Mock).mockReturnValue({
      user: null,
      isLoading: true,
    });

    render(<AuthStatus />);
    
    // Should show loading state
    const loadingElement = screen.getByTestId('auth-loading');
    expect(loadingElement).toBeInTheDocument();
  });

  test('shows login and register buttons when user is not authenticated', () => {
    (useAuth as jest.Mock).mockReturnValue({
      user: null,
      isLoading: false,
    });

    render(<AuthStatus />);
    
    // Should show login and register buttons
    const loginButton = screen.getByText('Log in');
    const registerButton = screen.getByText('Sign up');
    
    expect(loginButton).toBeInTheDocument();
    expect(registerButton).toBeInTheDocument();
  });

  test('shows user email and dropdown when authenticated', () => {
    const mockUser = {
      email: 'test@example.com',
    };
    
    (useAuth as jest.Mock).mockReturnValue({
      user: mockUser,
      isLoading: false,
      signOut: jest.fn().mockResolvedValue({ error: null }),
    });

    render(<AuthStatus />);
    
    // Should show user email
    const userMenu = screen.getByText('test@example.com');
    expect(userMenu).toBeInTheDocument();
  });
}); 