'use client';

import React, { useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ABTest, ABVariant } from "@/components/ab-testing/ab-test";
import { useABTesting } from "@/contexts/ab-testing-context";
import { useToast } from "@/components/ui/use-toast";

// A/B Test experiment ID
const DASHBOARD_WIDGET_STYLE_EXPERIMENT = "dashboard-widget-styles";

/**
 * Component that demonstrates A/B testing with dashboard widgets
 * Tests different visual styles for dashboard cards to see which drives more engagement
 */
export function ABTestingDashboardExample() {
  const { assignUserToExperiment, isUserInExperiment, trackConversion } = useABTesting();
  const { toast } = useToast();

  useEffect(() => {
    // Assign user to experiment when component mounts
    const assignUser = async () => {
      if (!isUserInExperiment(DASHBOARD_WIDGET_STYLE_EXPERIMENT)) {
        await assignUserToExperiment(DASHBOARD_WIDGET_STYLE_EXPERIMENT);
      }
    };
    
    assignUser();
  }, [assignUserToExperiment, isUserInExperiment]);

  const handleInteraction = () => {
    // Track conversion when user interacts with the widget
    trackConversion(DASHBOARD_WIDGET_STYLE_EXPERIMENT);
    
    toast({
      title: "Action recorded!",
      description: "Thanks for your feedback on this widget design.",
    });
  };

  return (
    <ABTest 
      experimentId={DASHBOARD_WIDGET_STYLE_EXPERIMENT}
      onInteraction={() => console.log("Widget viewed")}
    >
      {/* Variant A: Standard design */}
      <ABVariant id="standard-design">
        <Card className="dashboard-widget">
          <CardHeader>
            <CardTitle>Website Performance</CardTitle>
            <CardDescription>Key metrics from the last 30 days</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span>Page Speed</span>
                <span className="font-semibold">2.4s</span>
              </div>
              <div className="flex justify-between items-center">
                <span>Bounce Rate</span>
                <span className="font-semibold">32%</span>
              </div>
              <div className="flex justify-between items-center">
                <span>Conversion Rate</span>
                <span className="font-semibold">4.7%</span>
              </div>
              <Button 
                className="w-full mt-4"
                onClick={handleInteraction}
              >
                View Detailed Report
              </Button>
            </div>
          </CardContent>
        </Card>
      </ABVariant>
      
      {/* Variant B: Visual design with colorful accents */}
      <ABVariant id="visual-design">
        <Card className="dashboard-widget border-t-4 border-t-blue-500 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-blue-50 to-white pb-2">
            <CardTitle className="text-blue-800">Website Performance</CardTitle>
            <CardDescription>Key metrics from the last 30 days</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 pt-2">
              <div className="flex justify-between items-center p-2 rounded bg-blue-50">
                <span className="font-medium">Page Speed</span>
                <span className="font-bold text-blue-700">2.4s</span>
              </div>
              <div className="flex justify-between items-center p-2 rounded bg-green-50">
                <span className="font-medium">Bounce Rate</span>
                <span className="font-bold text-green-700">32%</span>
              </div>
              <div className="flex justify-between items-center p-2 rounded bg-purple-50">
                <span className="font-medium">Conversion Rate</span>
                <span className="font-bold text-purple-700">4.7%</span>
              </div>
              <Button 
                className="w-full mt-4 bg-gradient-to-r from-blue-500 to-blue-700 hover:from-blue-600 hover:to-blue-800"
                onClick={handleInteraction}
              >
                View Detailed Report
              </Button>
            </div>
          </CardContent>
        </Card>
      </ABVariant>
      
      {/* Variant C: Minimalist design with focus on data */}
      <ABVariant id="minimalist-design">
        <Card className="dashboard-widget border-0 shadow-sm">
          <CardHeader className="border-b pb-4">
            <CardTitle className="text-gray-800 text-lg">Website Performance</CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="space-y-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900">2.4s</div>
                <div className="text-sm text-gray-500 mt-1">Page Speed</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900">32%</div>
                <div className="text-sm text-gray-500 mt-1">Bounce Rate</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-900">4.7%</div>
                <div className="text-sm text-gray-500 mt-1">Conversion Rate</div>
              </div>
              <Button 
                variant="outline"
                className="w-full mt-4 border-gray-300"
                onClick={handleInteraction}
              >
                View Detailed Report
              </Button>
            </div>
          </CardContent>
        </Card>
      </ABVariant>
    </ABTest>
  );
} 