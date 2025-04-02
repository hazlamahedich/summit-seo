"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { Wifi, WifiOff, Upload, CheckCircle2, XCircle } from "lucide-react";
import { useOnlineStatus, useOfflineManager } from "@/lib/offline-manager";
import { hapticFeedback } from "@/lib/haptics";

interface OfflineStatusProps {
  className?: string;
  showSyncDetails?: boolean;
  position?: "top" | "bottom";
  showWhenOnline?: boolean;
  autoHide?: boolean;
  autoHideDelay?: number;
}

/**
 * Offline status indicator component that shows connection status and pending sync operations
 */
export function OfflineStatus({
  className,
  showSyncDetails = true,
  position = "top",
  showWhenOnline = false,
  autoHide = true,
  autoHideDelay = 3000,
}: OfflineStatusProps) {
  const isOnline = useOnlineStatus();
  const { pendingCount, processQueue } = useOfflineManager();
  const [expanded, setExpanded] = useState(false);
  const [visible, setVisible] = useState(true);
  const [syncStatus, setSyncStatus] = useState<"idle" | "syncing" | "success" | "error">("idle");
  const [lastSyncAttempt, setLastSyncAttempt] = useState<Date | null>(null);

  // Auto-hide when online if configured
  useEffect(() => {
    if (isOnline && autoHide && pendingCount === 0) {
      const timer = setTimeout(() => {
        setVisible(false);
      }, autoHideDelay);
      
      return () => clearTimeout(timer);
    } else {
      setVisible(true);
    }
  }, [isOnline, autoHide, autoHideDelay, pendingCount]);

  // Trigger haptic feedback when connection status changes
  useEffect(() => {
    if (typeof window !== "undefined") {
      hapticFeedback(isOnline ? "success" : "error");
    }
  }, [isOnline]);

  // Handle manual sync
  const handleSync = async () => {
    if (!isOnline || pendingCount === 0) return;
    
    try {
      setSyncStatus("syncing");
      hapticFeedback("selection");
      await processQueue();
      setSyncStatus("success");
      hapticFeedback("success");
      
      // Reset status after 2 seconds
      setTimeout(() => {
        setSyncStatus("idle");
      }, 2000);
    } catch (error) {
      setSyncStatus("error");
      hapticFeedback("error");
      
      // Reset status after 2 seconds
      setTimeout(() => {
        setSyncStatus("idle");
      }, 2000);
    }
    
    setLastSyncAttempt(new Date());
  };

  // Toggle expanded view
  const toggleExpanded = () => {
    setExpanded(!expanded);
    hapticFeedback("selection");
  };

  // Don't render if online and configured to hide
  if (isOnline && !showWhenOnline && pendingCount === 0 && !visible) {
    return null;
  }

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          className={cn(
            "fixed z-50 left-0 right-0 mx-auto w-fit px-2",
            position === "top" ? "top-2" : "bottom-2",
            className
          )}
          initial={{ opacity: 0, y: position === "top" ? -20 : 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: position === "top" ? -20 : 20 }}
          transition={{ duration: 0.2 }}
        >
          <motion.div
            className={cn(
              "rounded-xl backdrop-blur-sm shadow-lg overflow-hidden",
              isOnline ? "bg-green-500/10" : "bg-red-500/10",
              expanded ? "w-80" : "w-auto"
            )}
            layout
          >
            {/* Main status bar */}
            <div 
              className={cn(
                "flex items-center justify-between px-4 py-2 gap-2 cursor-pointer",
                expanded && "border-b border-border/20"
              )}
              onClick={toggleExpanded}
            >
              <div className="flex items-center gap-2">
                {isOnline ? (
                  <Wifi className="h-4 w-4 text-green-500" />
                ) : (
                  <WifiOff className="h-4 w-4 text-red-500" />
                )}
                <span className="text-sm font-medium">
                  {isOnline ? "Online" : "Offline"}
                </span>
              </div>
              
              {/* Pending requests count */}
              {pendingCount > 0 && (
                <div className="flex items-center gap-2">
                  <span className="text-xs bg-secondary/20 px-2 py-0.5 rounded-full">
                    {pendingCount} pending
                  </span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSync();
                    }}
                    className={cn(
                      "rounded-full p-1",
                      "hover:bg-secondary/20 focus:outline-none focus:ring-2 focus:ring-secondary",
                      syncStatus === "syncing" && "animate-spin text-secondary",
                      syncStatus === "success" && "text-green-500",
                      syncStatus === "error" && "text-red-500"
                    )}
                    disabled={syncStatus === "syncing"}
                  >
                    {syncStatus === "idle" && <Upload className="h-3 w-3" />}
                    {syncStatus === "syncing" && <Upload className="h-3 w-3" />}
                    {syncStatus === "success" && <CheckCircle2 className="h-3 w-3" />}
                    {syncStatus === "error" && <XCircle className="h-3 w-3" />}
                  </button>
                </div>
              )}
            </div>
            
            {/* Expanded details */}
            <AnimatePresence>
              {expanded && showSyncDetails && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="overflow-hidden"
                >
                  <div className="p-3 text-xs space-y-2">
                    <div className="flex justify-between">
                      <span className="opacity-70">Status:</span>
                      <span className={isOnline ? "text-green-500" : "text-red-500"}>
                        {isOnline ? "Connected" : "Disconnected"}
                      </span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="opacity-70">Pending requests:</span>
                      <span>{pendingCount}</span>
                    </div>
                    
                    {lastSyncAttempt && (
                      <div className="flex justify-between">
                        <span className="opacity-70">Last sync attempt:</span>
                        <span className="tabular-nums">
                          {lastSyncAttempt.toLocaleTimeString()}
                        </span>
                      </div>
                    )}
                    
                    {pendingCount > 0 && isOnline && (
                      <button
                        onClick={handleSync}
                        className={cn(
                          "w-full mt-2 py-1 rounded-md text-center text-xs font-medium",
                          "bg-secondary/20 hover:bg-secondary/30",
                          "focus:outline-none focus:ring-2 focus:ring-secondary",
                          "transition-colors"
                        )}
                        disabled={syncStatus === "syncing"}
                      >
                        {syncStatus === "idle" && "Sync now"}
                        {syncStatus === "syncing" && "Syncing..."}
                        {syncStatus === "success" && "Sync complete"}
                        {syncStatus === "error" && "Sync failed"}
                      </button>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
} 