"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useAuth } from "@/lib/auth";
import {
  Tour,
  TourStep,
  UserTourProgress,
  useTours,
  useUserTourProgress,
  useCompleteTour,
  useDismissTour,
  useUpdateTourStepProgress,
  useResetTourProgress
} from "@/lib/services/tour-service";

interface TourContextProps {
  // Current active tour
  activeTour: Tour | null;
  setActiveTour: (tour: Tour | null) => void;
  
  // Current step
  currentStep: number;
  setCurrentStep: (step: number) => void;
  
  // Tour visibility
  isTourVisible: boolean;
  showTour: (tourId: string) => void;
  hideTour: () => void;
  
  // Tour progress
  tourProgress: UserTourProgress[];
  
  // Tour actions
  startTour: (tourId: string) => void;
  completeTour: (tourId: string) => void;
  dismissTour: (tourId: string) => void;
  goToNextStep: () => void;
  goToPrevStep: () => void;
  goToStep: (stepIndex: number) => void;
  resetTourProgress: (tourId: string) => void;
  
  // Tour status helpers
  isTourCompleted: (tourId: string) => boolean;
  isTourDismissed: (tourId: string) => boolean;
  getLastCompletedStep: (tourId: string) => number;
  
  // Available tours
  availableTours: Tour[];
  isLoadingTours: boolean;
  
  // Load a specific tour
  loadTour: (tourId: string) => Promise<Tour | null>;
}

export const TourContext = createContext<TourContextProps | undefined>(undefined);

export const TourProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { data: session } = useAuth();
  const userId = session?.user?.id || "anonymous";
  
  // State
  const [activeTour, setActiveTour] = useState<Tour | null>(null);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [isTourVisible, setIsTourVisible] = useState<boolean>(false);
  
  // Data fetching
  const { data: tours = [], isLoading: isLoadingTours } = useTours();
  const { data: progress = [], isLoading: isLoadingProgress } = useUserTourProgress(userId);
  
  // Mutations
  const completeTourMutation = useCompleteTour();
  const dismissTourMutation = useDismissTour();
  const updateStepMutation = useUpdateTourStepProgress();
  const resetProgressMutation = useResetTourProgress();
  
  // Find a tour by ID
  const findTourById = (tourId: string): Tour | undefined => {
    return tours.find(tour => tour.id === tourId);
  };
  
  // Start a tour
  const startTour = (tourId: string) => {
    const tour = findTourById(tourId);
    if (!tour) return;
    
    // Get tour progress
    const tourProgress = progress.find(p => p.tourId === tourId);
    const lastCompletedStep = tourProgress?.lastStepCompleted || 0;
    
    // Set active tour and step
    setActiveTour(tour);
    setCurrentStep(lastCompletedStep);
    setIsTourVisible(true);
  };
  
  // Show a tour
  const showTour = (tourId: string) => {
    const tour = findTourById(tourId);
    if (!tour) return;
    
    setActiveTour(tour);
    setIsTourVisible(true);
  };
  
  // Hide the current tour
  const hideTour = () => {
    setIsTourVisible(false);
  };
  
  // Complete a tour
  const handleCompleteTour = (tourId: string) => {
    completeTourMutation.mutate({ userId, tourId });
    hideTour();
  };
  
  // Dismiss a tour
  const handleDismissTour = (tourId: string) => {
    dismissTourMutation.mutate({ userId, tourId });
    hideTour();
  };
  
  // Go to next step
  const goToNextStep = () => {
    if (!activeTour) return;
    
    const nextStep = currentStep + 1;
    
    // Check if this is the last step
    if (nextStep >= activeTour.steps.length) {
      handleCompleteTour(activeTour.id);
      return;
    }
    
    // Update progress and move to next step
    updateStepMutation.mutate({ 
      userId, 
      tourId: activeTour.id,
      stepIndex: nextStep 
    });
    
    setCurrentStep(nextStep);
  };
  
  // Go to previous step
  const goToPrevStep = () => {
    if (!activeTour || currentStep <= 0) return;
    
    const prevStep = currentStep - 1;
    setCurrentStep(prevStep);
  };
  
  // Go to a specific step
  const goToStep = (stepIndex: number) => {
    if (!activeTour) return;
    
    // Ensure step index is within bounds
    const boundedIndex = Math.max(0, Math.min(activeTour.steps.length - 1, stepIndex));
    
    updateStepMutation.mutate({
      userId,
      tourId: activeTour.id,
      stepIndex: boundedIndex
    });
    
    setCurrentStep(boundedIndex);
  };
  
  // Reset tour progress
  const handleResetTourProgress = (tourId: string) => {
    resetProgressMutation.mutate({ userId, tourId });
  };
  
  // Check if a tour is completed
  const isTourCompleted = (tourId: string): boolean => {
    return progress.some(p => p.tourId === tourId && p.completed);
  };
  
  // Check if a tour is dismissed
  const isTourDismissed = (tourId: string): boolean => {
    return progress.some(p => p.tourId === tourId && p.dismissed);
  };
  
  // Get the last completed step for a tour
  const getLastCompletedStep = (tourId: string): number => {
    const tourProgress = progress.find(p => p.tourId === tourId);
    return tourProgress?.lastStepCompleted || 0;
  };
  
  // Load a specific tour (useful for dynamic tour loading)
  const loadTour = async (tourId: string): Promise<Tour | null> => {
    // In a real implementation, this could fetch a specific tour from the API
    // For now, we'll just find it in our loaded tours
    const tour = findTourById(tourId);
    return tour || null;
  };
  
  // Value for the context
  const contextValue: TourContextProps = {
    activeTour,
    setActiveTour,
    currentStep,
    setCurrentStep,
    isTourVisible,
    showTour,
    hideTour,
    tourProgress: progress,
    startTour,
    completeTour: handleCompleteTour,
    dismissTour: handleDismissTour,
    goToNextStep,
    goToPrevStep,
    goToStep,
    resetTourProgress: handleResetTourProgress,
    isTourCompleted,
    isTourDismissed,
    getLastCompletedStep,
    availableTours: tours,
    isLoadingTours,
    loadTour,
  };
  
  return (
    <TourContext.Provider value={contextValue}>
      {children}
    </TourContext.Provider>
  );
};

export const useTourContext = () => {
  const context = useContext(TourContext);
  if (context === undefined) {
    throw new Error("useTourContext must be used within a TourProvider");
  }
  return context;
};

export const useActiveTour = () => {
  const { activeTour, currentStep, isTourVisible } = useTourContext();
  return { activeTour, currentStep, isTourVisible };
};

export const useTourControls = () => {
  const { 
    startTour,
    completeTour,
    dismissTour,
    goToNextStep,
    goToPrevStep,
    goToStep,
    resetTourProgress,
    showTour,
    hideTour
  } = useTourContext();
  
  return {
    startTour,
    completeTour,
    dismissTour,
    goToNextStep,
    goToPrevStep,
    goToStep,
    resetTourProgress,
    showTour,
    hideTour
  };
};

export const useTourStatus = (tourId: string) => {
  const { isTourCompleted, isTourDismissed, getLastCompletedStep } = useTourContext();
  
  return {
    isCompleted: isTourCompleted(tourId),
    isDismissed: isTourDismissed(tourId),
    lastCompletedStep: getLastCompletedStep(tourId)
  };
}; 