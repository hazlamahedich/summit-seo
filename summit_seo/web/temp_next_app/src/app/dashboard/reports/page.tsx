"use client";

import React from "react";
import { DashboardLayout } from "@/components/ui/dashboard-layout";
import { DefaultDashboardSidebar } from "@/components/ui/dashboard-sidebar";
import { Section } from "@/components/ui/section";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { SEOReportTemplate } from "@/components/reports/seo-report-template";
import { motion } from "framer-motion";
import { FileText, Clock, BarChart2 } from "lucide-react";

// Sample report data
const sampleReportData = {
  siteUrl: "example.com",
  reportDate: new Date().toLocaleDateString(),
  metrics: [
    { name: "Page Speed", value: 85 },
    { name: "Mobile Compatibility", value: 92 },
    { name: "SEO Score", value: 78 },
    { name: "Accessibility", value: 65 },
    { name: "Security", value: 88 },
  ],
  scores: [
    { name: "SEO", value: 78, color: "#4f46e5" },
    { name: "Performance", value: 85, color: "#10b981" },
    { name: "Security", value: 88, color: "#f59e0b" },
    { name: "Accessibility", value: 65, color: "#ef4444" },
  ],
  comparisonData: [
    { name: "Week 1", current: 65, previous: 55 },
    { name: "Week 2", current: 68, previous: 58 },
    { name: "Week 3", current: 72, previous: 60 },
    { name: "Week 4", current: 78, previous: 63 },
    { name: "Week 5", current: 82, previous: 67 },
    { name: "Week 6", current: 85, previous: 70 },
  ],
  progressMetrics: [
    { name: "Organic Traffic", value: 850, goal: 1000 },
    { name: "Conversions", value: 35, goal: 50 },
    { name: "Backlinks", value: 120, goal: 200 },
    { name: "Page Speed", value: 85, goal: 90 },
    { name: "Mobile Experience", value: 92, goal: 95 },
  ],
  findings: {
    critical: 2,
    high: 5,
    medium: 8,
    low: 12,
  },
  recommendations: [
    "Improve page loading speed by optimizing image sizes and implementing lazy loading",
    "Add meta descriptions to all pages that are currently missing them",
    "Implement proper heading structure (H1, H2, H3) across all pages",
    "Fix broken links and redirect issues on key landing pages",
    "Improve mobile responsiveness on product pages",
    "Enhance internal linking structure to improve crawlability",
  ],
};

// More sample data for additional reports
const recentReports = [
  {
    id: 1,
    title: "Monthly SEO Performance",
    date: "June 1, 2023",
    type: "Performance",
    description: "Monthly overview of key SEO metrics and improvements",
  },
  {
    id: 2,
    title: "Competitor Analysis",
    date: "May 15, 2023",
    type: "Competitive",
    description: "Detailed analysis of top 5 competitors in search rankings",
  },
  {
    id: 3,
    title: "Technical SEO Audit",
    date: "May 1, 2023",
    type: "Technical",
    description: "Complete technical audit identifying critical issues",
  },
];

export default function ReportsPage() {
  return (
    <DashboardLayout sidebar={<DefaultDashboardSidebar />}>
      <Section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-8"
        >
          <div>
            <h1 className="mb-2 text-3xl font-bold">Reports</h1>
            <p className="text-muted-foreground">
              Generate and view detailed SEO performance reports
            </p>
          </div>

          <Tabs defaultValue="generator" className="w-full">
            <TabsList className="mb-6">
              <TabsTrigger value="generator" className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Report Generator
              </TabsTrigger>
              <TabsTrigger value="recent" className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Recent Reports
              </TabsTrigger>
              <TabsTrigger value="templates" className="flex items-center gap-2">
                <BarChart2 className="h-4 w-4" />
                Templates
              </TabsTrigger>
            </TabsList>

            <TabsContent value="generator" className="mt-0">
              <SEOReportTemplate 
                data={sampleReportData} 
                title="SEO Performance Report"
                description="Comprehensive SEO analysis with metrics and recommendations"
              />
            </TabsContent>

            <TabsContent value="recent" className="mt-0">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
                {recentReports.map((report) => (
                  <motion.div
                    key={report.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Card>
                      <CardHeader>
                        <CardTitle>{report.title}</CardTitle>
                        <CardDescription>
                          {report.date} • {report.type} Report
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <p className="mb-4 text-sm text-muted-foreground">
                          {report.description}
                        </p>
                        <div className="flex flex-wrap gap-2">
                          <Button size="sm" variant="default">
                            View Report
                          </Button>
                          <Button size="sm" variant="outline">
                            Download PDF
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="templates" className="mt-0">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
                <Card>
                  <CardHeader>
                    <CardTitle>Comprehensive SEO Audit</CardTitle>
                    <CardDescription>
                      Complete technical and on-page SEO analysis
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="mb-4 text-sm text-muted-foreground">
                      Full analysis of technical SEO, on-page optimization, backlinks, and competitive landscape
                    </p>
                    <Button size="sm">Use Template</Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Performance Snapshot</CardTitle>
                    <CardDescription>
                      Quick overview of current SEO performance
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="mb-4 text-sm text-muted-foreground">
                      Summary of key performance metrics, traffic sources, and conversion rates
                    </p>
                    <Button size="sm">Use Template</Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Competitor Analysis</CardTitle>
                    <CardDescription>
                      Compare your site with competitors
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="mb-4 text-sm text-muted-foreground">
                      Side-by-side comparison with top competitors on key metrics and rankings
                    </p>
                    <Button size="sm">Use Template</Button>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </motion.div>
      </Section>
    </DashboardLayout>
  );
} 