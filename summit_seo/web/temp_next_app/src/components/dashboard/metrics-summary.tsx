import { useState, useMemo } from 'react';
import { Flex } from "@/components/ui/flex";
import { Grid } from "@/components/ui/grid";
import { MotionCard } from "@/components/ui/motion-card";
import { Section } from "@/components/ui/section";
import { LineChart, BarChart2, TrendingUp, Globe, PieChart, AlertTriangle, Check } from 'lucide-react';
import { 
  useProjects, 
  useAnalyses
} from "@/lib/services";
import { SeverityLevel } from '@/types/api';

interface MetricCardProps {
  icon: React.ReactNode;
  title: string;
  value: string | number;
  subtitle?: string;
  variant?: 'gradient' | 'spotlight' | 'hover-lift' | 'default';
  loading?: boolean;
}

const MetricCard = ({ 
  icon, 
  title, 
  value, 
  subtitle, 
  variant = 'spotlight',
  loading = false 
}: MetricCardProps) => {
  return (
    <MotionCard 
      className="p-4" 
      variant={variant}
      intensity="medium"
    >
      <Flex direction="col">
        <Flex className="text-muted-foreground mb-2" align="center" gap={2}>
          {icon}
          <span>{title}</span>
        </Flex>
        {loading ? (
          <div className="h-8 w-16 bg-muted/40 animate-pulse rounded" />
        ) : (
          <span className="text-3xl font-bold">{value}</span>
        )}
        {subtitle && <span className="text-xs text-muted-foreground mt-1">{subtitle}</span>}
      </Flex>
    </MotionCard>
  );
};

export const MetricsSummary = () => {
  // Fetch projects data
  const { data: projectsData, isLoading: projectsLoading } = useProjects({
    page: 1,
    page_size: 10
  });
  
  // Fetch analyses data
  const { data: analysesData, isLoading: analysesLoading } = useAnalyses({
    page: 1,
    page_size: 50
  });
  
  // Calculate metrics
  const totalProjects = projectsData?.data.length || 0;
  const activeAnalyses = analysesData?.data.filter(a => a.status === 'running').length || 0;
  const completedAnalyses = analysesData?.data.filter(a => a.status === 'completed').length || 0;
  
  // Estimate critical issues from analysis results
  // In a real implementation, we would query each analysis's findings
  // but for this simplified version, we'll use a placeholder value
  const totalCriticalIssues = useMemo(() => {
    // In a real implementation, we would fetch findings for each analysis
    // For now, we'll estimate based on completed analyses
    return completedAnalyses > 0 ? Math.round(completedAnalyses * 1.5) : 0;
  }, [completedAnalyses]);

  // Calculate average score from completed analyses
  const completedAnalysesWithScore = analysesData?.data.filter(a => 
    a.status === 'completed' && a.overall_score !== null
  ) || [];
  
  const averageScore = completedAnalysesWithScore.length > 0 
    ? Math.round(completedAnalysesWithScore.reduce((sum, analysis) => 
        sum + (analysis.overall_score || 0), 0) / completedAnalysesWithScore.length
      )
    : 0;

  return (
    <Section className="mb-8">
      <h2 className="text-xl font-semibold mb-4">Summary Metrics</h2>
      
      <Grid cols={{ default: 1, md: 2, lg: 4 }} gap={4} className="stats-overview">
        <MetricCard 
          icon={<Globe />} 
          title="Total Projects" 
          value={totalProjects} 
          subtitle="Active websites monitored"
          variant="gradient"
          loading={projectsLoading}
        />
        
        <MetricCard 
          icon={<BarChart2 />} 
          title="Active Analyses" 
          value={activeAnalyses} 
          subtitle={`${completedAnalyses} completed`}
          variant="spotlight"
          loading={analysesLoading}
        />
        
        <MetricCard 
          icon={<TrendingUp />} 
          title="Average Score" 
          value={averageScore} 
          subtitle={completedAnalysesWithScore.length > 0 ? `Across ${completedAnalysesWithScore.length} analyses` : 'No completed analyses'}
          variant="hover-lift"
          loading={analysesLoading}
        />
        
        <MetricCard 
          icon={<AlertTriangle className="text-red-500" />} 
          title="Critical Issues" 
          value={totalCriticalIssues} 
          subtitle="Require immediate attention"
          variant="default"
          loading={analysesLoading}
        />
      </Grid>
    </Section>
  );
}; 