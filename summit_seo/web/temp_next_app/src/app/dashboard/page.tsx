"use client";

import { useEffect, useState } from "react";
import { DefaultDashboardSidebar } from "@/components/ui/dashboard-sidebar";
import { DashboardLayout } from "@/components/ui/dashboard-layout";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { APP_TOURS } from "@/lib/tour-config";
import { CustomizableDashboard } from "@/components/dashboard/customizable-dashboard";
import { ABTestingDashboardExample } from "@/components/dashboard/ab-testing-example";
import { FeatureDiscovery } from "@/components/ui/feature-discovery";

export default function DashboardPage() {
  const [tourActive, setTourActive] = useState(false);
  
  // Logo imports and navigation setup
  const logo = '/images/logo.svg';
  
  const dashboardTour = {
    id: APP_TOURS.DASHBOARD_FEATURES,
    steps: [
      // Tour steps definition
    ],
  };
  
  // Function to end the tour
  const endTour = (tourId: string) => {
    localStorage.setItem(`tour-${tourId}-completed`, "true");
  };
  
  // Sidebar footer component
  const sidebarFooter = (
    <div className="flex flex-col gap-4 px-4">
      <Link href="/settings">
        <Button variant="outline" className="w-full">Settings</Button>
      </Link>
      <Link href="/help">
        <Button variant="outline" className="w-full">Help & Support</Button>
      </Link>
    </div>
  );
  
  // Navigation items
  const navigation = [
    // Navigation items definition
  ];

  useEffect(() => {
    // Check if tour was completed before
    const tourCompleted = localStorage.getItem(`tour-${dashboardTour.id}-completed`);
    if (!tourCompleted) {
      setTourActive(true);
    }
  }, []);

  return (
    <>
      <DashboardLayout
        headerLogo={logo}
        navigation={navigation}
        sidebar={<DefaultDashboardSidebar logo={logo} footer={sidebarFooter} className="sidebar-navigation" />}
        containerSize="xl"
        contentClassName="py-6"
      >
        {/* Customizable dashboard with widgets */}
        <CustomizableDashboard />
        
        {/* A/B Testing Example Widget */}
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Performance Metrics (A/B Test)</h2>
          <ABTestingDashboardExample />
        </div>
      </DashboardLayout>
      
      {/* Feature Discovery Tour */}
      <FeatureDiscovery 
        tour={dashboardTour}
        isOpen={tourActive}
        onClose={() => {
          setTourActive(false);
          endTour(dashboardTour.id);
        }}
      />
    </>
  );
} 