"use client";

import React, { useMemo, useCallback, memo } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useKeyboardShortcuts } from "@/hooks/useKeyboardShortcuts";
import { motion } from "framer-motion";

interface KeyboardShortcutsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

interface ShortcutCategoryProps {
  title: string;
  children: React.ReactNode;
}

const ShortcutCategory = memo(({ title, children }: ShortcutCategoryProps) => (
  <div className="mb-6">
    <h3 className="text-lg font-semibold mb-3">{title}</h3>
    <div className="space-y-2">
      {children}
    </div>
  </div>
));
ShortcutCategory.displayName = 'ShortcutCategory';

interface ShortcutItemProps {
  keys: string;
  description: string;
}

const ShortcutItem = memo(({ keys, description }: ShortcutItemProps) => (
  <motion.div 
    className="flex justify-between items-center py-2"
    initial={{ opacity: 0, y: 5 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -5 }}
    transition={{ duration: 0.2 }}
  >
    <span className="text-sm text-muted-foreground">{description}</span>
    <div className="flex items-center gap-1">
      {keys.split('+').map((key, index, array) => (
        <React.Fragment key={index}>
          <kbd className="px-2 py-1 text-xs font-semibold bg-muted border rounded shadow-sm">
            {key.trim()}
          </kbd>
          {index < array.length - 1 && <span className="text-xs">+</span>}
        </React.Fragment>
      ))}
    </div>
  </motion.div>
));
ShortcutItem.displayName = 'ShortcutItem';

export const KeyboardShortcutsDialog = memo(({ open, onOpenChange }: KeyboardShortcutsDialogProps) => {
  // Only fetch shortcuts when dialog is open to avoid unnecessary processing
  const keyboardShortcuts = useKeyboardShortcuts({
    enableStateUpdates: false,
    enableGlobalShortcuts: false // Avoid duplicate event listeners
  });

  // Use destructuring with a stable reference
  const { getAllShortcuts, formatKeyCombination } = keyboardShortcuts;

  // Safely get all shortcuts using useMemo to prevent unnecessary recalculations
  const allShortcuts = useMemo(() => {
    // Only process shortcuts when dialog is open
    if (!open) return { navigationShortcuts: [], generalShortcuts: [] };
    
    try {
      const shortcuts = getAllShortcuts() || [];
      
      const navShortcuts = shortcuts.filter(
        shortcut => shortcut && shortcut.description && shortcut.description.toLowerCase().includes('go to')
      );
      
      const genShortcuts = shortcuts.filter(
        shortcut => shortcut && shortcut.description && !shortcut.description.toLowerCase().includes('go to')
      );
      
      return { navigationShortcuts: navShortcuts, generalShortcuts: genShortcuts };
    } catch (e) {
      console.error('Error fetching shortcuts:', e);
      return { navigationShortcuts: [], generalShortcuts: [] };
    }
  }, [open, getAllShortcuts]);

  // Handle dialog open/close changes with memoized callback
  const handleOpenChange = useCallback((newOpen: boolean) => {
    if (typeof onOpenChange === 'function') {
      onOpenChange(newOpen);
    }
  }, [onOpenChange]);

  // Memoize sections to prevent unnecessary renders
  const generalSection = useMemo(() => (
    allShortcuts.generalShortcuts.length > 0 ? (
      <ShortcutCategory title="General">
        {allShortcuts.generalShortcuts.map((shortcut) => (
          <ShortcutItem 
            key={shortcut.key}
            keys={shortcut.formattedKey || formatKeyCombination(shortcut.key)}
            description={shortcut.description}
          />
        ))}
      </ShortcutCategory>
    ) : null
  ), [allShortcuts.generalShortcuts, formatKeyCombination]);

  const navigationSection = useMemo(() => (
    allShortcuts.navigationShortcuts.length > 0 ? (
      <ShortcutCategory title="Navigation">
        {allShortcuts.navigationShortcuts.map((shortcut) => (
          <ShortcutItem 
            key={shortcut.key}
            keys={shortcut.formattedKey || formatKeyCombination(shortcut.key)}
            description={shortcut.description}
          />
        ))}
      </ShortcutCategory>
    ) : null
  ), [allShortcuts.navigationShortcuts, formatKeyCombination]);

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Keyboard Shortcuts</DialogTitle>
          <DialogDescription>
            Use these keyboard shortcuts to navigate and interact with the application efficiently.
          </DialogDescription>
        </DialogHeader>
        
        {open && (
          <ScrollArea className="h-[60vh] pr-4">
            <div className="space-y-6 pr-4">
              {generalSection}
              {navigationSection}
              
              <div className="pt-4 border-t">
                <p className="text-sm text-muted-foreground">
                  Press <kbd className="px-2 py-1 text-xs font-semibold bg-muted border rounded shadow-sm">Shift</kbd>+
                  <kbd className="px-2 py-1 text-xs font-semibold bg-muted border rounded shadow-sm">?</kbd> to show this dialog anytime.
                </p>
              </div>
            </div>
          </ScrollArea>
        )}
      </DialogContent>
    </Dialog>
  );
});
KeyboardShortcutsDialog.displayName = 'KeyboardShortcutsDialog'; 