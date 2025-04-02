'use client';

import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { useABTestVariant } from "@/hooks/useABTestVariant";
import { motion } from 'framer-motion';
import { ArrowRight, ArrowUpRight, Sparkles } from 'lucide-react';

// CTA button experiment ID
const EXPERIMENT_ID = 'cta-button-design';

interface CTAButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
  size?: 'default' | 'sm' | 'lg' | 'icon' | null | undefined;
}

export function CTAButtonExperiment({ 
  children, 
  onClick, 
  className = '',
  size = 'default'
}: CTAButtonProps) {
  const { variantId, trackInteraction, trackConversion } = useABTestVariant(
    EXPERIMENT_ID, 
    true // track initial view
  );
  
  const handleClick = () => {
    // Track the interaction and conversion
    trackInteraction();
    trackConversion();
    
    // Call the parent callback
    onClick?.();
  };
  
  // If no variant assigned or still loading, show the default button
  // Or if the variant is specifically "control"
  if (!variantId || variantId === 'control') {
    return (
      <Button 
        onClick={handleClick}
        className={className}
        size={size}
      >
        {children}
      </Button>
    );
  }
  
  // Show variant A (animated button)
  if (variantId === 'variant-a') {
    return <AnimatedButton onClick={handleClick} className={className} size={size}>{children}</AnimatedButton>;
  }
  
  // Show variant B (gradient button)
  if (variantId === 'variant-b') {
    return <GradientButton onClick={handleClick} className={className} size={size}>{children}</GradientButton>;
  }
  
  // Show variant C (minimal button)
  if (variantId === 'variant-c') {
    return <MinimalButton onClick={handleClick} className={className} size={size}>{children}</MinimalButton>;
  }
  
  // Fallback to default button
  return (
    <Button 
      onClick={handleClick}
      className={className}
      size={size}
    >
      {children}
    </Button>
  );
}

// Animated button with hover effects (Variant A)
function AnimatedButton({ children, onClick, className = '', size = 'default' }: CTAButtonProps) {
  const [isHovered, setIsHovered] = useState(false);
  
  return (
    <motion.div
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className="relative inline-block"
    >
      <motion.div
        className={`
          relative z-10 overflow-hidden rounded-md
          ${size === 'sm' ? 'px-3 py-1.5 text-sm' : ''}
          ${size === 'lg' ? 'px-6 py-3 text-lg' : ''}
          ${size === 'default' ? 'px-4 py-2' : ''}
          ${className}
        `}
        style={{
          background: "linear-gradient(90deg, #2563eb, #6366f1)",
          color: "white"
        }}
        whileTap={{ scale: 0.98 }}
        onClick={onClick}
      >
        <motion.div 
          className="flex items-center justify-center gap-2"
          animate={{ x: isHovered ? 5 : 0 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
        >
          {children} 
          <motion.div
            animate={{ 
              x: isHovered ? 2 : 0,
              rotate: isHovered ? 45 : 0,
              opacity: isHovered ? 1 : 0.8
            }}
            transition={{ duration: 0.2 }}
          >
            <ArrowUpRight className="h-5 w-5" />
          </motion.div>
        </motion.div>
      </motion.div>
      
      <motion.div
        className="absolute inset-0 rounded-md"
        style={{ 
          background: "linear-gradient(90deg, #1d4ed8, #4f46e5)",
          opacity: 0
        }}
        animate={{ 
          opacity: isHovered ? 0.5 : 0,
          y: isHovered ? 3 : 0,
          x: isHovered ? 3 : 0
        }}
        transition={{ duration: 0.2 }}
      />
    </motion.div>
  );
}

// Gradient button with glow effect (Variant B)
function GradientButton({ children, onClick, className = '', size = 'default' }: CTAButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`
        relative group overflow-hidden rounded-full shadow-xl 
        ${size === 'sm' ? 'px-4 py-1.5 text-sm' : ''}
        ${size === 'lg' ? 'px-8 py-3.5 text-lg' : ''}
        ${size === 'default' ? 'px-6 py-2.5' : ''}
        font-medium text-white bg-gradient-to-r from-purple-500 via-indigo-500 to-purple-500 
        bg-size-200 bg-pos-0 hover:bg-pos-100 transition-all duration-500
        ${className}
      `}
    >
      <span className="relative z-10 flex items-center justify-center gap-2">
        {children}
        <Sparkles className="h-4 w-4 animate-pulse" />
      </span>
      <span className="absolute inset-0 h-full w-full bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 opacity-0 
             blur-xl group-hover:opacity-70 group-hover:blur-2xl transition-all duration-500" />
    </button>
  );
}

// Minimal, elegant button (Variant C)
function MinimalButton({ children, onClick, className = '', size = 'default' }: CTAButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`
        group relative inline-flex items-center justify-center
        ${size === 'sm' ? 'px-3 py-1 text-sm' : ''}
        ${size === 'lg' ? 'px-6 py-2.5 text-lg' : ''}
        ${size === 'default' ? 'px-4 py-1.5' : ''}
        font-medium tracking-wide text-primary hover:text-primary-foreground
        border-b-2 border-primary hover:border-transparent
        transition-all duration-300 ease-in-out
        ${className}
      `}
    >
      <span className="relative flex items-center gap-1.5">
        {children}
        <ArrowRight className="h-4 w-4 transform group-hover:translate-x-1 transition-transform" />
      </span>
      <span className="absolute bottom-0 left-0 h-0 w-full bg-primary transition-all duration-300 ease-in-out group-hover:h-full -z-10"></span>
    </button>
  );
} 