'use client';

import { useState } from 'react';
import { DashboardWidgetExperiment } from '@/components/ab-testing/dashboard-widget-experiment';
import { CTAButtonExperiment } from '@/components/ab-testing/cta-button-experiment';
import { ABTestAdminDashboard } from '@/components/ab-testing/ab-test-admin-dashboard';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { Separator } from '@/components/ui/separator';
import { Card, CardContent } from '@/components/ui/card';

export default function ABTestingExamplePage() {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('widget');
  
  // Sample data for dashboard widgets
  const sampleData = [
    { name: 'Jan', value: 400 },
    { name: 'Feb', value: 300 },
    { name: 'Mar', value: 600 },
    { name: 'Apr', value: 800 },
    { name: 'May', value: 500 },
    { name: 'Jun', value: 900 },
  ];
  
  const handleWidgetAction = () => {
    toast({
      title: 'Widget Action',
      description: 'You clicked on the widget action button',
    });
  };
  
  const handleCtaClick = () => {
    toast({
      title: 'CTA Button',
      description: 'You clicked on the CTA button',
    });
  };
  
  return (
    <div className="container py-10">
      <h1 className="text-4xl font-bold mb-2">A/B Testing Examples</h1>
      <p className="text-muted-foreground mb-8">
        This page demonstrates A/B testing capabilities in Summit SEO.
      </p>
      
      <Tabs defaultValue="widget" onValueChange={setActiveTab} className="w-full">
        <TabsList className="mb-8">
          <TabsTrigger value="widget">Dashboard Widget Test</TabsTrigger>
          <TabsTrigger value="cta">CTA Button Test</TabsTrigger>
          <TabsTrigger value="admin">Admin Dashboard</TabsTrigger>
        </TabsList>
        
        <TabsContent value="widget" className="space-y-8">
          <div>
            <h2 className="text-2xl font-bold mb-4">Dashboard Widget A/B Test</h2>
            <p className="text-muted-foreground mb-6">
              This widget is being A/B tested with three different designs. You'll be randomly assigned one of the variants:
            </p>
            <ul className="list-disc pl-6 space-y-2 mb-8">
              <li><strong>Control:</strong> Standard widget design</li>
              <li><strong>Variant A:</strong> Modern design with animation effects</li>
              <li><strong>Variant B:</strong> Compact layout with additional metrics</li>
            </ul>
            
            <div className="max-w-3xl">
              <DashboardWidgetExperiment
                title="Monthly Website Traffic"
                description="Analysis of website visitors over time"
                data={sampleData}
                onAction={handleWidgetAction}
              />
            </div>
            
            <div className="mt-8 p-4 bg-muted rounded-md">
              <h3 className="text-lg font-medium mb-2">How This Works</h3>
              <p className="mb-4">
                When you load this page, you are randomly assigned to one of three test variants for the dashboard widget above.
                Your interactions with this widget are tracked to analyze which design performs better.
              </p>
              <p>
                The A/B testing system records:
              </p>
              <ul className="list-disc pl-6 space-y-1 mt-2">
                <li>Which variant you were shown</li>
                <li>If you interacted with the widget (clicked the button)</li>
                <li>If you completed the desired action (conversion)</li>
              </ul>
            </div>
          </div>
          
          <Separator />
          
          <div>
            <h2 className="text-2xl font-bold mb-4">Widget Code Implementation</h2>
            <p className="mb-4">
              The widget above uses the <code className="bg-muted px-1 py-0.5 rounded">DashboardWidgetExperiment</code> component, 
              which leverages our A/B testing infrastructure to conditionally render different designs based on the 
              assigned variant.
            </p>
            <pre className="bg-muted p-4 rounded-md overflow-auto text-sm">
{`// Usage example:
<DashboardWidgetExperiment
  title="Monthly Website Traffic"
  description="Analysis of website visitors over time"
  data={sampleData}
  onAction={handleWidgetAction}
/>`}
            </pre>
            
            <div className="mt-6">
              <Button 
                onClick={() => {
                  toast({
                    title: 'Testing Completed',
                    description: 'Navigate to the Admin Dashboard tab to see test results',
                  });
                  setActiveTab('admin');
                }}
              >
                View Test Results in Admin Dashboard
              </Button>
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="cta" className="space-y-8">
          <div>
            <h2 className="text-2xl font-bold mb-4">Call-to-Action Button A/B Test</h2>
            <p className="text-muted-foreground mb-6">
              This example tests different CTA button designs to determine which drives the highest click-through rate.
              You'll be randomly assigned one of the variants:
            </p>
            <ul className="list-disc pl-6 space-y-2 mb-8">
              <li><strong>Control:</strong> Standard button from our design system</li>
              <li><strong>Variant A:</strong> Animated button with hover effects</li>
              <li><strong>Variant B:</strong> Gradient button with glow effect</li>
              <li><strong>Variant C:</strong> Minimal, elegant button design</li>
            </ul>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
              <Card>
                <CardContent className="p-8 flex flex-col items-center justify-center space-y-6">
                  <h3 className="text-xl font-semibold">Landing Page Hero</h3>
                  <p className="text-center text-muted-foreground">
                    Testing which CTA button design performs best in the hero section
                  </p>
                  <CTAButtonExperiment 
                    onClick={handleCtaClick} 
                    size="lg"
                  >
                    Get Started Now
                  </CTAButtonExperiment>
                </CardContent>
              </Card>
              
              <Card>
                <CardContent className="p-8 flex flex-col items-center justify-center space-y-6">
                  <h3 className="text-xl font-semibold">Pricing Page</h3>
                  <p className="text-center text-muted-foreground">
                    Testing which CTA button converts better on pricing pages
                  </p>
                  <CTAButtonExperiment onClick={handleCtaClick}>
                    Choose This Plan
                  </CTAButtonExperiment>
                </CardContent>
              </Card>
            </div>
            
            <div className="mt-8 p-4 bg-muted rounded-md">
              <h3 className="text-lg font-medium mb-2">Implementation Details</h3>
              <p className="mb-4">
                Using the <code className="bg-muted px-1 py-0.5 rounded">CTAButtonExperiment</code> component lets you
                easily A/B test different button designs without changing your page layout or user flow.
              </p>
              <pre className="bg-muted p-4 rounded-md overflow-auto text-sm mt-4">
{`// Usage example:
<CTAButtonExperiment onClick={handleCtaClick} size="lg">
  Get Started Now
</CTAButtonExperiment>`}
              </pre>
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="admin">
          <ABTestAdminDashboard />
        </TabsContent>
      </Tabs>
    </div>
  );
} 