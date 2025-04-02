import { cn } from "@/lib/utils";
import React, { useState } from "react";
import { Button } from "./button";
import { Menu, X } from "lucide-react";

interface SidebarLayoutProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  sidebar: React.ReactNode;
  sidebarWidth?: string;
  mobileSidebarWidth?: string;
  sidebarPosition?: "left" | "right";
  collapsible?: boolean;
}

/**
 * A sidebar layout component with optional collapsible behavior on mobile
 */
export function SidebarLayout({
  children,
  sidebar,
  sidebarWidth = "w-64",
  mobileSidebarWidth = "w-3/4",
  sidebarPosition = "left",
  collapsible = true,
  className,
  ...props
}: SidebarLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
  const closeSidebar = () => setSidebarOpen(false);

  const isRight = sidebarPosition === "right";

  return (
    <div
      className={cn("relative min-h-screen flex flex-col md:flex-row", className)}
      {...props}
    >
      {/* Mobile sidebar toggle button */}
      {collapsible && (
        <Button
          variant="outline"
          size="icon"
          className="fixed top-4 z-40 md:hidden"
          style={{ [isRight ? "right" : "left"]: "1rem" }}
          onClick={toggleSidebar}
        >
          <Menu className="h-4 w-4" />
          <span className="sr-only">Toggle sidebar</span>
        </Button>
      )}

      {/* Overlay for mobile sidebar */}
      {sidebarOpen && collapsible && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={closeSidebar}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed h-full z-40 transition-transform duration-300 ease-in-out bg-background border-r",
          sidebarWidth,
          isRight ? "right-0 border-l border-r-0" : "left-0",
          {
            "translate-x-0": sidebarOpen,
            [`${isRight ? "translate-x-full" : "-translate-x-full"}`]: !sidebarOpen,
          },
          "md:sticky md:top-0 md:translate-x-0",
          mobileSidebarWidth,
          "md:" + sidebarWidth
        )}
      >
        {collapsible && (
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-4 right-4 md:hidden"
            onClick={closeSidebar}
          >
            <X className="h-4 w-4" />
            <span className="sr-only">Close sidebar</span>
          </Button>
        )}

        <div className="h-full overflow-y-auto p-4">{sidebar}</div>
      </aside>

      {/* Main content */}
      <main
        className={cn(
          "flex-1",
          collapsible ? "pt-16 md:pt-0" : "",
          isRight ? "order-first" : "order-last"
        )}
      >
        {children}
      </main>
    </div>
  );
} 