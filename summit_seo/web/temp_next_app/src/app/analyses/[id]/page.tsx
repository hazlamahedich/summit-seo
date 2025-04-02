"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { AnimatedContainer } from "@/components/ui/animated-container";
import { FindingsChart } from "@/components/analyses/findings-chart";
import { ScoreCircle } from "@/components/analyses/score-circle";
import { Button } from "@/components/ui/button";

interface AnalysisResult {
  id: number;
  projectId: number;
  projectName: string;
  url: string;
  status: string;
  startedAt: string;
  completedAt: string | null;
  summary: {
    totalPages: number;
    analyzedPages: number;
    totalFindings: number;
    criticalFindings: number;
    highFindings: number;
    mediumFindings: number;
    lowFindings: number;
    averageScore: number;
    completionPercentage: number;
  };
}

export default function AnalysisResultsPage() {
  const params = useParams();
  const [loading, setLoading] = useState(true);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [activeTab, setActiveTab] = useState("overview");

  // Fetch analysis data
  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        setLoading(true);
        // TODO: Replace with actual API call when available
        const mockAnalysis: AnalysisResult = {
          id: Number(params.id),
          projectId: 1,
          projectName: "Example Project",
          url: "https://example.com",
          status: "completed",
          startedAt: new Date().toISOString(),
          completedAt: new Date().toISOString(),
          summary: {
            totalPages: 25,
            analyzedPages: 25,
            totalFindings: 42,
            criticalFindings: 3,
            highFindings: 7,
            mediumFindings: 15,
            lowFindings: 17,
            averageScore: 78.5,
            completionPercentage: 100
          }
        };
        
        setAnalysis(mockAnalysis);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching analysis:", error);
        setLoading(false);
      }
    };

    if (params.id) {
      fetchAnalysis();
    }
  }, [params.id]);

  const findingsCategories = analysis ? [
    { name: "Critical", count: analysis.summary.criticalFindings, color: "#ef4444" },
    { name: "High", count: analysis.summary.highFindings, color: "#f97316" },
    { name: "Medium", count: analysis.summary.mediumFindings, color: "#f59e0b" },
    { name: "Low", count: analysis.summary.lowFindings, color: "#0ea5e9" }
  ] : [];

  if (loading) {
    return <div className="p-8">Loading analysis results...</div>;
  }

  if (!analysis) {
    return <div className="p-8">Analysis not found</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-2xl font-bold mb-2">Analysis Results</h1>
          <div className="text-muted-foreground mb-1">
            Project: {analysis.projectName}
          </div>
          <div className="text-primary hover:underline">
            {analysis.url}
          </div>
        </div>
        <div className="flex flex-col items-end gap-4">
          <ScoreCircle score={analysis.summary.averageScore} size={160} />
          <Link href={`/analyses/${params.id}/findings`}>
            <Button variant="outline" className="mt-2">
              View Detailed Findings
            </Button>
          </Link>
        </div>
      </div>

      <Tabs defaultValue="overview" className="w-full" value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="seo">SEO</TabsTrigger>
          <TabsTrigger value="accessibility">Accessibility</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <AnimatedContainer>
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Analysis Summary</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-muted p-4 rounded-md">
                  <div className="text-sm text-muted-foreground">Pages Analyzed</div>
                  <div className="text-2xl font-bold">{analysis.summary.analyzedPages} / {analysis.summary.totalPages}</div>
                </div>
                <div className="bg-muted p-4 rounded-md">
                  <div className="text-sm text-muted-foreground">Total Findings</div>
                  <div className="text-2xl font-bold">{analysis.summary.totalFindings}</div>
                </div>
                <div className="bg-muted p-4 rounded-md">
                  <div className="text-sm text-muted-foreground">Critical Issues</div>
                  <div className="text-2xl font-bold text-red-500">{analysis.summary.criticalFindings}</div>
                </div>
                <div className="bg-muted p-4 rounded-md">
                  <div className="text-sm text-muted-foreground">Completion</div>
                  <div className="text-2xl font-bold">{analysis.summary.completionPercentage}%</div>
                </div>
              </div>
            </Card>
          </AnimatedContainer>
          
          <AnimatedContainer delay={0.1}>
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Findings By Category</h2>
              <div className="mt-4">
                <FindingsChart categories={findingsCategories} />
              </div>
            </Card>
          </AnimatedContainer>
          
          <AnimatedContainer delay={0.2}>
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Top Issues</h2>
              <div className="space-y-4">
                <div className="p-4 border border-red-200 bg-red-50 dark:bg-red-950/20 dark:border-red-900/50 rounded-md">
                  <div className="font-medium text-red-700 dark:text-red-400">Missing SSL Certificate</div>
                  <p className="text-sm text-red-600 dark:text-red-300 mt-1">The website is not using HTTPS, which is a security risk and can impact SEO rankings.</p>
                </div>
                <div className="p-4 border border-orange-200 bg-orange-50 dark:bg-orange-950/20 dark:border-orange-900/50 rounded-md">
                  <div className="font-medium text-orange-700 dark:text-orange-400">Missing Meta Descriptions</div>
                  <p className="text-sm text-orange-600 dark:text-orange-300 mt-1">7 pages are missing meta descriptions, which are important for search engine result pages.</p>
                </div>
                <div className="p-4 border border-amber-200 bg-amber-50 dark:bg-amber-950/20 dark:border-amber-900/50 rounded-md">
                  <div className="font-medium text-amber-700 dark:text-amber-400">Slow Page Load Time</div>
                  <p className="text-sm text-amber-600 dark:text-amber-300 mt-1">Average page load time is 4.2 seconds, exceeding the recommended 3 seconds.</p>
                </div>
              </div>
            </Card>
          </AnimatedContainer>
        </TabsContent>
        
        <TabsContent value="performance" className="space-y-4">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Performance Analysis</h2>
            <p className="text-muted-foreground">Performance analysis details will be shown here.</p>
          </Card>
        </TabsContent>
        
        <TabsContent value="seo" className="space-y-4">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">SEO Analysis</h2>
            <p className="text-muted-foreground">SEO analysis details will be shown here.</p>
          </Card>
        </TabsContent>
        
        <TabsContent value="accessibility" className="space-y-4">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Accessibility Analysis</h2>
            <p className="text-muted-foreground">Accessibility analysis details will be shown here.</p>
          </Card>
        </TabsContent>
        
        <TabsContent value="security" className="space-y-4">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Security Analysis</h2>
            <p className="text-muted-foreground">Security analysis details will be shown here.</p>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
} 