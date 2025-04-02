# Mobile Optimization Components

This document provides an overview of the mobile optimization components implemented for the Summit SEO application.

## Table of Contents
1. [Touch Interaction Components](#touch-interaction-components)
2. [Mobile-Specific UI Components](#mobile-specific-ui-components)
3. [Offline Capabilities](#offline-capabilities)
4. [Mobile Integration](#mobile-integration)
5. [Usage Examples](#usage-examples)

## Touch Interaction Components

### useSwipeGesture Hook
**File:** `src/hooks/useSwipeGesture.ts`

A custom hook that detects and handles swipe gestures on touch devices. It provides callbacks for different swipe directions and configurable options.

**Features:**
- Detection of left, right, up, and down swipes
- Configurable minimum swipe distance and maximum swipe time
- Optional scroll prevention during vertical swipes
- Returns touch event handlers that can be spread onto components

**Example Usage:**
```tsx
const { touchHandlers } = useSwipeGesture({
  onSwipeLeft: () => console.log("Swiped left"),
  onSwipeRight: () => console.log("Swiped right"),
  onSwipeUp: () => console.log("Swiped up"),
  onSwipeDown: () => console.log("Swiped down"),
});

return <div {...touchHandlers}>Swipeable content</div>;
```

### SwipeContainer Component
**File:** `src/components/ui/swipe-container.tsx`

A container component that adds swipe gesture capabilities to its children with visual indicators.

**Features:**
- Visual indicators for available swipe directions
- Support for all four swipe directions
- Auto-hiding hints for first-time users
- Option to restrict to mobile devices only

## Mobile-Specific UI Components

### BottomSheet Component
**File:** `src/components/ui/bottom-sheet.tsx`

A mobile-friendly bottom sheet component with drag-to-dismiss functionality.

**Features:**
- Customizable snap points
- Drag handle for easy interaction
- Momentum-based dismissal
- Backdrop click dismissal
- Responsive design (full-width on mobile, centered on desktop)

### SwipeCarousel Component
**File:** `src/components/ui/swipe-carousel.tsx`

A mobile-optimized carousel with swipe navigation.

**Features:**
- Touch swipe gestures for navigation
- Optional navigation arrows
- Pagination indicators
- Optional auto-play functionality
- Configurable item sizing and gaps
- Support for centering items smaller than container width

### PullToRefresh Component
**File:** `src/components/ui/pull-to-refresh.tsx`

A pull-to-refresh component for mobile data refreshing.

**Features:**
- Visual indicator during pull and refresh
- Customizable pull distance and threshold
- Haptic feedback on refresh
- Resistance effect during pulling
- Status text for pulling, release, and refreshing states

### ResponsiveImage Component
**File:** `src/components/ui/responsive-image.tsx`

An optimized image component for mobile devices.

**Features:**
- Device-specific image sources (mobile, tablet, desktop)
- Progressive loading with low-quality placeholders
- Error handling with fallback images
- Configurable loading strategies (eager, lazy, progressive)
- Aspect ratio and object-fit control

## Offline Capabilities

### Offline Manager
**File:** `src/lib/offline-manager.ts`

A utility for handling offline capabilities in mobile applications.

**Features:**
- Online/offline status detection
- Automatic request queueing when offline
- Prioritized request processing when back online
- Configurable retry strategy with backoff
- Local data storage with TTL (time-to-live)
- Storage size management to prevent quota issues

### useOfflineManager Hook
**File:** `src/lib/offline-manager.ts`

A React hook for using the offline manager in components.

**Features:**
- Access to online/offline status
- Methods for storing and retrieving data
- API for queuing requests
- Pending request count tracking
- Automatic queue processing when back online

### OfflineStatus Component
**File:** `src/components/ui/offline-status.tsx`

A status indicator for online/offline state with sync capabilities.

**Features:**
- Visual indicator of connection status
- Pending request count display
- Manual sync button
- Expandable details view
- Haptic feedback on status changes
- Auto-hiding when online (configurable)

## Mobile Integration

### Haptic Feedback Utility
**File:** `src/lib/haptics.ts`

A utility for providing haptic feedback on mobile devices.

**Features:**
- Different vibration patterns (light, medium, heavy)
- Notification-style patterns (success, warning, error)
- Custom pattern support
- Feature detection for haptic support

### MobileAppShell Component
**File:** `src/components/ui/mobile-app-shell.tsx`

A container component that integrates all mobile features.

**Features:**
- Integration with pull-to-refresh
- Swipe navigation between pages
- Offline status indicator
- Configurable header and footer
- Page transition animations
- Body scroll locking for native-like feel

### PWA Support
**Files:** 
- `next.config.ts` (PWA configuration)
- `public/manifest.json` (Web App Manifest)
- `src/app/sw.ts` (Service Worker)
- `src/components/ui/pwa-install-prompt.tsx` (Install Prompt)
- `src/hooks/usePWA.ts` (PWA Hook)
- `src/lib/pwa-utils.ts` (PWA Utilities)

The application now supports Progressive Web App features:

**Features:**
- Home screen installation with custom icons
- Offline access to cached resources
- App-like experience without browser UI
- Install prompt with tactile feedback
- Service worker for resource caching and background sync
- Standalone mode detection
- Cache management utilities

## Usage Examples

### Example Mobile Page
**File:** `src/app/example-mobile-page/page.tsx`

An example page that demonstrates all mobile optimization components together.

**Features:**
- Interactive demos of all components
- Code examples
- Feature descriptions
- Integration demonstration

### General Integration Pattern

To fully optimize a page for mobile:

1. Wrap the page content with `MobileAppShell`
2. Implement offline data handling with `useOfflineManager`
3. Use `SwipeContainer` for interactive elements
4. Replace standard images with `ResponsiveImage`
5. Use `BottomSheet` instead of modals where appropriate
6. Add haptic feedback to interactive elements
7. Ensure the page is responsive using the provided utility components 