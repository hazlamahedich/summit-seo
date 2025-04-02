"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useProjects, useCreateAnalysis } from "@/lib/services";
import { DashboardLayout } from "@/components/ui/dashboard-layout";
import { DefaultDashboardSidebar } from "@/components/ui/dashboard-sidebar";
import { Section } from "@/components/ui/section";
import { Grid } from "@/components/ui/grid";
import { Flex } from "@/components/ui/flex";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { MotionCard } from "@/components/ui/motion-card";
import Link from "next/link";
import { 
  ChevronDown, 
  Globe, 
  Search, 
  ArrowRight, 
  Database, 
  Shield, 
  LineChart, 
  Smartphone, 
  Check, 
  Loader2
} from "lucide-react";
import ThemeSwitcher from "@/components/theme-switcher";
import { Project } from "@/types/api";

// Available analyzer types
const ANALYZER_TYPES = [
  { 
    id: "seo", 
    name: "SEO", 
    description: "Analyzes meta tags, headings, links, and other SEO factors", 
    icon: <Database className="h-5 w-5" /> 
  },
  { 
    id: "performance", 
    name: "Performance", 
    description: "Checks page load time, resource usage, and optimization opportunities", 
    icon: <LineChart className="h-5 w-5" /> 
  },
  { 
    id: "security", 
    name: "Security", 
    description: "Scans for vulnerabilities, insecure headers, and other security issues", 
    icon: <Shield className="h-5 w-5" /> 
  },
  { 
    id: "accessibility", 
    name: "Accessibility", 
    description: "Checks for WCAG compliance and accessibility best practices", 
    icon: <Smartphone className="h-5 w-5" /> 
  }
];

export default function NewAnalysisPage() {
  const router = useRouter();
  
  // State
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [customUrl, setCustomUrl] = useState("");
  const [useCustomUrl, setUseCustomUrl] = useState(false);
  const [selectedAnalyzers, setSelectedAnalyzers] = useState<string[]>(["seo", "performance"]);
  const [projectSearchTerm, setProjectSearchTerm] = useState("");
  
  // Fetch projects
  const { 
    data: projectsData, 
    isLoading: projectsLoading 
  } = useProjects({
    page: 1,
    page_size: 50,
    search: projectSearchTerm || undefined
  });
  
  // Create analysis mutation
  const createAnalysis = useCreateAnalysis(selectedProject?.id || "");
  
  // Set custom URL from selected project by default
  useEffect(() => {
    if (selectedProject) {
      setCustomUrl(selectedProject.url);
    }
  }, [selectedProject]);
  
  // Filter projects based on search term
  const filteredProjects = projectsData?.data || [];
  
  // Handle project selection
  const handleSelectProject = (project: Project) => {
    setSelectedProject(project);
    setCustomUrl(project.url);
  };
  
  // Toggle analyzer selection
  const toggleAnalyzer = (analyzerId: string) => {
    setSelectedAnalyzers(prev => 
      prev.includes(analyzerId)
        ? prev.filter(id => id !== analyzerId)
        : [...prev, analyzerId]
    );
  };
  
  // Handle analysis creation
  const handleCreateAnalysis = async () => {
    if (!selectedProject && !useCustomUrl) {
      alert("Please select a project or enter a custom URL");
      return;
    }
    
    if (useCustomUrl && !customUrl) {
      alert("Please enter a valid URL");
      return;
    }
    
    if (selectedAnalyzers.length === 0) {
      alert("Please select at least one analyzer");
      return;
    }
    
    try {
      const result = await createAnalysis.mutateAsync({
        url: useCustomUrl ? customUrl : undefined,
        analyzers: selectedAnalyzers
      });
      
      if (result.data) {
        // Redirect to the analysis page
        router.push(`/analyses/${result.data.id}`);
      }
    } catch (error) {
      console.error("Failed to create analysis:", error);
      alert("Failed to create analysis. Please try again.");
    }
  };
  
  // Dashboard header with navigation
  const navigation = (
    <>
      <Button variant="ghost" asChild>
        <Link href="/dashboard">Dashboard</Link>
      </Button>
      <Button variant="ghost" asChild>
        <Link href="/projects">Projects</Link>
      </Button>
      <Button variant="ghost" asChild>
        <Link href="/analyses">Analyses</Link>
      </Button>
      <Button variant="ghost" asChild>
        <Link href="/settings">Settings</Link>
      </Button>
    </>
  );

  // Dashboard logo
  const logo = (
    <Link href="/dashboard" className="flex items-center">
      <span className="font-bold text-xl">Summit SEO</span>
    </Link>
  );

  // Sidebar footer
  const sidebarFooter = (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <span className="text-sm text-muted-foreground">Dark Mode</span>
        <ThemeSwitcher />
      </div>
      <Button size="sm" className="w-full" asChild>
        <Link href="/support">Get Support</Link>
      </Button>
    </div>
  );
  
  return (
    <DashboardLayout
      headerLogo={logo}
      navigation={navigation}
      sidebar={<DefaultDashboardSidebar logo={logo} footer={sidebarFooter} />}
      containerSize="xl"
      contentClassName="py-6"
    >
      <Section className="mb-6">
        <h1 className="text-3xl font-bold mb-2">New Analysis</h1>
        <p className="text-muted-foreground mb-6">
          Set up a new website analysis to identify SEO issues and improvement opportunities
        </p>
        
        <Grid cols={{ default: 1, lg: 2 }} gap={6}>
          {/* Left column - Project selection */}
          <div>
            <h2 className="text-xl font-semibold mb-4">Step 1: Select a website to analyze</h2>
            
            <div className="mb-6">
              <div className="relative mb-4">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search your projects..."
                  className="pl-10"
                  value={projectSearchTerm}
                  onChange={(e) => setProjectSearchTerm(e.target.value)}
                />
              </div>
              
              <div className="border rounded-md max-h-[350px] overflow-y-auto">
                {projectsLoading ? (
                  <div className="p-4 text-center">
                    <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
                    <p>Loading projects...</p>
                  </div>
                ) : filteredProjects.length === 0 ? (
                  <div className="p-4 text-center">
                    <p>No projects found</p>
                    <Button asChild className="mt-2" variant="outline">
                      <Link href="/projects/new">Create New Project</Link>
                    </Button>
                  </div>
                ) : (
                  filteredProjects.map(project => (
                    <div
                      key={project.id}
                      className={`p-4 border-b last:border-0 cursor-pointer transition-colors hover:bg-muted/50 ${
                        selectedProject?.id === project.id ? 'bg-primary/10' : ''
                      }`}
                      onClick={() => handleSelectProject(project)}
                    >
                      <Flex justify="between" align="center">
                        <div>
                          <h3 className="font-medium">{project.name}</h3>
                          <Flex align="center" gap={2} className="text-sm text-muted-foreground">
                            <Globe className="h-3 w-3" />
                            <span className="truncate">{project.url.replace(/^https?:\/\//i, '')}</span>
                          </Flex>
                        </div>
                        {selectedProject?.id === project.id && (
                          <Check className="h-5 w-5 text-primary" />
                        )}
                      </Flex>
                    </div>
                  ))
                )}
              </div>
            </div>
            
            <div className="mb-6">
              <div className="flex items-center mb-2">
                <input
                  type="checkbox"
                  id="useCustomUrl"
                  checked={useCustomUrl}
                  onChange={() => setUseCustomUrl(!useCustomUrl)}
                  className="h-4 w-4 rounded border-gray-300 mr-2"
                />
                <Label htmlFor="useCustomUrl">Or use a custom URL instead</Label>
              </div>
              
              <Input
                placeholder="https://example.com"
                value={customUrl}
                onChange={(e) => setCustomUrl(e.target.value)}
                disabled={!useCustomUrl && !!selectedProject}
                className={!useCustomUrl && !selectedProject ? "opacity-50" : ""}
              />
            </div>
          </div>
          
          {/* Right column - Analyzer selection */}
          <div>
            <h2 className="text-xl font-semibold mb-4">Step 2: Configure analysis settings</h2>
            
            <div className="mb-6">
              <Label className="block mb-2">Select analyzers to run:</Label>
              <Grid cols={{ default: 1, md: 2 }} gap={4}>
                {ANALYZER_TYPES.map(analyzer => (
                  <MotionCard
                    key={analyzer.id}
                    variant="hover-lift"
                    className={`p-4 cursor-pointer ${
                      selectedAnalyzers.includes(analyzer.id) 
                        ? 'border-primary' 
                        : 'border-muted'
                    }`}
                    onClick={() => toggleAnalyzer(analyzer.id)}
                  >
                    <Flex gap={3}>
                      <div className={`rounded-full p-2 ${
                        selectedAnalyzers.includes(analyzer.id) 
                          ? 'bg-primary/10 text-primary' 
                          : 'bg-muted text-muted-foreground'
                      }`}>
                        {analyzer.icon}
                      </div>
                      <div>
                        <h3 className="font-medium flex items-center">
                          {analyzer.name}
                          {selectedAnalyzers.includes(analyzer.id) && (
                            <Check className="h-4 w-4 text-primary ml-1" />
                          )}
                        </h3>
                        <p className="text-sm text-muted-foreground">{analyzer.description}</p>
                      </div>
                    </Flex>
                  </MotionCard>
                ))}
              </Grid>
            </div>
          </div>
        </Grid>
        
        {/* Action buttons */}
        <Flex justify="end" gap={4} className="mt-8">
          <Button variant="outline" asChild>
            <Link href="/analyses">Cancel</Link>
          </Button>
          <Button 
            onClick={handleCreateAnalysis} 
            disabled={
              createAnalysis.isPending || 
              (!selectedProject && !useCustomUrl) || 
              (useCustomUrl && !customUrl) || 
              selectedAnalyzers.length === 0
            }
          >
            {createAnalysis.isPending ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Creating Analysis...
              </>
            ) : (
              <>
                Start Analysis
                <ArrowRight className="h-4 w-4 ml-2" />
              </>
            )}
          </Button>
        </Flex>
      </Section>
    </DashboardLayout>
  );
} 