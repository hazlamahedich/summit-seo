"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Grid } from "@/components/ui/grid";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AnimatedMetricCard } from "./animated-metric-card";
import { Section } from "@/components/ui/section";
import { LineChart, BarChart, PieChart, Layers, Users, Clock, MousePointer, Eye, Activity } from "lucide-react";
import { SEOMetricsChart } from "@/components/charts/seo-metrics-chart";
import { DataComparisonChart } from "@/components/charts/data-comparison-chart";

// Sample engagement data for demonstration
const engagementData = {
  metrics: {
    pageViews: {
      current: 12486,
      previous: 10250,
      trendValue: 21.8,
      trend: "up" as const,
    },
    visitDuration: {
      current: 195,
      previous: 170,
      trendValue: 14.7,
      trend: "up" as const,
    },
    bounceRate: {
      current: 32,
      previous: 38,
      trendValue: 15.8,
      trend: "down" as const,
    },
    clickThroughRate: {
      current: 4.2,
      previous: 3.8,
      trendValue: 10.5,
      trend: "up" as const,
    },
    userCount: {
      current: 5831,
      previous: 4975,
      trendValue: 17.2,
      trend: "up" as const,
    },
    averagePagesPerSession: {
      current: 3.6,
      previous: 3.2,
      trendValue: 12.5,
      trend: "up" as const,
    },
  },
  pageEngagementData: [
    { name: "Homepage", value: 85 },
    { name: "Product Page", value: 72 },
    { name: "Blog", value: 91 },
    { name: "Contact", value: 65 },
    { name: "About", value: 78 },
  ],
  timeSeriesData: [
    { name: "Week 1", current: 8250, previous: 7100 },
    { name: "Week 2", current: 9400, previous: 7950 },
    { name: "Week 3", current: 10800, previous: 8800 },
    { name: "Week 4", current: 11500, previous: 9200 },
    { name: "Week 5", current: 12100, previous: 9700 },
    { name: "Week 6", current: 12486, previous: 10250 },
  ],
};

// Animation variants for staggered animations
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.3,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

export const EngagementMetricsDashboard: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState("month");
  const [isLoading, setIsLoading] = useState(true);

  // Simulate data loading
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1200);

    return () => clearTimeout(timer);
  }, []);

  // Format seconds to minutes and seconds display
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <Section className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Engagement Metrics</h2>
          <p className="text-muted-foreground">
            Monitor how users interact with your content
          </p>
        </div>
        
        <Tabs
          value={selectedPeriod}
          onValueChange={setSelectedPeriod}
          className="w-[400px]"
        >
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="week">Week</TabsTrigger>
            <TabsTrigger value="month">Month</TabsTrigger>
            <TabsTrigger value="quarter">Quarter</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>
      
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="space-y-6"
      >
        {/* Top metrics row */}
        <motion.div variants={item}>
          <Grid cols={{ default: 1, sm: 2, lg: 3 }} gap={4}>
            <AnimatedMetricCard
              title="Page Views"
              value={engagementData.metrics.pageViews.current}
              previousValue={engagementData.metrics.pageViews.previous}
              trend={engagementData.metrics.pageViews.trend}
              trendValue={engagementData.metrics.pageViews.trendValue}
              icon={<Eye className="h-5 w-5" />}
              description="Total page views"
              isLoading={isLoading}
              variant="gradient"
            />
            
            <AnimatedMetricCard
              title="Avg. Visit Duration"
              value={engagementData.metrics.visitDuration.current}
              previousValue={engagementData.metrics.visitDuration.previous}
              suffix={` seconds`}
              description={`(${formatTime(engagementData.metrics.visitDuration.current)})`}
              trend={engagementData.metrics.visitDuration.trend}
              trendValue={engagementData.metrics.visitDuration.trendValue}
              icon={<Clock className="h-5 w-5" />}
              isLoading={isLoading}
              variant="spotlight"
            />
            
            <AnimatedMetricCard
              title="Bounce Rate"
              value={engagementData.metrics.bounceRate.current}
              previousValue={engagementData.metrics.bounceRate.previous}
              suffix="%"
              trend={engagementData.metrics.bounceRate.trend}
              trendValue={engagementData.metrics.bounceRate.trendValue}
              icon={<MousePointer className="h-5 w-5" />}
              isLoading={isLoading}
              variant="hover-lift"
            />
          </Grid>
        </motion.div>
        
        {/* Second metrics row */}
        <motion.div variants={item}>
          <Grid cols={{ default: 1, sm: 2, lg: 3 }} gap={4}>
            <AnimatedMetricCard
              title="Click-Through Rate"
              value={engagementData.metrics.clickThroughRate.current}
              previousValue={engagementData.metrics.clickThroughRate.previous}
              suffix="%"
              trend={engagementData.metrics.clickThroughRate.trend}
              trendValue={engagementData.metrics.clickThroughRate.trendValue}
              icon={<Activity className="h-5 w-5" />}
              isLoading={isLoading}
              variant="default"
            />
            
            <AnimatedMetricCard
              title="Users"
              value={engagementData.metrics.userCount.current}
              previousValue={engagementData.metrics.userCount.previous}
              trend={engagementData.metrics.userCount.trend}
              trendValue={engagementData.metrics.userCount.trendValue}
              icon={<Users className="h-5 w-5" />}
              isLoading={isLoading}
              variant="gradient"
            />
            
            <AnimatedMetricCard
              title="Pages per Session"
              value={engagementData.metrics.averagePagesPerSession.current}
              previousValue={engagementData.metrics.averagePagesPerSession.previous}
              trend={engagementData.metrics.averagePagesPerSession.trend}
              trendValue={engagementData.metrics.averagePagesPerSession.trendValue}
              icon={<Layers className="h-5 w-5" />}
              isLoading={isLoading}
              variant="spotlight"
            />
          </Grid>
        </motion.div>
        
        {/* Charts row */}
        <motion.div variants={item}>
          <Grid cols={{ default: 1, lg: 2 }} gap={6}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.5 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>Traffic Trends</CardTitle>
                  <CardDescription>Page views over time</CardDescription>
                </CardHeader>
                <CardContent>
                  {!isLoading ? (
                    <DataComparisonChart
                      title=""
                      data={engagementData.timeSeriesData}
                      currentLabel="Current Period"
                      previousLabel="Previous Period"
                    />
                  ) : (
                    <div className="h-[350px] w-full bg-muted/20 animate-pulse rounded-md" />
                  )}
                </CardContent>
              </Card>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8, duration: 0.5 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>Page Engagement</CardTitle>
                  <CardDescription>Engagement metrics by page</CardDescription>
                </CardHeader>
                <CardContent>
                  {!isLoading ? (
                    <SEOMetricsChart
                      title=""
                      metrics={engagementData.pageEngagementData}
                    />
                  ) : (
                    <div className="h-[350px] w-full bg-muted/20 animate-pulse rounded-md" />
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        </motion.div>
      </motion.div>
    </Section>
  );
}; 