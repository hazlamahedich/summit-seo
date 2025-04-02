"use client";

import React from "react";
import { Grid } from "@/components/ui/grid";
import { DashboardLayout } from "@/components/ui/dashboard-layout";
import { DefaultDashboardSidebar } from "@/components/ui/dashboard-sidebar";
import { Section } from "@/components/ui/section";
import { SEOMetricsChart } from "@/components/charts/seo-metrics-chart";
import { ScoreVisualization } from "@/components/charts/score-visualization";
import { DataComparisonChart } from "@/components/charts/data-comparison-chart";
import { ProgressChart } from "@/components/charts/progress-chart";
import { motion } from "framer-motion";

// Sample data
const seoMetricsData = [
  { name: "Page Speed", value: 85 },
  { name: "Mobile Compatibility", value: 92 },
  { name: "SEO Score", value: 78 },
  { name: "Accessibility", value: 65 },
  { name: "Security", value: 88 },
];

const scoreData = [
  { name: "SEO", value: 78, color: "#4f46e5" },
  { name: "Performance", value: 85, color: "#10b981" },
  { name: "Security", value: 88, color: "#f59e0b" },
  { name: "Accessibility", value: 65, color: "#ef4444" },
];

const comparisonData = [
  { name: "Week 1", current: 65, previous: 55 },
  { name: "Week 2", current: 68, previous: 58 },
  { name: "Week 3", current: 72, previous: 60 },
  { name: "Week 4", current: 78, previous: 63 },
  { name: "Week 5", current: 82, previous: 67 },
  { name: "Week 6", current: 85, previous: 70 },
];

const progressData = [
  { name: "Organic Traffic", value: 850, goal: 1000 },
  { name: "Conversions", value: 35, goal: 50 },
  { name: "Backlinks", value: 120, goal: 200 },
  { name: "Page Speed", value: 85, goal: 90 },
  { name: "Mobile Experience", value: 92, goal: 95 },
];

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

export default function DataVisualizationPage() {
  return (
    <DashboardLayout sidebar={<DefaultDashboardSidebar />}>
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="space-y-8"
      >
        <motion.div variants={item}>
          <Section>
            <h1 className="mb-4 text-3xl font-bold">Data Visualization</h1>
            <p className="mb-8 text-muted-foreground">
              Interactive charts and visualizations for your SEO data
            </p>

            <Grid cols={{ default: 1, md: 2 }} gap={6} className="mb-8">
              <motion.div variants={item}>
                <SEOMetricsChart title="SEO Metrics" metrics={seoMetricsData} />
              </motion.div>
              <motion.div variants={item}>
                <ScoreVisualization title="Performance Overview" scores={scoreData} />
              </motion.div>
            </Grid>

            <Grid cols={{ default: 1, md: 2 }} gap={6} className="mb-8">
              <motion.div variants={item}>
                <DataComparisonChart
                  title="SEO Progress"
                  description="Comparing current period with previous period"
                  data={comparisonData}
                  currentLabel="Current Period"
                  previousLabel="Previous Period"
                />
              </motion.div>
              <motion.div variants={item}>
                <ScoreVisualization
                  title="Performance Breakdown"
                  scores={scoreData}
                  type="pie"
                />
              </motion.div>
            </Grid>

            <Grid cols={{ default: 1 }} gap={6}>
              <motion.div variants={item}>
                <ProgressChart
                  title="Goal Progress"
                  description="Track your progress toward key SEO goals"
                  metrics={progressData}
                />
              </motion.div>
            </Grid>
          </Section>
        </motion.div>
      </motion.div>
    </DashboardLayout>
  );
} 