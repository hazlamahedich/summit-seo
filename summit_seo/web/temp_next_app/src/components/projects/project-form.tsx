"use client";

import { useState, useEffect } from 'react';
import { Project } from "@/types/api";
import { 
  useCreateProject, 
  useUpdateProject,
  useProjectTags 
} from "@/lib/services";
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle,
  DialogFooter,
  DialogClose
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Flex } from "@/components/ui/flex";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { X, Plus } from "lucide-react";

interface ProjectFormProps {
  isOpen: boolean;
  onClose: () => void;
  editProject?: Project;
}

export function ProjectForm({ isOpen, onClose, editProject }: ProjectFormProps) {
  // State for form fields
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [url, setUrl] = useState("https://");
  const [tags, setTags] = useState<string[]>([]);
  const [currentTag, setCurrentTag] = useState("");
  
  // Mutations for creating and updating projects
  const createProject = useCreateProject();
  const updateProject = useUpdateProject(editProject?.id || "");
  
  // Query for getting all project tags
  const { data: existingTags } = useProjectTags();
  
  // Populate form when editing an existing project
  useEffect(() => {
    if (editProject) {
      setName(editProject.name);
      setDescription(editProject.description || "");
      setUrl(editProject.url);
      setTags(editProject.tags || []);
    } else {
      // Reset form when creating a new project
      setName("");
      setDescription("");
      setUrl("https://");
      setTags([]);
    }
  }, [editProject, isOpen]);
  
  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    if (!name || !url) {
      alert("Please fill out all required fields");
      return;
    }
    
    try {
      const projectData = {
        name,
        description,
        url,
        tags,
        status: "active",
        settings: {}
      };
      
      if (editProject) {
        // Update existing project
        await updateProject.mutateAsync(projectData);
      } else {
        // Create new project
        await createProject.mutateAsync(projectData);
      }
      
      // Close form after successful operation
      onClose();
    } catch (error) {
      console.error("Error saving project:", error);
      alert("Failed to save project. Please try again.");
    }
  };
  
  // Handle adding a tag
  const handleAddTag = () => {
    if (currentTag && !tags.includes(currentTag)) {
      setTags([...tags, currentTag]);
      setCurrentTag("");
    }
  };
  
  // Handle pressing Enter in the tag input
  const handleTagKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAddTag();
    }
  };
  
  // Handle removing a tag
  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };
  
  // Handle selecting an existing tag
  const handleSelectExistingTag = (tag: string) => {
    if (!tags.includes(tag)) {
      setTags([...tags, tag]);
    }
  };
  
  // Filter existing tags that are not already selected
  const filteredExistingTags = (existingTags || []).filter(
    (tag: string) => !tags.includes(tag)
  );
  
  return (
    <Dialog open={isOpen} onOpenChange={(open: boolean) => !open && onClose()}>
      <DialogContent className="sm:max-w-[550px]">
        <DialogHeader>
          <DialogTitle>
            {editProject ? "Edit Project" : "Create New Project"}
          </DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit}>
          <div className="grid gap-5 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name" className="required">Project Name</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="My Awesome Website"
                required
              />
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="A brief description of your project"
              />
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="url" className="required">Website URL</Label>
              <Input
                id="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com"
                required
              />
            </div>
            
            <div className="grid gap-2">
              <Label htmlFor="tags">Tags</Label>
              <Flex className="flex-wrap gap-2 mb-2">
                {tags.map((tag) => (
                  <Badge key={tag} className="flex gap-1 items-center pl-2">
                    {tag}
                    <button
                      type="button"
                      onClick={() => handleRemoveTag(tag)}
                      className="rounded-full hover:bg-muted p-0.5"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </Flex>
              
              <Flex gap={2}>
                <Input
                  id="tags"
                  value={currentTag}
                  onChange={(e) => setCurrentTag(e.target.value)}
                  onKeyDown={handleTagKeyDown}
                  placeholder="Add a tag"
                  className="flex-1"
                />
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={handleAddTag}
                  disabled={!currentTag || tags.includes(currentTag)}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </Flex>
              
              {filteredExistingTags.length > 0 && (
                <div className="mt-2">
                  <Label className="text-xs mb-1 block">Existing Tags</Label>
                  <Flex className="flex-wrap gap-1">
                    {filteredExistingTags.map((tag: string) => (
                      <Badge 
                        key={tag} 
                        variant="outline" 
                        className="cursor-pointer hover:bg-primary hover:text-primary-foreground"
                        onClick={() => handleSelectExistingTag(tag)}
                      >
                        {tag}
                      </Badge>
                    ))}
                  </Flex>
                </div>
              )}
            </div>
          </div>
          
          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="outline">Cancel</Button>
            </DialogClose>
            <Button 
              type="submit" 
              disabled={createProject.isPending || updateProject.isPending}
            >
              {(createProject.isPending || updateProject.isPending) 
                ? "Saving..." 
                : editProject ? "Update Project" : "Create Project"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
} 