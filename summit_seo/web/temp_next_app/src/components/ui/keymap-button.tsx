"use client";

import { Button } from "@/components/ui/button";
import { Keyboard } from "lucide-react";
import { useKeyboardShortcutsContext } from "@/contexts/keyboard-shortcuts-context";
import { cn } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { useCallback, memo } from "react";
import * as React from "react";

type KeymapButtonProps = Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, "onClick"> & {
  showTooltip?: boolean;
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
  size?: "default" | "sm" | "lg" | "icon";
};

// Use memo to prevent unnecessary re-renders
export const KeymapButton = memo(({ 
  showTooltip = true,
  className,
  variant = "outline",
  size = "icon",
  ...props 
}: KeymapButtonProps) => {
  const { toggleShortcutsHelp, isHelpVisible } = useKeyboardShortcutsContext();
  
  // Simple callback to toggle shortcuts dialog
  const handleClick = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    toggleShortcutsHelp();
  }, [toggleShortcutsHelp]);

  // Memoize the button component to avoid recreating it on every render
  const button = React.useMemo(() => (
    <Button
      variant={variant}
      size={size}
      onClick={handleClick}
      className={cn("relative", className)}
      {...props}
      aria-pressed={isHelpVisible}
      aria-label="Keyboard Shortcuts"
    >
      <Keyboard className="h-[1.2rem] w-[1.2rem]" />
      <span className="sr-only">Keyboard Shortcuts</span>
    </Button>
  ), [variant, size, handleClick, className, props, isHelpVisible]);

  // Only render tooltip if needed, memoized to avoid re-renders
  return React.useMemo(() => {
    if (showTooltip) {
      return (
        <TooltipProvider>
          <Tooltip delayDuration={300}>
            <TooltipTrigger asChild>
              {button}
            </TooltipTrigger>
            <TooltipContent side="bottom">
              <div className="text-sm">
                <p>Keyboard Shortcuts</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Press <kbd className="px-1 py-0.5 text-xs font-semibold bg-muted border rounded">Shift</kbd>+
                  <kbd className="px-1 py-0.5 text-xs font-semibold bg-muted border rounded">?</kbd>
                </p>
              </div>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      );
    }
    return button;
  }, [button, showTooltip]);
});

KeymapButton.displayName = 'KeymapButton'; 