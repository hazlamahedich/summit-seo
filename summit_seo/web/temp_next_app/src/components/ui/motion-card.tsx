import React from "react";
import { motion, useMotionTemplate, useMotionValue, MotionStyle, HTMLMotionProps } from "framer-motion";
import { cn } from "@/lib/utils";
import { useReducedMotion } from "@/lib/motion";

interface MotionCardProps extends Omit<HTMLMotionProps<"div">, "style"> {
  children: React.ReactNode;
  variant?: "default" | "gradient" | "spotlight" | "hover-lift";
  intensity?: "subtle" | "medium" | "strong";
  disableHoverEffects?: boolean;
}

// Create a type extension for our custom CSS properties
interface CustomMotionStyle extends MotionStyle {
  "--mouse-x"?: any;
  "--mouse-y"?: any;
  "--card-gradient-color"?: string;
  "--card-gradient-rgb"?: string;
  "--card-spotlight-rgb"?: string;
  "--spotlight-size"?: string;
  background?: string;
}

/**
 * A card component with various motion effects
 * Can be used as a container for various UI elements with enhanced visual feedback
 */
export function MotionCard({
  children,
  className,
  variant = "default",
  intensity = "medium",
  disableHoverEffects = false,
  ...props
}: MotionCardProps) {
  // Check if user prefers reduced motion
  const prefersReducedMotion = useReducedMotion();
  
  // Motion values for tracking mouse position
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  // Gradient and Spotlight effect values
  const gradientOpacity = {
    subtle: 0.2,
    medium: 0.4,
    strong: 0.6,
  };

  const spotlightSize = {
    subtle: 200,
    medium: 300,
    strong: 400,
  };

  const hoverLiftAmount = {
    subtle: 2,
    medium: 4,
    strong: 8,
  };

  // Mouse move handler for tracking position
  function handleMouseMove(e: React.MouseEvent<HTMLDivElement, MouseEvent>) {
    if (disableHoverEffects || prefersReducedMotion) return;
    
    const { currentTarget, clientX, clientY } = e;
    const { left, top } = currentTarget.getBoundingClientRect();
    
    mouseX.set(clientX - left);
    mouseY.set(clientY - top);
  }

  // Get style based on variant
  const getCardStyle = (): CustomMotionStyle => {
    // If user prefers reduced motion, return minimal styling
    if (prefersReducedMotion) {
      return {};
    }
    
    switch (variant) {
      case "gradient":
        return {
          background: "radial-gradient(circle at var(--mouse-x) var(--mouse-y), var(--card-gradient-color) 0%, transparent 70%)",
          "--mouse-x": useMotionTemplate`${mouseX}px`,
          "--mouse-y": useMotionTemplate`${mouseY}px`,
          "--card-gradient-color": `rgba(var(--card-gradient-rgb), ${gradientOpacity[intensity]})`,
        };
      case "spotlight":
        return {
          "--mouse-x": useMotionTemplate`${mouseX}px`,
          "--mouse-y": useMotionTemplate`${mouseY}px`,
          "--spotlight-size": `${spotlightSize[intensity]}px`,
        };
      case "hover-lift":
        return {};
      default:
        return {};
    }
  };

  // Get hover animation based on variant
  const getHoverAnimation = () => {
    if (disableHoverEffects || prefersReducedMotion) return {};

    switch (variant) {
      case "hover-lift":
        return {
          y: -hoverLiftAmount[intensity],
          transition: { type: "spring", stiffness: 300, damping: 25 }
        };
      default:
        return { scale: 1.01 };
    }
  };

  // Get initial animation based on reduced motion preference
  const getInitialAnimation = () => {
    if (prefersReducedMotion) {
      return {
        initial: { opacity: 0 },
        animate: { opacity: 1 },
        transition: { duration: 0.1 }
      };
    }
    
    return {
      initial: { opacity: 0, y: 10 },
      animate: { opacity: 1, y: 0 },
      transition: { duration: 0.3 }
    };
  };

  const baseClasses = "relative overflow-hidden rounded-lg border bg-card text-card-foreground shadow-sm transition-colors";
  
  const variantClasses = {
    default: "",
    gradient: prefersReducedMotion 
      ? "" 
      : "before:absolute before:inset-0 before:opacity-0 before:transition-opacity hover:before:opacity-100 border-0",
    spotlight: prefersReducedMotion
      ? ""
      : "before:pointer-events-none before:absolute before:inset-0 before:opacity-0 before:transition-opacity before:rounded-lg hover:before:opacity-100 before:bg-[radial-gradient(var(--spotlight-size)_circle_at_var(--mouse-x)_var(--mouse-y),rgba(var(--card-spotlight-rgb),0.15),transparent_80%)]",
    "hover-lift": "",
  };

  // Combine all style properties
  const cardStyle: CustomMotionStyle = {
    ...getCardStyle(),
    "--card-gradient-rgb": "var(--primary-rgb)",
    "--card-spotlight-rgb": "var(--primary-rgb)",
  };
  
  const { initial, animate, transition } = getInitialAnimation();

  return (
    <motion.div
      className={cn(
        baseClasses,
        variantClasses[variant],
        className
      )}
      style={cardStyle}
      onMouseMove={handleMouseMove}
      whileHover={getHoverAnimation()}
      initial={initial}
      animate={animate}
      transition={transition}
      {...props}
    >
      {children}
    </motion.div>
  );
} 