"use client";

import React, { createContext, useContext, useCallback, useMemo } from "react";
import { useBreakpoint } from "@/hooks/useBreakpoint";

// Define the props for the Responsive context type
type Breakpoint = "xs" | "sm" | "md" | "lg" | "xl" | "2xl";
type DeviceType = "mobile" | "tablet" | "laptop" | "desktop";

interface ResponsiveContextType {
  breakpoint: Breakpoint;
  deviceType: DeviceType;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  windowSize: {
    width: number;
    height: number;
  };
  isMin: (breakpoint: Breakpoint) => boolean;
  isMax: (breakpoint: Breakpoint) => boolean;
  isBetween: (min: Breakpoint, max: Breakpoint) => boolean;
}

// Create the context with a default value
const ResponsiveContext = createContext<ResponsiveContextType | undefined>(
  undefined
);

// Props for the ResponsiveProvider component
interface ResponsiveProviderProps {
  children: React.ReactNode;
}

/**
 * Provides responsive design context to the application
 * Includes breakpoint information, device type, and utility methods
 */
export function ResponsiveProvider({ children }: ResponsiveProviderProps) {
  const {
    breakpoint,
    windowSize,
    isMin,
    isMax,
    isBetween,
    mounted,
  } = useBreakpoint();

  // Determine device type based on breakpoint with useCallback
  const getDeviceType = useCallback((): DeviceType => {
    if (breakpoint === "xs" || breakpoint === "sm") return "mobile";
    if (breakpoint === "md") return "tablet";
    if (breakpoint === "lg") return "laptop";
    return "desktop";
  }, [breakpoint]);

  // Memoize derived values to prevent unnecessary calculations
  const deviceInfo = useMemo(() => {
    const deviceType = getDeviceType();
    const isMobile = deviceType === "mobile";
    const isTablet = deviceType === "tablet";
    const isDesktop = deviceType === "laptop" || deviceType === "desktop";
    
    return {
      deviceType,
      isMobile,
      isTablet,
      isDesktop
    };
  }, [getDeviceType]);

  // Memoize the context value to prevent unnecessary re-renders
  const contextValue = useMemo(
    () => ({
      breakpoint,
      ...deviceInfo,
      windowSize,
      isMin,
      isMax,
      isBetween,
    }),
    [
      breakpoint,
      deviceInfo,
      windowSize,
      isMin,
      isMax,
      isBetween,
    ]
  );

  // Avoid rendering on server to prevent hydration mismatch
  if (!mounted) {
    // Provide a minimal fallback that doesn't rely on window dimensions
    return (
      <ResponsiveContext.Provider
        value={{
          breakpoint: "xs",
          deviceType: "mobile",
          isMobile: true,
          isTablet: false,
          isDesktop: false,
          windowSize: { width: 0, height: 0 },
          isMin: () => false,
          isMax: () => false,
          isBetween: () => false,
        }}
      >
        {children}
      </ResponsiveContext.Provider>
    );
  }

  return (
    <ResponsiveContext.Provider value={contextValue}>
      {children}
    </ResponsiveContext.Provider>
  );
}

/**
 * Hook to access the responsive context
 * @returns ResponsiveContextType object with breakpoint information and utility methods
 */
export function useResponsive(): ResponsiveContextType {
  const context = useContext(ResponsiveContext);
  if (context === undefined) {
    throw new Error("useResponsive must be used within a ResponsiveProvider");
  }
  return context;
} 