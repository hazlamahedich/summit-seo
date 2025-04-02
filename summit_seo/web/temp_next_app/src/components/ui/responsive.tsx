"use client";

import React from "react";
import { useResponsive } from "@/contexts/responsive-context";
import { cn } from "@/lib/utils";

type Breakpoint = "xs" | "sm" | "md" | "lg" | "xl" | "2xl";

interface ResponsiveBaseProps {
  children: React.ReactNode;
  className?: string;
}

interface ResponsiveShowProps extends ResponsiveBaseProps {
  breakpoint: Breakpoint;
  /**
   * If true, display at this breakpoint and above (min-width)
   * If false, display at this breakpoint and below (max-width)
   */
  above?: boolean;
}

interface ResponsiveRangeProps extends ResponsiveBaseProps {
  from?: Breakpoint;
  to?: Breakpoint;
}

interface ResponsiveForProps extends ResponsiveBaseProps {
  only: Breakpoint | Breakpoint[];
}

interface ResponsiveDeviceProps extends ResponsiveBaseProps {
  device: "mobile" | "tablet" | "desktop" | "laptop" | Array<"mobile" | "tablet" | "desktop" | "laptop">;
}

/**
 * Shows content at specified breakpoint and above
 */
export function Show({
  children,
  breakpoint,
  above = true,
  className,
}: ResponsiveShowProps) {
  const { isMin, isMax } = useResponsive();
  const shouldRender = above ? isMin(breakpoint) : isMax(breakpoint);

  return shouldRender ? (
    <div className={className}>{children}</div>
  ) : null;
}

/**
 * Shows content within a range of breakpoints (inclusive)
 */
export function Range({
  children,
  from = "xs",
  to = "2xl",
  className,
}: ResponsiveRangeProps) {
  const { isBetween } = useResponsive();
  const shouldRender = isBetween(from, to);

  return shouldRender ? (
    <div className={className}>{children}</div>
  ) : null;
}

/**
 * Shows content only at specific breakpoint(s)
 */
export function For({ 
  children, 
  only, 
  className 
}: ResponsiveForProps) {
  const { breakpoint } = useResponsive();
  const breakpoints = Array.isArray(only) ? only : [only];
  const shouldRender = breakpoints.includes(breakpoint);

  return shouldRender ? (
    <div className={className}>{children}</div>
  ) : null;
}

/**
 * Shows content only on specific device type(s)
 */
export function Device({ 
  children, 
  device, 
  className 
}: ResponsiveDeviceProps) {
  const { deviceType } = useResponsive();
  const devices = Array.isArray(device) ? device : [device];
  const shouldRender = devices.includes(deviceType);

  return shouldRender ? (
    <div className={className}>{children}</div>
  ) : null;
}

/**
 * Container for all responsive components
 */
export const Responsive = {
  Show,
  Range,
  For,
  Device,
}; 