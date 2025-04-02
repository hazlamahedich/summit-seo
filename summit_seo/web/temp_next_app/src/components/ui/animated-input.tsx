"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { AlertCircle, CheckCircle2 } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { formErrorShakeVariants, formFieldFocusVariants } from "@/lib/animation-utils"
import { cn } from "@/lib/utils"
import { useReducedMotion } from "@/lib/motion"

interface AnimatedInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  success?: boolean
  hint?: string
  animated?: boolean
  icon?: React.ReactNode
  iconPosition?: "left" | "right"
}

export const AnimatedInput = React.forwardRef<HTMLInputElement, AnimatedInputProps>(
  ({ 
    className,
    label,
    error,
    success,
    hint,
    animated = true,
    icon,
    iconPosition = "left",
    id,
    ...props
  }, ref) => {
    const inputId = id || React.useId()
    const [hasFocus, setHasFocus] = React.useState(false)
    const [hasError, setHasError] = React.useState(false)
    const prefersReducedMotion = useReducedMotion()
    
    // Handle error animation
    React.useEffect(() => {
      if (error) {
        setHasError(true)
        const timer = setTimeout(() => {
          setHasError(false)
        }, 1000)
        return () => clearTimeout(timer)
      }
    }, [error])
    
    return (
      <div className="space-y-2 w-full">
        {label && (
          <Label 
            htmlFor={inputId} 
            className={cn(
              "transition-colors duration-200",
              hasFocus && "text-primary",
              error && "text-destructive"
            )}
          >
            {label}
          </Label>
        )}
        
        <motion.div
          initial="initial"
          animate={hasError ? "animate" : "initial"}
          variants={animated && !prefersReducedMotion ? formErrorShakeVariants : {}}
          className="relative"
        >
          <motion.div
            initial="initial"
            animate={hasFocus ? "focus" : "initial"}
            variants={animated && !prefersReducedMotion ? formFieldFocusVariants : {}}
            className={cn(
              "rounded-md",
              error && "ring-2 ring-destructive ring-offset-1",
              success && "ring-2 ring-green-500 ring-offset-1"
            )}
          >
            <div className="relative">
              {icon && iconPosition === "left" && (
                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                  {icon}
                </div>
              )}
              
              <Input
                id={inputId}
                ref={ref}
                onFocus={() => setHasFocus(true)}
                onBlur={() => setHasFocus(false)}
                className={cn(
                  "transition-all duration-200",
                  icon && iconPosition === "left" && "pl-10",
                  icon && iconPosition === "right" && "pr-10",
                  error && "border-destructive",
                  success && "border-green-500",
                  className
                )}
                aria-invalid={error ? "true" : "false"}
                {...props}
              />
              
              {icon && iconPosition === "right" && !error && !success && (
                <div className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
                  {icon}
                </div>
              )}
              
              <AnimatePresence>
                {error && (
                  <motion.div
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-destructive"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    transition={{ duration: 0.2 }}
                  >
                    <AlertCircle className="h-4 w-4" />
                  </motion.div>
                )}
                
                {success && !error && (
                  <motion.div
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-green-500"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    transition={{ duration: 0.2 }}
                  >
                    <CheckCircle2 className="h-4 w-4" />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        </motion.div>
        
        <AnimatePresence>
          {error && (
            <motion.p
              className="text-sm font-medium text-destructive mt-1"
              initial={{ opacity: 0, height: 0, marginTop: 0 }}
              animate={{ opacity: 1, height: "auto", marginTop: 4 }}
              exit={{ opacity: 0, height: 0, marginTop: 0 }}
              transition={{ duration: 0.2 }}
            >
              {error}
            </motion.p>
          )}
          
          {hint && !error && (
            <motion.p
              className="text-sm text-muted-foreground mt-1"
              initial={{ opacity: 0, height: 0, marginTop: 0 }}
              animate={{ opacity: 1, height: "auto", marginTop: 4 }}
              exit={{ opacity: 0, height: 0, marginTop: 0 }}
              transition={{ duration: 0.2 }}
            >
              {hint}
            </motion.p>
          )}
        </AnimatePresence>
      </div>
    )
  }
)

AnimatedInput.displayName = "AnimatedInput" 