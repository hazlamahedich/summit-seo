"use client";

import { useState, useEffect, useMemo, useCallback } from "react";

type Breakpoint = "xs" | "sm" | "md" | "lg" | "xl" | "2xl";

interface BreakpointConfig {
  xs: number;
  sm: number;
  md: number;
  lg: number;
  xl: number;
  "2xl": number;
}

// Default Tailwind CSS breakpoints
const defaultBreakpoints: BreakpointConfig = {
  xs: 0,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  "2xl": 1536,
};

/**
 * Custom hook to detect the current breakpoint based on window width
 * @param customBreakpoints Optional custom breakpoints configuration
 * @returns Current breakpoint, window dimensions, and utility functions
 */
export function useBreakpoint(customBreakpoints?: Partial<BreakpointConfig>) {
  // Initialize with default breakpoint to prevent hydration mismatch
  const [breakpoint, setBreakpoint] = useState<Breakpoint>("xs");
  const [windowSize, setWindowSize] = useState({
    width: 0,
    height: 0,
  });
  const [mounted, setMounted] = useState(false);

  // Stabilize breakpoints object with useMemo to prevent it from changing on each render
  const breakpoints = useMemo(
    () => ({ ...defaultBreakpoints, ...customBreakpoints }),
    [customBreakpoints]
  );

  // Create a stable determineBreakpoint function
  const determineBreakpoint = useCallback((width: number): Breakpoint => {
    if (width < breakpoints.sm) return "xs";
    if (width < breakpoints.md) return "sm";
    if (width < breakpoints.lg) return "md";
    if (width < breakpoints.xl) return "lg";
    if (width < breakpoints["2xl"]) return "xl";
    return "2xl";
  }, [breakpoints]);

  // Stable resize handler
  const handleResize = useCallback(() => {
    const width = window.innerWidth;
    const height = window.innerHeight;
    
    // Update window dimensions
    setWindowSize({ width, height });
    
    // Determine current breakpoint
    const newBreakpoint = determineBreakpoint(width);
    setBreakpoint(newBreakpoint);
  }, [determineBreakpoint]);

  // Run effect once on mount and when dependencies change
  useEffect(() => {
    // Mark as mounted to prevent hydration mismatch
    setMounted(true);

    // Set initial values
    handleResize();

    // Add event listener for window resize
    window.addEventListener("resize", handleResize);

    // Cleanup event listener on unmount
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [handleResize]); // Only depend on the stable handleResize function

  /**
   * Check if current breakpoint is at least the specified breakpoint
   * @param breakpointToCheck Breakpoint to check against
   * @returns boolean
   */
  const isMin = useCallback((breakpointToCheck: Breakpoint): boolean => {
    const breakpointValues: { [key in Breakpoint]: number } = breakpoints;
    return windowSize.width >= breakpointValues[breakpointToCheck];
  }, [breakpoints, windowSize.width]);

  /**
   * Check if current breakpoint is at most the specified breakpoint
   * @param breakpointToCheck Breakpoint to check against
   * @returns boolean
   */
  const isMax = useCallback((breakpointToCheck: Breakpoint): boolean => {
    const nextBreakpoint = getNextBreakpoint(breakpointToCheck);
    if (!nextBreakpoint) return true; // If no next breakpoint, it's always true
    
    const breakpointValues: { [key in Breakpoint]: number } = breakpoints;
    return windowSize.width < breakpointValues[nextBreakpoint];
  }, [breakpoints, windowSize.width]);

  /**
   * Get the next larger breakpoint
   * @param bp Current breakpoint
   * @returns Next breakpoint or null if already at largest
   */
  const getNextBreakpoint = (bp: Breakpoint): Breakpoint | null => {
    const breakpointsArray: Breakpoint[] = ["xs", "sm", "md", "lg", "xl", "2xl"];
    const currentIndex = breakpointsArray.indexOf(bp);
    if (currentIndex < breakpointsArray.length - 1) {
      return breakpointsArray[currentIndex + 1];
    }
    return null;
  };

  /**
   * Check if current breakpoint is between two specified breakpoints (inclusive)
   * @param min Minimum breakpoint (inclusive)
   * @param max Maximum breakpoint (inclusive)
   * @returns boolean
   */
  const isBetween = useCallback((min: Breakpoint, max: Breakpoint): boolean => {
    return isMin(min) && isMax(max);
  }, [isMin, isMax]);

  return {
    breakpoint,
    windowSize,
    isMin,
    isMax,
    isBetween,
    mounted,
  };
} 