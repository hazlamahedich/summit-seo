import { cn } from "@/lib/utils";
import React, { useState } from "react";
import Link from "next/link";
import { Button } from "./button";
import { ChevronDown, ChevronRight, Home, LineChart, Settings, Users, FolderSearch, Briefcase, BarChart2, FileSearch, ListChecks, FileText, Lightbulb, Sparkles } from "lucide-react";

export interface NavItem {
  title: string;
  href: string;
  icon?: React.ReactNode;
  isActive?: boolean;
}

export interface NavGroup {
  title: string;
  icon?: React.ReactNode;
  items: NavItem[];
  defaultOpen?: boolean;
}

export interface DashboardSidebarProps extends React.HTMLAttributes<HTMLDivElement> {
  logo?: React.ReactNode;
  groups?: NavGroup[];
  items?: NavItem[];
  footer?: React.ReactNode;
}

/**
 * A responsive sidebar component for dashboards with collapsible navigation groups
 */
export function DashboardSidebar({
  logo,
  groups = [],
  items = [],
  footer,
  className,
  ...props
}: DashboardSidebarProps) {
  return (
    <div className={cn("h-full flex flex-col", className)} {...props}>
      {/* Sidebar Header with Logo */}
      {logo && (
        <div className="h-16 flex items-center px-4 border-b">
          {logo}
        </div>
      )}

      {/* Main Navigation */}
      <div className="flex-1 overflow-y-auto py-4">
        {/* Standalone Navigation Items */}
        {items.length > 0 && (
          <div className="px-3 mb-6">
            {items.map((item, index) => (
              <NavLink
                key={index}
                title={item.title}
                href={item.href}
                icon={item.icon}
                isActive={item.isActive}
              />
            ))}
          </div>
        )}

        {/* Navigation Groups */}
        {groups.map((group, index) => (
          <NavGroup
            key={index}
            title={group.title}
            icon={group.icon}
            items={group.items}
            defaultOpen={group.defaultOpen}
          />
        ))}
      </div>

      {/* Sidebar Footer */}
      {footer && (
        <div className="mt-auto p-4 border-t">
          {footer}
        </div>
      )}
    </div>
  );
}

/* Navigation Group Component */
function NavGroup({ title, icon, items, defaultOpen = false }: NavGroup) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const toggleGroup = () => setIsOpen(!isOpen);

  return (
    <div className="mb-4">
      <button
        onClick={toggleGroup}
        className={cn(
          "w-full flex items-center justify-between px-3 py-2 text-sm font-medium",
          "hover:bg-accent rounded-md transition-colors"
        )}
      >
        <div className="flex items-center">
          {icon && <span className="mr-2">{icon}</span>}
          <span>{title}</span>
        </div>
        {isOpen ? (
          <ChevronDown className="h-4 w-4" />
        ) : (
          <ChevronRight className="h-4 w-4" />
        )}
      </button>

      {isOpen && (
        <div className="mt-1 pl-8 pr-2 space-y-1">
          {items.map((item, index) => (
            <NavLink
              key={index}
              title={item.title}
              href={item.href}
              icon={item.icon}
              isActive={item.isActive}
              compact
            />
          ))}
        </div>
      )}
    </div>
  );
}

/* Individual Navigation Link */
interface NavLinkProps extends NavItem {
  compact?: boolean;
}

function NavLink({ title, href, icon, isActive, compact }: NavLinkProps) {
  return (
    <Link 
      href={href}
      className={cn(
        "flex items-center py-2 px-3 rounded-md text-sm",
        isActive 
          ? "bg-accent text-accent-foreground font-medium"
          : "text-muted-foreground hover:text-foreground hover:bg-accent/50",
        compact ? "py-1" : ""
      )}
    >
      {icon && <span className={cn("mr-2", compact ? "h-4 w-4" : "h-5 w-5")}>{icon}</span>}
      <span>{title}</span>
    </Link>
  );
}

// Default sidebar with predefined navigation groups for easy implementation
export function DefaultDashboardSidebar({ logo, footer, className }: Omit<DashboardSidebarProps, 'groups' | 'items'>) {
  // Dashboard links
  const dashboardLinks = [
    { name: "Dashboard", href: "/dashboard", icon: <Home className="h-5 w-5" /> },
    { name: "Projects", href: "/dashboard/projects", icon: <Briefcase className="h-5 w-5" /> },
    { name: "Analyses", href: "/dashboard/analyses", icon: <BarChart2 className="h-5 w-5" /> },
    { name: "Findings", href: "/dashboard/findings", icon: <FileSearch className="h-5 w-5" /> },
    { name: "Recommendations", href: "/dashboard/recommendations", icon: <ListChecks className="h-5 w-5" /> },
    { name: "Engagement", href: "/dashboard/engagement", icon: <Users className="h-5 w-5" /> },
    { name: "Data Visualization", href: "/dashboard/data-visualization", icon: <LineChart className="h-5 w-5" /> },
    { name: "Reports", href: "/dashboard/reports", icon: <FileText className="h-5 w-5" /> },
    { name: "Settings", href: "/dashboard/settings", icon: <Settings className="h-5 w-5" /> },
  ];

  // Examples section
  const examplesGroup: NavGroup = {
    title: "Examples",
    icon: <Lightbulb className="h-5 w-5" />,
    items: [
      { title: "Ambient Backgrounds", href: "/examples/ambient-backgrounds", icon: <Sparkles className="h-4 w-4" /> },
    ],
    defaultOpen: false
  };

  // Convert dashboard links to NavItem format
  const navItems: NavItem[] = dashboardLinks.map(link => ({
    title: link.name,
    href: link.href,
    icon: link.icon
  }));

  return (
    <DashboardSidebar
      logo={logo}
      items={navItems}
      groups={[examplesGroup]}
      footer={footer}
      className={className}
    />
  );
} 