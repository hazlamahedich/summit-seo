"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { useResponsive } from "@/contexts/responsive-context";
import { RefreshCw } from "lucide-react";

interface PullToRefreshProps {
  onRefresh: () => Promise<void>;
  children: React.ReactNode;
  className?: string;
  threshold?: number;
  pullDistance?: number;
  maxPullDistance?: number;
  refreshingText?: string;
  pullingText?: string;
  releaseText?: string;
  showIndicator?: boolean;
  color?: string;
  disabled?: boolean;
}

/**
 * Pull-to-refresh component for mobile applications
 */
export function PullToRefresh({
  onRefresh,
  children,
  className,
  threshold = 80,
  pullDistance = 100,
  maxPullDistance = 120,
  refreshingText = "Refreshing...",
  pullingText = "Pull to refresh",
  releaseText = "Release to refresh",
  showIndicator = true,
  color = "var(--primary)",
  disabled = false,
}: PullToRefreshProps) {
  const [startY, setStartY] = useState(0);
  const [pulling, setPulling] = useState(false);
  const [pullDelta, setPullDelta] = useState(0);
  const [refreshing, setRefreshing] = useState(false);
  const [willRefresh, setWillRefresh] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const { isMobile } = useResponsive();

  // Reset state when disabled changes
  useEffect(() => {
    if (disabled) {
      setPulling(false);
      setPullDelta(0);
      setRefreshing(false);
      setWillRefresh(false);
    }
  }, [disabled]);

  // Handle touch start
  const handleTouchStart = (e: React.TouchEvent) => {
    if (disabled || refreshing) return;
    
    // Only trigger pull to refresh when at the top of the page
    if (window.scrollY > 5) return;
    
    setStartY(e.touches[0].clientY);
    setPulling(true);
  };

  // Handle touch move
  const handleTouchMove = (e: React.TouchEvent) => {
    if (!pulling || disabled || refreshing) return;
    
    const currentY = e.touches[0].clientY;
    const delta = Math.max(0, currentY - startY);
    
    // Apply resistance - the further you pull, the harder it gets
    const resistedDelta = Math.min(
      maxPullDistance,
      delta > pullDistance 
        ? pullDistance + Math.pow(delta - pullDistance, 0.8) 
        : delta
    );
    
    setPullDelta(resistedDelta);
    setWillRefresh(resistedDelta > threshold);
    
    // Prevent default scrolling when pulling
    if (resistedDelta > 5) {
      e.preventDefault();
    }
  };

  // Handle touch end
  const handleTouchEnd = async () => {
    if (!pulling || disabled || refreshing) return;
    
    if (pullDelta > threshold) {
      try {
        setRefreshing(true);
        await onRefresh();
      } catch (error) {
        console.error("Refresh failed:", error);
      } finally {
        setRefreshing(false);
      }
    }
    
    setPulling(false);
    setPullDelta(0);
    setWillRefresh(false);
  };

  // Calculate progress percentage
  const progress = Math.min(100, (pullDelta / threshold) * 100);
  
  // Determine indicator text
  const getIndicatorText = () => {
    if (refreshing) return refreshingText;
    if (willRefresh) return releaseText;
    return pullingText;
  };

  // Use touch handlers only on mobile
  const touchHandlers = isMobile && !disabled ? {
    onTouchStart: handleTouchStart,
    onTouchMove: handleTouchMove,
    onTouchEnd: handleTouchEnd,
    onTouchCancel: handleTouchEnd
  } : {};
  
  return (
    <div 
      className={cn("relative overflow-hidden", className)}
      ref={containerRef}
      {...touchHandlers}
    >
      {/* Pull indicator */}
      {showIndicator && (isMobile || pulling || refreshing) && (
        <motion.div
          className="absolute left-0 right-0 z-10 flex flex-col items-center justify-center overflow-hidden bg-background/80 backdrop-blur-sm"
          style={{ 
            height: pulling ? pullDelta : 0,
            top: 0,
            opacity: refreshing ? 1 : Math.min(1, pullDelta / 40),
          }}
        >
          <div className="flex items-center gap-2">
            <motion.div
              animate={{ 
                rotate: refreshing ? 360 : willRefresh ? 180 : progress * 1.8,
              }}
              transition={{ 
                duration: refreshing ? 1 : 0.2,
                ease: "linear",
                repeat: refreshing ? Infinity : 0,
              }}
            >
              <RefreshCw 
                style={{ color }} 
                className={cn(
                  "h-5 w-5",
                  refreshing && "opacity-100",
                  !refreshing && "opacity-70"
                )} 
              />
            </motion.div>
            <span 
              className="text-sm font-medium"
              style={{ color }}
            >
              {getIndicatorText()}
            </span>
          </div>
        </motion.div>
      )}
      
      {/* Content */}
      <motion.div
        style={{ 
          translateY: refreshing ? pullDistance / 3 : pullDelta,
        }}
      >
        {children}
      </motion.div>
    </div>
  );
} 