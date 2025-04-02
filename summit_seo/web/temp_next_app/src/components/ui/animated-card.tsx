"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"
import { cardHoverVariants } from "@/lib/animation-utils"
import { useReducedMotion } from "@/lib/motion"

type AnimatedCardVariant = "default" | "interactive" | "highlight"

interface AnimatedCardProps {
  children: React.ReactNode
  className?: string
  animated?: boolean
  variant?: AnimatedCardVariant
  onClick?: () => void
}

export function AnimatedCard({
  className,
  children,
  animated = true,
  variant = "default",
  onClick,
}: AnimatedCardProps) {
  const prefersReducedMotion = useReducedMotion()
  
  // Different variants have different animation intensities
  const getVariantStyles = (variant: AnimatedCardVariant) => {
    switch(variant) {
      case "interactive":
        return "hover:border-primary/50 cursor-pointer"
      case "highlight":
        return "border-primary/30 hover:border-primary"
      default:
        return "hover:border-border/80"
    }
  }
  
  const cardClasses = cn(
    "rounded-lg border bg-card p-6 text-card-foreground shadow",
    getVariantStyles(variant),
    className
  )
  
  if (!animated || prefersReducedMotion) {
    return (
      <div 
        className={cn(cardClasses, "transition-colors duration-200")} 
        onClick={onClick}
      >
        {children}
      </div>
    )
  }
  
  return (
    <motion.div
      className={cardClasses}
      initial="initial"
      whileHover="hover"
      variants={cardHoverVariants}
      onClick={onClick}
    >
      {children}
    </motion.div>
  )
} 