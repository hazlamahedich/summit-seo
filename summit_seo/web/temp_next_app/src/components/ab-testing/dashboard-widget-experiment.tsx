'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { useABTestVariant } from "@/hooks/useABTestVariant";
import { Bar, BarChart, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';
import { ArrowUpRight, TrendingUp, CheckCircle } from 'lucide-react';

// Dashboard widget experiment ID
const EXPERIMENT_ID = 'dashboard-widget-layout';

interface WidgetProps {
  title: string;
  description: string;
  data: Array<{
    name: string;
    value: number;
  }>;
  onAction?: () => void;
}

export function DashboardWidgetExperiment({ 
  title, 
  description, 
  data, 
  onAction 
}: WidgetProps) {
  const { variantId, trackInteraction, trackConversion } = useABTestVariant(
    EXPERIMENT_ID, 
    true // track initial view
  );
  const { toast } = useToast();
  
  const handleAction = () => {
    // Track the interaction and conversion
    trackInteraction();
    trackConversion();
    
    // Show a toast
    toast({
      title: "Action Tracked",
      description: `Interaction tracked for variant: ${variantId || 'default'}`
    });
    
    // Call the parent callback
    onAction?.();
  };
  
  // If no variant assigned or still loading, show the default widget
  // Or if the variant is specifically "control"
  if (!variantId || variantId === 'control') {
    return <DefaultWidget 
      title={title} 
      description={description} 
      data={data} 
      onAction={handleAction}
    />;
  }
  
  // Show variant A (modern layout)
  if (variantId === 'variant-a') {
    return <ModernWidget 
      title={title} 
      description={description} 
      data={data} 
      onAction={handleAction}
    />;
  }
  
  // Show variant B (compact layout)
  if (variantId === 'variant-b') {
    return <CompactWidget 
      title={title} 
      description={description} 
      data={data} 
      onAction={handleAction}
    />;
  }
  
  // Fallback to default widget
  return <DefaultWidget 
    title={title} 
    description={description} 
    data={data} 
    onAction={handleAction}
  />;
}

// Default widget layout (control)
function DefaultWidget({ title, description, data, onAction }: WidgetProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-60">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
      <CardFooter>
        <Button onClick={onAction}>View Details</Button>
      </CardFooter>
    </Card>
  );
}

// Modern widget layout (variant A)
function ModernWidget({ title, description, data, onAction }: WidgetProps) {
  const [hovering, setHovering] = useState(false);
  
  return (
    <motion.div 
      whileHover={{ 
        scale: 1.02, 
        boxShadow: "0 10px 30px rgba(0, 0, 0, 0.1)" 
      }}
      transition={{ duration: 0.2 }}
      onHoverStart={() => setHovering(true)}
      onHoverEnd={() => setHovering(false)}
    >
      <Card className="overflow-hidden border-0 shadow-lg bg-gradient-to-br from-primary/5 to-secondary/5">
        <CardHeader className="pb-0">
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="text-2xl font-bold">{title}</CardTitle>
              <CardDescription className="mt-1">{description}</CardDescription>
            </div>
            <motion.div 
              animate={{ rotate: hovering ? 45 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <ArrowUpRight className="h-6 w-6 text-primary" />
            </motion.div>
          </div>
        </CardHeader>
        <CardContent className="pt-6">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="h-52"
          >
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: "rgba(255, 255, 255, 0.95)",
                    borderRadius: "8px",
                    border: "none",
                    boxShadow: "0 4px 15px rgba(0, 0, 0, 0.1)"
                  }}
                />
                <Bar 
                  dataKey="value" 
                  fill="url(#colorGradient)" 
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>
        </CardContent>
        <CardFooter className="bg-muted/30 pt-4 pb-4">
          <Button 
            className="w-full" 
            variant="default" 
            onClick={onAction}
            size="lg"
          >
            <TrendingUp className="mr-2 h-5 w-5" />
            Explore Insights
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  );
}

// Compact widget layout (variant B)
function CompactWidget({ title, description, data, onAction }: WidgetProps) {
  // Calculate total and growth
  const total = data.reduce((sum, item) => sum + item.value, 0);
  const lastTwoValues = data.slice(-2).map(item => item.value);
  const growth = lastTwoValues.length > 1 
    ? ((lastTwoValues[1] - lastTwoValues[0]) / lastTwoValues[0] * 100).toFixed(1)
    : "0";
  
  return (
    <Card className="overflow-hidden border border-border">
      <div className="grid grid-cols-1 md:grid-cols-3 h-full">
        <div className="p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-xl font-bold">{title}</h3>
            <p className="text-muted-foreground text-sm mt-1">{description}</p>
          </div>
          
          <div className="mt-4">
            <div className="text-3xl font-bold">{total.toLocaleString()}</div>
            <div className="flex items-center mt-1 text-sm">
              <div className={`flex items-center ${Number(growth) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                <TrendingUp className="h-4 w-4 mr-1" />
                <span>{growth}%</span>
              </div>
              <span className="text-muted-foreground ml-2">vs previous period</span>
            </div>
          </div>
          
          <Button 
            variant="link" 
            className="pl-0 mt-4 flex items-center text-primary" 
            onClick={onAction}
          >
            <span>View Full Report</span>
            <CheckCircle className="ml-1 h-4 w-4" />
          </Button>
        </div>
        
        <div className="col-span-2 bg-muted/20 h-full flex items-center">
          <div className="h-40 w-full px-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data}>
                <XAxis dataKey="name" axisLine={false} tickLine={false} />
                <Tooltip />
                <Bar 
                  dataKey="value" 
                  fill="currentColor" 
                  className="text-primary/70" 
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </Card>
  );
} 