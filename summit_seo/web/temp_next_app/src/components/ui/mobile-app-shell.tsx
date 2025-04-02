"use client";

import React, { useState, useEffect } from "react";
import { cn } from "@/lib/utils";
import { useResponsive } from "@/contexts/responsive-context";
import { PullToRefresh } from "@/components/ui/pull-to-refresh";
import { useSwipeGesture } from "@/hooks/useSwipeGesture";
import { usePathname, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { OfflineStatus } from "@/components/ui/offline-status";
import { useOnlineStatus } from "@/lib/offline-manager";

interface MobileAppShellProps {
  children: React.ReactNode;
  className?: string;
  enablePullToRefresh?: boolean;
  onRefresh?: () => Promise<void>;
  enableSwipeNavigation?: boolean;
  showOfflineIndicator?: boolean;
  preventBodyScroll?: boolean;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  navRoutes?: {
    back?: string;
    forward?: string;
  };
  pageTransitionEffect?: "slide" | "fade" | "none";
}

/**
 * Mobile-optimized application shell with integrated mobile features
 */
export function MobileAppShell({
  children,
  className,
  enablePullToRefresh = true,
  onRefresh,
  enableSwipeNavigation = true,
  showOfflineIndicator = true,
  preventBodyScroll = true,
  header,
  footer,
  navRoutes,
  pageTransitionEffect = "slide",
}: MobileAppShellProps) {
  const { isMobile } = useResponsive();
  const router = useRouter();
  const pathname = usePathname();
  const isOnline = useOnlineStatus();
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [direction, setDirection] = useState<"left" | "right" | null>(null);

  // Prevent body scrolling if configured
  useEffect(() => {
    if (isMobile && preventBodyScroll) {
      document.body.style.overflow = "hidden";
      document.documentElement.style.position = "fixed";
      document.documentElement.style.width = "100%";
      document.documentElement.style.height = "100%";
      document.documentElement.style.overscrollBehaviorY = "none";
    }
    
    return () => {
      document.body.style.overflow = "";
      document.documentElement.style.position = "";
      document.documentElement.style.width = "";
      document.documentElement.style.height = "";
      document.documentElement.style.overscrollBehaviorY = "";
    };
  }, [isMobile, preventBodyScroll]);

  // Handle refresh
  const handleRefresh = async () => {
    if (isRefreshing || !onRefresh) return;
    
    try {
      setIsRefreshing(true);
      await onRefresh();
    } finally {
      setIsRefreshing(false);
    }
  };

  // Set up swipe navigation
  const handleSwipeLeft = () => {
    if (!enableSwipeNavigation || !navRoutes?.forward) return;
    setDirection("left");
    router.push(navRoutes.forward);
  };

  const handleSwipeRight = () => {
    if (!enableSwipeNavigation || !navRoutes?.back) return;
    setDirection("right");
    router.push(navRoutes.back);
  };

  const { touchHandlers } = useSwipeGesture({
    onSwipeLeft: handleSwipeLeft,
    onSwipeRight: handleSwipeRight,
  });

  // Animation variants for page transitions
  const pageVariants = {
    initial: {
      opacity: pageTransitionEffect === "none" ? 1 : 0,
      x: pageTransitionEffect === "slide" 
        ? direction === "left" 
          ? "100%" 
          : direction === "right" 
            ? "-100%" 
            : 0
        : 0,
    },
    animate: {
      opacity: 1,
      x: 0,
    },
    exit: {
      opacity: pageTransitionEffect === "none" ? 1 : 0,
      x: pageTransitionEffect === "slide" 
        ? direction === "left" 
          ? "-100%" 
          : direction === "right" 
            ? "100%" 
            : 0
        : 0,
    },
  };

  // Wrap content with necessary mobile optimizations
  const content = (
    <motion.div
      className={cn(
        "h-full w-full flex flex-col overflow-hidden",
        className
      )}
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageVariants}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      {/* Header */}
      {header && (
        <div className="flex-shrink-0">
          {header}
        </div>
      )}
      
      {/* Main content area */}
      <div 
        className="flex-1 overflow-auto relative"
        {...(isMobile && enableSwipeNavigation ? touchHandlers : {})}
      >
        {children}
      </div>
      
      {/* Footer */}
      {footer && (
        <div className="flex-shrink-0">
          {footer}
        </div>
      )}
      
      {/* Offline indicator */}
      {showOfflineIndicator && !isOnline && (
        <OfflineStatus position="bottom" />
      )}
    </motion.div>
  );

  // Apply pull-to-refresh only on mobile
  if (isMobile && enablePullToRefresh && onRefresh) {
    return (
      <PullToRefresh onRefresh={handleRefresh}>
        {content}
      </PullToRefresh>
    );
  }

  // Return without pull-to-refresh for non-mobile or when disabled
  return content;
} 