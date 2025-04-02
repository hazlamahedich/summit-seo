import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useFeatureDiscoveryContext } from '@/contexts/feature-discovery-context';
import { Button } from './button';
import { Info, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useReducedMotion } from '@/lib/motion';

interface TourNotificationProps {
  className?: string;
  position?: 'top-right' | 'bottom-right' | 'bottom-left' | 'top-left';
}

export function TourNotification({ 
  className, 
  position = 'bottom-right' 
}: TourNotificationProps) {
  const { 
    showTourNotification, 
    setShowTourNotification, 
    getNextRecommendedTour, 
    startTour,
    tours
  } = useFeatureDiscoveryContext();
  
  const prefersReducedMotion = useReducedMotion();
  
  const nextTourId = getNextRecommendedTour();
  const nextTour = nextTourId ? tours[nextTourId] : null;
  
  if (!showTourNotification || !nextTour) {
    return null;
  }
  
  const positions = {
    'top-right': 'top-4 right-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-left': 'top-4 left-4',
  };
  
  const getAnimationVariants = () => {
    if (prefersReducedMotion) {
      return {
        hidden: { opacity: 0 },
        visible: { opacity: 1 },
        exit: { opacity: 0 }
      };
    }
    
    // Position-specific animations
    switch (position) {
      case 'top-right':
        return {
          hidden: { opacity: 0, x: 20, y: -10 },
          visible: { opacity: 1, x: 0, y: 0 },
          exit: { opacity: 0, x: 20 }
        };
      case 'bottom-right':
        return {
          hidden: { opacity: 0, x: 20, y: 10 },
          visible: { opacity: 1, x: 0, y: 0 },
          exit: { opacity: 0, x: 20 }
        };
      case 'bottom-left':
        return {
          hidden: { opacity: 0, x: -20, y: 10 },
          visible: { opacity: 1, x: 0, y: 0 },
          exit: { opacity: 0, x: -20 }
        };
      case 'top-left':
        return {
          hidden: { opacity: 0, x: -20, y: -10 },
          visible: { opacity: 1, x: 0, y: 0 },
          exit: { opacity: 0, x: -20 }
        };
      default:
        return {
          hidden: { opacity: 0, y: 10 },
          visible: { opacity: 1, y: 0 },
          exit: { opacity: 0, y: 10 }
        };
    }
  };
  
  const handleStartTour = () => {
    if (nextTourId) {
      startTour(nextTourId);
      setShowTourNotification(false);
    }
  };
  
  const handleDismiss = () => {
    setShowTourNotification(false);
  };
  
  return (
    <AnimatePresence>
      <motion.div
        className={cn(
          'fixed z-50 w-80 p-4 rounded-lg shadow-lg bg-card border',
          positions[position],
          className
        )}
        initial="hidden"
        animate="visible"
        exit="exit"
        variants={getAnimationVariants()}
        transition={{ duration: prefersReducedMotion ? 0.1 : 0.3 }}
      >
        <Button
          variant="ghost"
          size="sm"
          className="absolute top-2 right-2 h-6 w-6 p-0"
          onClick={handleDismiss}
        >
          <X className="h-3 w-3" />
        </Button>
        
        <div className="flex items-start space-x-3">
          <div className="bg-primary/10 p-2 rounded-full">
            <Info className="h-5 w-5 text-primary" />
          </div>
          <div className="flex-1">
            <h4 className="font-medium mb-1">Feature Tour Available</h4>
            <p className="text-sm text-muted-foreground mb-3">
              Learn about {nextTour.name} with our interactive guide.
            </p>
            <div className="flex space-x-2">
              <Button size="sm" onClick={handleStartTour}>
                Start Tour
              </Button>
              <Button size="sm" variant="outline" onClick={handleDismiss}>
                Later
              </Button>
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
} 