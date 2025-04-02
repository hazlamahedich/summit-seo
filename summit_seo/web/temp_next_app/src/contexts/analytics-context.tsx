'use client';

import React, { createContext, useContext, useEffect, useRef, useState, ReactNode } from 'react';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import { v4 as uuidv4 } from 'uuid';
import { usePathname, useSearchParams } from 'next/navigation';
import { Database } from '@/types/supabase';

// Define analytics event types
export type EventType = 'page_view' | 'interaction' | 'form_submission' | 'error' | 'feature_usage' | 'conversion' | 'custom';

export type EventCategory = 'navigation' | 'ui' | 'content' | 'form' | 'feature' | 'error' | 'system' | 'user' | 'custom';

export interface AnalyticsEvent {
  eventType: EventType;
  eventCategory: EventCategory;
  eventAction: string;
  eventLabel?: string;
  eventValue?: any;
  clientTimestamp: Date;
}

export interface UserSession {
  sessionId: string;
  startTime: Date;
  lastActivityTime: Date;
  isActive: boolean;
  deviceInfo: {
    deviceType: string;
    browser: string;
    os: string;
    screenSize: string;
  };
  entryPage?: string;
  exitPage?: string;
  pageViews: number;
  eventsCount: number;
}

interface FeatureUsage {
  featureId: string;
  featureCategory: string;
  firstUsed: Date;
  lastUsed: Date;
  usageCount: number;
}

// Analytics context type
interface AnalyticsContextType {
  // Data
  currentSession: UserSession | null;
  isInitialized: boolean;
  isEnabled: boolean;
  
  // Methods
  trackEvent: (
    eventType: EventType,
    eventCategory: EventCategory,
    eventAction: string,
    eventLabel?: string,
    eventValue?: any
  ) => Promise<void>;
  trackPageView: (pagePath: string, pageTitle: string) => Promise<void>;
  trackFeatureUsage: (featureId: string, featureCategory: string) => Promise<void>;
  trackInteraction: (
    elementId: string,
    interactionType: string,
    elementType?: string
  ) => Promise<void>;
  trackFormSubmission: (
    formId: string,
    formName: string,
    success: boolean
  ) => Promise<void>;
  trackError: (
    errorType: string,
    errorMessage: string,
    errorContext?: any
  ) => Promise<void>;
  trackConversion: (
    conversionType: string,
    conversionValue?: number
  ) => Promise<void>;
  trackHeatmapData: (
    eventType: 'click' | 'move' | 'scroll',
    x?: number,
    y?: number,
    scrollDepth?: number
  ) => Promise<void>;
  enableAnalytics: () => void;
  disableAnalytics: () => void;
}

// Default context value
const defaultContext: AnalyticsContextType = {
  currentSession: null,
  isInitialized: false,
  isEnabled: true,
  trackEvent: async () => {},
  trackPageView: async () => {},
  trackFeatureUsage: async () => {},
  trackInteraction: async () => {},
  trackFormSubmission: async () => {},
  trackError: async () => {},
  trackConversion: async () => {},
  trackHeatmapData: async () => {},
  enableAnalytics: () => {},
  disableAnalytics: () => {},
};

// Create analytics context
const AnalyticsContext = createContext<AnalyticsContextType>(defaultContext);

// Analytics provider props
interface AnalyticsProviderProps {
  children: ReactNode;
  disabled?: boolean;
}

// Get browser and device information
function getDeviceInfo() {
  if (typeof window === 'undefined') {
    return {
      deviceType: 'unknown',
      browser: 'unknown',
      os: 'unknown',
      screenSize: 'unknown',
    };
  }

  // Detect device type
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  const isTablet = /iPad|Android(?!.*Mobile)/i.test(navigator.userAgent);
  const deviceType = isTablet ? 'tablet' : isMobile ? 'mobile' : 'desktop';

  // Detect browser
  const userAgent = navigator.userAgent;
  let browser = 'unknown';
  if (userAgent.indexOf('Chrome') > -1) browser = 'Chrome';
  else if (userAgent.indexOf('Safari') > -1) browser = 'Safari';
  else if (userAgent.indexOf('Firefox') > -1) browser = 'Firefox';
  else if (userAgent.indexOf('MSIE') > -1 || userAgent.indexOf('Trident') > -1) browser = 'IE';
  else if (userAgent.indexOf('Edge') > -1) browser = 'Edge';
  else if (userAgent.indexOf('Opera') > -1) browser = 'Opera';

  // Detect OS
  let os = 'unknown';
  if (userAgent.indexOf('Windows') > -1) os = 'Windows';
  else if (userAgent.indexOf('Mac') > -1) os = 'MacOS';
  else if (userAgent.indexOf('Linux') > -1) os = 'Linux';
  else if (userAgent.indexOf('Android') > -1) os = 'Android';
  else if (userAgent.indexOf('iOS') > -1 || userAgent.indexOf('iPhone') > -1 || userAgent.indexOf('iPad') > -1) os = 'iOS';

  // Get screen size
  const screenSize = `${window.innerWidth}x${window.innerHeight}`;

  return {
    deviceType,
    browser,
    os,
    screenSize,
  };
}

export function AnalyticsProvider({ children, disabled = false }: AnalyticsProviderProps) {
  const supabase = createClientComponentClient<Database>();
  const [currentSession, setCurrentSession] = useState<UserSession | null>(null);
  const [isInitialized, setIsInitialized] = useState<boolean>(false);
  const [isEnabled, setIsEnabled] = useState<boolean>(!disabled);
  const eventQueue = useRef<AnalyticsEvent[]>([]);
  const flushTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pathname = usePathname();
  const searchParams = useSearchParams();

  // Session initialization
  useEffect(() => {
    if (!isEnabled) return;
    
    const initializeSession = async () => {
      // Check for existing session ID in localStorage
      let sessionId = localStorage.getItem('analytics_session_id');
      
      // If no session exists, create a new one
      if (!sessionId) {
        sessionId = uuidv4();
        localStorage.setItem('analytics_session_id', sessionId);
      }
      
      const deviceInfo = getDeviceInfo();
      
      // Create session object
      const newSession: UserSession = {
        sessionId,
        startTime: new Date(),
        lastActivityTime: new Date(),
        isActive: true,
        deviceInfo,
        pageViews: 1,
        eventsCount: 0,
      };
      
      setCurrentSession(newSession);
      
      // Get the current user
      const { data: { user } } = await supabase.auth.getUser();
      
      if (user) {
        // Store session in database
        await supabase.rpc('analytics.update_user_session', {
          p_user_id: user.id,
          p_session_id: sessionId,
          p_page_path: pathname,
          p_device_type: deviceInfo.deviceType,
          p_browser: deviceInfo.browser,
          p_os: deviceInfo.os,
          p_screen_size: deviceInfo.screenSize
        });
      }
      
      setIsInitialized(true);
    };
    
    initializeSession();
    
    // Set up activity tracking
    const handleActivity = () => {
      if (currentSession) {
        setCurrentSession({
          ...currentSession,
          lastActivityTime: new Date(),
          isActive: true,
        });
      }
    };
    
    window.addEventListener('mousemove', handleActivity);
    window.addEventListener('keydown', handleActivity);
    window.addEventListener('scroll', handleActivity);
    window.addEventListener('click', handleActivity);
    
    // Set up session expiration check (30 minutes of inactivity)
    const inactivityInterval = setInterval(() => {
      if (currentSession && (new Date().getTime() - currentSession.lastActivityTime.getTime() > 30 * 60 * 1000)) {
        setCurrentSession({
          ...currentSession,
          isActive: false,
          exitPage: pathname,
        });
      }
    }, 60000); // Check every minute
    
    return () => {
      window.removeEventListener('mousemove', handleActivity);
      window.removeEventListener('keydown', handleActivity);
      window.removeEventListener('scroll', handleActivity);
      window.removeEventListener('click', handleActivity);
      clearInterval(inactivityInterval);
    };
  }, [isEnabled]);

  // Track page views when route changes
  useEffect(() => {
    if (isInitialized && isEnabled && currentSession) {
      trackPageView(pathname, document.title);
      
      // Update session in state
      setCurrentSession({
        ...currentSession,
        lastActivityTime: new Date(),
        pageViews: currentSession.pageViews + 1,
        exitPage: pathname,
      });
    }
  }, [pathname, searchParams, isInitialized, isEnabled]);

  // Event batching and flushing
  useEffect(() => {
    if (!isEnabled) return;
    
    const flushEvents = async () => {
      if (eventQueue.current.length === 0) return;
      
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;
      
      const events = [...eventQueue.current];
      eventQueue.current = [];
      
      // Batch insert events
      for (const event of events) {
        await supabase.from('analytics.user_events').insert({
          user_id: user.id,
          event_type: event.eventType,
          event_category: event.eventCategory,
          event_action: event.eventAction,
          event_label: event.eventLabel,
          event_value: event.eventValue ? JSON.stringify(event.eventValue) : null,
          page_path: pathname,
          page_title: document.title,
          client_timestamp: event.clientTimestamp.toISOString(),
          session_id: currentSession?.sessionId,
          device_type: currentSession?.deviceInfo.deviceType,
          browser: currentSession?.deviceInfo.browser,
          os: currentSession?.deviceInfo.os,
          screen_size: currentSession?.deviceInfo.screenSize,
          referrer: document.referrer
        });
      }
      
      // Update session event count
      if (currentSession) {
        setCurrentSession({
          ...currentSession,
          eventsCount: currentSession.eventsCount + events.length,
        });
      }
    };
    
    // Set up flush interval
    const flushInterval = setInterval(() => {
      if (eventQueue.current.length > 0) {
        flushEvents();
      }
    }, 10000); // Flush every 10 seconds
    
    return () => {
      clearInterval(flushInterval);
      if (flushTimeoutRef.current) {
        clearTimeout(flushTimeoutRef.current);
      }
    };
  }, [isEnabled, currentSession]);

  // Core tracking function
  const trackEvent = async (
    eventType: EventType,
    eventCategory: EventCategory,
    eventAction: string,
    eventLabel?: string,
    eventValue?: any
  ) => {
    if (!isEnabled || !isInitialized) return;
    
    const event: AnalyticsEvent = {
      eventType,
      eventCategory,
      eventAction,
      eventLabel,
      eventValue,
      clientTimestamp: new Date(),
    };
    
    // Add to queue
    eventQueue.current.push(event);
    
    // If queue gets too large, flush immediately
    if (eventQueue.current.length >= 20) {
      if (flushTimeoutRef.current) {
        clearTimeout(flushTimeoutRef.current);
      }
      flushTimeoutRef.current = setTimeout(() => {
        flushTimeoutRef.current = null;
        // This will trigger the useEffect to flush events
        setCurrentSession(prev => prev ? { ...prev } : null);
      }, 100);
    }
  };

  // Specialized tracking functions
  const trackPageView = async (pagePath: string, pageTitle: string) => {
    trackEvent('page_view', 'navigation', 'view_page', pageTitle, { path: pagePath });
  };

  const trackFeatureUsage = async (featureId: string, featureCategory: string) => {
    trackEvent('feature_usage', 'feature', 'use_feature', featureId, { category: featureCategory });
    
    // Also update feature usage stats
    const { data: { user } } = await supabase.auth.getUser();
    if (user) {
      await supabase.rpc('analytics.track_feature_usage', {
        p_user_id: user.id,
        p_feature_id: featureId,
        p_feature_category: featureCategory
      });
    }
  };

  const trackInteraction = async (
    elementId: string,
    interactionType: string,
    elementType?: string
  ) => {
    trackEvent(
      'interaction',
      'ui',
      interactionType,
      elementId,
      { elementType }
    );
  };

  const trackFormSubmission = async (
    formId: string,
    formName: string,
    success: boolean
  ) => {
    trackEvent(
      'form_submission',
      'form',
      success ? 'form_submit_success' : 'form_submit_failure',
      formName,
      { formId, success }
    );
  };

  const trackError = async (
    errorType: string,
    errorMessage: string,
    errorContext?: any
  ) => {
    trackEvent(
      'error',
      'error',
      errorType,
      errorMessage,
      errorContext
    );
  };

  const trackConversion = async (
    conversionType: string,
    conversionValue?: number
  ) => {
    trackEvent(
      'conversion',
      'user',
      conversionType,
      undefined,
      { value: conversionValue }
    );
  };

  const trackHeatmapData = async (
    eventType: 'click' | 'move' | 'scroll',
    x?: number,
    y?: number,
    scrollDepth?: number
  ) => {
    if (!isEnabled || !isInitialized) return;
    
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return;
    
    // Get viewport dimensions
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    await supabase.from('analytics.heatmap_data').insert({
      user_id: user.id,
      page_path: pathname,
      event_type: eventType,
      position_x: x,
      position_y: y,
      scroll_depth: scrollDepth,
      viewport_width: viewportWidth,
      viewport_height: viewportHeight
    });
  };

  const enableAnalytics = () => {
    setIsEnabled(true);
    localStorage.setItem('analytics_enabled', 'true');
  };

  const disableAnalytics = () => {
    setIsEnabled(false);
    localStorage.setItem('analytics_enabled', 'false');
  };

  const value: AnalyticsContextType = {
    currentSession,
    isInitialized,
    isEnabled,
    trackEvent,
    trackPageView,
    trackFeatureUsage,
    trackInteraction,
    trackFormSubmission,
    trackError,
    trackConversion,
    trackHeatmapData,
    enableAnalytics,
    disableAnalytics,
  };

  return (
    <AnalyticsContext.Provider value={value}>
      {children}
    </AnalyticsContext.Provider>
  );
}

// Hook for using the analytics context
export function useAnalytics() {
  const context = useContext(AnalyticsContext);
  if (context === undefined) {
    throw new Error('useAnalytics must be used within an AnalyticsProvider');
  }
  return context;
}

// Custom hook for tracking element interactions
export function useTrackInteraction(elementId: string, elementType?: string) {
  const { trackInteraction } = useAnalytics();
  
  return {
    onClick: () => trackInteraction(elementId, 'click', elementType),
    onHover: () => trackInteraction(elementId, 'hover', elementType),
    onFocus: () => trackInteraction(elementId, 'focus', elementType),
  };
}

// Custom hook for tracking feature usage
export function useTrackFeature(featureId: string, featureCategory: string) {
  const { trackFeatureUsage } = useAnalytics();
  
  return () => trackFeatureUsage(featureId, featureCategory);
}

// Custom hook for tracking form submissions
export function useTrackForm(formId: string, formName: string) {
  const { trackFormSubmission } = useAnalytics();
  
  return {
    onSuccess: () => trackFormSubmission(formId, formName, true),
    onFailure: () => trackFormSubmission(formId, formName, false),
  };
}

// Custom hook for tracking errors
export function useTrackError() {
  const { trackError } = useAnalytics();
  
  return (errorType: string, errorMessage: string, errorContext?: any) => 
    trackError(errorType, errorMessage, errorContext);
}

// Custom hook for tracking conversions
export function useTrackConversion() {
  const { trackConversion } = useAnalytics();
  
  return (conversionType: string, conversionValue?: number) => 
    trackConversion(conversionType, conversionValue);
}

// HOC to wrap components with analytics tracking
export function withAnalytics<P extends object>(
  Component: React.ComponentType<P>,
  options: {
    trackMount?: boolean;
    trackUnmount?: boolean;
    featureId?: string;
    featureCategory?: string;
    elementId?: string;
    elementType?: string;
  } = {}
) {
  return function WrappedComponent(props: P) {
    const {
      trackInteraction,
      trackFeatureUsage,
      isEnabled,
      isInitialized
    } = useAnalytics();
    
    useEffect(() => {
      if (!isEnabled || !isInitialized) return;
      
      if (options.trackMount) {
        if (options.elementId) {
          trackInteraction(
            options.elementId,
            'mount',
            options.elementType
          );
        }
        
        if (options.featureId && options.featureCategory) {
          trackFeatureUsage(
            options.featureId,
            options.featureCategory
          );
        }
      }
      
      return () => {
        if (options.trackUnmount && options.elementId) {
          trackInteraction(
            options.elementId,
            'unmount',
            options.elementType
          );
        }
      };
    }, [isEnabled, isInitialized]);
    
    return <Component {...props} />;
  };
} 