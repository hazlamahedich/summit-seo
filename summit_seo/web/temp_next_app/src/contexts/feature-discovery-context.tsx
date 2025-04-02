import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import { FeatureTour } from '@/components/ui/feature-discovery';
import { APP_TOURS, getCompletedTours, getNextSuggestedTour } from '@/lib/tour-config';

interface FeatureDiscoveryContextType {
  tours: Record<string, FeatureTour>;
  registerTour: (tour: FeatureTour) => void;
  unregisterTour: (tourId: string) => void;
  startTour: (tourId: string) => void;
  endTour: (tourId: string) => void;
  activeTourId: string | null;
  hasTourBeenCompleted: (tourId: string) => boolean;
  resetAllTours: () => void;
  getNextRecommendedTour: () => string | null;
  showTourNotification: boolean;
  setShowTourNotification: (show: boolean) => void;
}

const FeatureDiscoveryContext = createContext<FeatureDiscoveryContextType | undefined>(undefined);

export const useFeatureDiscoveryContext = () => {
  const context = useContext(FeatureDiscoveryContext);
  if (context === undefined) {
    throw new Error('useFeatureDiscoveryContext must be used within a FeatureDiscoveryProvider');
  }
  return context;
};

interface FeatureDiscoveryProviderProps {
  children: ReactNode;
}

export const FeatureDiscoveryProvider = ({ children }: FeatureDiscoveryProviderProps) => {
  const [tours, setTours] = useState<Record<string, FeatureTour>>(APP_TOURS);
  const [activeTourId, setActiveTourId] = useState<string | null>(null);
  const [completedTours, setCompletedTours] = useState<Record<string, boolean>>({});
  const [showTourNotification, setShowTourNotification] = useState<boolean>(false);

  // Load completed tours from localStorage on initial render
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const loadCompletedTours = () => {
        const storedTours: Record<string, boolean> = {};
        
        // Check localStorage for completed tours
        for (const key in localStorage) {
          if (key.startsWith('feature-discovery-tour-')) {
            const tourId = key.replace('feature-discovery-tour-', '');
            storedTours[tourId] = true;
          }
        }
        
        setCompletedTours(storedTours);
      };
      
      loadCompletedTours();
    }
  }, []);

  // Check if there's a recommended tour based on user's progress
  useEffect(() => {
    if (typeof window !== 'undefined' && !activeTourId) {
      const completedTourIds = getCompletedTours();
      const nextTourId = getNextSuggestedTour(completedTourIds);
      
      if (nextTourId && !completedTours[nextTourId]) {
        // Show notification that a new tour is available
        setShowTourNotification(true);
      }
    }
  }, [completedTours, activeTourId]);

  const registerTour = (tour: FeatureTour) => {
    setTours(prevTours => ({
      ...prevTours,
      [tour.id]: tour,
    }));
  };

  const unregisterTour = (tourId: string) => {
    setTours(prevTours => {
      const newTours = { ...prevTours };
      delete newTours[tourId];
      return newTours;
    });
  };

  const startTour = (tourId: string) => {
    if (tours[tourId] && !activeTourId) {
      setActiveTourId(tourId);
      setShowTourNotification(false);
    }
  };

  const endTour = (tourId: string) => {
    if (activeTourId === tourId) {
      setActiveTourId(null);
      
      // Mark the tour as completed
      localStorage.setItem(`feature-discovery-tour-${tourId}`, 'true');
      setCompletedTours(prev => ({
        ...prev,
        [tourId]: true,
      }));

      // After a short delay, check if there's a next recommended tour
      setTimeout(() => {
        const completedTourIds = getCompletedTours();
        const nextTourId = getNextSuggestedTour(completedTourIds);
        
        if (nextTourId && !completedTours[nextTourId]) {
          // Show notification about the next tour
          setShowTourNotification(true);
        }
      }, 1000);
    }
  };

  const hasTourBeenCompleted = (tourId: string): boolean => {
    return completedTours[tourId] || false;
  };

  const resetAllTours = (): void => {
    if (typeof window === 'undefined') {
      return;
    }
    
    for (const key in localStorage) {
      if (key.startsWith('feature-discovery-tour-') || key.startsWith('feature-discovery-step-')) {
        localStorage.removeItem(key);
      }
    }
    
    setCompletedTours({});
    setActiveTourId(null);
  };

  const getNextRecommendedTour = (): string | null => {
    const completedTourIds = getCompletedTours();
    return getNextSuggestedTour(completedTourIds);
  };

  const value = {
    tours,
    registerTour,
    unregisterTour,
    startTour,
    endTour,
    activeTourId,
    hasTourBeenCompleted,
    resetAllTours,
    getNextRecommendedTour,
    showTourNotification,
    setShowTourNotification
  };

  return (
    <FeatureDiscoveryContext.Provider value={value}>
      {children}
    </FeatureDiscoveryContext.Provider>
  );
};

export const useFeatureTour = (tour: FeatureTour) => {
  const { registerTour, unregisterTour, startTour, endTour, activeTourId, hasTourBeenCompleted } = useFeatureDiscoveryContext();
  
  // Register the tour on component mount
  useEffect(() => {
    registerTour(tour);
    return () => unregisterTour(tour.id);
  }, [tour, registerTour, unregisterTour]);
  
  const isActive = activeTourId === tour.id;
  const isCompleted = hasTourBeenCompleted(tour.id);
  
  return {
    start: () => startTour(tour.id),
    end: () => endTour(tour.id),
    isActive,
    isCompleted,
  };
}; 