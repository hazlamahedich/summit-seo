"use client";

import React, { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

// Variant presets
const variants = {
  fadeIn: {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { duration: 0.5 }
    }
  },
  slideUp: {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.3, ease: 'easeOut' }
    }
  },
  slideDown: {
    hidden: { opacity: 0, y: -20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { duration: 0.3, ease: 'easeOut' }
    }
  },
  slideLeft: {
    hidden: { opacity: 0, x: 20 },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: { duration: 0.3, ease: 'easeOut' }
    }
  },
  slideRight: {
    hidden: { opacity: 0, x: -20 },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: { duration: 0.3, ease: 'easeOut' }
    }
  },
};

type VariantType = keyof typeof variants;

interface AnimatedContainerProps {
  children: ReactNode;
  variant?: VariantType;
  delay?: number;
  duration?: number;
  className?: string;
  once?: boolean;
}

export function AnimatedContainer({
  children,
  variant = 'fadeIn',
  delay = 0,
  duration,
  className,
  once = true,
  ...props
}: AnimatedContainerProps) {
  const selectedVariant = variants[variant];
  
  return (
    <motion.div
      initial="hidden"
      whileInView="visible"
      viewport={{ once }}
      variants={selectedVariant}
      transition={{
        delay,
        ...(duration ? { duration } : {})
      }}
      className={cn(className)}
      {...props}
    >
      {children}
    </motion.div>
  );
}

export default AnimatedContainer; 