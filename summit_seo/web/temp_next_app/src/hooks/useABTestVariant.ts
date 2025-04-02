import { useEffect, useState } from 'react';
import { useABTesting } from '@/contexts/ab-testing-context';

/**
 * Hook to get the assigned variant for an experiment and track interactions.
 * 
 * @param experimentId The ID of the experiment to check
 * @param trackInitialView Whether to automatically track an interaction when the component mounts
 * @returns An object containing the variant ID, tracking functions, and loading state
 */
export function useABTestVariant(experimentId: string, trackInitialView = false) {
  const { 
    getVariant, 
    trackInteraction, 
    trackConversion, 
    isLoading, 
    isInExperiment 
  } = useABTesting();
  
  const [variantId, setVariantId] = useState<string | null>(null);
  
  // Get the variant assigned to the current user
  useEffect(() => {
    if (!isLoading) {
      const variant = getVariant(experimentId);
      setVariantId(variant?.id || null);
      
      // Track initial view if requested
      if (variant && trackInitialView && isInExperiment(experimentId)) {
        trackInteraction(experimentId);
      }
    }
  }, [experimentId, getVariant, isLoading, isInExperiment, trackInitialView, trackInteraction]);
  
  // Track an interaction with the variant
  const trackVariantInteraction = () => {
    if (variantId && isInExperiment(experimentId)) {
      trackInteraction(experimentId);
    }
  };
  
  // Track a conversion for the variant
  const trackVariantConversion = () => {
    if (variantId && isInExperiment(experimentId)) {
      trackConversion(experimentId);
    }
  };
  
  // Check if a variant matches the assigned variant
  const isVariant = (checkVariantId: string) => {
    return variantId === checkVariantId;
  };
  
  return {
    variantId,
    isVariant,
    trackInteraction: trackVariantInteraction,
    trackConversion: trackVariantConversion,
    isLoading
  };
} 