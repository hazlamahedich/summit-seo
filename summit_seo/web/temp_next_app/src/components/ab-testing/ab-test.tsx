import { ReactNode, useEffect } from 'react';
import { useABTesting } from '@/contexts/ab-testing-context';

interface ABTestProps {
  experimentId: string;
  children: ReactNode | ReactNode[];
  onLoad?: (variantId: string) => void;
  onInteraction?: () => void;
}

interface ABVariantProps {
  id: string;
  children: ReactNode;
}

/**
 * AB testing component that conditionally renders one of its ABVariant children
 * based on the variant assigned to the current user.
 * 
 * Example usage:
 * <ABTest experimentId="dashboard-widget-layout">
 *   <ABVariant id="control">Original Widget</ABVariant>
 *   <ABVariant id="variant-a">New Widget Design A</ABVariant>
 *   <ABVariant id="variant-b">New Widget Design B</ABVariant>
 * </ABTest>
 */
export function ABTest({ experimentId, children, onLoad, onInteraction }: ABTestProps) {
  const { getAssignedVariant, trackInteraction, loading, isUserInExperiment } = useABTesting();
  
  // Get the variant assigned to the current user
  const variantId = getAssignedVariant(experimentId);
  
  // Track that this component was rendered
  useEffect(() => {
    if (variantId && !loading && isUserInExperiment(experimentId)) {
      // Notify parent component which variant was loaded
      onLoad?.(variantId);
    }
  }, [variantId, loading, experimentId, isUserInExperiment, onLoad]);
  
  // Handle interaction tracking
  const handleInteraction = () => {
    if (variantId && isUserInExperiment(experimentId)) {
      trackInteraction(experimentId);
      onInteraction?.();
    }
  };
  
  // If no variant is assigned or we're still loading, return the first child (default/control)
  if (!variantId || loading) {
    const firstChild = Array.isArray(children) ? children[0] : children;
    return <div onClick={handleInteraction}>{firstChild}</div>;
  }
  
  // Find the matching variant component
  const variantComponent = Array.isArray(children) 
    ? children.find((child: any) => child.props.id === variantId) 
    : children;
  
  // If no matching variant is found, return the first child (default/control)
  if (!variantComponent) {
    const firstChild = Array.isArray(children) ? children[0] : children;
    return <div onClick={handleInteraction}>{firstChild}</div>;
  }
  
  // Return the selected variant component wrapped in a div to track interactions
  return <div onClick={handleInteraction}>{variantComponent}</div>;
}

/**
 * Represents a single variant in an AB test
 */
export function ABVariant({ id, children }: ABVariantProps) {
  return <>{children}</>;
} 