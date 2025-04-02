"use client";

import { useState } from "react";
import { ProjectList } from "@/components/examples/project-list";
import { AnalysisList } from "@/components/examples/analysis-list";
import { OptimisticDemo } from "@/components/examples/optimistic-demo";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Container } from "@/components/ui/container";
import { Section } from "@/components/ui/section";

/**
 * Demo page showcasing API service layer and React Query integration
 */
export default function DataDemoPage() {
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);
  
  return (
    <Container className="max-w-6xl mx-auto">
      <Section>
        <h1 className="text-3xl font-bold mb-2">Data Management Demo</h1>
        <p className="text-muted-foreground mb-8">
          This page demonstrates the API service layer, React Query integration, and optimistic updates.
        </p>
        
        <Tabs defaultValue="projects" className="w-full">
          <TabsList className="mb-8">
            <TabsTrigger value="projects">Projects</TabsTrigger>
            <TabsTrigger 
              value="analyses" 
              disabled={!selectedProjectId}
              title={!selectedProjectId ? "Select a project first" : "View analyses"}
            >
              Analyses
            </TabsTrigger>
            <TabsTrigger value="optimistic">Optimistic Updates</TabsTrigger>
          </TabsList>
          
          <TabsContent value="projects">
            <div className="bg-card p-6 rounded-lg border">
              <ProjectList onSelectProject={(id) => setSelectedProjectId(id)} />
            </div>
          </TabsContent>
          
          <TabsContent value="analyses">
            {selectedProjectId && (
              <div className="bg-card p-6 rounded-lg border">
                <AnalysisList projectId={selectedProjectId} />
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="optimistic">
            <div className="bg-card p-6 rounded-lg border">
              <OptimisticDemo />
            </div>
          </TabsContent>
        </Tabs>
      </Section>
    </Container>
  );
} 