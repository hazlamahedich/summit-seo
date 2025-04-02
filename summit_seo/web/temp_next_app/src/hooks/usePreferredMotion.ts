import { useEffect, useState } from 'react';
import { useReducedMotion } from '@/lib/motion';

export type MotionPreference = 'full' | 'reduced' | 'none';

/**
 * Hook for managing motion preferences across the application.
 * Respects user's system preferences while allowing for app-specific overrides.
 * 
 * @param defaultPreference - Optional default preference to use ('full', 'reduced', 'none')
 * @returns An object with the current motion preference and methods to update it
 */
export function usePreferredMotion(defaultPreference?: MotionPreference) {
  // Get system preference for reduced motion
  const systemPrefersReducedMotion = useReducedMotion();
  
  // Initialize state from localStorage or system preference if available
  const [preference, setPreference] = useState<MotionPreference>(() => {
    // Only run in browser environment
    if (typeof window === 'undefined') {
      return defaultPreference || (systemPrefersReducedMotion ? 'reduced' : 'full');
    }
    
    // Try to get stored preference
    const stored = localStorage.getItem('motion-preference');
    if (stored && (stored === 'full' || stored === 'reduced' || stored === 'none')) {
      return stored as MotionPreference;
    }
    
    // Fall back to system preference or default
    return defaultPreference || (systemPrefersReducedMotion ? 'reduced' : 'full');
  });
  
  // Update localStorage when preference changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('motion-preference', preference);
    }
  }, [preference]);
  
  // Update preference if system preference changes
  useEffect(() => {
    // Only update if the user hasn't explicitly set a preference
    const stored = localStorage.getItem('motion-preference');
    if (!stored) {
      setPreference(systemPrefersReducedMotion ? 'reduced' : 'full');
    }
  }, [systemPrefersReducedMotion]);
  
  // Helper functions
  const enableFullMotion = () => setPreference('full');
  const enableReducedMotion = () => setPreference('reduced');
  const disableMotion = () => setPreference('none');
  
  // Check if animations should be enabled
  const isMotionEnabled = preference !== 'none';
  
  // Check if full animations should be enabled
  const isFullMotionEnabled = preference === 'full';
  
  // Toggle between full and reduced motion
  const toggleMotion = () => {
    setPreference(prev => prev === 'full' ? 'reduced' : 'full');
  };
  
  // Toggle between the three states
  const cycleMotion = () => {
    setPreference(prev => {
      if (prev === 'full') return 'reduced';
      if (prev === 'reduced') return 'none';
      return 'full';
    });
  };
  
  return {
    preference,
    setPreference,
    isMotionEnabled,
    isFullMotionEnabled,
    enableFullMotion,
    enableReducedMotion,
    disableMotion,
    toggleMotion,
    cycleMotion,
    systemPrefersReducedMotion
  };
}

export default usePreferredMotion; 