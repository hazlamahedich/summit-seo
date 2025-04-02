'use client';

import { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { getExperimentStats, endExperiment } from "@/utils/ab-test-utils";
import { useABTesting } from "@/contexts/ab-testing-context";
import { Experiment } from "@/contexts/ab-testing-context";
import { 
  Dialog, 
  DialogContent, 
  DialogDescription, 
  DialogFooter, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { 
  Form, 
  FormControl, 
  FormDescription, 
  FormField, 
  FormItem, 
  FormLabel, 
  FormMessage 
} from "@/components/ui/form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { Loader2, Plus, X, RefreshCcw, BarChart } from "lucide-react";
import { motion } from "framer-motion";

interface ExperimentStats {
  experiment: any;
  variantStats: Array<{
    variant: any;
    totalUsers: number;
    interactionCount: number;
    conversionCount: number;
    conversionRate: number;
  }>;
}

// Form schema for creating a new experiment
const formSchema = z.object({
  name: z.string().min(2, {
    message: "Experiment name must be at least 2 characters.",
  }),
  description: z.string().optional(),
  variantA: z.string().min(1, {
    message: "Variant A name is required.",
  }),
  variantB: z.string().min(1, {
    message: "Variant B name is required.",
  }),
  weightA: z.coerce.number().int().min(1).max(100),
  weightB: z.coerce.number().int().min(1).max(100),
});

export function ABTestAdminDashboard() {
  const { experiments, loadExperiments, createExperiment } = useABTesting();
  const [loading, setLoading] = useState(true);
  const [statsMap, setStatsMap] = useState<Map<string, ExperimentStats>>(new Map());
  const [isLoadingStats, setIsLoadingStats] = useState<string[]>([]);
  const [openDialog, setOpenDialog] = useState(false);
  const { toast } = useToast();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      description: "",
      variantA: "Control",
      variantB: "Variant",
      weightA: 50,
      weightB: 50,
    },
  });

  useEffect(() => {
    const fetchData = async () => {
      await loadExperiments();
      setLoading(false);
    };

    fetchData();
  }, [loadExperiments]);

  // Load statistics for an experiment
  const loadStats = async (experimentId: string) => {
    setIsLoadingStats(prev => [...prev, experimentId]);
    
    try {
      const stats = await getExperimentStats(experimentId);
      if (stats) {
        setStatsMap(prev => new Map(prev).set(experimentId, stats));
      }
    } catch (error) {
      console.error('Error loading stats:', error);
      toast({
        title: "Error",
        description: "Failed to load experiment statistics",
        variant: "destructive",
      });
    } finally {
      setIsLoadingStats(prev => prev.filter(id => id !== experimentId));
    }
  };

  // End an experiment
  const handleEndExperiment = async (experimentId: string) => {
    try {
      const success = await endExperiment(experimentId);
      
      if (success) {
        toast({
          title: "Success",
          description: "Experiment ended successfully",
        });
        
        // Reload experiments
        await loadExperiments();
        
        // Reload stats if available
        if (statsMap.has(experimentId)) {
          await loadStats(experimentId);
        }
      } else {
        toast({
          title: "Error",
          description: "Failed to end experiment",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error ending experiment:', error);
      toast({
        title: "Error",
        description: "Failed to end experiment",
        variant: "destructive",
      });
    }
  };

  // Create a new experiment
  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    try {
      // Create variants array
      const variants = [
        { name: values.variantA, weight: values.weightA },
        { name: values.variantB, weight: values.weightB },
      ];
      
      const experimentId = await createExperiment(
        values.name, 
        values.description || null,
        variants
      );
      
      if (experimentId) {
        toast({
          title: "Success",
          description: "Experiment created successfully",
        });
        
        // Reset form
        form.reset();
        
        // Close dialog
        setOpenDialog(false);
        
        // Reload experiments
        await loadExperiments();
      } else {
        toast({
          title: "Error",
          description: "Failed to create experiment",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error creating experiment:', error);
      toast({
        title: "Error",
        description: "Failed to create experiment",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">A/B Testing</h2>
          <p className="text-muted-foreground">
            Manage and monitor A/B testing experiments
          </p>
        </div>
        
        <Dialog open={openDialog} onOpenChange={setOpenDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Experiment
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[525px]">
            <DialogHeader>
              <DialogTitle>Create New Experiment</DialogTitle>
              <DialogDescription>
                Set up a new A/B testing experiment with two variants.
              </DialogDescription>
            </DialogHeader>
            
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Experiment Name</FormLabel>
                      <FormControl>
                        <Input placeholder="Dashboard Layout" {...field} />
                      </FormControl>
                      <FormDescription>
                        A unique name to identify this experiment
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <FormField
                  control={form.control}
                  name="description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Description (Optional)</FormLabel>
                      <FormControl>
                        <Input placeholder="Testing different dashboard layouts" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="variantA"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Variant A Name</FormLabel>
                          <FormControl>
                            <Input {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="weightA"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Weight (%)</FormLabel>
                          <FormControl>
                            <Input type="number" min="1" max="100" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                  
                  <div className="space-y-4">
                    <FormField
                      control={form.control}
                      name="variantB"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Variant B Name</FormLabel>
                          <FormControl>
                            <Input {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="weightB"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Weight (%)</FormLabel>
                          <FormControl>
                            <Input type="number" min="1" max="100" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>
                
                <DialogFooter>
                  <Button type="submit">Create Experiment</Button>
                </DialogFooter>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>
      
      <div className="grid gap-4">
        {loading ? (
          <Card>
            <CardContent className="p-8 flex justify-center">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </CardContent>
          </Card>
        ) : experiments.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <p className="text-muted-foreground">No experiments found</p>
              <p className="text-sm text-muted-foreground mt-2">
                Create a new experiment to get started with A/B testing
              </p>
            </CardContent>
          </Card>
        ) : (
          <div>
            {experiments.map((experiment) => (
              <motion.div
                key={experiment.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.3 }}
                className="mb-4"
              >
                <Card>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle>{experiment.name}</CardTitle>
                        <CardDescription>
                          {experiment.description || "No description provided"}
                        </CardDescription>
                      </div>
                      <Badge variant={experiment.active ? "default" : "secondary"}>
                        {experiment.active ? "Active" : "Inactive"}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="text-sm">
                        <span className="font-medium">Started:</span>{" "}
                        {new Date(experiment.start_date).toLocaleDateString()}
                      </div>
                      {experiment.end_date && (
                        <div className="text-sm">
                          <span className="font-medium">Ended:</span>{" "}
                          {new Date(experiment.end_date).toLocaleDateString()}
                        </div>
                      )}
                      
                      {experiment.variants && experiment.variants.length > 0 && (
                        <div className="mt-4">
                          <h4 className="font-medium mb-2">Variants</h4>
                          <div className="grid grid-cols-2 gap-2">
                            {experiment.variants.map((variant) => (
                              <Card key={variant.id} className="bg-muted/50">
                                <CardContent className="p-3">
                                  <div className="font-medium">{variant.name}</div>
                                  <div className="text-sm text-muted-foreground">
                                    Weight: {variant.weight}%
                                  </div>
                                </CardContent>
                              </Card>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {statsMap.has(experiment.id) && (
                        <div className="mt-6">
                          <h4 className="font-medium mb-2">Statistics</h4>
                          <Table>
                            <TableHeader>
                              <TableRow>
                                <TableHead>Variant</TableHead>
                                <TableHead className="text-right">Users</TableHead>
                                <TableHead className="text-right">Interactions</TableHead>
                                <TableHead className="text-right">Conversions</TableHead>
                                <TableHead className="text-right">Conversion Rate</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {statsMap.get(experiment.id)?.variantStats.map((stats) => (
                                <TableRow key={stats.variant.id}>
                                  <TableCell className="font-medium">
                                    {stats.variant.name}
                                  </TableCell>
                                  <TableCell className="text-right">{stats.totalUsers}</TableCell>
                                  <TableCell className="text-right">{stats.interactionCount}</TableCell>
                                  <TableCell className="text-right">{stats.conversionCount}</TableCell>
                                  <TableCell className="text-right">
                                    {stats.conversionRate.toFixed(1)}%
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </div>
                      )}
                    </div>
                  </CardContent>
                  <CardFooter className="flex justify-between">
                    {!statsMap.has(experiment.id) ? (
                      <Button 
                        variant="outline" 
                        onClick={() => loadStats(experiment.id)}
                        disabled={isLoadingStats.includes(experiment.id)}
                      >
                        {isLoadingStats.includes(experiment.id) ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Loading...
                          </>
                        ) : (
                          <>
                            <BarChart className="mr-2 h-4 w-4" />
                            View Statistics
                          </>
                        )}
                      </Button>
                    ) : (
                      <Button 
                        variant="outline"
                        onClick={() => loadStats(experiment.id)}
                        disabled={isLoadingStats.includes(experiment.id)}
                      >
                        {isLoadingStats.includes(experiment.id) ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Refreshing...
                          </>
                        ) : (
                          <>
                            <RefreshCcw className="mr-2 h-4 w-4" />
                            Refresh Stats
                          </>
                        )}
                      </Button>
                    )}
                    
                    {experiment.active && (
                      <Button 
                        variant="destructive"
                        onClick={() => handleEndExperiment(experiment.id)}
                      >
                        <X className="mr-2 h-4 w-4" />
                        End Experiment
                      </Button>
                    )}
                  </CardFooter>
                </Card>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
} 