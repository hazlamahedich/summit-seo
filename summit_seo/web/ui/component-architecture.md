# Summit SEO - React Component Architecture

## Overview

This document outlines the React component architecture for the Summit SEO web interface. The architecture follows a hierarchical structure with reusable components that align with the mockups created in the first phase of the UI implementation.

## Component Hierarchy

```
App
├── AuthenticatedLayout
│   ├── Sidebar
│   │   ├── Logo
│   │   └── Navigation
│   └── MainLayout
│       ├── Header
│       │   ├── PageTitle
│       │   └── ActionButtons
│       └── Content (varies by page)
├── Routes
│   ├── Dashboard
│   │   ├── MetricOverview
│   │   │   └── MetricCard
│   │   ├── CategoryGrid
│   │   │   └── CategoryCard
│   │   └── QuickWins
│   │       └── RecommendationCard
│   ├── AnalysisResults
│   │   ├── SiteSummary
│   │   ├── CategoryTabs
│   │   ├── FindingsList
│   │   │   └── FindingCard
│   │   │       ├── FindingHeader
│   │   │       ├── FindingContent
│   │   │       ├── CodeSnippet
│   │   │       ├── Recommendation
│   │   │       └── FindingFooter
│   │   └── Pagination
│   ├── Settings
│   │   ├── SettingsTabs
│   │   └── SettingsSection
│   │       ├── ProjectSettings
│   │       ├── AnalysisConfiguration
│   │       ├── NotificationSettings
│   │       ├── APISettings
│   │       └── UserPreferences
│   └── Other Routes...
└── Common Components
    ├── Card
    ├── Button
    ├── ProgressBar
    ├── Tag
    ├── Form Components
    │   ├── Input
    │   ├── Select
    │   ├── Checkbox
    │   ├── RadioButton
    │   ├── Toggle
    │   ├── Slider
    │   └── TagsInput
    ├── Indicators
    │   ├── SeverityIndicator
    │   ├── ImpactIndicator
    │   └── StatusBadge
    └── Loaders
        ├── Spinner
        ├── SkeletonLoader
        └── ProgressIndicator
```

## Component Specifications

### Layout Components

#### `AuthenticatedLayout`
- Container for all authenticated pages
- Manages the layout structure with sidebar and main content area
- Props:
  - `children`: React node to render in the main content area

#### `Sidebar`
- Navigation sidebar displayed on all authenticated pages
- Props:
  - `activePage`: Current active page identifier
  - `onNavigate`: Function to handle navigation

#### `MainLayout`
- Layout container for the main content area
- Includes header and content container
- Props:
  - `children`: React node for page content
  - `pageTitle`: Title for the current page
  - `actions`: Array of action objects for header buttons

### Common Components

#### `Card`
- Base container component for content sections
- Props:
  - `children`: React node for card content
  - `title`: Optional card title
  - `subtitle`: Optional card subtitle
  - `className`: Additional CSS classes
  - `headerActions`: Optional buttons/actions in header

#### `Button`
- Reusable button component with different variants
- Props:
  - `children`: React node for button content
  - `variant`: 'primary' | 'secondary' | 'danger' | 'success'
  - `size`: 'sm' | 'md' | 'lg'
  - `onClick`: Function for click handler
  - `disabled`: Boolean to disable the button
  - `icon`: Optional icon to display
  - `className`: Additional CSS classes

#### `ProgressBar`
- Visual representation of progress or scores
- Props:
  - `value`: Number representing current value (0-100)
  - `variant`: 'excellent' | 'good' | 'fair' | 'poor'
  - `showLabel`: Boolean to show percentage label
  - `height`: Optional height override
  - `className`: Additional CSS classes

#### `Tag`
- Component for displaying tag-like items
- Props:
  - `children`: React node for tag content
  - `onRemove`: Optional function for remove button
  - `color`: Optional color variant
  - `className`: Additional CSS classes

### Form Components

#### `Input`
- Text input component
- Props:
  - `value`: Current input value
  - `onChange`: Change handler function
  - `type`: Input type ('text', 'email', etc.)
  - `label`: Input label
  - `hint`: Optional hint text
  - `error`: Optional error message
  - `placeholder`: Placeholder text
  - `required`: Boolean for required field

#### `Select`
- Dropdown select component
- Props:
  - `value`: Current selected value
  - `onChange`: Change handler function
  - `options`: Array of option objects
  - `label`: Select label
  - `hint`: Optional hint text
  - `error`: Optional error message
  - `placeholder`: Placeholder text
  - `required`: Boolean for required field

#### `TagsInput`
- Component for managing multiple tag values
- Props:
  - `values`: Array of current tag values
  - `onChange`: Function called when tags change
  - `label`: Input label
  - `hint`: Optional hint text
  - `placeholder`: Placeholder text
  - `error`: Optional error message

#### `Toggle`
- Switch/toggle component
- Props:
  - `checked`: Boolean for toggle state
  - `onChange`: Change handler function
  - `label`: Toggle label
  - `disabled`: Boolean to disable the toggle

### Indicators

#### `SeverityIndicator`
- Visual indicator for issue severity
- Props:
  - `severity`: 'critical' | 'warning' | 'info' | 'success'
  - `showLabel`: Boolean to show severity text
  - `size`: 'sm' | 'md' | 'lg'

#### `ImpactIndicator`
- Visual indicator for recommendation impact
- Props:
  - `impact`: Number from 1-5 representing impact level
  - `showLabel`: Boolean to show impact text

### Dashboard Components

#### `MetricCard`
- Card for displaying key metrics with changes
- Props:
  - `title`: Metric title
  - `value`: Current metric value
  - `change`: Change value or percentage
  - `changeDirection`: 'positive' | 'negative' | 'neutral'
  - `icon`: Optional icon

#### `CategoryCard`
- Card for displaying category scores and issues
- Props:
  - `title`: Category name
  - `score`: Category score (0-100)
  - `findings`: Array of finding objects
  - `onClick`: Handler for clicking on category

#### `RecommendationCard`
- Card for displaying quick win recommendations
- Props:
  - `category`: Recommendation category
  - `title`: Recommendation title
  - `description`: Detailed description
  - `impact`: Impact level (1-5)
  - `onClick`: Handler for clicking on recommendation

### Analysis Results Components

#### `FindingCard`
- Card for displaying detailed analysis findings
- Props:
  - `title`: Finding title
  - `location`: Where the issue was found
  - `severity`: 'critical' | 'warning' | 'info' | 'success'
  - `description`: Detailed description
  - `codeSnippet`: Optional code example
  - `recommendation`: Recommendation object
  - `impact`: Impact level (1-5)
  - `category`: Finding category
  - `onLearnMore`: Handler for learn more action
  - `onIgnore`: Handler for ignore action
  - `onFix`: Handler for fix action

#### `Pagination`
- Component for paginating through results
- Props:
  - `currentPage`: Current page number
  - `totalPages`: Total number of pages
  - `onPageChange`: Function called when page changes
  - `showFirstLast`: Boolean to show first/last buttons

### Settings Components

#### `SettingsTabs`
- Tab navigation for settings sections
- Props:
  - `activeTab`: Current active tab
  - `onTabChange`: Function called when tab changes
  - `tabs`: Array of tab objects

#### `SettingsSection`
- Container for a group of related settings
- Props:
  - `title`: Section title
  - `description`: Section description
  - `children`: React node for section content

## State Management

The application will use a combination of:

1. **React Context** - For global application state such as:
   - Authentication state
   - User preferences
   - Current project context

2. **Redux** - For more complex state management:
   - Analysis results data
   - Settings configuration
   - Asynchronous operations

3. **Local Component State** - For UI-specific state:
   - Form inputs
   - UI toggles
   - Pagination

## Data Flow

```
API Client <-> Redux Store <-> React Components
```

1. Components dispatch actions to request data
2. Redux middleware handles API calls
3. API responses update the Redux store
4. Components receive updated data via selectors

## Theming and Styling

- Base styles defined in `common.css` 
- Component-specific styles using CSS modules
- Theme variables from CSS custom properties
- Responsive design using media queries
- Accessibility considerations in all components

## Next Implementation Steps

1. Set up React project structure with required dependencies
2. Create base layout components (AuthenticatedLayout, Sidebar, MainLayout)
3. Implement common components (Card, Button, etc.)
4. Build form components for settings pages
5. Implement page-specific components for Dashboard
6. Set up state management with Redux
7. Connect components to state management
8. Implement API client integration
9. Add responsive behavior for mobile devices
10. Ensure accessibility compliance throughout the interface 