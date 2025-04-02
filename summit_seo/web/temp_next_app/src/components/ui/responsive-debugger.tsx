"use client";

import React from "react";
import { cn } from "@/lib/utils";
import { Separator } from "./separator";

interface ResponsiveDebuggerProps {
  visible?: boolean;
  position?: "top-left" | "top-right" | "bottom-left" | "bottom-right";
  showDeviceType?: boolean;
  showBreakpoint?: boolean;
  showDimensions?: boolean;
  className?: string;
}

/**
 * A development helper component that shows current screen dimensions
 * and Tailwind breakpoints. Only visible in development mode.
 */
export function ResponsiveDebugger({
  visible = true,
  position = "bottom-right",
  showDeviceType = true,
  showBreakpoint = true,
  showDimensions = true,
  className,
}: ResponsiveDebuggerProps) {
  const [mounted, setMounted] = React.useState(false);
  const [dimensions, setDimensions] = React.useState({ width: 0, height: 0 });
  
  // Only show in development
  const isDevelopment = process.env.NODE_ENV === "development";
  
  React.useEffect(() => {
    setMounted(true);
    
    const updateDimensions = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };
    
    updateDimensions();
    window.addEventListener("resize", updateDimensions);
    
    return () => {
      window.removeEventListener("resize", updateDimensions);
    };
  }, []);

  // Don't render anything on the server
  if (!mounted || !isDevelopment || !visible) return null;
  
  const getBreakpoint = (width: number): string => {
    if (width < 640) return "xs"; // Default Tailwind
    if (width < 768) return "sm";
    if (width < 1024) return "md";
    if (width < 1280) return "lg";
    if (width < 1536) return "xl";
    return "2xl";
  };

  const getDeviceType = (width: number): string => {
    if (width < 640) return "Mobile";
    if (width < 768) return "Mobile (Large)";
    if (width < 1024) return "Tablet";
    if (width < 1280) return "Laptop";
    if (width < 1536) return "Desktop";
    return "Large Desktop";
  };

  const breakpoint = getBreakpoint(dimensions.width);
  const deviceType = getDeviceType(dimensions.width);
  
  const positionClasses = {
    "top-left": "top-2 left-2",
    "top-right": "top-2 right-2",
    "bottom-left": "bottom-2 left-2",
    "bottom-right": "bottom-2 right-2",
  };

  const getBreakpointColor = (bp: string): string => {
    const colors = {
      xs: "text-red-500",
      sm: "text-orange-500",
      md: "text-yellow-500",
      lg: "text-green-500",
      xl: "text-blue-500",
      "2xl": "text-purple-500",
    };
    return colors[bp as keyof typeof colors] || "text-gray-500";
  };

  return (
    <div
      className={cn(
        "fixed z-50 p-2 bg-background border rounded shadow text-xs font-mono",
        positionClasses[position],
        className
      )}
    >
      {showBreakpoint && (
        <div className="flex items-center justify-between gap-2">
          <span>Breakpoint:</span>
          <span className={cn("font-bold", getBreakpointColor(breakpoint))}>
            {breakpoint}
          </span>
        </div>
      )}
      
      {showDeviceType && (
        <div className="flex items-center justify-between gap-2">
          <span>Device:</span>
          <span className="font-bold">{deviceType}</span>
        </div>
      )}
      
      {showDimensions && (
        <div className="flex items-center justify-between gap-2">
          <span>Size:</span>
          <span className="font-bold">
            {dimensions.width} × {dimensions.height}
          </span>
        </div>
      )}
      
      <div className="flex pt-1 mt-1 border-t gap-1">
        <div className="hidden sm:block h-2 w-2 bg-red-500 rounded-full" title="xs"></div>
        <div className="hidden md:block h-2 w-2 bg-orange-500 rounded-full" title="sm"></div>
        <div className="hidden lg:block h-2 w-2 bg-yellow-500 rounded-full" title="md"></div>
        <div className="hidden xl:block h-2 w-2 bg-green-500 rounded-full" title="lg"></div>
        <div className="hidden 2xl:block h-2 w-2 bg-blue-500 rounded-full" title="xl"></div>
        <div className="h-2 w-2 bg-purple-500 rounded-full" title="2xl"></div>
      </div>
    </div>
  );
} 