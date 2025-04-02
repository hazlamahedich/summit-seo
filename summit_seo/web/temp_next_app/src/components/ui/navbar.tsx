"use client";

import React, { ReactNode, useCallback, memo } from "react";
import { cn } from "@/lib/utils";
import { MobileNav } from "./mobile-nav";
import { useResponsive } from "@/contexts/responsive-context";
import { KeymapButton } from "./keymap-button";
import { useKeyboardShortcutsContext } from "@/contexts/keyboard-shortcuts-context";

interface NavbarProps {
  logo?: ReactNode;
  children?: ReactNode;
  sticky?: boolean;
  transparent?: boolean;
  className?: string;
  /**
   * Controls visibility of menu items directly in navbar
   * When hidden, all items are only visible in mobile menu
   */
  showMenuItems?: boolean;
  /**
   * Whether to show the keyboard shortcuts button in the navbar
   */
  showKeyboardShortcuts?: boolean;
}

// Type for child elements with extended props
interface ChildProps {
  isGroup?: boolean;
  label?: string;
  icon?: ReactNode;
  children?: React.ReactNode;
  asChild?: boolean;
  href?: string;
}

/**
 * Responsive navigation bar with desktop and mobile views
 */
export const Navbar = memo(({
  logo,
  children,
  sticky = false,
  transparent = false,
  className,
  showMenuItems = true,
  showKeyboardShortcuts = true,
}: NavbarProps) => {
  const { isMobile, isTablet } = useResponsive();
  const { toggleShortcutsHelp } = useKeyboardShortcutsContext();
  const shouldShowMobileNav = isMobile || isTablet;
  
  // Safe shortcut toggle handler with event prevention
  const handleToggleShortcuts = useCallback((event?: React.MouseEvent) => {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    toggleShortcutsHelp();
  }, [toggleShortcutsHelp]);
  
  // Memoize the mobile nav items to prevent unnecessary recalculations
  const mobileNavItems = React.useMemo(() => {
    return React.Children.map(children, (child) => {
      if (!React.isValidElement(child)) return null;
      
      // Safe type assertion
      const childProps = child.props as ChildProps;
      
      // Handle Link wrapped in Button
      if (childProps.asChild && childProps.children) {
        // Try to access the link child
        const linkChild = childProps.children as React.ReactElement;
        if (React.isValidElement(linkChild)) {
          const linkProps = linkChild.props as { href?: string; children?: ReactNode };
          if (linkProps.href) {
            return (
              <MobileNav.Item href={linkProps.href}>
                {linkProps.children}
              </MobileNav.Item>
            );
          }
        }
      }
      
      // If it's a group, we'll create a mobile nav group
      if (childProps.isGroup && childProps.label) {
        return (
          <MobileNav.Group 
            label={childProps.label} 
            icon={childProps.icon}
          >
            {childProps.children}
          </MobileNav.Group>
        );
      }
      
      // Return the child as is for other components
      return child;
    });
  }, [children]);
  
  return (
    <nav
      className={cn(
        "w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60",
        sticky && "sticky top-0 z-40",
        transparent && "bg-transparent backdrop-blur-none supports-[backdrop-filter]:bg-transparent border-transparent",
        className
      )}
    >
      <div className="container flex h-16 items-center justify-between px-4 md:px-6">
        {/* Logo */}
        <div className="flex items-center">
          {logo}
        </div>

        {/* Desktop Navigation - hidden on mobile */}
        {showMenuItems && !shouldShowMobileNav && (
          <div className="hidden gap-6 md:flex items-center">
            {children}
            {showKeyboardShortcuts && <KeymapButton className="ml-2" />}
          </div>
        )}

        {/* Mobile Navigation - shown only on mobile */}
        <div className="flex items-center gap-2">
          {showKeyboardShortcuts && shouldShowMobileNav && (
            <KeymapButton className="mr-1" />
          )}
          <MobileNav logo={logo}>
            {mobileNavItems}
            <MobileNav.Item 
              href="#keyboard-shortcuts" 
              onClick={handleToggleShortcuts}
            >
              Keyboard Shortcuts
            </MobileNav.Item>
          </MobileNav>
        </div>
      </div>
    </nav>
  );
});

Navbar.displayName = 'Navbar'; 