import React from 'react';
import styles from './ProgressBar.module.css';

/**
 * ProgressBar component - Visual representation of progress or scores
 * 
 * @param {Object} props - Component props
 * @param {number} props.value - Number representing current value (0-100)
 * @param {'excellent' | 'good' | 'fair' | 'poor'} [props.variant] - Visual variant based on score
 * @param {boolean} [props.showLabel=false] - Whether to show percentage label
 * @param {string} [props.height] - Optional height override
 * @param {string} [props.className] - Additional CSS classes
 * @returns {React.ReactElement} ProgressBar component
 */
const ProgressBar = ({
  value,
  variant,
  showLabel = false,
  height,
  className = '',
}) => {
  // Clamp value between 0 and 100
  const normalizedValue = Math.min(Math.max(value, 0), 100);
  
  // Determine variant if not provided
  const derivedVariant = variant || getVariantFromValue(normalizedValue);
  
  // Build CSS class names
  const containerClasses = [
    styles['progress-container'],
    className
  ].filter(Boolean).join(' ');
  
  const progressClasses = [
    styles.progress,
    styles[derivedVariant]
  ].filter(Boolean).join(' ');
  
  // Custom styles
  const containerStyle = height ? { height } : {};
  const progressStyle = { width: `${normalizedValue}%` };
  
  return (
    <div className={containerClasses} style={containerStyle}>
      <div className={progressClasses} style={progressStyle} />
      {showLabel && (
        <div className={styles.label}>
          {normalizedValue}%
        </div>
      )}
    </div>
  );
};

/**
 * Helper function to determine variant based on value
 * 
 * @param {number} value - Score value (0-100)
 * @returns {'excellent' | 'good' | 'fair' | 'poor'} Variant based on value
 */
function getVariantFromValue(value) {
  if (value >= 90) return 'excellent';
  if (value >= 70) return 'good';
  if (value >= 50) return 'fair';
  return 'poor';
}

export default ProgressBar; 