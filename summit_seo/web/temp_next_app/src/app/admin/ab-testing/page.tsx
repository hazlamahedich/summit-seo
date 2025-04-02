"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, CheckCircle, PieChart, Plus, Trash } from "lucide-react";
import { Section } from "@/components/ui/section";
import { Grid } from "@/components/ui/grid";
import { Flex } from "@/components/ui/flex";
import { supabase } from "@/lib/supabase";
import { useAuth } from "@/contexts/auth-context";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Switch } from "@/components/ui/switch";
import { Experiment, Variant } from "@/contexts/ab-testing-context";

export default function ABTestingAdminPage() {
  const { user } = useAuth();
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [newExperimentOpen, setNewExperimentOpen] = useState(false);
  const [newExperiment, setNewExperiment] = useState({
    name: "",
    description: "",
    variants: [
      { name: "Control", weight: 50 },
      { name: "Variant A", weight: 50 }
    ]
  });
  const [selectedExperiment, setSelectedExperiment] = useState<Experiment | null>(null);
  const [experimentMetrics, setExperimentMetrics] = useState<Record<string, any>>({});

  // Load experiments
  useEffect(() => {
    const loadExperiments = async () => {
      try {
        setIsLoading(true);
        
        // Fetch all experiments
        const { data: experimentsData, error: experimentsError } = await supabase
          .from('ab_experiments')
          .select('*');
          
        if (experimentsError) {
          console.error('Error fetching experiments:', experimentsError);
          return;
        }
        
        // Fetch variants for each experiment
        const experimentsWithVariants: Experiment[] = [];
        
        for (const experiment of experimentsData) {
          const { data: variantsData, error: variantsError } = await supabase
            .from('ab_variants')
            .select('*')
            .eq('experiment_id', experiment.id);
            
          if (variantsError) {
            console.error(`Error fetching variants for experiment ${experiment.id}:`, variantsError);
            continue;
          }
          
          // Format experiment data
          experimentsWithVariants.push({
            id: experiment.id,
            name: experiment.name,
            description: experiment.description,
            active: experiment.active,
            startDate: experiment.start_date,
            endDate: experiment.end_date,
            variants: variantsData.map(variant => ({
              id: variant.id,
              name: variant.name,
              experimentId: variant.experiment_id,
              weight: variant.weight
            }))
          });
        }
        
        setExperiments(experimentsWithVariants);
        
        // Load metrics for each experiment
        await loadExperimentMetrics(experimentsWithVariants);
      } catch (error) {
        console.error('Error in loadExperiments:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadExperiments();
  }, []);
  
  // Load metrics for experiments
  const loadExperimentMetrics = async (experiments: Experiment[]) => {
    const metrics: Record<string, any> = {};
    
    for (const experiment of experiments) {
      try {
        // Fetch user assignments
        const { data: assignmentsData, error: assignmentsError } = await supabase
          .from('ab_user_experiments')
          .select('*')
          .eq('experiment_id', experiment.id);
          
        if (assignmentsError) {
          console.error(`Error fetching assignments for experiment ${experiment.id}:`, assignmentsError);
          continue;
        }
        
        // Calculate metrics
        const variantMetrics: Record<string, {
          assignments: number;
          interactions: number;
          conversions: number;
          conversionRate: number;
        }> = {};
        
        // Initialize variant metrics
        for (const variant of experiment.variants) {
          variantMetrics[variant.id] = {
            assignments: 0,
            interactions: 0,
            conversions: 0,
            conversionRate: 0
          };
        }
        
        // Calculate metrics for each variant
        for (const assignment of assignmentsData) {
          const variantId = assignment.variant_id;
          
          if (variantMetrics[variantId]) {
            variantMetrics[variantId].assignments++;
            variantMetrics[variantId].interactions += assignment.interactions || 0;
            
            if (assignment.converted) {
              variantMetrics[variantId].conversions++;
            }
          }
        }
        
        // Calculate conversion rates
        for (const variantId in variantMetrics) {
          const metric = variantMetrics[variantId];
          metric.conversionRate = metric.assignments > 0 
            ? (metric.conversions / metric.assignments) * 100 
            : 0;
        }
        
        metrics[experiment.id] = {
          variantMetrics,
          totalAssignments: assignmentsData.length,
          totalInteractions: assignmentsData.reduce((sum, a) => sum + (a.interactions || 0), 0),
          totalConversions: assignmentsData.filter(a => a.converted).length
        };
      } catch (error) {
        console.error(`Error calculating metrics for experiment ${experiment.id}:`, error);
      }
    }
    
    setExperimentMetrics(metrics);
  };
  
  // Create a new experiment
  const createExperiment = async () => {
    try {
      // Validate input
      if (!newExperiment.name || !newExperiment.description) {
        alert('Please provide a name and description for the experiment');
        return;
      }
      
      // Make sure variants have valid weights
      const totalWeight = newExperiment.variants.reduce((sum, variant) => sum + variant.weight, 0);
      if (totalWeight !== 100) {
        alert('Variant weights must sum to 100%');
        return;
      }
      
      // Create experiment
      const { data: experimentData, error: experimentError } = await supabase
        .from('ab_experiments')
        .insert({
          name: newExperiment.name,
          description: newExperiment.description,
          active: true,
          start_date: new Date().toISOString()
        })
        .select()
        .single();
        
      if (experimentError) {
        console.error('Error creating experiment:', experimentError);
        alert('Failed to create experiment');
        return;
      }
      
      // Create variants
      for (const variant of newExperiment.variants) {
        const { error: variantError } = await supabase
          .from('ab_variants')
          .insert({
            name: variant.name,
            experiment_id: experimentData.id,
            weight: variant.weight
          });
          
        if (variantError) {
          console.error('Error creating variant:', variantError);
        }
      }
      
      // Reset form and close dialog
      setNewExperiment({
        name: "",
        description: "",
        variants: [
          { name: "Control", weight: 50 },
          { name: "Variant A", weight: 50 }
        ]
      });
      setNewExperimentOpen(false);
      
      // Reload experiments
      window.location.reload();
    } catch (error) {
      console.error('Error in createExperiment:', error);
      alert('An error occurred while creating the experiment');
    }
  };
  
  // Toggle experiment active status
  const toggleExperimentActive = async (experimentId: string, active: boolean) => {
    try {
      const { error } = await supabase
        .from('ab_experiments')
        .update({
          active,
          ...(active ? {} : { end_date: new Date().toISOString() })
        })
        .eq('id', experimentId);
        
      if (error) {
        console.error('Error updating experiment:', error);
        alert('Failed to update experiment');
        return;
      }
      
      // Update local state
      setExperiments(prev => 
        prev.map(exp => 
          exp.id === experimentId 
            ? { 
                ...exp, 
                active, 
                ...(active ? {} : { endDate: new Date().toISOString() }) 
              } 
            : exp
        )
      );
    } catch (error) {
      console.error('Error in toggleExperimentActive:', error);
      alert('An error occurred while updating the experiment');
    }
  };
  
  // Add a new variant to the new experiment form
  const addVariant = () => {
    setNewExperiment(prev => ({
      ...prev,
      variants: [
        ...prev.variants,
        { name: `Variant ${String.fromCharCode(65 + prev.variants.length - 1)}`, weight: 0 }
      ]
    }));
  };
  
  // Update a variant in the new experiment form
  const updateVariant = (index: number, field: keyof typeof newExperiment.variants[0], value: any) => {
    setNewExperiment(prev => {
      const variants = [...prev.variants];
      variants[index] = { ...variants[index], [field]: field === 'weight' ? Number(value) : value };
      return { ...prev, variants };
    });
  };
  
  // Remove a variant from the new experiment form
  const removeVariant = (index: number) => {
    if (newExperiment.variants.length <= 2) {
      alert('An experiment must have at least two variants');
      return;
    }
    
    setNewExperiment(prev => {
      const variants = prev.variants.filter((_, i) => i !== index);
      return { ...prev, variants };
    });
  };
  
  // Show experiment details
  const showExperimentDetails = (experiment: Experiment) => {
    setSelectedExperiment(experiment);
  };

  return (
    <div className="p-6">
      <Section className="mb-6">
        <Flex justify="between" align="center">
          <div>
            <h1 className="text-3xl font-bold mb-2">A/B Testing Dashboard</h1>
            <p className="text-muted-foreground">
              Manage experiments and view results
            </p>
          </div>
          
          <Dialog open={newExperimentOpen} onOpenChange={setNewExperimentOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                New Experiment
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New Experiment</DialogTitle>
                <DialogDescription>
                  Set up a new A/B test to optimize your user experience.
                </DialogDescription>
              </DialogHeader>
              
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="name" className="text-right">
                    Name
                  </Label>
                  <Input
                    id="name"
                    value={newExperiment.name}
                    onChange={(e) => setNewExperiment({ ...newExperiment, name: e.target.value })}
                    className="col-span-3"
                  />
                </div>
                
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="description" className="text-right">
                    Description
                  </Label>
                  <Input
                    id="description"
                    value={newExperiment.description}
                    onChange={(e) => setNewExperiment({ ...newExperiment, description: e.target.value })}
                    className="col-span-3"
                  />
                </div>
                
                <div className="mt-4">
                  <Label className="mb-2 block">Variants</Label>
                  <p className="text-sm text-muted-foreground mb-4">
                    Define the variants for this experiment. Weights must sum to 100%.
                  </p>
                  
                  <div className="space-y-3">
                    {newExperiment.variants.map((variant, index) => (
                      <Flex key={index} align="center" gap={4}>
                        <Input
                          value={variant.name}
                          onChange={(e) => updateVariant(index, 'name', e.target.value)}
                          placeholder="Variant name"
                          className="flex-1"
                        />
                        <div className="w-24">
                          <Input
                            type="number"
                            min="0"
                            max="100"
                            value={variant.weight}
                            onChange={(e) => updateVariant(index, 'weight', e.target.value)}
                            placeholder="Weight"
                          />
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => removeVariant(index)}
                          disabled={newExperiment.variants.length <= 2}
                        >
                          <Trash className="h-4 w-4" />
                        </Button>
                      </Flex>
                    ))}
                  </div>
                  
                  <div className="mt-2">
                    <Button variant="outline" size="sm" onClick={addVariant}>
                      Add Variant
                    </Button>
                    
                    <div className="mt-2 text-sm">
                      Total Weight: {newExperiment.variants.reduce((sum, v) => sum + v.weight, 0)}%
                      {newExperiment.variants.reduce((sum, v) => sum + v.weight, 0) !== 100 && (
                        <span className="text-red-500 ml-2">
                          (Must be 100%)
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              
              <DialogFooter>
                <Button variant="outline" onClick={() => setNewExperimentOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={createExperiment}>
                  Create Experiment
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </Flex>
      </Section>
      
      <Tabs defaultValue="active">
        <TabsList className="mb-4">
          <TabsTrigger value="active">Active Experiments</TabsTrigger>
          <TabsTrigger value="completed">Completed Experiments</TabsTrigger>
          <TabsTrigger value="all">All Experiments</TabsTrigger>
        </TabsList>
        
        <TabsContent value="active">
          <Grid cols={{ default: 1, lg: 2 }} gap={6}>
            {isLoading ? (
              <p>Loading experiments...</p>
            ) : (
              experiments
                .filter(exp => exp.active)
                .map(experiment => (
                  <ExperimentCard
                    key={experiment.id}
                    experiment={experiment}
                    metrics={experimentMetrics[experiment.id]}
                    onViewDetails={() => showExperimentDetails(experiment)}
                    onToggleActive={() => toggleExperimentActive(experiment.id, !experiment.active)}
                  />
                ))
            )}
            {!isLoading && experiments.filter(exp => exp.active).length === 0 && (
              <p>No active experiments. Create one to get started!</p>
            )}
          </Grid>
        </TabsContent>
        
        <TabsContent value="completed">
          <Grid cols={{ default: 1, lg: 2 }} gap={6}>
            {isLoading ? (
              <p>Loading experiments...</p>
            ) : (
              experiments
                .filter(exp => !exp.active)
                .map(experiment => (
                  <ExperimentCard
                    key={experiment.id}
                    experiment={experiment}
                    metrics={experimentMetrics[experiment.id]}
                    onViewDetails={() => showExperimentDetails(experiment)}
                    onToggleActive={() => toggleExperimentActive(experiment.id, !experiment.active)}
                  />
                ))
            )}
            {!isLoading && experiments.filter(exp => !exp.active).length === 0 && (
              <p>No completed experiments yet.</p>
            )}
          </Grid>
        </TabsContent>
        
        <TabsContent value="all">
          <Grid cols={{ default: 1, lg: 2 }} gap={6}>
            {isLoading ? (
              <p>Loading experiments...</p>
            ) : (
              experiments.map(experiment => (
                <ExperimentCard
                  key={experiment.id}
                  experiment={experiment}
                  metrics={experimentMetrics[experiment.id]}
                  onViewDetails={() => showExperimentDetails(experiment)}
                  onToggleActive={() => toggleExperimentActive(experiment.id, !experiment.active)}
                />
              ))
            )}
            {!isLoading && experiments.length === 0 && (
              <p>No experiments found. Create one to get started!</p>
            )}
          </Grid>
        </TabsContent>
      </Tabs>
      
      {/* Experiment Details Dialog */}
      {selectedExperiment && (
        <Dialog open={!!selectedExperiment} onOpenChange={(open) => !open && setSelectedExperiment(null)}>
          <DialogContent className="max-w-4xl">
            <DialogHeader>
              <DialogTitle>{selectedExperiment.name}</DialogTitle>
              <DialogDescription>
                {selectedExperiment.description}
              </DialogDescription>
            </DialogHeader>
            
            <div className="py-4">
              <Flex justify="between" align="center" className="mb-4">
                <div>
                  <Badge variant={selectedExperiment.active ? "default" : "secondary"}>
                    {selectedExperiment.active ? "Active" : "Completed"}
                  </Badge>
                  <div className="mt-2 text-sm">
                    Started: {new Date(selectedExperiment.startDate).toLocaleDateString()}
                    {selectedExperiment.endDate && (
                      <span> • Ended: {new Date(selectedExperiment.endDate).toLocaleDateString()}</span>
                    )}
                  </div>
                </div>
                
                <Button
                  variant={selectedExperiment.active ? "destructive" : "default"}
                  onClick={() => {
                    toggleExperimentActive(selectedExperiment.id, !selectedExperiment.active);
                    setSelectedExperiment({
                      ...selectedExperiment,
                      active: !selectedExperiment.active,
                      ...(selectedExperiment.active ? { endDate: new Date().toISOString() } : {})
                    });
                  }}
                >
                  {selectedExperiment.active ? "Stop Experiment" : "Restart Experiment"}
                </Button>
              </Flex>
              
              <div className="mb-6">
                <h3 className="text-lg font-medium mb-2">Variants</h3>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Variant</TableHead>
                      <TableHead>Weight</TableHead>
                      <TableHead>Assignments</TableHead>
                      <TableHead>Interactions</TableHead>
                      <TableHead>Conversions</TableHead>
                      <TableHead>Conversion Rate</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {selectedExperiment.variants.map(variant => {
                      const metrics = experimentMetrics[selectedExperiment.id]?.variantMetrics[variant.id] || {
                        assignments: 0,
                        interactions: 0,
                        conversions: 0,
                        conversionRate: 0
                      };
                      
                      return (
                        <TableRow key={variant.id}>
                          <TableCell>{variant.name}</TableCell>
                          <TableCell>{variant.weight}%</TableCell>
                          <TableCell>{metrics.assignments}</TableCell>
                          <TableCell>{metrics.interactions}</TableCell>
                          <TableCell>{metrics.conversions}</TableCell>
                          <TableCell>{metrics.conversionRate.toFixed(2)}%</TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>
              
              <div>
                <h3 className="text-lg font-medium mb-2">Results Summary</h3>
                <Grid cols={{ default: 1, md: 3 }} gap={4}>
                  <Card>
                    <CardContent className="pt-6">
                      <div className="text-2xl font-bold">
                        {experimentMetrics[selectedExperiment.id]?.totalAssignments || 0}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Total Users
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="pt-6">
                      <div className="text-2xl font-bold">
                        {experimentMetrics[selectedExperiment.id]?.totalInteractions || 0}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Total Interactions
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="pt-6">
                      <div className="text-2xl font-bold">
                        {experimentMetrics[selectedExperiment.id]?.totalConversions || 0}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Total Conversions
                      </div>
                    </CardContent>
                  </Card>
                </Grid>
                
                {/* Recommendations based on results */}
                {experimentMetrics[selectedExperiment.id] && (
                  <Card className="mt-4">
                    <CardHeader>
                      <CardTitle>Recommendations</CardTitle>
                      <CardDescription>
                        Based on the experiment data, here are some recommendations:
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {generateRecommendations(selectedExperiment, experimentMetrics[selectedExperiment.id])}
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}

// Helper component for experiment cards
function ExperimentCard({ 
  experiment, 
  metrics, 
  onViewDetails, 
  onToggleActive 
}: { 
  experiment: Experiment; 
  metrics: any; 
  onViewDetails: () => void; 
  onToggleActive: () => void; 
}) {
  return (
    <Card>
      <CardHeader>
        <Flex justify="between" align="start">
          <div>
            <CardTitle>{experiment.name}</CardTitle>
            <CardDescription className="mt-1">
              {experiment.description}
            </CardDescription>
          </div>
          <Badge variant={experiment.active ? "default" : "secondary"}>
            {experiment.active ? "Active" : "Completed"}
          </Badge>
        </Flex>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium mb-1">Variants</h4>
            <div className="space-y-1">
              {experiment.variants.map(variant => (
                <div key={variant.id} className="text-sm flex justify-between">
                  <span>{variant.name}</span>
                  <span>{variant.weight}%</span>
                </div>
              ))}
            </div>
          </div>
          
          {metrics && (
            <div>
              <h4 className="text-sm font-medium mb-1">Metrics</h4>
              <Grid cols={{ default: 3 }} gap={2}>
                <div className="text-center">
                  <div className="text-lg font-semibold">{metrics.totalAssignments || 0}</div>
                  <div className="text-xs text-muted-foreground">Users</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold">{metrics.totalInteractions || 0}</div>
                  <div className="text-xs text-muted-foreground">Interactions</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold">{metrics.totalConversions || 0}</div>
                  <div className="text-xs text-muted-foreground">Conversions</div>
                </div>
              </Grid>
            </div>
          )}
          
          <Flex gap={2}>
            <Button variant="outline" className="flex-1" onClick={onViewDetails}>
              View Details
            </Button>
            <Button 
              variant={experiment.active ? "destructive" : "default"} 
              className="flex-1"
              onClick={onToggleActive}
            >
              {experiment.active ? "Stop" : "Restart"}
            </Button>
          </Flex>
        </div>
      </CardContent>
    </Card>
  );
}

// Generate recommendations based on experiment data
function generateRecommendations(experiment: Experiment, metrics: any) {
  if (!metrics) return <p>No data available to generate recommendations.</p>;
  
  const { variantMetrics } = metrics;
  
  // Find the variant with the highest conversion rate
  let bestVariant: { id: string; name: string; conversionRate: number } | null = null;
  let significantDifference = false;
  
  for (const variantId in variantMetrics) {
    const variant = experiment.variants.find(v => v.id === variantId);
    if (!variant) continue;
    
    const metric = variantMetrics[variantId];
    
    if (!bestVariant || metric.conversionRate > bestVariant.conversionRate) {
      // Check if this is significantly better than the previous best
      if (bestVariant && metric.conversionRate > bestVariant.conversionRate * 1.1) {
        significantDifference = true;
      }
      
      bestVariant = {
        id: variantId,
        name: variant.name,
        conversionRate: metric.conversionRate
      };
    }
  }
  
  if (!bestVariant) return <p>No conversion data available yet.</p>;
  
  // Generate recommendations
  return (
    <div className="space-y-4">
      {significantDifference ? (
        <Flex align="center" gap={2}>
          <CheckCircle className="text-green-500 h-5 w-5" />
          <div>
            <p className="font-medium">
              <span className="font-bold">{bestVariant.name}</span> is performing significantly better with a {bestVariant.conversionRate.toFixed(2)}% conversion rate.
            </p>
            <p className="text-sm text-muted-foreground">
              Consider implementing this variant permanently.
            </p>
          </div>
        </Flex>
      ) : (
        <Flex align="center" gap={2}>
          <AlertTriangle className="text-amber-500 h-5 w-5" />
          <div>
            <p className="font-medium">
              No significant difference between variants yet.
            </p>
            <p className="text-sm text-muted-foreground">
              Continue running the experiment to gather more data.
            </p>
          </div>
        </Flex>
      )}
      
      {metrics.totalAssignments < 100 && (
        <Flex align="center" gap={2}>
          <PieChart className="text-blue-500 h-5 w-5" />
          <div>
            <p className="font-medium">
              Sample size may be too small.
            </p>
            <p className="text-sm text-muted-foreground">
              Current sample: {metrics.totalAssignments} users. Consider running the experiment until you have at least 100 users per variant.
            </p>
          </div>
        </Flex>
      )}
      
      {experiment.active && experiment.startDate && new Date(experiment.startDate).getTime() < Date.now() - 30 * 24 * 60 * 60 * 1000 && (
        <Flex align="center" gap={2}>
          <AlertTriangle className="text-red-500 h-5 w-5" />
          <div>
            <p className="font-medium">
              Experiment has been running for over 30 days.
            </p>
            <p className="text-sm text-muted-foreground">
              Consider concluding this experiment and implementing the winning variant.
            </p>
          </div>
        </Flex>
      )}
    </div>
  );
} 