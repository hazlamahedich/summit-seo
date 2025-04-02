"use client";

import React, { useState, useEffect, useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X, ArrowRight, ArrowLeft, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useSoundEffectsContext } from "@/contexts/sound-effects-context";

// Define tour step interface
export interface TourStep {
  target: string; // CSS selector for the target element
  title: string;
  content: React.ReactNode;
  placement?: 'top' | 'right' | 'bottom' | 'left';
  highlighted?: boolean; // Whether to highlight the target element
  width?: number; // Optional fixed width for the tooltip
}

interface ProductTourProps {
  steps: TourStep[];
  onComplete?: () => void;
  onSkip?: () => void;
  isOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
  storageKey?: string; // localStorage key to track tour completion
}

export function ProductTour({
  steps,
  onComplete,
  onSkip,
  isOpen: controlledIsOpen,
  onOpenChange,
  storageKey = "product-tour-completed"
}: ProductTourProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [targetElement, setTargetElement] = useState<HTMLElement | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });
  const [isVisible, setIsVisible] = useState(controlledIsOpen ?? false);
  const tooltipRef = useRef<HTMLDivElement>(null);
  
  // Get sound effects
  const { playClick, playSuccess } = useSoundEffectsContext();

  // Check if the tour has been completed before
  useEffect(() => {
    if (controlledIsOpen === undefined) {
      const completed = localStorage.getItem(storageKey) === "true";
      setIsVisible(!completed);
    }
  }, [storageKey, controlledIsOpen]);

  // Handle controlled state
  useEffect(() => {
    if (controlledIsOpen !== undefined) {
      setIsVisible(controlledIsOpen);
    }
  }, [controlledIsOpen]);

  // Update target element when step changes
  useEffect(() => {
    if (!isVisible) return;
    
    const target = document.querySelector(steps[currentStep].target) as HTMLElement;
    setTargetElement(target);
  }, [currentStep, steps, isVisible]);

  // Position tooltip relative to target element
  useEffect(() => {
    if (!targetElement || !tooltipRef.current || !isVisible) return;

    const updatePosition = () => {
      const targetRect = targetElement.getBoundingClientRect();
      const tooltipRect = tooltipRef.current?.getBoundingClientRect() || { width: 0, height: 0 };
      const placement = steps[currentStep].placement || 'bottom';

      let top = 0;
      let left = 0;

      // Calculate position based on placement
      switch (placement) {
        case 'top':
          top = targetRect.top - tooltipRect.height - 10;
          left = targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2);
          break;
        case 'right':
          top = targetRect.top + (targetRect.height / 2) - (tooltipRect.height / 2);
          left = targetRect.right + 10;
          break;
        case 'bottom':
          top = targetRect.bottom + 10;
          left = targetRect.left + (targetRect.width / 2) - (tooltipRect.width / 2);
          break;
        case 'left':
          top = targetRect.top + (targetRect.height / 2) - (tooltipRect.height / 2);
          left = targetRect.left - tooltipRect.width - 10;
          break;
      }

      // Adjust position to stay within viewport
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      // Ensure tooltip stays within horizontal bounds
      left = Math.max(10, Math.min(viewportWidth - tooltipRect.width - 10, left));
      
      // Ensure tooltip stays within vertical bounds
      top = Math.max(10, Math.min(viewportHeight - tooltipRect.height - 10, top));

      setTooltipPosition({ top, left });
    };

    // Initial position update
    updatePosition();

    // Update position on resize or scroll
    window.addEventListener('resize', updatePosition);
    window.addEventListener('scroll', updatePosition);
    
    // Add highlight class to target element if needed
    if (steps[currentStep].highlighted) {
      targetElement.classList.add('tour-highlight');
    }

    return () => {
      window.removeEventListener('resize', updatePosition);
      window.removeEventListener('scroll', updatePosition);
      
      // Remove highlight class
      if (steps[currentStep].highlighted) {
        targetElement.classList.remove('tour-highlight');
      }
    };
  }, [targetElement, currentStep, steps, isVisible]);

  // Handle navigation
  const goToNextStep = () => {
    playClick();
    
    if (currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      completeTour();
    }
  };

  const goToPrevStep = () => {
    playClick();
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const completeTour = () => {
    playSuccess();
    setIsVisible(false);
    localStorage.setItem(storageKey, "true");
    
    if (onComplete) {
      onComplete();
    }
    
    if (onOpenChange) {
      onOpenChange(false);
    }
  };

  const skipTour = () => {
    playClick();
    setIsVisible(false);
    localStorage.setItem(storageKey, "true");
    
    if (onSkip) {
      onSkip();
    }
    
    if (onOpenChange) {
      onOpenChange(false);
    }
  };

  // Restart the tour
  const restartTour = () => {
    setCurrentStep(0);
    setIsVisible(true);
    if (onOpenChange) {
      onOpenChange(true);
    }
  };

  if (!isVisible || steps.length === 0) {
    return null;
  }

  return (
    <>
      {/* Overlay */}
      <div className="fixed inset-0 bg-black/50 z-[999] pointer-events-none" />
      
      {/* Tooltip */}
      <AnimatePresence>
        <motion.div
          ref={tooltipRef}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          transition={{ duration: 0.2 }}
          style={{
            position: 'fixed',
            top: tooltipPosition.top,
            left: tooltipPosition.left,
            width: steps[currentStep].width || 'auto',
            zIndex: 1000,
          }}
          className="bg-card border rounded-lg shadow-lg overflow-hidden max-w-sm"
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b p-4">
            <h3 className="font-medium">{steps[currentStep].title}</h3>
            <Button 
              size="icon" 
              variant="ghost" 
              className="h-6 w-6" 
              onClick={skipTour}
              aria-label="Close tour"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          
          {/* Content */}
          <div className="p-4">
            {steps[currentStep].content}
          </div>
          
          {/* Footer */}
          <div className="flex items-center justify-between p-4 border-t bg-muted/50">
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">
                {currentStep + 1} of {steps.length}
              </span>
              
              {currentStep > 0 ? (
                <Button 
                  size="sm" 
                  variant="outline" 
                  className="h-8" 
                  onClick={goToPrevStep}
                >
                  <ArrowLeft className="h-3 w-3 mr-1" /> Previous
                </Button>
              ) : (
                <Button 
                  size="sm" 
                  variant="outline" 
                  className="h-8" 
                  onClick={skipTour}
                >
                  Skip Tour
                </Button>
              )}
            </div>
            
            <Button 
              size="sm" 
              className="h-8" 
              onClick={goToNextStep}
            >
              {currentStep < steps.length - 1 ? (
                <>Next <ArrowRight className="h-3 w-3 ml-1" /></>
              ) : (
                'Finish'
              )}
            </Button>
          </div>
        </motion.div>
      </AnimatePresence>
    </>
  );
}

// Button to trigger the product tour
export function TourButton({
  className,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  const [isOpen, setIsOpen] = useState(false);
  const { playClick } = useSoundEffectsContext();
  
  // Define product tour steps
  const steps: TourStep[] = [
    {
      target: '.navbar', // Example target
      title: 'Welcome to Summit SEO',
      content: (
        <div>
          <p>This quick tour will guide you through our app's key features.</p>
          <p className="mt-2 text-sm text-muted-foreground">Let's get started!</p>
        </div>
      ),
      placement: 'bottom',
      highlighted: true,
    },
    // Add more steps as needed for your specific app
  ];
  
  const handleClick = () => {
    playClick();
    // Remove the completed flag from localStorage
    localStorage.removeItem('product-tour-completed');
    setIsOpen(true);
  };
  
  return (
    <>
      <Button
        variant="outline"
        size="sm"
        className={cn("gap-2", className)}
        onClick={handleClick}
        {...props}
      >
        <BookOpen className="h-4 w-4" />
        <span>Product Tour</span>
      </Button>
      
      <ProductTour 
        steps={steps} 
        isOpen={isOpen} 
        onOpenChange={setIsOpen}
      />
    </>
  );
} 