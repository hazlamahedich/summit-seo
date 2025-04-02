"use client";

import React, { useState, useEffect } from 'react';
import { X, BookOpen } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { TourButton } from './product-tour';
import { motion, AnimatePresence } from 'framer-motion';
import { useSoundEffectsContext } from '@/contexts/sound-effects-context';

interface TourNotificationProps {
  delay?: number; // Delay in ms before showing notification
  storageKey?: string; // localStorage key to track notification dismissal
}

export function TourNotification({
  delay = 3000,
  storageKey = 'tour-notification-dismissed'
}: TourNotificationProps) {
  const [isVisible, setIsVisible] = useState(false);
  const { playNotification } = useSoundEffectsContext();
  
  useEffect(() => {
    // Check if notification has been dismissed before
    const isDismissed = localStorage.getItem(storageKey) === 'true';
    
    // Only show notification if it hasn't been dismissed
    if (!isDismissed) {
      // Set timeout to show notification after delay
      const timer = setTimeout(() => {
        setIsVisible(true);
        playNotification();
      }, delay);
      
      return () => clearTimeout(timer);
    }
  }, [delay, storageKey, playNotification]);
  
  // Handle dismissal
  const handleDismiss = () => {
    setIsVisible(false);
    localStorage.setItem(storageKey, 'true');
  };
  
  // Handle taking the tour
  const handleTakeTour = () => {
    setIsVisible(false);
    localStorage.setItem(storageKey, 'true');
    
    // The actual tour will be triggered by the TourButton component
  };
  
  if (!isVisible) return null;
  
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 20 }}
        transition={{ duration: 0.3 }}
        className="fixed bottom-4 right-4 max-w-sm bg-card border rounded-lg shadow-lg overflow-hidden z-50"
      >
        <div className="flex items-start p-4">
          <div className="flex-shrink-0 mr-3">
            <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
              <BookOpen className="h-5 w-5 text-primary" />
            </div>
          </div>
          
          <div className="flex-1 pr-6">
            <h4 className="font-medium text-sm">New to Summit SEO?</h4>
            <p className="text-sm text-muted-foreground mt-1">
              Take a quick tour to discover all the powerful features at your fingertips.
            </p>
            
            <div className="mt-3">
              <TourButton className="mr-2" onClick={handleTakeTour} />
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={handleDismiss}
              >
                Maybe Later
              </Button>
            </div>
          </div>
          
          <button
            className="absolute top-2 right-2 text-muted-foreground hover:text-foreground"
            onClick={handleDismiss}
            aria-label="Dismiss"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </motion.div>
    </AnimatePresence>
  );
} 