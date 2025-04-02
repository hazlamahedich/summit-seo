import { cn } from "@/lib/utils";
import React from "react";

interface SectionProps extends React.HTMLAttributes<HTMLElement> {
  children: React.ReactNode;
  size?: "sm" | "md" | "lg" | "xl" | "none";
  className?: string;
}

/**
 * A section component that provides consistent vertical spacing
 */
export function Section({
  children,
  className,
  size = "md",
  ...props
}: SectionProps) {
  const sizeClasses = {
    none: "",
    sm: "py-4 md:py-6",
    md: "py-6 md:py-10",
    lg: "py-10 md:py-16",
    xl: "py-16 md:py-24",
  };
  
  return (
    <section className={cn(sizeClasses[size], className)} {...props}>
      {children}
    </section>
  );
} 