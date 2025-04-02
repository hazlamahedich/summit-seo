"use client";

import { useState } from "react";
import { useProjects, useCreateProject } from "@/lib/services";
import { Button } from "@/components/ui/button";

interface ProjectListProps {
  onSelectProject?: (id: string) => void;
}

/**
 * Example project list component demonstrating React Query and API service usage
 */
export function ProjectList({ onSelectProject }: ProjectListProps) {
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const [searchTerm, setSearchTerm] = useState("");
  
  // Query projects with pagination and search
  const { data: projectsData, isLoading, error } = useProjects({
    page,
    page_size: pageSize,
    search: searchTerm || undefined,
  });
  
  // Mutation for creating a project
  const createProject = useCreateProject();
  
  // Handle creating a new project
  const handleCreateProject = () => {
    createProject.mutate({
      name: "New Project",
      description: "Created from example component",
      url: "https://example.com",
      tags: ["example"],
      status: "active",
      settings: {},
    });
  };
  
  // Handle pagination
  const handleNextPage = () => {
    if (projectsData?.pagination && projectsData.pagination.page < projectsData.pagination.pages) {
      setPage(page + 1);
    }
  };
  
  const handlePrevPage = () => {
    if (page > 1) {
      setPage(page - 1);
    }
  };
  
  // Handle search
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setPage(1); // Reset to first page when searching
  };

  // Handle project selection
  const handleSelectProject = (id: string) => {
    if (onSelectProject) {
      onSelectProject(id);
    }
  };
  
  if (isLoading) {
    return <div className="p-4">Loading projects...</div>;
  }
  
  if (error) {
    return <div className="p-4 text-red-500">Error: {String(error)}</div>;
  }
  
  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Projects</h2>
        <Button onClick={handleCreateProject} disabled={createProject.isPending}>
          {createProject.isPending ? "Creating..." : "Create Project"}
        </Button>
      </div>
      
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search projects..."
          className="px-3 py-2 border rounded w-full"
          value={searchTerm}
          onChange={handleSearch}
        />
      </div>
      
      {!projectsData?.data?.length ? (
        <div className="p-4 text-center">No projects found</div>
      ) : (
        <>
          <div className="grid gap-4">
            {projectsData.data.map((project) => (
              <div
                key={project.id}
                className="p-4 border rounded shadow hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => handleSelectProject(project.id)}
              >
                <h3 className="text-xl font-semibold">{project.name}</h3>
                <p className="text-gray-600">{project.description}</p>
                <div className="mt-2 flex flex-wrap gap-1">
                  {project.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-4 flex justify-between items-center">
            <div className="text-sm text-gray-600">
              Showing {projectsData.pagination?.page || 1} of {projectsData.pagination?.pages || 1} pages
            </div>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                onClick={handlePrevPage} 
                disabled={page <= 1}
              >
                Previous
              </Button>
              <Button 
                variant="outline" 
                onClick={handleNextPage} 
                disabled={!projectsData?.pagination || projectsData.pagination.page >= projectsData.pagination.pages}
              >
                Next
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
} 