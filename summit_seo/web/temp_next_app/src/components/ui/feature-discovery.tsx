import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "./button";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

export interface FeatureStep {
  id: string;
  title: string;
  description: string;
  element?: string; // CSS selector for the target element
  position?: "top" | "right" | "bottom" | "left";
  dismissable?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export interface FeatureTour {
  id: string;
  name: string;
  steps: FeatureStep[];
  onComplete?: () => void;
}

interface FeatureDiscoveryProps {
  tour: FeatureTour;
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

export function FeatureDiscovery({
  tour,
  isOpen,
  onClose,
  className,
}: FeatureDiscoveryProps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [position, setPosition] = useState({ top: 0, left: 0, width: 0, height: 0 });
  const currentStep = tour.steps[currentStepIndex];

  useEffect(() => {
    if (isOpen && currentStep?.element) {
      const targetElement = document.querySelector(currentStep.element);
      if (targetElement) {
        const rect = targetElement.getBoundingClientRect();
        setPosition({
          top: rect.top + window.scrollY,
          left: rect.left + window.scrollX,
          width: rect.width,
          height: rect.height,
        });
      }
    }
  }, [isOpen, currentStep, currentStepIndex]);

  const goToNextStep = () => {
    if (currentStepIndex < tour.steps.length - 1) {
      setCurrentStepIndex(currentStepIndex + 1);
    } else {
      completeTour();
    }
  };

  const goToPrevStep = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(currentStepIndex - 1);
    }
  };

  const completeTour = () => {
    localStorage.setItem(`feature-discovery-tour-${tour.id}`, "true");
    if (tour.onComplete) {
      tour.onComplete();
    }
    onClose();
  };

  const completeStep = () => {
    if (currentStep.action?.onClick) {
      currentStep.action.onClick();
    }
    goToNextStep();
  };

  const completeStep2 = () => {
    localStorage.setItem(`feature-discovery-step-${currentStep.id}`, "true");
    goToNextStep();
  };

  const completeAll = () => {
    completeStep();
    if (tour.onComplete) {
      tour.onComplete();
    }
  };

  const completeStep3 = () => {
    goToNextStep();
  };

  const completeAll3 = () => {
    onClose();
  };

  const completeStep4 = () => {
    localStorage.setItem(`feature-discovery-step-${currentStep.id}`, "true");
    goToNextStep();
  };

  const completeAll4 = () => {
    localStorage.setItem(`feature-discovery-step-${currentStep.id}`, "true");
    localStorage.setItem(`feature-discovery-tour-${tour.id}`, "true");
    if (tour.onComplete) {
      tour.onComplete();
    }
    onClose();
  };

  const completeTooltipStep = () => {
    localStorage.setItem(`feature-discovery-step-${currentStep.id}`, "true");
    goToNextStep();
  };

  const completeTooltipAll = () => {
    localStorage.setItem(`feature-discovery-step-${currentStep.id}`, "true");
    localStorage.setItem(`feature-discovery-tour-${tour.id}`, "true");
    if (tour.onComplete) {
      tour.onComplete();
    }
    onClose();
  };

  const completeCustomStep = () => {
    if (currentStep.action?.onClick) {
      currentStep.action.onClick();
    }
    localStorage.setItem(`feature-discovery-step-${currentStep.id}`, "true");
    goToNextStep();
  };

  const completeCustomAll = () => {
    if (currentStep.action?.onClick) {
      currentStep.action.onClick();
    }
    localStorage.setItem(`feature-discovery-step-${currentStep.id}`, "true");
    localStorage.setItem(`feature-discovery-tour-${tour.id}`, "true");
    if (tour.onComplete) {
      tour.onComplete();
    }
    onClose();
  };

  const completeEither = () => {
    if (currentStepIndex < tour.steps.length - 1) {
      completeTooltipStep();
    } else {
      completeTooltipAll();
    }
  };

  const dismissTooltip = () => {
    if (currentStep.dismissable) {
      onClose();
    }
  };

  const completeTooltip = () => {
    if (currentStepIndex < tour.steps.length - 1) {
      completeTooltipStep();
    } else {
      completeTooltipAll();
    }
  };

  const getTooltipPosition = () => {
    const pos = currentStep.position || "bottom";
    const spacing = 12; // Spacing between tooltip and target element

    switch (pos) {
      case "top":
        return {
          top: position.top - spacing,
          left: position.left + position.width / 2,
          transform: "translate(-50%, -100%)",
        };
      case "right":
        return {
          top: position.top + position.height / 2,
          left: position.left + position.width + spacing,
          transform: "translateY(-50%)",
        };
      case "left":
        return {
          top: position.top + position.height / 2,
          left: position.left - spacing,
          transform: "translate(-100%, -50%)",
        };
      case "bottom":
      default:
        return {
          top: position.top + position.height + spacing,
          left: position.left + position.width / 2,
          transform: "translateX(-50%)",
        };
    }
  };

  if (!isOpen || !currentStep) return null;

  const tooltipPosition = getTooltipPosition();

  return (
    <div className={cn("feature-discovery-container", className)}>
      {/* Overlay */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.5 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black z-50"
        style={{ pointerEvents: 'none' }}
      />

      {/* Highlight */}
      {currentStep.element && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute z-50 border-2 border-primary rounded-md pointer-events-none"
          style={{
            top: position.top,
            left: position.left,
            width: position.width, 
            height: position.height,
            boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.5)',
          }}
        />
      )}

      {/* Tooltip */}
      <AnimatePresence>
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
          className="absolute bg-card text-card-foreground p-4 rounded-lg shadow-lg z-50 max-w-xs"
          style={{
            top: tooltipPosition.top,
            left: tooltipPosition.left,
            transform: tooltipPosition.transform,
          }}
        >
          {currentStep.dismissable && (
            <Button
              variant="ghost"
              size="sm"
              className="absolute top-1 right-1 h-6 w-6 p-0"
              onClick={dismissTooltip}
            >
              <X className="h-4 w-4" />
            </Button>
          )}
          <div className="space-y-2">
            <h3 className="font-medium text-lg">{currentStep.title}</h3>
            <p className="text-sm text-muted-foreground">{currentStep.description}</p>
            <div className="flex items-center justify-between mt-4">
              <div className="flex space-x-1">
                {tour.steps.map((_, index) => (
                  <div
                    key={index}
                    className={`h-1.5 w-5 rounded-full ${
                      index === currentStepIndex ? "bg-primary" : "bg-muted"
                    }`}
                  />
                ))}
              </div>
              <div className="flex space-x-2">
                {currentStepIndex > 0 && (
                  <Button variant="outline" size="sm" onClick={goToPrevStep}>
                    Back
                  </Button>
                )}
                <Button variant="default" size="sm" onClick={completeEither}>
                  {currentStepIndex < tour.steps.length - 1
                    ? "Next"
                    : "Done"}
                </Button>
              </div>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}

export const useFeatureDiscovery = (tourId: string) => {
  const [isOpen, setIsOpen] = useState(false);
  
  useEffect(() => {
    // Check if the tour has been completed
    const isTourCompleted = localStorage.getItem(`feature-discovery-tour-${tourId}`);
    if (!isTourCompleted) {
      // Open the tour if it hasn't been completed
      setIsOpen(true);
    }
  }, [tourId]);

  return {
    isOpen,
    openTour: () => setIsOpen(true),
    closeTour: () => setIsOpen(false),
  };
}; 