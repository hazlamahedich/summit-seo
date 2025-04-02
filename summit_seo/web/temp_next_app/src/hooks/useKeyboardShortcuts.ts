"use client";

import { useState, useEffect, useCallback, useMemo, useRef } from 'react';

// Define shortcut types
export type KeyCombination = string; // e.g. "ctrl+k", "shift+?"
export type ShortcutAction = () => void;
export type ShortcutCategory = 'general' | 'navigation' | 'actions' | 'custom';

// Interface for shortcut options
export interface ShortcutOptions {
  action: ShortcutAction;
  description: string;
  category?: ShortcutCategory;
  global?: boolean; // Whether the shortcut works everywhere
  preventDefault?: boolean; // Whether to prevent default browser behavior
}

// Interface to represent a registered shortcut
export interface RegisteredShortcut extends ShortcutOptions {
  key: KeyCombination;
  // Add formatted key display for UI
  formattedKey: string;
}

// Hook options
export interface KeyboardShortcutsOptions {
  enableGlobalShortcuts?: boolean;
  enableStateUpdates?: boolean; // Whether to update help visibility state in the hook
}

// Format key combination for display
export function formatKeyCombination(key: KeyCombination): string {
  return key
    .toLowerCase()
    .split('+')
    .map(part => {
      switch (part) {
        case 'ctrl':
          return '⌃';
        case 'alt':
          return '⌥';
        case 'shift':
          return '⇧';
        case 'meta':
        case 'cmd':
          return '⌘';
        case 'escape':
          return 'Esc';
        case 'arrowup':
          return '↑';
        case 'arrowdown':
          return '↓';
        case 'arrowleft':
          return '←';
        case 'arrowright':
          return '→';
        case '?':
          return '?';
        case ' ':
          return 'Space';
        default:
          return part.length === 1 ? part.toUpperCase() : part;
      }
    })
    .join(' + ');
}

/**
 * Custom hook to manage keyboard shortcuts
 */
export function useKeyboardShortcuts(options: KeyboardShortcutsOptions = {}) {
  const { 
    enableGlobalShortcuts = true, 
    enableStateUpdates = true 
  } = options;
  
  // Store registered shortcuts
  const [shortcuts, setShortcuts] = useState<Record<KeyCombination, RegisteredShortcut>>({});
  const [helpVisible, setHelpVisible] = useState<boolean>(false);
  
  // Use a ref to track if we're in a toggle operation to avoid infinite recursion
  const isToggling = useRef(false);
  
  // Normalize key combination to a standard format
  const normalizeKey = useCallback((combination: KeyCombination): KeyCombination => {
    return combination
      .toLowerCase()
      .split('+')
      .sort()
      .join('+');
  }, []);
  
  // Handle keyboard events
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    // Build the key combination
    const keys: string[] = [];
    
    if (event.ctrlKey) keys.push('ctrl');
    if (event.altKey) keys.push('alt');
    if (event.shiftKey) keys.push('shift');
    if (event.metaKey) keys.push('meta');
    
    // Add the actual key
    const key = event.key.toLowerCase();
    if (!['control', 'alt', 'shift', 'meta'].includes(key)) {
      keys.push(key);
    }
    
    // Normalize the key combination
    const combination = normalizeKey(keys.join('+'));
    
    // Look for a matching shortcut
    const shortcut = shortcuts[combination];
    
    if (shortcut) {
      // Only execute global shortcuts or if the focus is not in an input field
      const target = event.target as HTMLElement;
      const isInputField = 
        target.tagName === 'INPUT' || 
        target.tagName === 'TEXTAREA' || 
        target.isContentEditable;
      
      if (shortcut.global || !isInputField) {
        // Call the shortcut action
        shortcut.action();
        
        // Prevent default behavior if specified
        if (shortcut.preventDefault) {
          event.preventDefault();
        }
      }
    }
  }, [shortcuts, normalizeKey]);
  
  // Register event listeners
  useEffect(() => {
    // Only attach listener if we have shortcuts and global shortcuts are enabled
    if (Object.keys(shortcuts).length > 0 && enableGlobalShortcuts) {
      window.addEventListener('keydown', handleKeyDown);
      
      return () => {
        window.removeEventListener('keydown', handleKeyDown);
      };
    }
  }, [shortcuts, handleKeyDown, enableGlobalShortcuts]);
  
  // Register a new shortcut
  const registerShortcut = useCallback((key: KeyCombination, options: ShortcutOptions): void => {
    const normalizedKey = normalizeKey(key);
    
    // Create a formatted key for display
    const formattedKey = formatKeyCombination(key);
    
    setShortcuts(prev => ({
      ...prev,
      [normalizedKey]: {
        ...options,
        key: normalizedKey,
        formattedKey,
        category: options.category || 'general',
      },
    }));
  }, [normalizeKey]);
  
  // Unregister a shortcut
  const unregisterShortcut = useCallback((key: KeyCombination): void => {
    const normalizedKey = normalizeKey(key);
    
    setShortcuts(prev => {
      const newShortcuts = { ...prev };
      delete newShortcuts[normalizedKey];
      return newShortcuts;
    });
  }, [normalizeKey]);
  
  // Unregister all shortcuts
  const clearShortcuts = useCallback((): void => {
    setShortcuts({});
  }, []);
  
  // Get all shortcuts in a specific category
  const getShortcutsByCategory = useCallback((category?: ShortcutCategory) => {
    return Object.values(shortcuts).filter(
      shortcut => !category || shortcut.category === category
    );
  }, [shortcuts]);
  
  // Get all shortcut categories currently in use
  const getCategories = useMemo(() => {
    const categories = Object.values(shortcuts).map(s => s.category);
    return Array.from(new Set(categories));
  }, [shortcuts]);
  
  // Show keyboard shortcuts help
  const showShortcutsHelp = useCallback(() => {
    if (isToggling.current) return;
    isToggling.current = true;
    
    // Only update state if enabled
    if (enableStateUpdates) {
      setHelpVisible(true);
    }
    
    setTimeout(() => {
      isToggling.current = false;
    }, 0);
  }, [enableStateUpdates]);

  // Hide keyboard shortcuts help
  const hideShortcutsHelp = useCallback(() => {
    if (isToggling.current) return;
    isToggling.current = true;
    
    // Only update state if enabled
    if (enableStateUpdates) {
      setHelpVisible(false);
    }
    
    setTimeout(() => {
      isToggling.current = false;
    }, 0);
  }, [enableStateUpdates]);

  // Toggle keyboard shortcuts help
  const toggleShortcutsHelp = useCallback(() => {
    if (isToggling.current) return;
    isToggling.current = true;
    
    // Only update state if enabled
    if (enableStateUpdates) {
      setHelpVisible((prev) => !prev);
    }
    
    setTimeout(() => {
      isToggling.current = false;
    }, 0);
  }, [enableStateUpdates]);

  // Register application defaults
  useEffect(() => {
    // Only register default shortcuts if state updates are enabled
    // This prevents duplicate registrations when using in KeyboardShortcutsProvider
    if (enableStateUpdates) {
      // Register the help shortcut (Shift+?)
      registerShortcut("shift+?", {
        action: toggleShortcutsHelp,
        description: "Show keyboard shortcuts",
        category: "general",
        global: true,
        preventDefault: true
      });

      // Register escape to close help dialog
      registerShortcut("escape", {
        action: hideShortcutsHelp,
        description: "Close dialogs",
        category: "general",
        global: true,
        preventDefault: false
      });

      // Return cleanup function
      return () => {
        unregisterShortcut("shift+?");
        unregisterShortcut("escape");
      };
    }
    return undefined;
  }, [registerShortcut, unregisterShortcut, toggleShortcutsHelp, hideShortcutsHelp, enableStateUpdates]);
  
  // Format shortcut for display
  const formatShortcut = useCallback((shortcut: RegisteredShortcut): string => {
    return shortcut.formattedKey || formatKeyCombination(shortcut.key);
  }, []);
  
  // Export methods and properties
  return {
    shortcuts,
    registerShortcut,
    unregisterShortcut,
    clearShortcuts,
    getShortcutsByCategory,
    getAllShortcuts: () => Object.values(shortcuts),
    getCategories,
    formatKeyCombination,
    formatShortcut,
    showShortcutsHelp,
    hideShortcutsHelp,
    toggleShortcutsHelp,
    isHelpVisible: helpVisible
  };
} 