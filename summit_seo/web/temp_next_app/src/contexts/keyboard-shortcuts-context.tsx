"use client";

import React, { createContext, useContext, useState, useRef, useCallback } from "react";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";
import { KeyboardShortcutsDialog } from "@/components/ui/keyboard-shortcuts-dialog";

interface KeyboardShortcutsContextProps {
  // Dialog management
  isHelpVisible: boolean;
  showShortcutsHelp: () => void;
  hideShortcutsHelp: () => void;
  toggleShortcutsHelp: () => void;
  
  // Shortcut registration
  registerShortcut: ReturnType<typeof useKeyboardShortcuts>["registerShortcut"];
  unregisterShortcut: ReturnType<typeof useKeyboardShortcuts>["unregisterShortcut"];
}

const KeyboardShortcutsContext = createContext<KeyboardShortcutsContextProps | undefined>(undefined);

export const useKeyboardShortcutsContext = () => {
  const context = useContext(KeyboardShortcutsContext);
  if (context === undefined) {
    throw new Error("useKeyboardShortcutsContext must be used within a KeyboardShortcutsProvider");
  }
  return context;
};

interface KeyboardShortcutsProviderProps {
  children: React.ReactNode;
}

export function KeyboardShortcutsProvider({ children }: KeyboardShortcutsProviderProps) {
  // Create a stable keyboard shortcuts instance
  const keyboardShortcuts = useKeyboardShortcuts({
    enableGlobalShortcuts: true,
    enableStateUpdates: false // Tell the hook not to manage dialog visibility state
  });
  
  // Manage dialog visibility in this component only
  const [dialogOpen, setDialogOpen] = useState(false);
  
  // Use a ref to prevent multiple state updates
  const isUpdating = useRef(false);
  const stableHandlers = useRef({
    registerShortcut: keyboardShortcuts.registerShortcut,
    unregisterShortcut: keyboardShortcuts.unregisterShortcut
  });
  
  // Show shortcuts help with debounce protection
  const showShortcutsHelp = useCallback(() => {
    if (isUpdating.current) return;
    isUpdating.current = true;
    
    // Use functional update to avoid stale state
    setDialogOpen(true);
    
    // Reset the updating flag after a delay
    setTimeout(() => {
      isUpdating.current = false;
    }, 100);
  }, []);
  
  // Hide shortcuts help with debounce protection
  const hideShortcutsHelp = useCallback(() => {
    if (isUpdating.current) return;
    isUpdating.current = true;
    
    // Use functional update to avoid stale state
    setDialogOpen(false);
    
    // Reset the updating flag after a delay
    setTimeout(() => {
      isUpdating.current = false;
    }, 100);
  }, []);
  
  // Toggle shortcuts help with debounce protection
  const toggleShortcutsHelp = useCallback(() => {
    if (isUpdating.current) return;
    isUpdating.current = true;
    
    // Use functional update to avoid stale state
    setDialogOpen(prev => !prev);
    
    // Reset the updating flag after a delay
    setTimeout(() => {
      isUpdating.current = false;
    }, 100);
  }, []);
  
  // Register keyboard shortcuts for dialog management
  React.useEffect(() => {
    // Register the help shortcut (Shift+?)
    stableHandlers.current.registerShortcut("shift+?", {
      action: toggleShortcutsHelp,
      description: "Show keyboard shortcuts",
      category: "general",
      global: true,
      preventDefault: true
    });

    // Register escape to close help dialog
    stableHandlers.current.registerShortcut("escape", {
      action: hideShortcutsHelp,
      description: "Close dialogs",
      category: "general",
      global: true,
      preventDefault: false
    });

    // Return cleanup function
    return () => {
      stableHandlers.current.unregisterShortcut("shift+?");
      stableHandlers.current.unregisterShortcut("escape");
    };
  }, [toggleShortcutsHelp, hideShortcutsHelp]);
  
  // Create a stable context value that won't change on every render
  const contextValue = React.useMemo(() => ({
    isHelpVisible: dialogOpen,
    showShortcutsHelp,
    hideShortcutsHelp,
    toggleShortcutsHelp,
    registerShortcut: stableHandlers.current.registerShortcut,
    unregisterShortcut: stableHandlers.current.unregisterShortcut,
  }), [
    dialogOpen,
    showShortcutsHelp,
    hideShortcutsHelp,
    toggleShortcutsHelp
  ]);

  // Handle dialog open state changes
  const handleOpenChange = useCallback((open: boolean) => {
    if (isUpdating.current) return;
    
    if (open !== dialogOpen) {
      isUpdating.current = true;
      setDialogOpen(open);
      
      // Reset the updating flag after a delay
      setTimeout(() => {
        isUpdating.current = false;
      }, 100);
    }
  }, [dialogOpen]);

  return (
    <KeyboardShortcutsContext.Provider value={contextValue}>
      {children}
      <KeyboardShortcutsDialog 
        open={dialogOpen} 
        onOpenChange={handleOpenChange}
      />
    </KeyboardShortcutsContext.Provider>
  );
} 