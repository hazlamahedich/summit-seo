"use client";

import React, { useState, useEffect } from "react";
import { motion, useSpring, animate, useMotionValue, useTransform } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface AnimatedMetricCardProps {
  title: string;
  value: number;
  previousValue?: number;
  suffix?: string;
  prefix?: string;
  icon?: React.ReactNode;
  description?: string;
  trend?: "up" | "down" | "neutral";
  trendValue?: number;
  isLoading?: boolean;
  animationDuration?: number;
  variant?: "default" | "gradient" | "spotlight" | "hover-lift";
  className?: string;
  onClick?: () => void;
}

export const AnimatedMetricCard: React.FC<AnimatedMetricCardProps> = ({
  title,
  value,
  previousValue,
  suffix = "",
  prefix = "",
  icon,
  description,
  trend = "neutral",
  trendValue,
  isLoading = false,
  animationDuration = 2,
  variant = "default",
  className,
  onClick,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const countValue = useMotionValue(previousValue || 0);
  const roundedValue = useTransform(countValue, (val) => Math.round(val));
  const displayValue = useTransform(roundedValue, (val) => `${val}`);
  
  // Spring animation configuration for hover effect
  const springConfig = { stiffness: 300, damping: 30 };
  const scale = useSpring(1, springConfig);
  
  // Determine trend color
  const trendColor = trend === "up" 
    ? "text-green-500" 
    : trend === "down" 
      ? "text-red-500" 
      : "text-gray-500";
  
  // Card variants based on style
  const cardVariants = {
    default: "bg-card hover:border-primary/50 transition-all",
    gradient: "bg-gradient-to-br from-primary/10 to-primary/5 hover:from-primary/20 hover:to-primary/10",
    spotlight: "relative bg-card overflow-hidden before:absolute before:inset-0 before:-translate-x-full hover:before:translate-x-full before:bg-gradient-to-r before:from-transparent before:via-white/10 before:to-transparent before:transition-transform before:duration-700",
    "hover-lift": "bg-card transition-all hover:-translate-y-1 hover:shadow-lg",
  };

  useEffect(() => {
    setIsVisible(true);
    
    // Animate the counter from previous value (or 0) to current value
    const controls = animate(countValue, value, {
      duration: animationDuration,
      ease: "easeOut",
    });

    return () => controls.stop();
  }, [value, countValue, animationDuration]);

  // Skeleton animation for loading state
  if (isLoading) {
    return (
      <Card className={cn("animate-pulse", className)}>
        <CardContent className="p-6">
          <div className="h-4 w-1/3 bg-muted rounded mb-3" />
          <div className="h-8 w-1/2 bg-muted rounded mb-2" />
          <div className="h-4 w-2/3 bg-muted rounded" />
        </CardContent>
      </Card>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={isVisible ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
      transition={{ duration: 0.5 }}
      whileHover={{ scale: variant === "hover-lift" ? 1.02 : 1 }}
      onClick={onClick}
      className={cn(
        "cursor-pointer", 
        onClick ? "cursor-pointer" : "cursor-default",
        className
      )}
    >
      <Card className={cn("overflow-hidden", cardVariants[variant])}>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-muted-foreground">{title}</h3>
            {icon && <div className="text-primary">{icon}</div>}
          </div>
          
          <div className="flex items-end space-x-1 mb-1">
            {prefix && <span className="text-2xl font-semibold">{prefix}</span>}
            <motion.span className="text-3xl font-bold">
              {displayValue}
            </motion.span>
            {suffix && <span className="text-xl font-semibold">{suffix}</span>}
          </div>
          
          {(description || trendValue) && (
            <div className="flex items-center mt-1">
              {trendValue && (
                <span className={cn("text-sm font-medium mr-2 flex items-center", trendColor)}>
                  {trend === "up" && "↑"}
                  {trend === "down" && "↓"}
                  {trendValue}%
                  
                  <motion.span
                    className="ml-1 inline-block"
                    initial={{ width: 0 }}
                    animate={{ width: "auto" }}
                    transition={{ delay: animationDuration - 0.5, duration: 0.3 }}
                  >
                    {trend === "up" && "increase"}
                    {trend === "down" && "decrease"}
                  </motion.span>
                </span>
              )}
              {description && (
                <span className="text-sm text-muted-foreground">
                  {description}
                </span>
              )}
            </div>
          )}
          
          {/* Optional animation flourish at the bottom of the card */}
          <motion.div
            className="w-full h-1 bg-primary/10 mt-4 rounded-full overflow-hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: animationDuration * 0.5, duration: 0.5 }}
          >
            <motion.div
              className="h-full bg-primary"
              initial={{ width: "0%" }}
              animate={{ width: `${(value / 100) * 100}%` }}
              transition={{ delay: animationDuration * 0.75, duration: 0.8, ease: "easeOut" }}
            />
          </motion.div>
        </CardContent>
      </Card>
    </motion.div>
  );
}; 