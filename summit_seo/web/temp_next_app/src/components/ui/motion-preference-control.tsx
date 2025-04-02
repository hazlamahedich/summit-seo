"use client";

import React from 'react';
import { Bike, Zap, XCircle } from 'lucide-react';
import { AnimatedButton } from '@/components/ui/animated-button';
import { AnimatedTooltip } from '@/components/ui/animated-tooltip';
import { AnimatedIcon } from '@/components/ui/animated-icon';
import { cn } from '@/lib/utils';
import { usePreferredMotion, MotionPreference } from '@/hooks/usePreferredMotion';

interface MotionPreferenceControlProps {
  className?: string;
  showText?: boolean;
  showIcons?: boolean;
  variant?: 'buttons' | 'toggle' | 'select';
}

export function MotionPreferenceControl({
  className,
  showText = true,
  showIcons = true,
  variant = 'buttons',
}: MotionPreferenceControlProps) {
  const { 
    preference, 
    setPreference, 
    cycleMotion 
  } = usePreferredMotion();

  const getIconForPreference = (pref: MotionPreference) => {
    switch (pref) {
      case 'full':
        return <Zap className="h-4 w-4" />;
      case 'reduced':
        return <Bike className="h-4 w-4" />;
      case 'none':
        return <XCircle className="h-4 w-4" />;
    }
  };

  const getTextForPreference = (pref: MotionPreference) => {
    switch (pref) {
      case 'full':
        return 'Full Motion';
      case 'reduced':
        return 'Reduced Motion';
      case 'none':
        return 'No Motion';
    }
  };

  const getTooltipForPreference = (pref: MotionPreference) => {
    switch (pref) {
      case 'full':
        return 'Full animations and motion effects';
      case 'reduced':
        return 'Simplified animations for improved accessibility';
      case 'none':
        return 'No animations or motion effects';
    }
  };

  if (variant === 'buttons') {
    return (
      <div className={cn("flex items-center gap-2", className)}>
        {(['full', 'reduced', 'none'] as MotionPreference[]).map((pref) => (
          <AnimatedButton
            key={pref}
            size="sm"
            variant={preference === pref ? "default" : "outline"}
            onClick={() => setPreference(pref)}
            icon={showIcons ? getIconForPreference(pref) : undefined}
            className={cn(
              "transition-all",
              !showText && showIcons && "p-2"
            )}
          >
            {showText && getTextForPreference(pref)}
          </AnimatedButton>
        ))}
      </div>
    );
  }

  if (variant === 'toggle') {
    return (
      <div className={cn("inline-block", className)}>
        <AnimatedTooltip 
          content={getTooltipForPreference(preference)}
          side="top"
        >
          <button
            onClick={cycleMotion}
            className={cn(
              "flex items-center gap-2 px-3 py-2 rounded-md border",
              "transition-all hover:bg-accent",
              preference === 'full' && "bg-blue-100 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800",
              preference === 'reduced' && "bg-amber-100 dark:bg-amber-900/30 border-amber-200 dark:border-amber-800",
              preference === 'none' && "bg-gray-100 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700"
            )}
          >
            <AnimatedIcon 
              size="sm" 
              animationType={preference === 'none' ? 'none' : 'none'} // No animation when 'none' is selected
              className="flex-shrink-0"
            >
              {getIconForPreference(preference)}
            </AnimatedIcon>
            
            {showText && (
              <span className="text-sm">{getTextForPreference(preference)}</span>
            )}
          </button>
        </AnimatedTooltip>
      </div>
    );
  }

  if (variant === 'select') {
    return (
      <select
        value={preference}
        onChange={(e) => setPreference(e.target.value as MotionPreference)}
        className={cn(
          "px-3 py-2 rounded-md border bg-background",
          "focus:outline-none focus:ring-2 focus:ring-blue-500",
          className
        )}
      >
        <option value="full">Full Motion</option>
        <option value="reduced">Reduced Motion</option>
        <option value="none">No Motion</option>
      </select>
    );
  }

  return null;
} 