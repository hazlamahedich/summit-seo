"use client"

import * as React from "react"
import { motion } from "framer-motion"
import { Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { buttonHoverVariants, buttonLoadingVariants } from "@/lib/animation-utils"
import { cn } from "@/lib/utils"
import { useReducedMotion } from "@/lib/motion"

interface AnimatedButtonProps extends React.ComponentProps<typeof Button> {
  loading?: boolean
  loadingText?: string
  animated?: boolean
  feedback?: "success" | "error" | "none"
  icon?: React.ReactNode
  iconPosition?: "left" | "right"
}

export const AnimatedButton = React.forwardRef<
  HTMLButtonElement,
  AnimatedButtonProps
>(({
  className,
  variant = "default",
  size = "default",
  loading = false,
  loadingText = "Loading...",
  animated = true,
  feedback = "none",
  icon,
  iconPosition = "left",
  onClick,
  children,
  disabled,
  ...props
}, ref) => {
  const [feedbackState, setFeedbackState] = React.useState<"success" | "error" | "none">("none")
  const prefersReducedMotion = useReducedMotion()
  
  // Apply feedback and then reset
  React.useEffect(() => {
    if (feedback !== "none") {
      setFeedbackState(feedback)
      const timer = setTimeout(() => {
        setFeedbackState("none")
      }, 1500)
      return () => clearTimeout(timer)
    }
  }, [feedback])
  
  // Handle click with feedback animation
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (onClick) {
      onClick(e)
    }
  }
  
  // Set feedback style
  const getFeedbackStyle = () => {
    if (feedbackState === "success") {
      return "bg-green-500 text-white border-green-600 hover:bg-green-600"
    } else if (feedbackState === "error") {
      return "bg-red-500 text-white border-red-600 hover:bg-red-600"
    }
    return ""
  }
  
  return (
    <motion.div
      initial="initial"
      whileHover={animated && !disabled && !loading ? "hover" : "initial"}
      whileTap={animated && !disabled && !loading ? "tap" : "initial"}
      variants={prefersReducedMotion ? {} : buttonHoverVariants}
      className="inline-block"
    >
      <Button
        ref={ref}
        variant={variant}
        size={size}
        className={cn(
          "relative overflow-hidden transition-all",
          loading && "pointer-events-none",
          feedbackState !== "none" && getFeedbackStyle(),
          className
        )}
        onClick={handleClick}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <motion.span 
            className="absolute inset-0 flex items-center justify-center bg-inherit"
            initial="initial"
            animate="animate"
            variants={prefersReducedMotion ? {} : buttonLoadingVariants}
          >
            <Loader2 className="h-4 w-4 mr-2" />
            {loadingText}
          </motion.span>
        )}
        
        <span className={cn(
          "flex items-center gap-2",
          loading && "opacity-0",
          iconPosition === "right" ? "flex-row-reverse" : "flex-row"
        )}>
          {icon && (
            <motion.span
              animate={animated && !disabled ? { scale: [1, 1.2, 1] } : {}}
              transition={{ duration: 0.3 }}
            >
              {icon}
            </motion.span>
          )}
          {children}
        </span>
      </Button>
    </motion.div>
  )
})

AnimatedButton.displayName = "AnimatedButton" 