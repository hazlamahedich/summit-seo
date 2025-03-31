# Summit SEO - Responsive Design Guidelines

## Overview

This document outlines the responsive design approach for Summit SEO's web interface. These guidelines ensure a consistent, accessible, and optimal user experience across devices of various screen sizes, from mobile phones to large desktop monitors.

## Breakpoints

Summit SEO follows a mobile-first approach with the following standard breakpoints:

| Breakpoint | Device Category | Media Query                |
|------------|----------------|----------------------------|
| XS         | Small phones   | `@media (max-width: 575px)`|
| SM         | Large phones   | `@media (min-width: 576px)`|
| MD         | Tablets        | `@media (min-width: 768px)`|
| LG         | Laptops        | `@media (min-width: 992px)`|
| XL         | Desktops       | `@media (min-width: 1200px)`|
| XXL        | Large desktops | `@media (min-width: 1400px)`|

## Grid System

The layout uses CSS Grid and Flexbox for responsive behavior:

- **Main Layout**: CSS Grid for the overall page structure (sidebar and content)
- **Component Layouts**: Flexbox for component-level layouts
- **Card Grids**: CSS Grid with auto-fit/auto-fill for responsive card layouts

### Grid Template Examples

```css
/* Main layout grid */
.container {
  display: grid;
  grid-template-columns: 1fr; /* Mobile: full width */
}

@media (min-width: 992px) {
  .container {
    grid-template-columns: 240px 1fr; /* Desktop: sidebar + content */
  }
}

/* Responsive card grid */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--spacing-md);
}
```

## Layout Transformations

As screen size changes, layouts transform to maintain usability:

### Sidebar Navigation
- **≥ 992px (LG)**: Persistent sidebar on the left side
- **< 992px**: Collapsible sidebar with toggle button in header

### Card Grids
- **XL**: 4 cards per row
- **LG**: 3 cards per row
- **MD**: 2 cards per row
- **SM/XS**: 1 card per row (full width)

### Data Tables
- **≥ 768px (MD)**: Full table with all columns
- **< 768px**: Responsive techniques:
  - Horizontal scrolling for important tables
  - Card-based layout for data (one card per row)
  - Column prioritization (hide less important columns)

## Component Adaptations

Components adapt to screen size in the following ways:

### Navigation
- **≥ 992px**: Full sidebar with text labels
- **768px - 992px**: Collapsed sidebar with icons only, expanding on hover
- **< 768px**: Bottom navigation bar (mobile) or hamburger menu

### Cards
- **≥ 768px**: Standard card layout with header + content
- **< 768px**: 
  - Simplified headers
  - Reduced padding
  - Stacked action buttons

### Forms
- **≥ 768px**: Multi-column layouts for form sections
- **< 768px**: Single column layout for all inputs

### Buttons
- **≥ 768px**: Standard buttons with icons and text
- **< 768px**: 
  - Primary actions full width
  - Secondary actions as icon buttons or in overflow menu

### Dialogs and Modals
- **≥ 768px**: Centered with fixed width (max 600px)
- **< 768px**: Full width with small margins (10px)

## Typography

Font sizes adjust automatically using the following approach:

```css
:root {
  --font-size-base: 16px;
  --font-size-scale: 1.25;
  
  /* Responsive scaling */
  @media (max-width: 576px) {
    --font-size-base: 14px;
    --font-size-scale: 1.2;
  }
}

/* Calculated sizes */
--font-size-xs: calc(var(--font-size-base) / var(--font-size-scale));
--font-size-sm: calc(var(--font-size-base));
--font-size-md: calc(var(--font-size-base) * var(--font-size-scale));
--font-size-lg: calc(var(--font-size-base) * var(--font-size-scale) * var(--font-size-scale));
--font-size-xl: calc(var(--font-size-base) * var(--font-size-scale) * var(--font-size-scale) * var(--font-size-scale));
```

## Images and Media

- Use responsive images with the `srcset` attribute and appropriate sizes
- Implement lazy loading for images below the fold
- Optimize images for different device resolutions
- Use SVG for icons and graphics whenever possible

```html
<img 
  src="image-md.jpg" 
  srcset="image-sm.jpg 576w, image-md.jpg 768w, image-lg.jpg 1200w" 
  sizes="(max-width: 576px) 100vw, (max-width: 992px) 50vw, 33vw"
  alt="Description"
  loading="lazy"
/>
```

## Touch Considerations

- Minimum touch target size: 44px × 44px
- Adequate spacing between interactive elements (minimum 8px)
- Implement touch-friendly UI elements for mobile
- Support touch gestures where appropriate (swipe, pinch-to-zoom)

## Responsive Testing Strategy

Test on the following device categories:

1. **Mobile phones** (320px - 576px)
   - iPhone SE (320px width)
   - iPhone X/11/12/13 (375px width)
   - Larger Android devices (412px width)

2. **Tablets** (577px - 991px)
   - iPad Mini/Air (768px width)
   - iPad Pro (834px width)
   - Android tablets (various)

3. **Laptops/Desktops** (992px - 1399px)
   - Laptops (1366px width)
   - Small desktop monitors (1440px width)

4. **Large Desktops** (1400px+)
   - Standard monitors (1920px width)
   - Large/high-resolution displays (2560px+)

## Implementation Guidelines

### CSS Structure

CSS should be organized to follow the mobile-first approach:

```css
/* Base styles for mobile */
.component {
  /* Mobile styles */
}

/* Tablet styles */
@media (min-width: 768px) {
  .component {
    /* Tablet-specific overrides */
  }
}

/* Desktop styles */
@media (min-width: 992px) {
  .component {
    /* Desktop-specific overrides */
  }
}
```

### Performance Considerations

- Minimize CSS and JS payload for mobile devices
- Consider conditional loading of non-critical resources
- Optimize render-blocking resources
- Use responsive image techniques to reduce bandwidth usage
- Implement code splitting for feature-rich pages

## Examples

### Responsive Card Component

```jsx
// Card.jsx
import React from 'react';
import styles from './Card.module.css';

const Card = ({ title, children, className }) => {
  return (
    <div className={`${styles.card} ${className}`}>
      {title && <div className={styles.cardHeader}>{title}</div>}
      <div className={styles.cardBody}>{children}</div>
    </div>
  );
};

// Card.module.css
.card {
  padding: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

@media (min-width: 768px) {
  .card {
    padding: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
  }
}

@media (min-width: 992px) {
  .card {
    padding: var(--spacing-lg);
  }
}
```

### Responsive Dashboard Layout

```jsx
// Dashboard.jsx
import React from 'react';
import { MetricCard, CategoryCard } from '../components';
import styles from './Dashboard.module.css';

const Dashboard = () => {
  return (
    <div>
      <div className={styles.metricGrid}>
        {/* Metric cards */}
      </div>
      <div className={styles.categoryGrid}>
        {/* Category cards */}
      </div>
    </div>
  );
};

// Dashboard.module.css
.metricGrid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-sm);
}

.categoryGrid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-md);
  margin-top: var(--spacing-lg);
}

@media (min-width: 576px) {
  .metricGrid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 768px) {
  .metricGrid {
    gap: var(--spacing-md);
  }
  
  .categoryGrid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 992px) {
  .metricGrid {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

## Best Practices

1. **Mobile-First Development**
   - Start with mobile layouts and enhance for larger screens
   - Use min-width media queries for progressive enhancement

2. **Fluid Layouts**
   - Use relative units (%, rem, em) instead of fixed pixel values
   - Implement dynamic spacing that scales with viewport size

3. **Content Prioritization**
   - Identify and prioritize essential content for mobile
   - Consider alternative layouts for less important content on small screens

4. **Testing Across Devices**
   - Test on actual devices whenever possible
   - Use browser dev tools for device emulation during development
   - Consider automated testing for responsive behaviors

5. **Performance Optimization**
   - Optimize images and assets for different viewport sizes
   - Monitor performance metrics like FCP and TTI across device categories

6. **Accessibility**
   - Ensure responsive designs maintain accessibility
   - Test keyboard navigation at all breakpoints
   - Maintain sufficient contrast and readable text sizes

## Tools and Resources

- **Browser Dev Tools**: Chrome/Firefox device emulation
- **Responsive Testing Tools**: BrowserStack, Responsively App
- **Performance Testing**: Lighthouse, WebPageTest
- **Design References**: Material Design Responsive guidelines, iOS Human Interface Guidelines

## Implementation Timeline

1. Update common.css with responsive variables and utility classes
2. Implement responsive layouts for main containers
3. Update existing components with responsive behavior
4. Create responsive variants of page-specific layouts
5. Implement responsive navigation system
6. Test across all target device categories
7. Optimize performance for mobile devices 