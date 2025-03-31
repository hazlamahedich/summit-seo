import React from 'react';
import styles from './Button.module.css';

/**
 * Button component - Reusable button with different variants and sizes
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Button content
 * @param {'primary' | 'secondary' | 'danger' | 'success'} [props.variant='primary'] - Button variant
 * @param {'sm' | 'md' | 'lg'} [props.size='md'] - Button size
 * @param {Function} [props.onClick] - Click handler function
 * @param {boolean} [props.disabled] - Whether the button is disabled
 * @param {React.ReactNode} [props.icon] - Optional icon to display
 * @param {string} [props.className] - Additional CSS classes
 * @param {string} [props.type='button'] - Button type (button, submit, reset)
 * @returns {React.ReactElement} Button component
 */
const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  onClick,
  disabled = false,
  icon,
  className = '',
  type = 'button',
  ...rest
}) => {
  // Build CSS class names
  const buttonClasses = [
    styles.button,
    styles[`button-${variant}`],
    styles[`button-${size}`],
    disabled && styles.disabled,
    icon && !children && styles['icon-only'],
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      type={type}
      className={buttonClasses}
      onClick={onClick}
      disabled={disabled}
      {...rest}
    >
      {icon && <span className={styles['button-icon']}>{icon}</span>}
      {children && <span className={styles['button-text']}>{children}</span>}
    </button>
  );
};

export default Button; 