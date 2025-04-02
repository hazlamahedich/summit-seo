"use client";

import React from "react";
import { Grid } from "@/components/ui/grid";
import { Separator } from "@/components/ui/separator"; 
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { SEOMetricsChart } from "@/components/charts/seo-metrics-chart";
import { ScoreVisualization } from "@/components/charts/score-visualization";
import { DataComparisonChart } from "@/components/charts/data-comparison-chart";
import { ProgressChart } from "@/components/charts/progress-chart";
import { ReportGenerator } from "./report-generator";

interface SEOMetric {
  name: string;
  value: number;
  color?: string;
}

interface ScoreData {
  name: string;
  value: number;
  color?: string;
}

interface ComparisonData {
  name: string;
  current: number;
  previous: number;
}

interface ProgressMetric {
  name: string;
  value: number;
  goal: number;
  color?: string;
}

interface SEOReportData {
  siteUrl: string;
  reportDate: string;
  metrics: SEOMetric[];
  scores: ScoreData[];
  comparisonData: ComparisonData[];
  progressMetrics: ProgressMetric[];
  findings?: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  recommendations?: string[];
}

interface SEOReportTemplateProps {
  data: SEOReportData;
  title?: string;
  description?: string;
  className?: string;
}

export const SEOReportTemplate: React.FC<SEOReportTemplateProps> = ({
  data,
  title = "SEO Performance Report",
  description,
  className = "",
}) => {
  const reportDescription = description || `Comprehensive SEO analysis for ${data.siteUrl}`;
  
  // Format findings data for visualization if available
  const findingCategories = data.findings 
    ? [
        { name: "Critical", count: data.findings.critical, color: "#ef4444" },
        { name: "High", count: data.findings.high, color: "#f59e0b" },
        { name: "Medium", count: data.findings.medium, color: "#10b981" },
        { name: "Low", count: data.findings.low, color: "#3b82f6" },
      ]
    : [];

  return (
    <ReportGenerator
      title={title}
      description={reportDescription}
      filename={`seo-report-${data.siteUrl.replace(/[^a-z0-9]/gi, '-')}.pdf`}
      orientation="portrait"
      paperSize="a4"
      className={className}
    >
      {/* Report Header */}
      <div className="mb-6 space-y-2">
        <div className="flex flex-wrap items-start justify-between">
          <div>
            <h2 className="font-medium">Website: <span className="font-normal">{data.siteUrl}</span></h2>
            <h2 className="font-medium">Report Date: <span className="font-normal">{data.reportDate}</span></h2>
          </div>
        </div>
      </div>

      <Separator className="my-6" />

      {/* Performance Overview */}
      <div className="mb-8">
        <h2 className="mb-4 text-xl font-semibold">Performance Overview</h2>
        <Grid cols={{ default: 1, md: 2 }} gap={6} className="print:grid-cols-2">
          <SEOMetricsChart title="SEO Metrics" metrics={data.metrics} />
          <ScoreVisualization title="Performance Scores" scores={data.scores} />
        </Grid>
      </div>

      <Separator className="my-6" />

      {/* Progress and Comparison */}
      <div className="mb-8">
        <h2 className="mb-4 text-xl font-semibold">Progress & Comparison</h2>
        <Grid cols={{ default: 1, md: 2 }} gap={6} className="print:grid-cols-2">
          <DataComparisonChart
            title="Performance Trends"
            description="Comparing current period with previous period"
            data={data.comparisonData}
            currentLabel="Current Period"
            previousLabel="Previous Period"
          />
          <ProgressChart
            title="Goal Progress"
            description="Progress toward key performance indicators"
            metrics={data.progressMetrics}
            showRadar={false}
          />
        </Grid>
      </div>

      {/* Findings Summary */}
      {data.findings && (
        <>
          <Separator className="my-6" />
          <div className="mb-8">
            <h2 className="mb-4 text-xl font-semibold">Findings Summary</h2>
            <Card>
              <CardHeader>
                <CardTitle>Issues by Severity</CardTitle>
                <CardDescription>Distribution of issues found during analysis</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {findingCategories.map((category) => (
                    <div key={category.name} className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span>{category.name}</span>
                        <span className="font-medium">{category.count}</span>
                      </div>
                      <div className="h-4 w-full bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{ 
                            backgroundColor: category.color,
                            width: `${(category.count / Math.max(...findingCategories.map(c => c.count), 1)) * 100}%`
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      )}

      {/* Recommendations */}
      {data.recommendations && data.recommendations.length > 0 && (
        <>
          <Separator className="my-6" />
          <div className="mb-8">
            <h2 className="mb-4 text-xl font-semibold">Top Recommendations</h2>
            <Card>
              <CardHeader>
                <CardTitle>Suggested Improvements</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="list-disc pl-5 space-y-2">
                  {data.recommendations.map((recommendation, index) => (
                    <li key={index}>{recommendation}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </ReportGenerator>
  );
}; 