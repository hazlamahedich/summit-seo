import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * Main navigation component for Summit SEO web UI
 * Includes responsive behavior, keyboard navigation, and accessibility features
 */
const Navigation = ({ activeItem = 'dashboard', onNavigate }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navRef = useRef(null);
  const menuButtonRef = useRef(null);
  
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: 'chart-bar' },
    { id: 'projects', label: 'Projects', icon: 'folder' },
    { id: 'analyses', label: 'Analyses', icon: 'search' },
    { id: 'reports', label: 'Reports', icon: 'file-alt' },
    { id: 'settings', label: 'Settings', icon: 'cog' }
  ];
  
  // Handle Escape key to close mobile menu
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && mobileMenuOpen) {
        setMobileMenuOpen(false);
        menuButtonRef.current?.focus();
      }
    };
    
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [mobileMenuOpen]);
  
  // Focus trap for mobile menu
  useEffect(() => {
    if (!mobileMenuOpen) return;
    
    const navElement = navRef.current;
    const focusableElements = navElement?.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    if (!focusableElements?.length) return;
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    const handleTabKey = (e) => {
      if (e.key !== 'Tab') return;
      
      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement.focus();
          e.preventDefault();
        }
      }
    };
    
    navElement.addEventListener('keydown', handleTabKey);
    return () => navElement.removeEventListener('keydown', handleTabKey);
  }, [mobileMenuOpen]);
  
  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };
  
  const handleNavigation = (itemId) => {
    onNavigate(itemId);
    setMobileMenuOpen(false);
  };
  
  // Render icon (placeholder for actual icon component)
  const renderIcon = (iconName) => (
    <span className="nav-icon" aria-hidden="true">{iconName}</span>
  );
  
  return (
    <nav 
      className="main-navigation" 
      role="navigation" 
      aria-label="Main Navigation"
      ref={navRef}
    >
      {/* Skip Link - Accessibility Feature */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>
      
      {/* Mobile Navigation Toggle */}
      <button
        ref={menuButtonRef}
        className="mobile-menu-toggle"
        onClick={toggleMobileMenu}
        aria-expanded={mobileMenuOpen}
        aria-controls="navigation-menu"
        aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
      >
        <span className="sr-only">Menu</span>
        <span className="menu-icon" aria-hidden="true">
          {mobileMenuOpen ? "✕" : "☰"}
        </span>
      </button>
      
      {/* Navigation Items */}
      <ul 
        id="navigation-menu" 
        className={`nav-list ${mobileMenuOpen ? 'nav-list-mobile-open' : ''}`}
        role="menubar"
      >
        {navItems.map((item) => (
          <li key={item.id} role="none">
            <a
              href={`#${item.id}`}
              onClick={(e) => {
                e.preventDefault();
                handleNavigation(item.id);
              }}
              className={`nav-item ${activeItem === item.id ? 'nav-item-active' : ''}`}
              role="menuitem"
              aria-current={activeItem === item.id ? 'page' : undefined}
            >
              {renderIcon(item.icon)}
              <span className="nav-label">{item.label}</span>
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
};

Navigation.propTypes = {
  /** Currently active navigation item */
  activeItem: PropTypes.oneOf(['dashboard', 'projects', 'analyses', 'reports', 'settings']),
  /** Callback function when navigation item is selected */
  onNavigate: PropTypes.func.isRequired
};

export default Navigation; 