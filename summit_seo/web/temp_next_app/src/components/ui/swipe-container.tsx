"use client";

import React, { useState, useEffect } from "react";
import { useSwipeGesture } from "@/hooks/useSwipeGesture";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { useResponsive } from "@/contexts/responsive-context";

interface SwipeContainerProps {
  children: React.ReactNode;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  className?: string;
  swipeIndicator?: boolean;
  showSwipeHint?: boolean;
  restrictToMobile?: boolean;
  swipeDistance?: number;
  preventScrollY?: boolean;
}

interface SwipeIndicatorProps {
  direction: "left" | "right" | "up" | "down";
  visible: boolean;
}

const swipeAnimations = {
  left: {
    initial: { x: "0%" },
    animate: { x: "0%" },
    exit: { x: "-100%" },
    swipeIndicator: { x: 10, opacity: 0.7 },
  },
  right: {
    initial: { x: "0%" },
    animate: { x: "0%" },
    exit: { x: "100%" },
    swipeIndicator: { x: -10, opacity: 0.7 },
  },
  up: {
    initial: { y: "0%" },
    animate: { y: "0%" },
    exit: { y: "-100%" },
    swipeIndicator: { y: 10, opacity: 0.7 },
  },
  down: {
    initial: { y: "0%" },
    animate: { y: "0%" },
    exit: { y: "100%" },
    swipeIndicator: { y: -10, opacity: 0.7 },
  },
};

const SwipeIndicator: React.FC<SwipeIndicatorProps> = ({ direction, visible }) => {
  const isHorizontal = direction === "left" || direction === "right";
  const oppositeDirection = 
    direction === "left" ? "right" :
    direction === "right" ? "left" :
    direction === "up" ? "down" : "up";

  return (
    <motion.div
      className={cn(
        "absolute z-10 flex items-center justify-center",
        isHorizontal ? "h-16 w-8" : "h-8 w-16",
        direction === "left" && "left-2 top-1/2 -translate-y-1/2",
        direction === "right" && "right-2 top-1/2 -translate-y-1/2",
        direction === "up" && "top-2 left-1/2 -translate-x-1/2",
        direction === "down" && "bottom-2 left-1/2 -translate-x-1/2",
      )}
      initial={{ opacity: 0 }}
      animate={visible ? 
        { ...swipeAnimations[oppositeDirection].swipeIndicator } :
        { opacity: 0 }
      }
      transition={{ duration: 0.3, repeat: visible ? Infinity : 0, repeatType: "reverse" }}
    >
      <div 
        className={cn(
          "bg-primary-600/20 rounded-full flex items-center justify-center",
          isHorizontal ? "h-16 w-8" : "h-8 w-16"
        )}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className={cn(
            "text-primary-600",
            direction === "left" && "rotate-180",
            direction === "up" && "-rotate-90",
            direction === "down" && "rotate-90"
          )}
        >
          <path d="m9 18 6-6-6-6" />
        </svg>
      </div>
    </motion.div>
  );
};

/**
 * Container component that enables swipe gestures for mobile navigation
 */
export function SwipeContainer({
  children,
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  className,
  swipeIndicator = true,
  showSwipeHint = false,
  restrictToMobile = true,
  swipeDistance = 50,
  preventScrollY = false,
}: SwipeContainerProps) {
  const { isMobile } = useResponsive();
  const [showHint, setShowHint] = useState(showSwipeHint);
  const [direction, setDirection] = useState<"left" | "right" | "up" | "down" | null>(null);
  const [swipeTriggered, setSwipeTriggered] = useState(false);

  // Determine available swipe directions
  const hasLeftSwipe = Boolean(onSwipeLeft);
  const hasRightSwipe = Boolean(onSwipeRight);
  const hasUpSwipe = Boolean(onSwipeUp);
  const hasDownSwipe = Boolean(onSwipeDown);

  const { touchHandlers, swipeState } = useSwipeGesture(
    {
      onSwipeLeft: () => {
        if (hasLeftSwipe) {
          setDirection("left");
          setSwipeTriggered(true);
          onSwipeLeft?.();
        }
      },
      onSwipeRight: () => {
        if (hasRightSwipe) {
          setDirection("right");
          setSwipeTriggered(true);
          onSwipeRight?.();
        }
      },
      onSwipeUp: () => {
        if (hasUpSwipe) {
          setDirection("up");
          setSwipeTriggered(true);
          onSwipeUp?.();
        }
      },
      onSwipeDown: () => {
        if (hasDownSwipe) {
          setDirection("down");
          setSwipeTriggered(true);
          onSwipeDown?.();
        }
      },
    },
    {
      minDistance: swipeDistance,
      preventScrollOnSwipeY: preventScrollY,
    }
  );

  // Hide hint after first swipe or after 5 seconds
  useEffect(() => {
    if (swipeTriggered) {
      setShowHint(false);
    }

    if (showHint) {
      const timer = setTimeout(() => {
        setShowHint(false);
      }, 5000);

      return () => clearTimeout(timer);
    }
  }, [swipeTriggered, showHint]);

  // Reset swipe triggered state after animation
  useEffect(() => {
    if (swipeTriggered) {
      const timer = setTimeout(() => {
        setSwipeTriggered(false);
        setDirection(null);
      }, 300);

      return () => clearTimeout(timer);
    }
  }, [swipeTriggered]);

  // Don't attach gesture handlers if restricting to mobile and not on mobile
  const shouldEnableSwipe = !restrictToMobile || isMobile;

  return (
    <motion.div
      className={cn("relative overflow-hidden touch-pan-y", className)}
      {...(shouldEnableSwipe ? touchHandlers : {})}
    >
      {children}
      
      {/* Swipe indicators */}
      {swipeIndicator && isMobile && (
        <>
          {hasLeftSwipe && (
            <SwipeIndicator 
              direction="left" 
              visible={showHint && hasLeftSwipe}
            />
          )}
          {hasRightSwipe && (
            <SwipeIndicator 
              direction="right" 
              visible={showHint && hasRightSwipe}
            />
          )}
          {hasUpSwipe && (
            <SwipeIndicator 
              direction="up" 
              visible={showHint && hasUpSwipe}
            />
          )}
          {hasDownSwipe && (
            <SwipeIndicator 
              direction="down" 
              visible={showHint && hasDownSwipe}
            />
          )}
        </>
      )}
    </motion.div>
  );
} 