"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence, useAnimation, PanInfo } from "framer-motion";
import { cn } from "@/lib/utils";
import { useResponsive } from "@/contexts/responsive-context";

interface BottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  className?: string;
  height?: string;
  snapPoints?: string[];
  showHandle?: boolean;
  backdrop?: boolean;
  closeOnBackdropClick?: boolean;
}

/**
 * Mobile-friendly bottom sheet component with drag-to-dismiss functionality
 */
export function BottomSheet({
  isOpen,
  onClose,
  children,
  className,
  height = "50vh",
  snapPoints = ["25vh", "50vh", "75vh"],
  showHandle = true,
  backdrop = true,
  closeOnBackdropClick = true,
}: BottomSheetProps) {
  const { isMobile } = useResponsive();
  const controls = useAnimation();
  const [currentSnapPoint, setCurrentSnapPoint] = useState(height);
  const [isDragging, setIsDragging] = useState(false);

  // Sync with isOpen prop
  useEffect(() => {
    if (isOpen) {
      controls.start("visible");
      setCurrentSnapPoint(height);
    } else {
      controls.start("hidden");
    }
  }, [isOpen, controls, height]);

  // Handle drag end - snap to points or close
  const handleDragEnd = (_: any, info: PanInfo) => {
    setIsDragging(false);
    const { velocity, offset } = info;
    
    // If swiped down with velocity, close it
    if (velocity.y > 500) {
      onClose();
      return;
    }

    // If dragged down significantly, close it
    if (offset.y > 100) {
      onClose();
      return;
    }

    // Find the closest snap point based on current height
    const element = document.getElementById("bottom-sheet-content");
    if (!element) return;
    
    const currentHeight = element.getBoundingClientRect().height;
    const windowHeight = window.innerHeight;
    const currentPercentage = (currentHeight / windowHeight) * 100;
    
    // Convert snap points to percentages
    const percentageSnapPoints = snapPoints.map(point => {
      if (point.endsWith("vh")) {
        return parseInt(point);
      }
      if (point.endsWith("%")) {
        return parseInt(point);
      }
      // Default to percentage if no unit
      return parseInt(point);
    });
    
    // Find closest snap point
    let closestSnap = percentageSnapPoints[0];
    let minDistance = Math.abs(currentPercentage - percentageSnapPoints[0]);
    
    for (let i = 1; i < percentageSnapPoints.length; i++) {
      const distance = Math.abs(currentPercentage - percentageSnapPoints[i]);
      if (distance < minDistance) {
        minDistance = distance;
        closestSnap = percentageSnapPoints[i];
      }
    }
    
    // Animate to the closest snap point
    setCurrentSnapPoint(`${closestSnap}vh`);
    controls.start({
      height: `${closestSnap}vh`,
      transition: { type: "spring", damping: 30, stiffness: 400 }
    });
  };

  // Handle backdrop click
  const handleBackdropClick = () => {
    if (closeOnBackdropClick) {
      onClose();
    }
  };

  // Make bottom sheet full-width on mobile, dialog-like on desktop
  const sheetVariants = {
    hidden: { 
      y: "100%",
      opacity: 0,
      transition: {
        y: { type: "spring", damping: 25, stiffness: 500 },
        opacity: { duration: 0.15 }
      }
    },
    visible: { 
      y: "0%",
      opacity: 1,
      transition: {
        y: { type: "spring", damping: 25, stiffness: 400, delay: 0.1 },
        opacity: { duration: 0.15, delay: 0.1 }
      }
    },
  };

  // Handle dragging
  const handleDrag = (_: any, info: PanInfo) => {
    setIsDragging(true);
    const element = document.getElementById("bottom-sheet-content");
    if (!element) return;
    
    const { offset } = info;
    if (offset.y < 0) return; // Prevent dragging upward beyond the set height
    
    const currentHeight = element.getBoundingClientRect().height;
    const windowHeight = window.innerHeight;
    const newHeight = (1 - (offset.y / windowHeight)) * 100;
    
    // If dragged too low, start fading out
    if (newHeight < 15) {
      controls.set({
        opacity: newHeight / 15,
      });
    }
    
    controls.set({
      height: `${newHeight}vh`,
    });
  };
  
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          {backdrop && (
            <motion.div
              className="fixed inset-0 bg-black/40 z-40"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={handleBackdropClick}
            />
          )}
          
          {/* Bottom Sheet */}
          <motion.div
            className={cn(
              "fixed bottom-0 left-0 right-0 z-50 overflow-hidden rounded-t-xl bg-background shadow-lg",
              isMobile ? "w-full" : "max-w-md mx-auto left-1/2 transform -translate-x-1/2",
              className
            )}
            drag="y"
            dragConstraints={{ top: 0 }}
            dragElastic={0.2}
            dragMomentum={false}
            onDrag={handleDrag}
            onDragEnd={handleDragEnd}
            dragListener={isMobile}
            variants={sheetVariants}
            initial="hidden"
            animate={controls}
            exit="hidden"
            style={{ height: currentSnapPoint }}
            id="bottom-sheet-content"
          >
            {/* Drag Handle */}
            {showHandle && (
              <div className="flex justify-center pt-2 pb-2">
                <div className="w-10 h-1 bg-muted-foreground/25 rounded-full" />
              </div>
            )}
            
            {/* Content */}
            <div 
              className={cn(
                "overflow-y-auto",
                showHandle ? "max-h-[calc(100%-20px)]" : "max-h-full",
                isDragging ? "pointer-events-none" : "pointer-events-auto"
              )}
            >
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
} 