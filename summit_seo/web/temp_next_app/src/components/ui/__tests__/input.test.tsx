import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Input } from '../input';

describe('Input Component', () => {
  test('renders an input element', () => {
    render(<Input data-testid="test-input" />);
    const input = screen.getByTestId('test-input');
    expect(input).toBeInTheDocument();
    expect(input.tagName).toBe('INPUT');
  });

  test('applies default classes', () => {
    render(<Input data-testid="test-input" />);
    const input = screen.getByTestId('test-input');
    expect(input).toHaveClass('flex');
    expect(input).toHaveClass('h-10');
    expect(input).toHaveClass('rounded-md');
    expect(input).toHaveClass('border');
  });

  test('applies additional classes via className prop', () => {
    render(<Input data-testid="test-input" className="custom-class" />);
    const input = screen.getByTestId('test-input');
    expect(input).toHaveClass('custom-class');
  });

  test('passes through HTML attributes', () => {
    render(
      <Input
        data-testid="test-input"
        placeholder="Enter text"
        disabled
        maxLength={10}
      />
    );
    const input = screen.getByTestId('test-input');
    expect(input).toHaveAttribute('placeholder', 'Enter text');
    expect(input).toBeDisabled();
    expect(input).toHaveAttribute('maxLength', '10');
  });

  test('sets the correct input type', () => {
    const { rerender } = render(<Input data-testid="test-input" />);
    let input = screen.getByTestId('test-input');
    // Default type should be text
    expect(input).toHaveAttribute('type', 'text');

    rerender(<Input data-testid="test-input" type="password" />);
    input = screen.getByTestId('test-input');
    expect(input).toHaveAttribute('type', 'password');

    rerender(<Input data-testid="test-input" type="email" />);
    input = screen.getByTestId('test-input');
    expect(input).toHaveAttribute('type', 'email');
  });

  test('user can type in the input', async () => {
    render(<Input data-testid="test-input" />);
    const input = screen.getByTestId('test-input');
    
    await userEvent.type(input, 'Hello, world!');
    expect(input).toHaveValue('Hello, world!');
  });

  test('forwards the ref to the input element', () => {
    const ref = React.createRef<HTMLInputElement>();
    render(<Input data-testid="test-input" ref={ref} />);
    expect(ref.current).toBeInstanceOf(HTMLInputElement);
    expect(ref.current).toBe(screen.getByTestId('test-input'));
  });
}); 