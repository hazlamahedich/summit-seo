"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useSwipeGesture } from "@/hooks/useSwipeGesture";
import { useResponsive } from "@/contexts/responsive-context";

interface SwipeCarouselProps {
  children: React.ReactNode[];
  className?: string;
  showArrows?: boolean;
  showDots?: boolean;
  autoPlay?: boolean;
  interval?: number;
  loop?: boolean;
  gapBetweenItems?: number;
  centerItems?: boolean;
  itemWidthPercentage?: number;
}

/**
 * Mobile-friendly carousel component with swipe gestures
 */
export function SwipeCarousel({
  children,
  className,
  showArrows = true,
  showDots = true,
  autoPlay = false,
  interval = 5000,
  loop = true,
  gapBetweenItems = 16,
  centerItems = false,
  itemWidthPercentage = 100,
}: SwipeCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const carouselRef = useRef<HTMLDivElement>(null);
  const autoPlayTimerRef = useRef<NodeJS.Timeout | null>(null);
  const { isMobile } = useResponsive();

  const items = React.Children.toArray(children);
  const itemCount = items.length;

  // Handle next slide
  const next = () => {
    if (currentIndex < itemCount - 1) {
      setCurrentIndex(currentIndex + 1);
    } else if (loop) {
      setCurrentIndex(0);
    }
  };

  // Handle previous slide
  const prev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    } else if (loop) {
      setCurrentIndex(itemCount - 1);
    }
  };

  // Set up autoplay
  useEffect(() => {
    if (autoPlay && !isDragging) {
      autoPlayTimerRef.current = setInterval(() => {
        next();
      }, interval);
    }

    return () => {
      if (autoPlayTimerRef.current) {
        clearInterval(autoPlayTimerRef.current);
      }
    };
  }, [autoPlay, interval, currentIndex, itemCount, isDragging]);

  // Setup swipe gestures
  const { touchHandlers } = useSwipeGesture({
    onSwipeLeft: next,
    onSwipeRight: prev,
  });

  // Calculate item width as percentage of container width
  const itemWidth = `${itemWidthPercentage}%`;
  
  // Calculate offset for centering items
  const calculateCenterOffset = () => {
    if (!centerItems || itemWidthPercentage >= 100) return "0px";
    return `calc((100% - ${itemWidth}) / 2)`;
  };

  // Calculate transform for current index
  const calculateTransform = () => {
    if (centerItems && itemWidthPercentage < 100) {
      // For centered items with width less than 100%
      const itemWidthWithGap = itemWidthPercentage + (gapBetweenItems / 100);
      return `translateX(calc(-${currentIndex * itemWidthWithGap}% - ${calculateCenterOffset()}))`;
    } else {
      // Standard transform
      return `translateX(-${currentIndex * 100}%)`;
    }
  };
  
  return (
    <div className={cn("relative overflow-hidden", className)}>
      {/* Main Carousel */}
      <div 
        className="relative w-full"
        {...(isMobile ? touchHandlers : {})}
        ref={carouselRef}
        onMouseDown={() => setIsDragging(true)}
        onMouseUp={() => setIsDragging(false)}
        onMouseLeave={() => setIsDragging(false)}
        onTouchStart={() => setIsDragging(true)}
        onTouchEnd={() => setIsDragging(false)}
      >
        <motion.div
          className="flex"
          style={{ 
            transform: calculateTransform(),
            gap: `${gapBetweenItems}px`,
            marginLeft: calculateCenterOffset()
          }}
          animate={{ transform: calculateTransform() }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
        >
          {items.map((item, index) => (
            <div
              key={index}
              className="flex-shrink-0"
              style={{ width: itemWidth }}
            >
              {item}
            </div>
          ))}
        </motion.div>
      </div>

      {/* Navigation Arrows */}
      {showArrows && itemCount > 1 && (
        <>
          <button
            onClick={prev}
            className={cn(
              "absolute left-2 top-1/2 z-10 -translate-y-1/2 rounded-full bg-background/80 p-2 shadow-md",
              "text-primary hover:bg-background focus:outline-none focus:ring-2 focus:ring-primary",
              "transition-opacity",
              (!loop && currentIndex === 0) && "opacity-50 cursor-not-allowed"
            )}
            disabled={!loop && currentIndex === 0}
            aria-label="Previous slide"
          >
            <ChevronLeft className="h-6 w-6" />
          </button>
          <button
            onClick={next}
            className={cn(
              "absolute right-2 top-1/2 z-10 -translate-y-1/2 rounded-full bg-background/80 p-2 shadow-md",
              "text-primary hover:bg-background focus:outline-none focus:ring-2 focus:ring-primary",
              "transition-opacity",
              (!loop && currentIndex === itemCount - 1) && "opacity-50 cursor-not-allowed"
            )}
            disabled={!loop && currentIndex === itemCount - 1}
            aria-label="Next slide"
          >
            <ChevronRight className="h-6 w-6" />
          </button>
        </>
      )}

      {/* Pagination Dots */}
      {showDots && itemCount > 1 && (
        <div className="absolute bottom-4 left-0 right-0 flex justify-center gap-2">
          {items.map((_, index) => (
            <button
              key={index}
              className={cn(
                "h-2 w-2 rounded-full transition-all",
                index === currentIndex ? "bg-primary w-4" : "bg-primary/30"
              )}
              onClick={() => setCurrentIndex(index)}
              aria-label={`Go to slide ${index + 1}`}
            />
          ))}
        </div>
      )}
    </div>
  );
} 