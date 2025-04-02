"use client";

import { useState } from "react";
import { 
  useProjects, 
  useCreateProject, 
  useUpdateProject, 
  useDeleteProject 
} from "@/lib/services";
import { Button } from "@/components/ui/button";
import { Project } from "@/types/api";

/**
 * Example component demonstrating optimistic updates with React Query
 */
export function OptimisticDemo() {
  const [projectName, setProjectName] = useState("New Optimistic Project");
  const [selectedProject, setSelectedProject] = useState<string | null>(null);
  
  // Query projects
  const { data: projectsData, isLoading, error } = useProjects({
    page: 1,
    page_size: 10
  });
  
  // Mutations with optimistic updates
  const createProject = useCreateProject();
  const updateProject = useUpdateProject(selectedProject || "");
  const deleteProject = useDeleteProject();
  
  // Handle creating a new project
  const handleCreateProject = () => {
    createProject.mutate({
      name: projectName,
      description: "Created with optimistic updates",
      url: "https://example.com",
      tags: ["optimistic", "demo"],
      status: "active",
      settings: {},
    });
    
    // Reset the input
    setProjectName("New Optimistic Project");
  };
  
  // Handle updating a project
  const handleUpdateProject = () => {
    if (!selectedProject) return;
    
    updateProject.mutate({
      name: `${projectName} (Updated)`,
      description: "Updated with optimistic updates",
    });
  };
  
  // Handle deleting a project
  const handleDeleteProject = () => {
    if (!selectedProject) return;
    
    deleteProject.mutate(selectedProject);
    setSelectedProject(null);
  };
  
  if (isLoading) {
    return <div className="p-4">Loading projects...</div>;
  }
  
  if (error) {
    return <div className="p-4 text-red-500">Error: {String(error)}</div>;
  }
  
  return (
    <div className="p-4 space-y-8">
      <div className="p-4 border rounded-lg bg-card">
        <h2 className="text-2xl font-bold mb-4">Optimistic Updates Demo</h2>
        <p className="mb-4 text-muted-foreground">
          This component demonstrates React Query's optimistic updates. Create, update, or delete 
          projects and observe how the UI updates immediately, even before the server responds.
        </p>
        
        <div className="flex flex-col space-y-4 sm:flex-row sm:space-y-0 sm:space-x-4">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">Project Name</label>
            <input
              type="text"
              className="w-full px-3 py-2 border rounded"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
            />
          </div>
          
          <div className="flex space-x-2 sm:self-end">
            <Button
              onClick={handleCreateProject}
              disabled={createProject.isPending}
              className="whitespace-nowrap"
            >
              {createProject.isPending ? "Creating..." : "Create Project"}
            </Button>
            
            <Button
              onClick={handleUpdateProject}
              disabled={updateProject.isPending || !selectedProject}
              variant="outline"
              className="whitespace-nowrap"
            >
              {updateProject.isPending ? "Updating..." : "Update Selected"}
            </Button>
            
            <Button
              onClick={handleDeleteProject}
              disabled={deleteProject.isPending || !selectedProject}
              variant="destructive"
              className="whitespace-nowrap"
            >
              {deleteProject.isPending ? "Deleting..." : "Delete Selected"}
            </Button>
          </div>
        </div>
      </div>
      
      <div className="grid gap-4">
        <h3 className="text-xl font-semibold">Projects</h3>
        
        {!projectsData?.data?.length ? (
          <div className="p-4 text-center border rounded">No projects found</div>
        ) : (
          projectsData.data.map((project: Project) => (
            <div
              key={project.id}
              className={`p-4 border rounded cursor-pointer transition-colors ${
                selectedProject === project.id
                  ? "border-primary bg-primary/5"
                  : "hover:bg-muted/50"
              }`}
              onClick={() => setSelectedProject(project.id)}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-semibold">{project.name}</h3>
                  <p className="text-muted-foreground">{project.description}</p>
                  
                  <div className="mt-2 flex flex-wrap gap-1">
                    {project.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-0.5 bg-secondary text-secondary-foreground rounded-full text-xs"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div className="text-sm text-muted-foreground">
                  {project.id.startsWith("temp-") ? (
                    <span className="inline-flex items-center px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs">
                      Creating...
                    </span>
                  ) : (
                    <span className="text-xs">ID: {project.id.substring(0, 8)}...</span>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
} 