"use client";

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useAnalysisInsights, useGenerateInsight, useInsightCategories } from '@/lib/services';
import { InsightCard } from '@/components/dashboard/insight-card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AnimatedContainer } from '@/components/ui/animated-container';
import { Brain, Rocket, PlusCircle, BrainCircuit } from 'lucide-react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { InsightStatus } from '@/types/api';

interface AIInsightsSectionProps {
  analysisId: string;
  className?: string;
}

export const AIInsightsSection: React.FC<AIInsightsSectionProps> = ({
  analysisId,
  className
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  
  // Fetch insights for this analysis
  const { 
    data: insightsData, 
    isLoading: isLoadingInsights, 
    error: insightsError 
  } = useAnalysisInsights(analysisId);
  
  // Fetch available insight categories
  const {
    data: categoriesData,
    isLoading: isLoadingCategories
  } = useInsightCategories(analysisId);
  
  // Generate insight mutation
  const generateInsight = useGenerateInsight(analysisId);
  
  // Handle generating a new insight
  const handleGenerateInsight = (type: string) => {
    generateInsight.mutate({ 
      type, 
      context: { source: 'dashboard' } 
    });
  };
  
  // Filter insights based on selected category
  const filteredInsights = insightsData?.data?.filter(insight => 
    selectedCategory === 'all' || insight.type === selectedCategory
  ) || [];
  
  // Handle category selection
  const handleCategoryChange = (value: string) => {
    setSelectedCategory(value);
  };
  
  // Animation variants for staggered item appearance
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };
  
  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };
  
  // Loading state
  if (isLoadingInsights || isLoadingCategories) {
    return (
      <AnimatedContainer 
        variant="fadeIn" 
        className={className}
      >
        <div className="flex items-center justify-center p-8">
          <BrainCircuit className="h-8 w-8 text-primary animate-pulse mr-3" />
          <h3 className="text-xl font-medium">Loading AI Insights...</h3>
        </div>
      </AnimatedContainer>
    );
  }
  
  // Error state
  if (insightsError) {
    return (
      <AnimatedContainer 
        variant="fadeIn" 
        className={className}
      >
        <Card className="border-red-200 bg-red-50 dark:bg-red-950/30 dark:border-red-800">
          <CardHeader>
            <CardTitle className="text-lg">Error Loading Insights</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              We encountered a problem while loading AI insights: {String(insightsError)}
            </p>
          </CardContent>
        </Card>
      </AnimatedContainer>
    );
  }
  
  // Empty state
  if (!insightsData?.data || insightsData.data.length === 0) {
    return (
      <AnimatedContainer 
        variant="fadeIn" 
        className={className}
      >
        <Card className="bg-primary/5 dark:bg-primary/10 border-primary/20 dark:border-primary/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              <span>AI-Powered Insights</span>
            </CardTitle>
            <CardDescription>
              Generate intelligent insights and recommendations based on your analysis data
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center p-8 text-center">
            <BrainCircuit className="h-16 w-16 text-primary/50 mb-4" />
            <h3 className="text-xl font-medium mb-2">No insights yet</h3>
            <p className="text-sm text-muted-foreground mb-6 max-w-md mx-auto">
              Generate your first AI insight to get intelligent recommendations based on your analysis data.
            </p>
            <div className="flex flex-wrap gap-3 justify-center">
              {categoriesData?.map(category => (
                <Button
                  key={category}
                  variant="outline"
                  className="flex items-center gap-2"
                  onClick={() => handleGenerateInsight(category)}
                >
                  <PlusCircle className="h-4 w-4" />
                  <span className="capitalize">{category} Insight</span>
                </Button>
              ))}
              {!categoriesData && (
                <Button
                  variant="outline"
                  className="flex items-center gap-2"
                  onClick={() => handleGenerateInsight('general')}
                >
                  <PlusCircle className="h-4 w-4" />
                  <span>General Insight</span>
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </AnimatedContainer>
    );
  }
  
  // Render insights
  return (
    <AnimatedContainer 
      variant="fadeIn" 
      className={className}
    >
      <div className="mb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight mb-1 flex items-center gap-2">
            <Brain className="h-6 w-6 text-primary" />
            <span>AI-Powered Insights</span>
          </h2>
          <p className="text-sm text-muted-foreground">
            Intelligent recommendations and insights generated from your analysis data
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Select value={selectedCategory} onValueChange={handleCategoryChange}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Categories</SelectItem>
              {categoriesData?.map(category => (
                <SelectItem key={category} value={category} className="capitalize">
                  {category}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Button
            variant="outline"
            className="flex items-center gap-2"
            onClick={() => handleGenerateInsight(
              selectedCategory !== 'all' ? selectedCategory : 'general'
            )}
          >
            <PlusCircle className="h-4 w-4" />
            <span className="hidden sm:inline">New Insight</span>
          </Button>
        </div>
      </div>
      
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 md:grid-cols-2 gap-6"
      >
        {filteredInsights.map(insight => (
          <motion.div key={insight.id} variants={itemVariants}>
            <InsightCard insight={insight} />
          </motion.div>
        ))}
        
        {/* If there are insights but none match the filter */}
        {filteredInsights.length === 0 && (
          <motion.div variants={itemVariants} className="col-span-full">
            <Card className="border-primary/10 bg-primary/5">
              <CardContent className="flex flex-col items-center justify-center p-8 text-center">
                <p className="text-sm text-muted-foreground mb-4">
                  No insights found for the selected category.
                </p>
                <Button
                  variant="outline"
                  className="flex items-center gap-2"
                  onClick={() => handleGenerateInsight(selectedCategory)}
                >
                  <PlusCircle className="h-4 w-4" />
                  <span>Generate {selectedCategory !== 'all' ? selectedCategory : 'general'} Insight</span>
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </motion.div>
    </AnimatedContainer>
  );
}; 