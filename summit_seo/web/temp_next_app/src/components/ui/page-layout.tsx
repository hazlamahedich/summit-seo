import { cn } from "@/lib/utils";
import React from "react";
import { Container } from "./container";

interface PageLayoutProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  containerSize?: "sm" | "md" | "lg" | "xl" | "full";
  className?: string;
  contentClassName?: string;
  header?: React.ReactNode;
  footer?: React.ReactNode;
}

/**
 * A page layout component that combines container and provides structure
 * for header, main content, and footer areas
 */
export function PageLayout({
  children,
  containerSize = "lg",
  className,
  contentClassName,
  header,
  footer,
  ...props
}: PageLayoutProps) {
  return (
    <div className={cn("min-h-screen flex flex-col", className)} {...props}>
      {header && (
        <header className="w-full">
          <Container size={containerSize}>{header}</Container>
        </header>
      )}
      
      <main className={cn("flex-1", contentClassName)}>
        <Container size={containerSize}>{children}</Container>
      </main>
      
      {footer && (
        <footer className="w-full">
          <Container size={containerSize}>{footer}</Container>
        </footer>
      )}
    </div>
  );
} 