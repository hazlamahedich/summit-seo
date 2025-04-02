"use client";

import React from "react";
import { useSoundEffectsContext } from "@/contexts/sound-effects-context";
import { Switch } from "./switch";
import { Slider } from "./slider";
import { VolumeX, Volume2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface SoundSettingsProps {
  className?: string;
  showLabel?: boolean;
  compact?: boolean;
}

/**
 * Sound settings component with volume slider and mute toggle
 */
export function SoundSettings({ 
  className, 
  showLabel = true,
  compact = false 
}: SoundSettingsProps) {
  const { 
    enabled, 
    toggleEnabled, 
    volume, 
    setVolume,
    playToggle,
    playClick
  } = useSoundEffectsContext();

  const handleVolumeChange = (value: number[]) => {
    setVolume(value[0]);
    if (enabled && value[0] > 0) {
      playClick();
    }
  };

  const handleToggle = (checked: boolean) => {
    toggleEnabled();
    playToggle();
  };

  return (
    <div className={cn(
      "flex items-center gap-4", 
      compact ? "flex-col" : "flex-row",
      className
    )}>
      {showLabel && (
        <span className="text-sm font-medium">Sound Effects</span>
      )}
      
      <div className="flex items-center gap-2">
        <Switch 
          checked={enabled} 
          onCheckedChange={handleToggle}
          aria-label={enabled ? "Mute sound effects" : "Unmute sound effects"}
        />
        {!compact && (
          <span className="text-xs text-muted-foreground">
            {enabled ? "On" : "Off"}
          </span>
        )}
      </div>
      
      <div className={cn(
        "flex items-center gap-2", 
        compact ? "w-full" : "min-w-[140px]"
      )}>
        <VolumeX className="h-4 w-4 text-muted-foreground" />
        <Slider
          disabled={!enabled}
          value={[volume]}
          min={0}
          max={1}
          step={0.01}
          onValueChange={handleVolumeChange}
          aria-label="Adjust sound volume"
        />
        <Volume2 className="h-4 w-4 text-muted-foreground" />
      </div>
    </div>
  );
} 