"use client";

import React, { useState } from "react";
import { Sheet, SheetTrigger, SheetContent, SheetClose } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { Menu, X, ChevronDown, ChevronRight } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

interface MobileNavProps extends React.HTMLAttributes<HTMLDivElement> {
  logo?: React.ReactNode;
  showCloseButton?: boolean;
  children?: React.ReactNode;
}

interface NavItemProps {
  href: string;
  children: React.ReactNode;
  className?: string;
  activeClassName?: string;
  icon?: React.ReactNode;
  onClick?: (event?: React.MouseEvent<HTMLAnchorElement>) => void;
}

interface NavGroupProps {
  label: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

/**
 * Mobile navigation component that displays a burger menu and a slide-in sheet
 */
export function MobileNav({
  logo,
  showCloseButton = true,
  children,
  className,
  ...props
}: MobileNavProps) {
  return (
    <div className={cn("block md:hidden", className)} {...props}>
      <Sheet>
        <SheetTrigger asChild>
          <Button size="icon" variant="ghost" className="md:hidden">
            <Menu className="h-5 w-5" />
            <span className="sr-only">Open menu</span>
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-[80vw] max-w-sm p-0">
          <div className="flex flex-col h-full">
            <div className="flex items-center justify-between border-b p-4">
              {logo && <div className="flex-1">{logo}</div>}
              {showCloseButton && (
                <SheetClose asChild>
                  <Button variant="ghost" size="icon" className="rounded-full">
                    <X className="h-5 w-5" />
                    <span className="sr-only">Close menu</span>
                  </Button>
                </SheetClose>
              )}
            </div>
            <div className="flex-1 overflow-auto py-2">
              {children}
            </div>
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}

/**
 * Single navigation item for mobile
 */
export function MobileNavItem({
  href,
  children,
  className,
  activeClassName = "bg-accent",
  icon,
  onClick,
}: NavItemProps) {
  const pathname = usePathname();
  const isActive = pathname === href;

  return (
    <SheetClose asChild>
      <Link
        href={href}
        className={cn(
          "flex items-center gap-2 px-4 py-3 transition-colors",
          isActive && activeClassName,
          className
        )}
        onClick={onClick}
      >
        {icon && <span className="text-muted-foreground">{icon}</span>}
        <span>{children}</span>
      </Link>
    </SheetClose>
  );
}

/**
 * Grouped navigation items with collapsible section
 */
export function MobileNavGroup({
  label,
  icon,
  children,
  className,
}: NavGroupProps) {
  const [open, setOpen] = useState(false);

  const toggleOpen = () => setOpen(!open);

  return (
    <div className={className}>
      <button
        onClick={toggleOpen}
        className="flex w-full items-center justify-between px-4 py-3 text-left"
      >
        <div className="flex items-center gap-2">
          {icon && <span className="text-muted-foreground">{icon}</span>}
          <span>{label}</span>
        </div>
        <ChevronDown
          className={cn(
            "h-4 w-4 text-muted-foreground transition-transform duration-200",
            open && "rotate-180"
          )}
        />
      </button>
      {open && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="overflow-hidden pl-6"
        >
          {children}
        </motion.div>
      )}
    </div>
  );
}

// Export the mobile navigation components
MobileNav.Item = MobileNavItem;
MobileNav.Group = MobileNavGroup; 