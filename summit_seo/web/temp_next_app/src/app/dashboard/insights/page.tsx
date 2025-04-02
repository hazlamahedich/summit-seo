"use client";

import { useState } from 'react';
import { Section } from '@/components/ui/section';
import { Container } from '@/components/ui/container';
import { AIInsightsSection } from '@/components/dashboard/ai-insights-section';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Brain, Lightbulb, ChevronRight, Filter, Rocket } from 'lucide-react';
import { useProjects } from '@/lib/services';
import { Insight, InsightStatus } from '@/types/api';

// Mock data for demonstration
const MOCK_ANALYSES = [
  { id: 'analysis-1', name: 'Website Performance Analysis', project: 'Project Alpha', date: '2023-12-15' },
  { id: 'analysis-2', name: 'SEO Content Analysis', project: 'Project Beta', date: '2023-12-10' },
  { id: 'analysis-3', name: 'Competitors Analysis', project: 'Project Gamma', date: '2023-12-05' },
];

// For demo purposes, we'll create mock insights directly
const MOCK_INSIGHTS: Insight[] = [
  {
    id: 'insight-1',
    analysis_id: 'analysis-1',
    type: 'performance',
    title: 'Page Speed Optimization',
    content: 'Your page load time is 3.8 seconds, which is slower than the recommended 2 seconds. This could be affecting your user experience and SEO rankings. Consider optimizing image sizes, implementing lazy loading, and reducing JavaScript execution time. Specifically, we identified large uncompressed images on your homepage that are adding over 1.5 seconds to your load time. Compressing these images could result in a 30% improvement in overall page load time.',
    status: InsightStatus.GENERATED,
    created_at: '2023-12-20T15:30:00Z',
    updated_at: '2023-12-20T15:30:00Z',
    metadata: {
      confidence: 0.94,
      priority: 'high',
    },
  },
  {
    id: 'insight-2',
    analysis_id: 'analysis-1',
    type: 'seo',
    title: 'Meta Description Improvements',
    content: 'Several of your key pages are missing meta descriptions or have descriptions that exceed the recommended 155-160 character limit. Meta descriptions are crucial for improving click-through rates from search engine results. We recommend adding concise, compelling meta descriptions to all important pages, focusing on including relevant keywords while still engaging potential visitors. The most critical pages missing descriptions are your About and Services pages.',
    status: InsightStatus.GENERATED,
    created_at: '2023-12-20T15:35:00Z',
    updated_at: '2023-12-20T15:35:00Z',
    metadata: {
      confidence: 0.87,
      priority: 'medium',
    },
  },
  {
    id: 'insight-3',
    analysis_id: 'analysis-1',
    type: 'security',
    title: 'HTTPS Implementation Issues',
    content: 'We detected that your site is correctly using HTTPS, but several resources are still being loaded over HTTP. This creates "mixed content" issues that can trigger browser warnings and reduce visitor trust. Specifically, we found 3 image resources and 2 script files loading over insecure connections. Update all resource references to use HTTPS to ensure full security coverage.',
    status: InsightStatus.GENERATED,
    created_at: '2023-12-20T15:40:00Z',
    updated_at: '2023-12-20T15:40:00Z',
    metadata: {
      confidence: 0.96,
      priority: 'high',
    },
  },
  {
    id: 'insight-4',
    analysis_id: 'analysis-1',
    type: 'accessibility',
    title: 'Contrast Ratio Improvements',
    content: 'Several text elements on your site have insufficient contrast ratios, making them difficult to read for users with visual impairments. We identified 8 instances where text contrast falls below the WCAG AA standard of 4.5:1. This affects primarily gray text on white backgrounds in your blog section and footer links. Increasing the contrast of these elements would improve accessibility for all users and help ensure compliance with accessibility standards.',
    status: InsightStatus.PENDING,
    created_at: '2023-12-20T15:45:00Z',
    updated_at: '2023-12-20T15:45:00Z',
    metadata: {},
  },
];

export default function InsightsPage() {
  const [selectedAnalysis, setSelectedAnalysis] = useState(MOCK_ANALYSES[0].id);
  const [activeTab, setActiveTab] = useState('insights');
  
  // This would normally come from the API, but we're using mock data for demonstration
  const { data: projectsData, isLoading: isLoadingProjects } = useProjects({
    page: 1,
    page_size: 100
  });
  
  // Mock function to get analysis name from ID
  const getAnalysisName = (id: string) => {
    const analysis = MOCK_ANALYSES.find(a => a.id === id);
    return analysis ? analysis.name : 'Unknown Analysis';
  };
  
  return (
    <Container>
      <Section>
        <div className="flex flex-col gap-8">
          {/* Page header */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight mb-1">AI Insights</h1>
              <p className="text-muted-foreground">
                Discover intelligent recommendations powered by AI analysis
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              <Select 
                value={selectedAnalysis} 
                onValueChange={setSelectedAnalysis}
              >
                <SelectTrigger className="w-[260px]">
                  <SelectValue placeholder="Select analysis" />
                </SelectTrigger>
                <SelectContent>
                  {MOCK_ANALYSES.map(analysis => (
                    <SelectItem key={analysis.id} value={analysis.id}>
                      {analysis.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          
          {/* Analysis summary */}
          <Card className="bg-primary/5 dark:bg-primary/10 border-primary/20 dark:border-primary/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                <span>{getAnalysisName(selectedAnalysis)}</span>
              </CardTitle>
              <CardDescription>
                AI-powered insights and recommendations for your website analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-background/80 rounded-md p-4 border border-border/50">
                  <div className="text-sm font-medium text-muted-foreground mb-1">Total Insights</div>
                  <div className="text-2xl font-bold">{MOCK_INSIGHTS.length}</div>
                </div>
                <div className="bg-background/80 rounded-md p-4 border border-border/50">
                  <div className="text-sm font-medium text-muted-foreground mb-1">High Priority</div>
                  <div className="text-2xl font-bold">2</div>
                </div>
                <div className="bg-background/80 rounded-md p-4 border border-border/50">
                  <div className="text-sm font-medium text-muted-foreground mb-1">Pending Generation</div>
                  <div className="text-2xl font-bold">1</div>
                </div>
              </div>
              
              <div className="pt-2 flex items-center gap-2">
                <Rocket className="h-4 w-4 text-primary" />
                <span className="text-sm text-muted-foreground">
                  <span className="font-medium">Pro tip:</span> Filter insights by category to focus on specific areas for improvement
                </span>
              </div>
            </CardContent>
          </Card>
          
          {/* Tabs for different sections */}
          <Tabs defaultValue="insights" value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="mb-4">
              <TabsTrigger value="insights" className="flex items-center gap-2">
                <Lightbulb className="h-4 w-4" />
                <span>Insights & Recommendations</span>
              </TabsTrigger>
              <TabsTrigger value="reports" className="flex items-center gap-2">
                <Filter className="h-4 w-4" />
                <span>Insight Reports</span>
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="insights" className="mt-0">
              {/* This is the component we just created - it normally gets data from the API */}
              <AIInsightsSection 
                analysisId={selectedAnalysis} 
                className="mt-0"
              />
            </TabsContent>
            
            <TabsContent value="reports" className="mt-0">
              <Card>
                <CardHeader>
                  <CardTitle>Insight Reports</CardTitle>
                  <CardDescription>
                    Comprehensive reports based on AI analysis of your website
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex flex-col items-center justify-center p-8 text-center">
                  <Rocket className="h-16 w-16 text-primary/50 mb-4" />
                  <h3 className="text-xl font-medium mb-2">Reports Coming Soon</h3>
                  <p className="text-sm text-muted-foreground mb-6 max-w-md mx-auto">
                    We're working on comprehensive insight reports that will provide deeper analysis of your website's performance.
                  </p>
                  <Button variant="outline" className="flex items-center gap-2">
                    <span>Learn More</span>
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </Section>
    </Container>
  );
} 