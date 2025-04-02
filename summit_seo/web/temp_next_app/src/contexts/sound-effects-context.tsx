"use client";

import React, { createContext, useContext, ReactNode } from "react";
import { useSoundEffects, SoundEffectType } from "@/hooks/useSoundEffects";

// Interface for the sound effects context
interface SoundEffectsContextProps {
  playSound: (type: SoundEffectType, customUrl?: string, customVolume?: number) => void;
  volume: number;
  setVolume: (level: number) => void;
  enabled: boolean;
  toggleEnabled: () => void;
  
  // Convenience methods
  playClick: () => void;
  playSuccess: () => void;
  playError: () => void;
  playHover: () => void;
  playNotification: () => void;
  playSubmit: () => void;
  playToggle: () => void;
}

// Create the context with a default undefined value
const SoundEffectsContext = createContext<SoundEffectsContextProps | undefined>(undefined);

// Hook to use the sound effects context
export function useSoundEffectsContext() {
  const context = useContext(SoundEffectsContext);
  
  if (context === undefined) {
    throw new Error("useSoundEffectsContext must be used within a SoundEffectsProvider");
  }
  
  return context;
}

// Props for the ResponsiveProvider component
interface SoundEffectsProviderProps {
  children: ReactNode;
  initialVolume?: number;
  initiallyEnabled?: boolean;
  disableStartupSound?: boolean;
}

export function SoundEffectsProvider({
  children,
  initialVolume = 0.5,
  initiallyEnabled = true,
  disableStartupSound = true,
}: SoundEffectsProviderProps) {
  // Use the sound effects hook
  const {
    playSound,
    volume,
    setVolume,
    enabled,
    toggleEnabled,
  } = useSoundEffects({
    initialVolume,
    initiallyEnabled,
    disableStartupSound,
  });
  
  // Create convenience methods
  const playClick = () => playSound('click');
  const playSuccess = () => playSound('success');
  const playError = () => playSound('error');
  const playHover = () => playSound('hover');
  const playNotification = () => playSound('notification');
  const playSubmit = () => playSound('submit');
  const playToggle = () => playSound('toggle');
  
  // Value to provide through the context
  const value: SoundEffectsContextProps = {
    playSound,
    volume,
    setVolume,
    enabled,
    toggleEnabled,
    
    // Convenience methods
    playClick,
    playSuccess,
    playError,
    playHover,
    playNotification,
    playSubmit,
    playToggle,
  };
  
  return (
    <SoundEffectsContext.Provider value={value}>
      {children}
    </SoundEffectsContext.Provider>
  );
} 