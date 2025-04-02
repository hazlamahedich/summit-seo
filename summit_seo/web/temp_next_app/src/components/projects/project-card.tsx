"use client";

import { useState } from 'react';
import { Project } from "@/types/api";
import { MotionCard } from "@/components/ui/motion-card";
import { Flex } from "@/components/ui/flex";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { Globe, Calendar, BarChart2, MoreHorizontal } from 'lucide-react';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu";
import { useRouter } from "next/navigation";
import { useDeleteProject } from "@/lib/services";
import { formatDistanceToNow } from 'date-fns';

export interface ProjectCardProps {
  project: Project;
  onEdit?: (project: Project) => void;
}

export function ProjectCard({ project, onEdit }: ProjectCardProps) {
  const router = useRouter();
  const deleteProject = useDeleteProject();
  const [isDeleting, setIsDeleting] = useState(false);
  
  // Format the date for display
  const formattedDate = formatDistanceToNow(new Date(project.updated_at), { addSuffix: true });
  
  // Handle project deletion
  const handleDelete = async () => {
    if (confirm("Are you sure you want to delete this project? This action cannot be undone.")) {
      setIsDeleting(true);
      try {
        await deleteProject.mutateAsync(project.id);
      } catch (error) {
        console.error("Failed to delete project:", error);
        alert("Failed to delete project. Please try again.");
      } finally {
        setIsDeleting(false);
      }
    }
  };
  
  return (
    <MotionCard 
      variant="hover-lift" 
      className="p-5 h-full"
      intensity="medium"
    >
      <Flex direction="col" className="h-full">
        <Flex justify="between" className="mb-3">
          <h3 className="text-xl font-semibold line-clamp-1">{project.name}</h3>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="rounded-full h-8 w-8">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onEdit?.(project)}>
                Edit Project
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleDelete} disabled={isDeleting} className="text-red-500">
                {isDeleting ? "Deleting..." : "Delete Project"}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </Flex>
        
        <p className="text-muted-foreground mb-4 line-clamp-2">{project.description}</p>
        
        <Flex className="mb-3">
          <Flex align="center" gap={2} className="text-sm text-muted-foreground">
            <Globe className="h-4 w-4" />
            <a 
              href={project.url} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="hover:underline truncate max-w-[200px]"
            >
              {project.url.replace(/^https?:\/\//i, '')}
            </a>
          </Flex>
        </Flex>
        
        <Flex className="mb-4">
          <Flex align="center" gap={2} className="text-sm text-muted-foreground">
            <Calendar className="h-4 w-4" />
            <span>Updated {formattedDate}</span>
          </Flex>
        </Flex>
        
        <Flex gap={2} className="mb-4 flex-wrap">
          {project.tags.map((tag) => (
            <Badge key={tag} variant="outline" className="capitalize">
              {tag}
            </Badge>
          ))}
        </Flex>
        
        {/* Push the button to the bottom */}
        <div className="mt-auto">
          <Button asChild className="w-full">
            <Link href={`/projects/${project.id}`}>
              <Flex gap={2} align="center" justify="center">
                <BarChart2 className="h-4 w-4" />
                <span>View Project</span>
              </Flex>
            </Link>
          </Button>
        </div>
      </Flex>
    </MotionCard>
  );
} 