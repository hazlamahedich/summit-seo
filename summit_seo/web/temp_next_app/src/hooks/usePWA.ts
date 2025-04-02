"use client";

import { useState, useEffect } from "react";

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed"; platform: string }>;
}

interface PWAStatus {
  isInstallable: boolean;
  isInstalled: boolean;
  installPrompt: BeforeInstallPromptEvent | null;
  showInstallPrompt: () => Promise<"accepted" | "dismissed" | null>;
}

/**
 * Custom hook to handle PWA functionality
 * @returns PWA status and methods
 */
export function usePWA(): PWAStatus {
  const [installPrompt, setInstallPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [isInstalled, setIsInstalled] = useState(false);
  
  useEffect(() => {
    // Check if app is already in standalone mode (installed)
    const checkIfInstalled = () => {
      if (typeof window !== "undefined") {
        if (window.matchMedia('(display-mode: standalone)').matches) {
          setIsInstalled(true);
        }
      }
    };
    
    // Listen for beforeinstallprompt event
    const handleBeforeInstallPrompt = (e: Event) => {
      // Prevent the default browser install prompt
      e.preventDefault();
      // Store the event for later use
      setInstallPrompt(e as BeforeInstallPromptEvent);
    };
    
    // Listen for appinstalled event
    const handleAppInstalled = () => {
      setIsInstalled(true);
      setInstallPrompt(null);
    };
    
    // Add event listeners
    if (typeof window !== "undefined") {
      window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.addEventListener('appinstalled', handleAppInstalled);
      checkIfInstalled();
    }
    
    // Clean up
    return () => {
      if (typeof window !== "undefined") {
        window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
        window.removeEventListener('appinstalled', handleAppInstalled);
      }
    };
  }, []);
  
  /**
   * Shows the install prompt and returns the user's choice
   * @returns Promise that resolves to "accepted" or "dismissed" based on user choice
   */
  const showInstallPrompt = async (): Promise<"accepted" | "dismissed" | null> => {
    if (!installPrompt) return null;
    
    try {
      // Show the install prompt
      await installPrompt.prompt();
      
      // Wait for the user to respond to the prompt
      const choiceResult = await installPrompt.userChoice;
      
      // Reset the install prompt
      setInstallPrompt(null);
      
      // Return the outcome
      return choiceResult.outcome;
    } catch (error) {
      console.error('Error showing install prompt:', error);
      return null;
    }
  };
  
  return {
    isInstallable: !!installPrompt,
    isInstalled,
    installPrompt,
    showInstallPrompt,
  };
} 