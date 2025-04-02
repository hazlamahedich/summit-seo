"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { useReducedMotion } from '@/lib/motion';

interface AnimatedTooltipProps {
  content: React.ReactNode;
  children: React.ReactNode;
  side?: 'top' | 'right' | 'bottom' | 'left';
  align?: 'start' | 'center' | 'end';
  delay?: number;
  className?: string;
  contentClassName?: string;
  maxWidth?: number;
  interactive?: boolean;
}

export function AnimatedTooltip({
  content,
  children,
  side = 'top',
  align = 'center',
  delay = 0.5,
  className,
  contentClassName,
  maxWidth = 250,
  interactive = false,
}: AnimatedTooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [hoverTimeout, setHoverTimeout] = useState<NodeJS.Timeout | null>(null);
  const prefersReducedMotion = useReducedMotion();

  // Calculate position based on side and align
  const getPositionStyles = () => {
    const positions: Record<string, Record<string, any>> = {
      top: {
        bottom: '100%',
        marginBottom: '10px',
        left: align === 'start' ? '0' : align === 'end' ? 'auto' : '50%',
        right: align === 'end' ? '0' : 'auto',
        transform: align === 'center' ? 'translateX(-50%)' : 'none',
      },
      right: {
        left: '100%',
        marginLeft: '10px',
        top: align === 'start' ? '0' : align === 'end' ? 'auto' : '50%',
        bottom: align === 'end' ? '0' : 'auto',
        transform: align === 'center' ? 'translateY(-50%)' : 'none',
      },
      bottom: {
        top: '100%',
        marginTop: '10px',
        left: align === 'start' ? '0' : align === 'end' ? 'auto' : '50%',
        right: align === 'end' ? '0' : 'auto',
        transform: align === 'center' ? 'translateX(-50%)' : 'none',
      },
      left: {
        right: '100%',
        marginRight: '10px',
        top: align === 'start' ? '0' : align === 'end' ? 'auto' : '50%',
        bottom: align === 'end' ? '0' : 'auto',
        transform: align === 'center' ? 'translateY(-50%)' : 'none',
      },
    };

    return positions[side];
  };

  // Animation variants based on side
  const getAnimationVariants = () => {
    if (prefersReducedMotion) {
      return {
        hidden: { opacity: 0 },
        visible: { opacity: 1 },
      };
    }

    const variants: Record<string, any> = {
      top: {
        hidden: { opacity: 0, y: 10 },
        visible: { opacity: 1, y: 0 },
      },
      right: {
        hidden: { opacity: 0, x: -10 },
        visible: { opacity: 1, x: 0 },
      },
      bottom: {
        hidden: { opacity: 0, y: -10 },
        visible: { opacity: 1, y: 0 },
      },
      left: {
        hidden: { opacity: 0, x: 10 },
        visible: { opacity: 1, x: 0 },
      },
    };

    return variants[side];
  };

  // Handle mouse events
  const handleMouseEnter = () => {
    if (hoverTimeout) clearTimeout(hoverTimeout);
    const timeout = setTimeout(() => {
      setIsVisible(true);
    }, delay * 1000);
    setHoverTimeout(timeout);
  };

  const handleMouseLeave = () => {
    if (hoverTimeout) clearTimeout(hoverTimeout);
    if (!interactive) {
      setIsVisible(false);
    }
  };

  // Handle tooltip content mouse events (for interactive tooltips)
  const handleContentMouseEnter = () => {
    if (interactive && hoverTimeout) {
      clearTimeout(hoverTimeout);
    }
  };

  const handleContentMouseLeave = () => {
    if (interactive) {
      setIsVisible(false);
    }
  };

  return (
    <div
      className={cn('relative inline-block', className)}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onFocus={handleMouseEnter}
      onBlur={handleMouseLeave}
    >
      {children}
      <AnimatePresence>
        {isVisible && (
          <motion.div
            className={cn(
              'absolute z-50 px-3 py-2 text-sm rounded shadow-md',
              'bg-popover text-popover-foreground border',
              contentClassName
            )}
            style={{
              ...getPositionStyles(),
              maxWidth: `${maxWidth}px`,
            }}
            initial="hidden"
            animate="visible"
            exit="hidden"
            variants={getAnimationVariants()}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            onMouseEnter={handleContentMouseEnter}
            onMouseLeave={handleContentMouseLeave}
          >
            {content}
            <motion.div
              className={cn(
                'absolute w-2 h-2 bg-popover rotate-45 border',
                side === 'top' && 'bottom-0 translate-y-1/2 border-b-0 border-l-0',
                side === 'right' && 'left-0 -translate-x-1/2 border-t-0 border-r-0',
                side === 'bottom' && 'top-0 -translate-y-1/2 border-t-0 border-r-0',
                side === 'left' && 'right-0 translate-x-1/2 border-b-0 border-l-0',
                align === 'start' && 'left-3',
                align === 'center' && (side === 'top' || side === 'bottom') && 'left-1/2 -translate-x-1/2',
                align === 'center' && (side === 'left' || side === 'right') && 'top-1/2 -translate-y-1/2',
                align === 'end' && 'right-3'
              )}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
} 