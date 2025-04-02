import { cn } from "@/lib/utils";
import React, { ReactNode } from "react";
import { SidebarLayout } from "./sidebar-layout";
import { PageLayout } from "./page-layout";
import { Navbar } from "./navbar";
import { Footer } from "./footer";

export interface DashboardLayoutProps {
  children: ReactNode;
  sidebar: ReactNode;
  sidebarPosition?: "left" | "right";
  sidebarWidth?: string;
  mobileSidebarWidth?: string;
  header?: ReactNode;
  headerLogo?: ReactNode;
  navigation?: ReactNode;
  footer?: ReactNode;
  footerLogo?: ReactNode;
  footerContent?: ReactNode;
  className?: string;
  contentClassName?: string;
  containerSize?: "sm" | "md" | "lg" | "xl" | "full";
  stickyHeader?: boolean;
  transparentHeader?: boolean;
}

/**
 * A comprehensive dashboard layout that combines sidebar, header, footer, and content areas
 * with responsive behavior for all screen sizes.
 */
export function DashboardLayout({
  children,
  sidebar,
  sidebarPosition = "left",
  sidebarWidth = "w-64",
  mobileSidebarWidth = "w-3/4",
  header,
  headerLogo,
  navigation,
  footer,
  footerLogo,
  footerContent,
  className,
  contentClassName,
  containerSize = "full",
  stickyHeader = true,
  transparentHeader = false,
}: DashboardLayoutProps) {
  // Create default header if none provided
  const headerContent = header || (
    <Navbar 
      logo={headerLogo} 
      sticky={stickyHeader} 
      transparent={transparentHeader}
    >
      {navigation}
    </Navbar>
  );

  // Create default footer if none provided
  const renderedFooter = footer || (
    <Footer logo={footerLogo}>
      {footerContent}
    </Footer>
  );

  return (
    <SidebarLayout
      sidebar={sidebar}
      sidebarPosition={sidebarPosition}
      sidebarWidth={sidebarWidth}
      mobileSidebarWidth={mobileSidebarWidth}
      className={cn("min-h-screen", className)}
    >
      <PageLayout
        header={headerContent}
        footer={renderedFooter}
        containerSize={containerSize}
        contentClassName={cn("p-4 md:p-6", contentClassName)}
      >
        {children}
      </PageLayout>
    </SidebarLayout>
  );
} 