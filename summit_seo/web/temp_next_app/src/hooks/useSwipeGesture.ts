"use client";

import { useState, useEffect } from "react";

interface SwipeHandlers {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
}

interface SwipeConfig {
  minDistance?: number;
  maxTime?: number;
  preventScrollOnSwipeY?: boolean;
}

interface SwipeState {
  swiping: boolean;
  direction: "left" | "right" | "up" | "down" | null;
  startX: number;
  startY: number;
  startTime: number;
  distance: number;
}

/**
 * Hook for detecting swipe gestures on touch devices
 * @param handlers Object containing callback functions for different swipe directions
 * @param config Configuration options for swipe detection
 * @returns Object containing event handlers to attach to a component
 */
export function useSwipeGesture(
  handlers: SwipeHandlers = {},
  config: SwipeConfig = {}
) {
  const {
    onSwipeLeft,
    onSwipeRight,
    onSwipeUp,
    onSwipeDown,
  } = handlers;

  const {
    minDistance = 50,
    maxTime = 300,
    preventScrollOnSwipeY = false,
  } = config;

  const [swipeState, setSwipeState] = useState<SwipeState>({
    swiping: false,
    direction: null,
    startX: 0,
    startY: 0,
    startTime: 0,
    distance: 0,
  });

  // Handle start of touch
  const handleTouchStart = (e: React.TouchEvent) => {
    const touch = e.touches[0];
    setSwipeState({
      swiping: true,
      direction: null,
      startX: touch.clientX,
      startY: touch.clientY,
      startTime: Date.now(),
      distance: 0,
    });
  };

  // Handle touch move
  const handleTouchMove = (e: React.TouchEvent) => {
    if (!swipeState.swiping) return;

    const touch = e.touches[0];
    const deltaX = touch.clientX - swipeState.startX;
    const deltaY = touch.clientY - swipeState.startY;
    
    // Prevent default scrolling behavior for vertical swipes if configured
    if (preventScrollOnSwipeY && Math.abs(deltaY) > Math.abs(deltaX) && Math.abs(deltaY) > 10) {
      e.preventDefault();
    }
    
    // Update state with current direction and distance
    let direction: "left" | "right" | "up" | "down" | null = null;
    let distance = 0;
    
    if (Math.abs(deltaX) > Math.abs(deltaY)) {
      // Horizontal swipe
      direction = deltaX > 0 ? "right" : "left";
      distance = Math.abs(deltaX);
    } else {
      // Vertical swipe
      direction = deltaY > 0 ? "down" : "up";
      distance = Math.abs(deltaY);
    }
    
    setSwipeState(prev => ({
      ...prev,
      direction,
      distance,
    }));
  };

  // Handle end of touch
  const handleTouchEnd = (e: React.TouchEvent) => {
    if (!swipeState.swiping) return;
    
    const endTime = Date.now();
    const timeTaken = endTime - swipeState.startTime;
    
    // Check if swipe meets minimum distance and maximum time criteria
    if (swipeState.distance > minDistance && timeTaken < maxTime) {
      // Trigger the appropriate handler based on direction
      switch (swipeState.direction) {
        case "left":
          onSwipeLeft && onSwipeLeft();
          break;
        case "right":
          onSwipeRight && onSwipeRight();
          break;
        case "up":
          onSwipeUp && onSwipeUp();
          break;
        case "down":
          onSwipeDown && onSwipeDown();
          break;
      }
    }
    
    // Reset swipe state
    setSwipeState(prev => ({
      ...prev,
      swiping: false,
    }));
  };

  // Handle touch cancel
  const handleTouchCancel = () => {
    setSwipeState(prev => ({
      ...prev,
      swiping: false,
    }));
  };

  return {
    touchHandlers: {
      onTouchStart: handleTouchStart,
      onTouchMove: handleTouchMove,
      onTouchEnd: handleTouchEnd,
      onTouchCancel: handleTouchCancel,
    },
    swipeState,
  };
} 