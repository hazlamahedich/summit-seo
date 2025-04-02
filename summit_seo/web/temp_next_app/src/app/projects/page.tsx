"use client";

import { useState } from "react";
import { Project } from "@/types/api";
import { useProjects } from "@/lib/services";
import { DashboardLayout } from "@/components/ui/dashboard-layout";
import { DefaultDashboardSidebar } from "@/components/ui/dashboard-sidebar";
import { Section } from "@/components/ui/section";
import { Grid } from "@/components/ui/grid";
import { Flex } from "@/components/ui/flex";
import { Button } from "@/components/ui/button";
import { ProjectCard } from "@/components/projects/project-card";
import { ProjectForm } from "@/components/projects/project-form";
import Link from "next/link";
import { Plus, Search, Filter, RefreshCw } from "lucide-react";
import ThemeSwitcher from "@/components/theme-switcher";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

export default function ProjectsPage() {
  // State for project form
  const [formOpen, setFormOpen] = useState(false);
  const [editProject, setEditProject] = useState<Project | undefined>(undefined);
  const [searchTerm, setSearchTerm] = useState("");
  const [page, setPage] = useState(1);
  const pageSize = 12;

  // Fetch projects
  const { 
    data: projectsData, 
    isLoading, 
    error,
    refetch
  } = useProjects({
    page,
    page_size: pageSize,
    search: searchTerm || undefined,
  });

  // Handle edit project action
  const handleEdit = (project: Project) => {
    setEditProject(project);
    setFormOpen(true);
  };

  // Handle form close
  const handleFormClose = () => {
    setFormOpen(false);
    setEditProject(undefined);
  };

  // Handle search
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setPage(1);
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
    <>
      <DashboardLayout
        headerLogo={logo}
        navigation={navigation}
        sidebar={<DefaultDashboardSidebar logo={logo} footer={sidebarFooter} />}
        containerSize="xl"
        contentClassName="py-6"
      >
        <Section className="mb-6">
          <Flex justify="between" align="center" className="mb-4">
            <h1 className="text-3xl font-bold">Projects</h1>
            <Button onClick={() => setFormOpen(true)}>
              <Flex gap={2} align="center">
                <Plus className="h-4 w-4" />
                New Project
              </Flex>
            </Button>
          </Flex>
          
          <p className="text-muted-foreground mb-6">
            Manage your websites and SEO projects
          </p>
          
          {/* Search and filters */}
          <Flex gap={4} className="mb-8">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search projects..."
                className="pl-10"
                value={searchTerm}
                onChange={handleSearch}
              />
            </div>
            <Button variant="outline" size="icon" onClick={() => refetch()}>
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button variant="outline">
              <Flex gap={2} align="center">
                <Filter className="h-4 w-4" />
                Filters
              </Flex>
            </Button>
          </Flex>
          
          {isLoading ? (
            // Loading state
            <div className="py-12 text-center">
              <div className="inline-block animate-spin mr-2">
                <RefreshCw className="h-6 w-6" />
              </div>
              <p>Loading projects...</p>
            </div>
          ) : error ? (
            // Error state
            <div className="py-12 text-center text-red-500">
              <p>Error loading projects. Please try again.</p>
              <Button variant="outline" className="mt-4" onClick={() => refetch()}>
                Retry
              </Button>
            </div>
          ) : !projectsData?.data?.length ? (
            // Empty state
            <div className="py-12 text-center border rounded-lg">
              <h3 className="text-xl font-medium mb-2">No projects found</h3>
              <p className="text-muted-foreground mb-4">
                {searchTerm 
                  ? `No projects match "${searchTerm}"`
                  : "Get started by creating your first project"}
              </p>
              
              <Button onClick={() => setFormOpen(true)}>
                <Flex gap={2} align="center">
                  <Plus className="h-4 w-4" />
                  Create New Project
                </Flex>
              </Button>
            </div>
          ) : (
            // Projects grid
            <>
              <Grid
                cols={{ default: 1, sm: 2, lg: 3, xl: 4 }}
                gap={6}
                className="mb-8"
              >
                {projectsData.data.map((project) => (
                  <ProjectCard
                    key={project.id}
                    project={project}
                    onEdit={handleEdit}
                  />
                ))}
              </Grid>
              
              {/* Pagination */}
              {projectsData.pagination && projectsData.pagination.pages > 1 && (
                <Flex justify="between" align="center" className="mt-6">
                  <div className="text-sm text-muted-foreground">
                    Showing {((page - 1) * pageSize) + 1} - {Math.min(page * pageSize, projectsData.pagination.total)} of {projectsData.pagination.total} projects
                  </div>
                  <Flex gap={2}>
                    <Button
                      variant="outline"
                      disabled={page <= 1}
                      onClick={() => setPage(page - 1)}
                    >
                      Previous
                    </Button>
                    {Array.from({ length: Math.min(3, projectsData.pagination.pages) }, (_, i) => {
                      // Show first page, current page, and last page
                      let pageNum;
                      if (i === 0) pageNum = 1;
                      else if (i === 1 && projectsData.pagination.pages <= 3) pageNum = 2;
                      else if (i === 1) pageNum = page;
                      else pageNum = projectsData.pagination.pages;
                      
                      return (
                        <Button
                          key={pageNum}
                          variant={pageNum === page ? "default" : "outline"}
                          onClick={() => setPage(pageNum)}
                          className="w-10"
                        >
                          {pageNum}
                        </Button>
                      );
                    })}
                    <Button
                      variant="outline"
                      disabled={page >= projectsData.pagination.pages}
                      onClick={() => setPage(page + 1)}
                    >
                      Next
                    </Button>
                  </Flex>
                </Flex>
              )}
            </>
          )}
        </Section>
      </DashboardLayout>
      
      {/* Project form */}
      <ProjectForm 
        isOpen={formOpen} 
        onClose={handleFormClose} 
        editProject={editProject} 
      />
    </>
  );
} 