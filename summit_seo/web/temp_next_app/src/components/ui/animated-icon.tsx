"use client";

import React from 'react';
import { motion, MotionProps, HTMLMotionProps, Transition, Variants } from 'framer-motion';
import { cn } from '@/lib/utils';
import { useReducedMotion } from '@/lib/motion';
import { iconHoverVariants } from '@/lib/animation-utils';

type RepeatType = "loop" | "reverse" | "mirror";

// Use HTMLMotionProps to ensure we have the correct typing for motion.div
export interface AnimatedIconProps extends HTMLMotionProps<"div"> {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: string;
  animationType?: 'pulse' | 'rotate' | 'bounce' | 'shake' | 'none';
  hoverEffect?: boolean;
  clickEffect?: boolean;
  cycleColors?: string[];
  motionProps?: MotionProps;
}

export const AnimatedIcon = ({
  children,
  size = 'md',
  color,
  animationType = 'none',
  hoverEffect = true,
  clickEffect = true,
  cycleColors,
  className,
  motionProps,
  onClick,
  style,
  ...props
}: AnimatedIconProps) => {
  const prefersReducedMotion = useReducedMotion();
  const [colorIndex, setColorIndex] = React.useState(0);

  // Generate size classes
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-10 h-10',
  };

  // Animation variants based on type
  const getAnimationVariants = (): Variants | undefined => {
    if (prefersReducedMotion) return undefined;

    switch (animationType) {
      case 'pulse':
        return {
          animate: {
            scale: [1, 1.1, 1],
            transition: {
              duration: 1.5,
              repeat: Infinity,
              repeatType: "loop" as RepeatType,
            },
          },
        };
      case 'rotate':
        return {
          animate: {
            rotate: [0, 360],
            transition: {
              duration: 2,
              repeat: Infinity,
              ease: 'linear',
            },
          },
        };
      case 'bounce':
        return {
          animate: {
            y: [0, -5, 0],
            transition: {
              duration: 1,
              repeat: Infinity,
              repeatType: "loop" as RepeatType,
            },
          },
        };
      case 'shake':
        return {
          animate: {
            x: [0, -2, 2, -2, 2, 0],
            transition: {
              duration: 0.5,
              repeat: Infinity,
              repeatType: "loop" as RepeatType,
              repeatDelay: 2,
            },
          },
        };
      default:
        return undefined;
    }
  };

  // Handle click for color cycling if enabled
  const handleClick = (e: React.MouseEvent<HTMLDivElement> | MouseEvent | TouchEvent | PointerEvent) => {
    if (cycleColors && cycleColors.length > 0) {
      setColorIndex((prev) => (prev + 1) % cycleColors.length);
    }
    
    // Forward the click event
    if (onClick) {
      // Check if it's a React MouseEvent
      if ('currentTarget' in e && e.currentTarget instanceof HTMLDivElement) {
        onClick(e as React.MouseEvent<HTMLDivElement>);
      }
    }
  };

  // Get current color from cycle or from direct prop
  const currentColor = cycleColors && cycleColors.length > 0
    ? cycleColors[colorIndex]
    : color;

  // Generate animation states based on selected animation type
  const animationVariants = getAnimationVariants();
  
  // Apply continuous animation if selected
  const continuousAnimation = 
    animationType !== 'none' && !prefersReducedMotion
      ? { animate: "animate" }
      : {};

  return (
    <motion.div
      className={cn(
        'flex items-center justify-center',
        sizeClasses[size],
        className
      )}
      initial="initial"
      whileHover={hoverEffect && !prefersReducedMotion ? "hover" : undefined}
      whileTap={clickEffect && !prefersReducedMotion ? "tap" : undefined}
      variants={{
        ...iconHoverVariants,
        ...(animationVariants || {})
      }}
      {...continuousAnimation}
      style={{
        color: currentColor,
        ...style,
      }}
      onClick={handleClick}
      {...motionProps}
      {...props}
    >
      {children}
    </motion.div>
  );
};

export default AnimatedIcon; 