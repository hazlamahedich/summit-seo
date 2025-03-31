import React, { useState } from 'react';
import PropTypes from 'prop-types';

/**
 * Accessible form input component
 */
const FormInput = ({
  id,
  label,
  type = 'text',
  value,
  onChange,
  required = false,
  error = '',
  hint = '',
  placeholder = '',
  disabled = false,
  className = '',
  min,
  max,
  pattern,
  autoComplete
}) => {
  const inputId = id || `input-${label.toLowerCase().replace(/\s+/g, '-')}`;
  const errorId = `${inputId}-error`;
  const hintId = `${inputId}-hint`;
  
  const describedBy = [
    hint ? hintId : null,
    error ? errorId : null
  ].filter(Boolean).join(' ') || undefined;
  
  return (
    <div className={`form-group ${error ? 'has-error' : ''} ${className}`}>
      <label 
        htmlFor={inputId} 
        className={`form-label ${required ? 'form-required' : ''}`}
      >
        {label}
      </label>
      
      {hint && (
        <span id={hintId} className="form-hint">
          {hint}
        </span>
      )}
      
      <input
        id={inputId}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`form-input ${error ? 'error' : ''}`}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={describedBy}
        required={required}
        disabled={disabled}
        min={min}
        max={max}
        pattern={pattern}
        autoComplete={autoComplete}
      />
      
      {error && (
        <span id={errorId} className="form-error-message" aria-live="polite">
          {error}
        </span>
      )}
    </div>
  );
};

/**
 * Accessible textarea component
 */
const FormTextarea = ({
  id,
  label,
  value,
  onChange,
  required = false,
  error = '',
  hint = '',
  placeholder = '',
  disabled = false,
  className = '',
  rows = 4
}) => {
  const textareaId = id || `textarea-${label.toLowerCase().replace(/\s+/g, '-')}`;
  const errorId = `${textareaId}-error`;
  const hintId = `${textareaId}-hint`;
  
  const describedBy = [
    hint ? hintId : null,
    error ? errorId : null
  ].filter(Boolean).join(' ') || undefined;
  
  return (
    <div className={`form-group ${error ? 'has-error' : ''} ${className}`}>
      <label 
        htmlFor={textareaId} 
        className={`form-label ${required ? 'form-required' : ''}`}
      >
        {label}
      </label>
      
      {hint && (
        <span id={hintId} className="form-hint">
          {hint}
        </span>
      )}
      
      <textarea
        id={textareaId}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`form-textarea ${error ? 'error' : ''}`}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={describedBy}
        required={required}
        disabled={disabled}
        rows={rows}
      />
      
      {error && (
        <span id={errorId} className="form-error-message" aria-live="polite">
          {error}
        </span>
      )}
    </div>
  );
};

/**
 * Accessible select component
 */
const FormSelect = ({
  id,
  label,
  value,
  onChange,
  options = [],
  required = false,
  error = '',
  hint = '',
  disabled = false,
  className = ''
}) => {
  const selectId = id || `select-${label.toLowerCase().replace(/\s+/g, '-')}`;
  const errorId = `${selectId}-error`;
  const hintId = `${selectId}-hint`;
  
  const describedBy = [
    hint ? hintId : null,
    error ? errorId : null
  ].filter(Boolean).join(' ') || undefined;
  
  return (
    <div className={`form-group ${error ? 'has-error' : ''} ${className}`}>
      <label 
        htmlFor={selectId} 
        className={`form-label ${required ? 'form-required' : ''}`}
      >
        {label}
      </label>
      
      {hint && (
        <span id={hintId} className="form-hint">
          {hint}
        </span>
      )}
      
      <select
        id={selectId}
        value={value}
        onChange={onChange}
        className={`form-select ${error ? 'error' : ''}`}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={describedBy}
        required={required}
        disabled={disabled}
      >
        {options.map((option) => (
          <option 
            key={option.value} 
            value={option.value}
            disabled={option.disabled}
          >
            {option.label}
          </option>
        ))}
      </select>
      
      {error && (
        <span id={errorId} className="form-error-message" aria-live="polite">
          {error}
        </span>
      )}
    </div>
  );
};

/**
 * Accessible checkbox component
 */
const FormCheckbox = ({
  id,
  label,
  checked,
  onChange,
  required = false,
  error = '',
  hint = '',
  disabled = false,
  className = ''
}) => {
  const checkboxId = id || `checkbox-${label.toLowerCase().replace(/\s+/g, '-')}`;
  const errorId = `${checkboxId}-error`;
  const hintId = `${checkboxId}-hint`;
  
  const describedBy = [
    hint ? hintId : null,
    error ? errorId : null
  ].filter(Boolean).join(' ') || undefined;
  
  return (
    <div className={`form-group ${error ? 'has-error' : ''} ${className}`}>
      <div className="form-checkbox-wrapper">
        <input
          id={checkboxId}
          type="checkbox"
          checked={checked}
          onChange={onChange}
          className={`form-checkbox ${error ? 'error' : ''}`}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={describedBy}
          required={required}
          disabled={disabled}
        />
        
        <label 
          htmlFor={checkboxId} 
          className={`form-checkbox-label ${required ? 'form-required' : ''}`}
        >
          {label}
        </label>
      </div>
      
      {hint && (
        <span id={hintId} className="form-hint">
          {hint}
        </span>
      )}
      
      {error && (
        <span id={errorId} className="form-error-message" aria-live="polite">
          {error}
        </span>
      )}
    </div>
  );
};

/**
 * Accessible radio button group component
 */
const FormRadioGroup = ({
  id,
  legend,
  options = [],
  value,
  onChange,
  required = false,
  error = '',
  hint = '',
  disabled = false,
  className = '',
  inline = false
}) => {
  const groupId = id || `radio-${legend.toLowerCase().replace(/\s+/g, '-')}`;
  const errorId = `${groupId}-error`;
  const hintId = `${groupId}-hint`;
  
  const describedBy = [
    hint ? hintId : null,
    error ? errorId : null
  ].filter(Boolean).join(' ') || undefined;
  
  return (
    <div className={`form-group ${error ? 'has-error' : ''} ${className}`}>
      <fieldset>
        <legend className={`form-label ${required ? 'form-required' : ''}`}>
          {legend}
        </legend>
        
        {hint && (
          <span id={hintId} className="form-hint">
            {hint}
          </span>
        )}
        
        <div className={`form-radio-group ${inline ? 'form-radio-group-inline' : ''}`} role="radiogroup" aria-describedby={describedBy}>
          {options.map((option) => {
            const radioId = `${groupId}-${option.value}`;
            
            return (
              <div key={option.value} className="form-radio-wrapper">
                <input
                  id={radioId}
                  type="radio"
                  name={groupId}
                  value={option.value}
                  checked={value === option.value}
                  onChange={() => onChange(option.value)}
                  className={`form-radio ${error ? 'error' : ''}`}
                  aria-invalid={error ? 'true' : 'false'}
                  required={required}
                  disabled={disabled || option.disabled}
                />
                
                <label 
                  htmlFor={radioId} 
                  className="form-radio-label"
                >
                  {option.label}
                </label>
              </div>
            );
          })}
        </div>
        
        {error && (
          <span id={errorId} className="form-error-message" aria-live="polite">
            {error}
          </span>
        )}
      </fieldset>
    </div>
  );
};

/**
 * Sample form component that demonstrates all form controls
 */
const SampleForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    message: '',
    category: '',
    priority: 'medium',
    notifications: false,
    agreeTerms: false
  });
  
  const [errors, setErrors] = useState({});
  const [submitStatus, setSubmitStatus] = useState(null);
  
  // Priority options for radio buttons
  const priorityOptions = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' }
  ];
  
  // Category options for select dropdown
  const categoryOptions = [
    { value: '', label: 'Select a category', disabled: true },
    { value: 'seo', label: 'SEO Optimization' },
    { value: 'security', label: 'Security Analysis' },
    { value: 'performance', label: 'Performance Testing' },
    { value: 'accessibility', label: 'Accessibility Audit' }
  ];
  
  // Handle input changes
  const handleChange = (event) => {
    const { name, value, type, checked } = event.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: ''
      });
    }
  };
  
  // Handle radio button changes
  const handleRadioChange = (value) => {
    setFormData({
      ...formData,
      priority: value
    });
  };
  
  // Validate form
  const validateForm = () => {
    const newErrors = {};
    
    // Name validation
    if (!formData.name) {
      newErrors.name = 'Name is required';
    }
    
    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }
    
    // Category validation
    if (!formData.category) {
      newErrors.category = 'Please select a category';
    }
    
    // Terms agreement validation
    if (!formData.agreeTerms) {
      newErrors.agreeTerms = 'You must agree to the terms and conditions';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  // Handle form submission
  const handleSubmit = (event) => {
    event.preventDefault();
    setSubmitStatus(null);
    
    if (validateForm()) {
      // Simulate API call
      setTimeout(() => {
        setSubmitStatus('success');
      }, 1000);
    } else {
      setSubmitStatus('error');
      
      // Focus on the first element with an error
      const firstErrorField = Object.keys(errors)[0];
      if (firstErrorField) {
        document.getElementById(firstErrorField)?.focus();
      }
    }
  };
  
  return (
    <div className="form-container">
      <h2 id="form-heading">New Project Request</h2>
      
      {submitStatus === 'success' && (
        <div className="alert alert-success" role="alert">
          <strong>Success!</strong> Your project request has been submitted.
        </div>
      )}
      
      {submitStatus === 'error' && (
        <div className="alert alert-danger" role="alert">
          <strong>Error!</strong> Please fix the errors in the form.
        </div>
      )}
      
      <form 
        onSubmit={handleSubmit} 
        aria-labelledby="form-heading"
        noValidate
      >
        <FormInput
          id="name"
          name="name"
          label="Name"
          value={formData.name}
          onChange={handleChange}
          placeholder="Your full name"
          required
          error={errors.name}
          autoComplete="name"
        />
        
        <FormInput
          id="email"
          name="email"
          type="email"
          label="Email Address"
          value={formData.email}
          onChange={handleChange}
          placeholder="Your email address"
          required
          error={errors.email}
          autoComplete="email"
          hint="We'll never share your email with anyone else."
        />
        
        <FormInput
          id="password"
          name="password"
          type="password"
          label="Password"
          value={formData.password}
          onChange={handleChange}
          placeholder="Create a password"
          required
          error={errors.password}
          autoComplete="new-password"
          hint="Password must be at least 8 characters long."
        />
        
        <FormSelect
          id="category"
          name="category"
          label="Service Category"
          value={formData.category}
          onChange={handleChange}
          options={categoryOptions}
          required
          error={errors.category}
          hint="Select the type of service you need."
        />
        
        <FormRadioGroup
          id="priority"
          name="priority"
          legend="Priority Level"
          options={priorityOptions}
          value={formData.priority}
          onChange={handleRadioChange}
          hint="How quickly do you need this service?"
          inline
        />
        
        <FormTextarea
          id="message"
          name="message"
          label="Project Details"
          value={formData.message}
          onChange={handleChange}
          placeholder="Describe your project requirements"
          hint="Provide as much detail as possible about your project."
          rows={5}
        />
        
        <FormCheckbox
          id="notifications"
          name="notifications"
          label="Receive email notifications about this project"
          checked={formData.notifications}
          onChange={handleChange}
        />
        
        <FormCheckbox
          id="agreeTerms"
          name="agreeTerms"
          label="I agree to the terms and conditions"
          checked={formData.agreeTerms}
          onChange={handleChange}
          required
          error={errors.agreeTerms}
        />
        
        <div className="form-actions">
          <button type="submit" className="button button-primary">
            Submit Request
          </button>
          
          <button type="button" className="button button-secondary">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

// PropTypes
FormInput.propTypes = {
  id: PropTypes.string,
  label: PropTypes.string.isRequired,
  type: PropTypes.string,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onChange: PropTypes.func.isRequired,
  required: PropTypes.bool,
  error: PropTypes.string,
  hint: PropTypes.string,
  placeholder: PropTypes.string,
  disabled: PropTypes.bool,
  className: PropTypes.string,
  min: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  max: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  pattern: PropTypes.string,
  autoComplete: PropTypes.string
};

FormTextarea.propTypes = {
  id: PropTypes.string,
  label: PropTypes.string.isRequired,
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  required: PropTypes.bool,
  error: PropTypes.string,
  hint: PropTypes.string,
  placeholder: PropTypes.string,
  disabled: PropTypes.bool,
  className: PropTypes.string,
  rows: PropTypes.number
};

FormSelect.propTypes = {
  id: PropTypes.string,
  label: PropTypes.string.isRequired,
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  options: PropTypes.arrayOf(PropTypes.shape({
    value: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    disabled: PropTypes.bool
  })).isRequired,
  required: PropTypes.bool,
  error: PropTypes.string,
  hint: PropTypes.string,
  disabled: PropTypes.bool,
  className: PropTypes.string
};

FormCheckbox.propTypes = {
  id: PropTypes.string,
  label: PropTypes.string.isRequired,
  checked: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
  required: PropTypes.bool,
  error: PropTypes.string,
  hint: PropTypes.string,
  disabled: PropTypes.bool,
  className: PropTypes.string
};

FormRadioGroup.propTypes = {
  id: PropTypes.string,
  legend: PropTypes.string.isRequired,
  options: PropTypes.arrayOf(PropTypes.shape({
    value: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    disabled: PropTypes.bool
  })).isRequired,
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  required: PropTypes.bool,
  error: PropTypes.string,
  hint: PropTypes.string,
  disabled: PropTypes.bool,
  className: PropTypes.string,
  inline: PropTypes.bool
};

export {
  FormInput,
  FormTextarea,
  FormSelect,
  FormCheckbox,
  FormRadioGroup,
  SampleForm
}; 