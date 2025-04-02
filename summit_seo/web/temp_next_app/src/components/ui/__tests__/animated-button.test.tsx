import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AnimatedButton } from '../animated-button';
import * as framerMotion from 'framer-motion';

// Mock framer-motion to avoid issues with animations in tests
jest.mock('framer-motion', () => {
  const actual = jest.requireActual('framer-motion');
  return {
    ...actual,
    motion: {
      div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
      span: ({ children, ...props }: any) => <span {...props}>{children}</span>,
    },
  };
});

// Mock the useReducedMotion hook
jest.mock('@/lib/motion', () => ({
  useReducedMotion: jest.fn().mockReturnValue(false),
}));

describe('AnimatedButton Component', () => {
  test('renders correctly with default props', () => {
    render(<AnimatedButton>Click me</AnimatedButton>);
    expect(screen.getByRole('button', { name: /Click me/i })).toBeInTheDocument();
  });

  test('displays loading state when loading prop is true', () => {
    render(<AnimatedButton loading>Click me</AnimatedButton>);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeDisabled();
  });

  test('uses custom loading text when provided', () => {
    render(<AnimatedButton loading loadingText="Please wait...">Click me</AnimatedButton>);
    expect(screen.getByText('Please wait...')).toBeInTheDocument();
  });

  test('is disabled when disabled prop is true', () => {
    render(<AnimatedButton disabled>Click me</AnimatedButton>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  test('displays icon when provided', () => {
    render(
      <AnimatedButton 
        icon={<span data-testid="test-icon">🔍</span>}
      >
        Search
      </AnimatedButton>
    );
    expect(screen.getByTestId('test-icon')).toBeInTheDocument();
  });

  test('positions icon on the right when iconPosition is right', () => {
    render(
      <AnimatedButton 
        icon={<span data-testid="test-icon">🔍</span>}
        iconPosition="right"
      >
        Search
      </AnimatedButton>
    );
    
    // Find the parent span that should have flex-row-reverse class
    const iconContainer = screen.getByTestId('test-icon').closest('span');
    const parentSpan = iconContainer?.parentElement;
    
    expect(parentSpan).toHaveClass('flex-row-reverse');
  });

  test('calls onClick handler when clicked', async () => {
    const handleClick = jest.fn();
    render(<AnimatedButton onClick={handleClick}>Click me</AnimatedButton>);
    
    await userEvent.click(screen.getByRole('button', { name: /Click me/i }));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('applies custom className', () => {
    render(<AnimatedButton className="custom-class">Click me</AnimatedButton>);
    expect(screen.getByRole('button')).toHaveClass('custom-class');
  });

  test('applies success feedback style', () => {
    render(<AnimatedButton feedback="success">Click me</AnimatedButton>);
    const button = screen.getByRole('button');
    
    // Allow the useEffect to run
    jest.advanceTimersByTime(0);
    
    expect(button).toHaveClass('bg-green-500');
    expect(button).toHaveClass('text-white');
  });

  test('applies error feedback style', () => {
    render(<AnimatedButton feedback="error">Click me</AnimatedButton>);
    const button = screen.getByRole('button');
    
    // Allow the useEffect to run
    jest.advanceTimersByTime(0);
    
    expect(button).toHaveClass('bg-red-500');
    expect(button).toHaveClass('text-white');
  });
}); 