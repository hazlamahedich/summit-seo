import React, { ReactNode } from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { useReducedMotion } from '@/lib/motion';
import { cn } from '@/lib/utils';
import { 
  formFieldFocus, 
  authButtonAnimation, 
  authLinkAnimation, 
  successAnimation, 
  errorAnimation
} from '@/lib/motion';
import Link from 'next/link';

// Animated Input Component
interface AnimatedInputProps extends Omit<HTMLMotionProps<"input">, "children"> {
  className?: string;
}

export const AnimatedInput = ({ className, ...props }: AnimatedInputProps) => {
  const prefersReducedMotion = useReducedMotion();
  
  return (
    <motion.input
      className={cn(
        "w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary",
        className
      )}
      {...formFieldFocus(prefersReducedMotion || false)}
      {...props}
    />
  );
};

// Animated Form Field Container
interface AnimatedFormFieldProps {
  children: ReactNode;
  className?: string;
  delay?: number;
}

export const AnimatedFormField = ({ 
  children, 
  className,
  delay = 0 
}: AnimatedFormFieldProps) => {
  const prefersReducedMotion = useReducedMotion();
  
  return (
    <motion.div
      className={cn("space-y-2", className)}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        delay: prefersReducedMotion ? 0 : delay,
        duration: prefersReducedMotion ? 0.1 : 0.3,
        ease: "easeOut"
      }}
    >
      {children}
    </motion.div>
  );
};

// Animated Label
interface AnimatedLabelProps extends Omit<HTMLMotionProps<"label">, "whileHover"> {
  className?: string;
}

export const AnimatedLabel = ({ children, className, ...props }: AnimatedLabelProps) => {
  return (
    <motion.label
      className={cn("block text-sm font-medium", className)}
      whileHover={{ color: "rgb(var(--primary))" }}
      {...props}
    >
      {children}
    </motion.label>
  );
};

// Animated Error Message
interface AnimatedErrorProps {
  message: string | null;
  className?: string;
}

export const AnimatedError = ({ message, className }: AnimatedErrorProps) => {
  const prefersReducedMotion = useReducedMotion();
  
  if (!message) return null;
  
  return (
    <motion.div 
      className={cn("bg-destructive/15 text-destructive p-4 rounded-md", className)}
      variants={errorAnimation(prefersReducedMotion || false)}
      initial="hidden"
      animate="visible"
    >
      <p>{message}</p>
    </motion.div>
  );
};

// Animated Success Message
interface AnimatedSuccessProps {
  message: string | null;
  className?: string;
}

export const AnimatedSuccess = ({ message, className }: AnimatedSuccessProps) => {
  const prefersReducedMotion = useReducedMotion();
  
  if (!message) return null;
  
  return (
    <motion.div 
      className={cn("bg-success/15 text-success p-4 rounded-md", className)}
      variants={successAnimation(prefersReducedMotion || false)}
      initial="hidden"
      animate="visible"
    >
      <p>{message}</p>
    </motion.div>
  );
};

// Animated Form Link
interface AnimatedFormLinkProps {
  href: string;
  children: ReactNode;
  className?: string;
}

export const AnimatedFormLink = ({ href, children, className }: AnimatedFormLinkProps) => {
  const prefersReducedMotion = useReducedMotion();
  
  return (
    <Link href={href} passHref>
      <motion.a
        className={cn("text-primary hover:underline", className)}
        {...authLinkAnimation(prefersReducedMotion || false)}
      >
        {children}
      </motion.a>
    </Link>
  );
};

// Animated Button Wrapper
interface AnimatedButtonWrapperProps {
  children: ReactNode;
  className?: string;
}

export const AnimatedButtonWrapper = ({ children, className }: AnimatedButtonWrapperProps) => {
  const prefersReducedMotion = useReducedMotion();
  
  return (
    <motion.div
      className={cn(className)}
      {...authButtonAnimation(prefersReducedMotion || false)}
    >
      {children}
    </motion.div>
  );
};

// Loading Spinner
export const LoadingSpinner = () => {
  return (
    <motion.div
      className="h-4 w-4 border-2 border-current border-t-transparent rounded-full"
      animate={{ rotate: 360 }}
      transition={{
        duration: 1,
        repeat: Infinity,
        ease: "linear"
      }}
    />
  );
};

// Form Section with staggered children animation
interface FormSectionProps {
  children: ReactNode;
  className?: string;
}

export const FormSection = ({ children, className }: FormSectionProps) => {
  const prefersReducedMotion = useReducedMotion();
  
  return (
    <motion.div
      className={cn("space-y-4", className)}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{
        duration: prefersReducedMotion ? 0.1 : 0.3,
        staggerChildren: prefersReducedMotion ? 0 : 0.1
      }}
    >
      {children}
    </motion.div>
  );
}; 