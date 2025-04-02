"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Download, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { hapticFeedback } from "@/lib/haptics";

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed"; platform: string }>;
}

interface PWAInstallPromptProps {
  className?: string;
  position?: "top" | "bottom";
  autoHide?: boolean;
  autoHideDelay?: number;
}

/**
 * Component that displays a prompt to install the PWA
 */
export function PWAInstallPrompt({
  className,
  position = "bottom",
  autoHide = true,
  autoHideDelay = 10000,
}: PWAInstallPromptProps) {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  
  // Listen for the beforeinstallprompt event
  useEffect(() => {
    const handleBeforeInstallPrompt = (e: Event) => {
      // Prevent Chrome 67 and earlier from automatically showing the prompt
      e.preventDefault();
      // Store the event for later use
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      // Show the prompt to the user
      setShowPrompt(true);
    };
    
    // Check if app is already installed
    const checkIfInstalled = () => {
      if (window.matchMedia('(display-mode: standalone)').matches) {
        setIsInstalled(true);
      }
    };
    
    // Auto-hide the prompt after delay if configured
    let hideTimeout: NodeJS.Timeout;
    if (showPrompt && autoHide) {
      hideTimeout = setTimeout(() => {
        setShowPrompt(false);
      }, autoHideDelay);
    }
    
    // Add event listeners
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', () => setIsInstalled(true));
    checkIfInstalled();
    
    // Clean up
    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', () => setIsInstalled(true));
      if (hideTimeout) clearTimeout(hideTimeout);
    };
  }, [autoHide, autoHideDelay, showPrompt]);
  
  // Handle install click
  const handleInstallClick = async () => {
    if (!deferredPrompt) return;
    
    try {
      hapticFeedback("medium");
      // Show the install prompt
      await deferredPrompt.prompt();
      
      // Wait for the user to respond to the prompt
      const choiceResult = await deferredPrompt.userChoice;
      
      if (choiceResult.outcome === 'accepted') {
        console.log('User accepted the install prompt');
        setIsInstalled(true);
      } else {
        console.log('User dismissed the install prompt');
      }
      
      // Clear the deferredPrompt
      setDeferredPrompt(null);
      setShowPrompt(false);
    } catch (error) {
      console.error('Error during installation:', error);
    }
  };
  
  // Handle dismiss click
  const handleDismissClick = () => {
    hapticFeedback("light");
    setShowPrompt(false);
  };
  
  // Don't show anything if already installed or no install prompt available
  if (isInstalled || !showPrompt) {
    return null;
  }
  
  return (
    <div
      className={cn(
        "fixed left-0 right-0 z-50 mx-auto w-full max-w-md px-4",
        position === "top" ? "top-4" : "bottom-4",
        className
      )}
    >
      <div className="rounded-lg border bg-background p-4 shadow-md">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-full bg-primary/10 p-2">
              <Download className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h3 className="font-medium">Install Summit SEO</h3>
              <p className="text-sm text-muted-foreground">Get the full app experience</p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={handleDismissClick}
          >
            <X className="h-4 w-4" />
            <span className="sr-only">Dismiss</span>
          </Button>
        </div>
        <div className="mt-3 flex gap-2">
          <Button
            variant="secondary"
            size="sm"
            className="flex-1"
            onClick={handleDismissClick}
          >
            Not now
          </Button>
          <Button
            variant="default"
            size="sm"
            className="flex-1"
            onClick={handleInstallClick}
          >
            Install
          </Button>
        </div>
      </div>
    </div>
  );
} 