"use client";

import React, { useRef, useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { X, ArrowRight, ArrowLeft, CheckCircle2, SkipForward, List } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Tour, TourStep } from "@/lib/services/tour-service";
import { useTourControls, useActiveTour } from "@/contexts/tour-context";

interface GuidedTourProps {
  tourId: string;
  className?: string;
  onComplete?: () => void;
  autoStart?: boolean;
}

export const GuidedTour: React.FC<GuidedTourProps> = ({
  tourId,
  className,
  onComplete,
  autoStart = false
}) => {
  // Reference for the tooltip element
  const tooltipRef = useRef<HTMLDivElement>(null);
  
  // Get current tour state from context
  const { activeTour, currentStep, isTourVisible } = useActiveTour();
  
  // Get tour controls from context
  const {
    startTour,
    completeTour,
    dismissTour,
    goToNextStep,
    goToPrevStep,
    showTour,
    hideTour
  } = useTourControls();
  
  // Local state for UI
  const [targetElement, setTargetElement] = useState<HTMLElement | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });
  const [isOverviewOpen, setIsOverviewOpen] = useState(false);
  
  // Auto-start the tour if specified
  useEffect(() => {
    if (autoStart) {
      startTour(tourId);
    }
  }, [autoStart, tourId, startTour]);
  
  // Get current step details
  const currentTourStep = activeTour?.steps[currentStep];
  
  // Update target element when step changes
  useEffect(() => {
    if (!isTourVisible || !currentTourStep) return;
    
    const target = document.querySelector(currentTourStep.target) as HTMLElement;
    setTargetElement(target);
  }, [currentStep, activeTour, isTourVisible, currentTourStep]);
  
  // Position tooltip relative to target element
  useEffect(() => {
    if (!targetElement || !tooltipRef.current || !isTourVisible || !currentTourStep) return;

    const updatePosition = () => {
      const targetRect = targetElement.getBoundingClientRect();
      const tooltipRect = tooltipRef.current?.getBoundingClientRect() || { width: 0, height: 0 };
      const placement = currentTourStep.placement || 'bottom';

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
    if (currentTourStep.highlighted) {
      targetElement.classList.add('tour-highlight');
    }

    return () => {
      window.removeEventListener('resize', updatePosition);
      window.removeEventListener('scroll', updatePosition);
      
      // Remove highlight class
      if (currentTourStep.highlighted) {
        targetElement.classList.remove('tour-highlight');
      }
    };
  }, [targetElement, currentStep, activeTour, isTourVisible, currentTourStep]);
  
  // Handle complete button click
  const handleComplete = () => {
    if (!activeTour) return;
    
    completeTour(activeTour.id);
    
    if (onComplete) {
      onComplete();
    }
  };
  
  // Handle skip button click
  const handleSkip = () => {
    if (!activeTour) return;
    dismissTour(activeTour.id);
  };
  
  // Toggle step overview
  const toggleOverview = () => {
    setIsOverviewOpen(!isOverviewOpen);
  };
  
  // Jump to a specific step in the overview
  const jumpToStep = (index: number) => {
    goToNextStep();
    setIsOverviewOpen(false);
  };
  
  // Calculate progress percentage
  const progressPercentage = activeTour 
    ? ((currentStep + 1) / activeTour.steps.length) * 100 
    : 0;
  
  if (!isTourVisible || !activeTour || !currentTourStep) {
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
            zIndex: 1000,
          }}
          className={cn(
            "bg-card border rounded-lg shadow-lg overflow-hidden w-80",
            className
          )}
        >
          {/* Progress indicator */}
          <Progress value={progressPercentage} className="rounded-none h-1" />
          
          {/* Header */}
          <div className="flex items-center justify-between border-b p-4">
            <h3 className="font-medium">{currentTourStep.title}</h3>
            <div className="flex items-center gap-1">
              <Button 
                size="icon" 
                variant="ghost" 
                className="h-6 w-6" 
                onClick={toggleOverview}
                aria-label="Show step overview"
              >
                <List className="h-4 w-4" />
              </Button>
              <Button 
                size="icon" 
                variant="ghost" 
                className="h-6 w-6" 
                onClick={handleSkip}
                aria-label="Skip tour"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
          
          {/* Content */}
          <div className="p-4">
            {typeof currentTourStep.content === 'string' 
              ? <p className="text-sm text-muted-foreground">{currentTourStep.content}</p>
              : currentTourStep.content
            }
          </div>
          
          {/* Footer */}
          <div className="flex items-center justify-between p-4 border-t bg-muted/50">
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">
                {currentStep + 1} of {activeTour.steps.length}
              </span>
              
              {currentStep > 0 ? (
                <Button 
                  size="sm" 
                  variant="outline" 
                  className="h-8" 
                  onClick={goToPrevStep}
                >
                  <ArrowLeft className="h-4 w-4 mr-1" />
                  Back
                </Button>
              ) : (
                <Button 
                  size="sm" 
                  variant="outline" 
                  className="h-8" 
                  onClick={handleSkip}
                >
                  <SkipForward className="h-4 w-4 mr-1" />
                  Skip
                </Button>
              )}
            </div>
            
            {currentStep < activeTour.steps.length - 1 ? (
              <Button 
                size="sm" 
                className="h-8" 
                onClick={goToNextStep}
              >
                Next
                <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
            ) : (
              <Button 
                size="sm" 
                className="h-8" 
                onClick={handleComplete}
              >
                Finish
                <CheckCircle2 className="h-4 w-4 ml-1" />
              </Button>
            )}
          </div>
          
          {/* Step overview panel */}
          <AnimatePresence>
            {isOverviewOpen && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="absolute inset-0 bg-background border rounded-lg shadow-lg z-10 p-4 flex flex-col"
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium">Tour Steps</h3>
                  <Button 
                    size="icon" 
                    variant="ghost" 
                    className="h-6 w-6" 
                    onClick={toggleOverview}
                    aria-label="Close overview"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
                <div className="overflow-y-auto flex-1">
                  {activeTour.steps.map((step, index) => (
                    <button
                      key={step.id || index}
                      onClick={() => jumpToStep(index)}
                      className={cn(
                        "w-full text-left p-2 rounded-md mb-1 text-sm flex items-center",
                        index === currentStep 
                          ? "bg-primary/10 text-primary font-medium" 
                          : index < currentStep 
                            ? "bg-muted/50 text-muted-foreground"
                            : "hover:bg-muted/70"
                      )}
                    >
                      <span className="w-5 h-5 rounded-full bg-muted flex items-center justify-center mr-2 text-xs">
                        {index + 1}
                      </span>
                      {step.title}
                      {index < currentStep && (
                        <CheckCircle2 className="h-4 w-4 ml-auto text-primary" />
                      )}
                    </button>
                  ))}
                </div>
                <div className="pt-3 border-t mt-3">
                  <Button 
                    className="w-full"
                    size="sm"
                    onClick={toggleOverview}
                  >
                    Continue Tour
                  </Button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </AnimatePresence>
    </>
  );
};

// Component for showing the tour start button
interface TourStartButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  tourId: string;
  label?: string;
}

export const TourStartButton: React.FC<TourStartButtonProps> = ({
  tourId,
  label = "Take the Tour",
  className,
  ...props
}) => {
  const { startTour } = useTourControls();
  
  const handleStartTour = () => {
    startTour(tourId);
  };
  
  return (
    <Button
      size="sm"
      variant="outline"
      className={cn("flex items-center gap-2", className)}
      onClick={handleStartTour}
      {...props}
    >
      <CheckCircle2 className="h-4 w-4" />
      <span>{label}</span>
    </Button>
  );
};

// Component to show tour progress
interface TourProgressIndicatorProps {
  tourId: string;
  className?: string;
}

export const TourProgressIndicator: React.FC<TourProgressIndicatorProps> = ({
  tourId,
  className
}) => {
  const { activeTour, currentStep } = useActiveTour();
  const { startTour } = useTourControls();
  
  const totalSteps = activeTour?.steps.length || 0;
  const progressPercentage = activeTour && activeTour.id === tourId
    ? ((currentStep + 1) / totalSteps) * 100
    : 0;
  
  const handleClick = () => {
    startTour(tourId);
  };
  
  return (
    <div 
      className={cn("flex flex-col gap-1 cursor-pointer", className)}
      onClick={handleClick}
    >
      <div className="flex items-center justify-between text-xs">
        <span className="text-muted-foreground">Tour Progress</span>
        <span className="font-medium">
          {currentStep + 1}/{totalSteps}
        </span>
      </div>
      <Progress value={progressPercentage} className="h-1.5" />
    </div>
  );
}; 