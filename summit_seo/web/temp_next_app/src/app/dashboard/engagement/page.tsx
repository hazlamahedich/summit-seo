"use client";

import React from "react";
import { DashboardLayout } from "@/components/ui/dashboard-layout";
import { DefaultDashboardSidebar } from "@/components/ui/dashboard-sidebar";
import { Section } from "@/components/ui/section";
import { EngagementMetricsDashboard } from "@/components/dashboard/engagement-metrics-dashboard";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { motion } from "framer-motion";
import { DownloadCloud, Share2, RefreshCcw } from "lucide-react";

export default function EngagementPage() {
  return (
    <DashboardLayout sidebar={<DefaultDashboardSidebar />}>
      <motion.div 
        initial={{ opacity: 0 }} 
        animate={{ opacity: 1 }} 
        transition={{ duration: 0.5 }}
        className="space-y-8"
      >
        {/* Page Header */}
        <Section className="pb-0">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Engagement Dashboard</h1>
              <p className="text-muted-foreground mt-1">
                Monitor user interactions and engagement metrics
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" className="gap-1">
                <RefreshCcw className="h-4 w-4" />
                Refresh
              </Button>
              <Button variant="outline" size="sm" className="gap-1">
                <Share2 className="h-4 w-4" />
                Share
              </Button>
              <Button variant="default" size="sm" className="gap-1">
                <DownloadCloud className="h-4 w-4" />
                Export
              </Button>
            </div>
          </div>

          <Separator className="my-6" />
        </Section>

        {/* Engagement Metrics Dashboard */}
        <EngagementMetricsDashboard />

        {/* Additional Insights Section */}
        <Section>
          <h2 className="text-2xl font-bold tracking-tight mb-6">Engagement Insights</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.5 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>User Behavior Highlights</CardTitle>
                  <CardDescription>Key insights from user interactions</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center gap-2">
                      <div className="h-2 w-2 rounded-full bg-green-500"></div>
                      <span>Users spend the most time on blog articles with visual content</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="h-2 w-2 rounded-full bg-green-500"></div>
                      <span>Mobile engagement has increased by 24% over the previous period</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="h-2 w-2 rounded-full bg-yellow-500"></div>
                      <span>Product pages have a higher than average bounce rate</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="h-2 w-2 rounded-full bg-green-500"></div>
                      <span>Social media referrals generate more page views per session</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="h-2 w-2 rounded-full bg-blue-500"></div>
                      <span>Weekend traffic shows different engagement patterns than weekdays</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.5 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>Recommendations</CardTitle>
                  <CardDescription>Optimization suggestions based on engagement</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-center gap-2">
                      <div className="h-2 w-2 rounded-full bg-primary"></div>
                      <span>Improve product page layout to reduce bounce rate</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="h-2 w-2 rounded-full bg-primary"></div>
                      <span>Add more visual content to increase time on page</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="h-2 w-2 rounded-full bg-primary"></div>
                      <span>Implement user segmentation for personalized content</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="h-2 w-2 rounded-full bg-primary"></div>
                      <span>Optimize mobile navigation to improve conversion rates</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <div className="h-2 w-2 rounded-full bg-primary"></div>
                      <span>Enhance weekend content strategy based on traffic patterns</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </Section>
      </motion.div>
    </DashboardLayout>
  );
} 