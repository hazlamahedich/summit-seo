"use client";

import { useState, useCallback, useEffect } from "react";

// Sound effect types
export type SoundEffectType = 
  | 'click'      // Standard click/selection
  | 'success'    // Operation completed successfully
  | 'error'      // Error occurred
  | 'hover'      // Hover over interactive elements
  | 'notification' // New notification
  | 'submit'     // Form submission
  | 'toggle'     // Toggle state change
  | 'startup'    // App startup/initialization
  | 'custom';    // Custom sound effect

// Configuration options
export interface SoundEffectsOptions {
  initialVolume?: number;      // Initial volume (0-1)
  initiallyEnabled?: boolean;  // Whether sound effects are initially enabled
  sounds?: Record<Exclude<SoundEffectType, 'custom'>, string>; // Custom sound URL mapping
  disableStartupSound?: boolean; // Whether to disable the startup sound
}

// Default sound URLs (these would be replaced with actual sound files in a production app)
const DEFAULT_SOUNDS: Record<Exclude<SoundEffectType, 'custom'>, string> = {
  click: '/sounds/click.wav',
  success: '/sounds/success.wav',
  error: '/sounds/error.wav',
  hover: '/sounds/hover.wav',
  notification: '/sounds/notification.wav',
  submit: '/sounds/submit.wav',
  toggle: '/sounds/toggle.wav',
  startup: '/sounds/startup.wav',
};

/**
 * Hook for managing UI sound effects
 * 
 * @param options Configuration options for sound effects
 * @returns Methods to play sounds and control sound settings
 */
export function useSoundEffects(options: SoundEffectsOptions = {}) {
  const {
    initialVolume = 0.5,
    initiallyEnabled = true,
    sounds = DEFAULT_SOUNDS,
    disableStartupSound = true, // Default to true since we have placeholder files
  } = options;

  // Local state for volume and enabled/disabled status
  const [volume, setVolume] = useState<number>(initialVolume);
  const [enabled, setEnabled] = useState<boolean>(initiallyEnabled);
  
  // Audio context for sound generation
  const [audioContext, setAudioContext] = useState<AudioContext | null>(null);
  
  // Keep track of sound file errors to avoid repeated errors
  const [failedSounds, setFailedSounds] = useState<Set<string>>(new Set());
  
  // Initialize audio context on client side only
  useEffect(() => {
    // Create AudioContext only in browser environment
    if (typeof window !== 'undefined' && !audioContext) {
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      if (AudioContextClass) {
        try {
          setAudioContext(new AudioContextClass());
        } catch (e) {
          console.error("Failed to initialize AudioContext:", e);
          // Disable sound effects if we can't create an audio context
          setEnabled(false);
        }
      }
    }

    // Check for user preference in localStorage
    const storedVolume = localStorage.getItem('soundEffectsVolume');
    if (storedVolume !== null) {
      setVolume(parseFloat(storedVolume));
    }
    
    const storedEnabled = localStorage.getItem('soundEffectsEnabled');
    if (storedEnabled !== null) {
      setEnabled(storedEnabled === 'true');
    }

    // Cleanup function
    return () => {
      if (audioContext) {
        audioContext.close();
      }
    };
  }, []);

  // Save preferences to localStorage when they change
  useEffect(() => {
    localStorage.setItem('soundEffectsVolume', volume.toString());
  }, [volume]);

  useEffect(() => {
    localStorage.setItem('soundEffectsEnabled', enabled.toString());
  }, [enabled]);

  // Play the startup sound when the app initializes (if not disabled)
  useEffect(() => {
    // Play startup sound with a slight delay
    if (!disableStartupSound && enabled && audioContext) {
      const timer = setTimeout(() => {
        playSound('startup');
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [audioContext, disableStartupSound]);

  /**
   * Play a sound effect
   */
  const playSound = useCallback((
    type: SoundEffectType, 
    customUrl?: string,
    customVolume?: number
  ) => {
    // Skip if sounds are disabled or no audio context
    if (!enabled || !audioContext) return;
    
    // Get the URL for the sound
    const soundUrl = type === 'custom' 
      ? customUrl 
      : sounds[type] || DEFAULT_SOUNDS[type];
    
    if (!soundUrl) return;
    
    // Skip if this sound has previously failed
    if (failedSounds.has(soundUrl)) return;
    
    // Use specified volume or default
    const soundVolume = customVolume !== undefined ? customVolume : volume;
    
    // Create and play the sound
    fetch(soundUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Failed to fetch sound file: ${response.status} ${response.statusText}`);
        }
        return response.arrayBuffer();
      })
      .then(arrayBuffer => {
        // Skip empty files
        if (arrayBuffer.byteLength === 0) {
          throw new Error('Sound file is empty');
        }
        
        return audioContext.decodeAudioData(arrayBuffer).catch(error => {
          throw new Error(`Failed to decode audio data: ${error.message}`);
        });
      })
      .then(audioBuffer => {
        const source = audioContext.createBufferSource();
        source.buffer = audioBuffer;
        
        // Create a gain node to control volume
        const gainNode = audioContext.createGain();
        gainNode.gain.value = soundVolume;
        
        // Connect the source to the gain node and the gain node to the destination
        source.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        // Play the sound
        source.start(0);
      })
      .catch(error => {
        // Add to failed sounds set to avoid repeated errors
        setFailedSounds(prev => new Set(prev).add(soundUrl));
        
        // Only log the error in development
        if (process.env.NODE_ENV === 'development') {
          console.warn(`Sound effect error (${type}):`, error.message);
        }
      });
  }, [enabled, audioContext, volume, sounds, failedSounds]);

  // Toggle sound effects on/off
  const toggleSoundEffects = useCallback(() => {
    setEnabled(prev => !prev);
  }, []);

  // Set the volume level (0-1)
  const setVolumeLevel = useCallback((level: number) => {
    // Ensure volume is between 0 and 1
    const normalizedVolume = Math.max(0, Math.min(1, level));
    setVolume(normalizedVolume);
  }, []);

  return {
    playSound,
    volume,
    setVolume: setVolumeLevel,
    enabled,
    toggleEnabled: toggleSoundEffects,
  };
}

// Create a simplified version with prebaked sounds
export function useSimpleSoundEffects() {
  const { playSound, enabled, toggleEnabled } = useSoundEffects();
  
  return {
    playClick: () => playSound('click'),
    playSuccess: () => playSound('success'),
    playError: () => playSound('error'),
    playHover: () => playSound('hover'),
    playNotification: () => playSound('notification'),
    playSubmit: () => playSound('submit'),
    playToggle: () => playSound('toggle'),
    enabled,
    toggleEnabled,
  };
} 