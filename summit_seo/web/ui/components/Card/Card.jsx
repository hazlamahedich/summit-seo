import React from 'react';
import styles from './Card.module.css';

/**
 * Card component - Base container component for content sections
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Content to render inside the card
 * @param {string} [props.title] - Optional card title
 * @param {string} [props.subtitle] - Optional card subtitle
 * @param {string} [props.className] - Additional CSS classes
 * @param {React.ReactNode} [props.headerActions] - Optional buttons/actions in header
 * @param {string} [props.variant] - Card variant ('primary', 'secondary', 'warning', 'danger')
 * @returns {React.ReactElement} Card component
 */
const Card = ({ 
  children, 
  title, 
  subtitle, 
  className = '', 
  headerActions,
  variant
}) => {
  // Determine if we need to render the header
  const hasHeader = title || subtitle || headerActions;
  
  // Build CSS class names
  const cardClasses = [
    styles.card,
    variant && styles[`card-${variant}`],
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={cardClasses}>
      {hasHeader && (
        <div className={styles['card-header']}>
          <div>
            {title && <h3 className={styles['card-title']}>{title}</h3>}
            {subtitle && <div className={styles['card-subtitle']}>{subtitle}</div>}
          </div>
          {headerActions && (
            <div className={styles['card-actions']}>
              {headerActions}
            </div>
          )}
        </div>
      )}
      <div className={styles['card-body']}>
        {children}
      </div>
    </div>
  );
};

export default Card; 