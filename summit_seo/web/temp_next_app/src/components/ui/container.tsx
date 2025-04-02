import { cn } from "@/lib/utils";
import React from "react";

interface ContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  as?: React.ElementType;
  size?: "sm" | "md" | "lg" | "xl" | "full";
}

/**
 * A responsive container component that centers content with appropriate max-width
 * and horizontal padding for different screen sizes.
 */
export function Container({ 
  children, 
  className, 
  as: Component = "div", 
  size = "lg", 
  ...props 
}: ContainerProps) {
  return (
    <Component
      className={cn(
        "mx-auto px-4 sm:px-6 lg:px-8",
        {
          "max-w-screen-sm": size === "sm",
          "max-w-screen-md": size === "md",
          "max-w-screen-lg": size === "lg",
          "max-w-screen-xl": size === "xl",
          "max-w-none": size === "full",
        },
        className
      )}
      {...props}
    >
      {children}
    </Component>
  );
} 