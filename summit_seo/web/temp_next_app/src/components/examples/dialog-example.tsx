"use client"

import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";

export function DialogExample() {
  const { toast } = useToast();
  const [open, setOpen] = React.useState(false);
  const [url, setUrl] = React.useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) {
      toast({
        title: "Validation Error",
        description: "Please enter a valid URL",
        variant: "destructive",
      });
      return;
    }
    
    toast({
      title: "Analysis Started",
      description: `Starting analysis for ${url}`,
      variant: "success",
    });
    
    setOpen(false);
    
    // Reset the form
    setUrl("");
  };

  return (
    <div className="flex flex-col items-center space-y-4">
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <Button size="lg">Start New Analysis</Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Start Website Analysis</DialogTitle>
            <DialogDescription>
              Enter the URL of the website you want to analyze. We'll generate a comprehensive SEO report.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="url" className="text-right">
                  Website URL
                </Label>
                <Input
                  id="url"
                  placeholder="https://example.com"
                  className="col-span-3"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                />
              </div>
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="depth" className="text-right">
                  Scan Depth
                </Label>
                <select 
                  id="depth" 
                  className="col-span-3 flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <option value="1">Basic (Homepage only)</option>
                  <option value="2">Standard (Up to 2 levels deep)</option>
                  <option value="3">Comprehensive (Up to 3 levels deep)</option>
                </select>
              </div>
            </div>
            <DialogFooter>
              <Button type="submit">Start Analysis</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
      
      <p className="text-center text-sm text-muted-foreground max-w-md mt-4">
        Our analysis tool scans your website for SEO issues, accessibility problems, performance bottlenecks, and security vulnerabilities.
      </p>
    </div>
  );
} 