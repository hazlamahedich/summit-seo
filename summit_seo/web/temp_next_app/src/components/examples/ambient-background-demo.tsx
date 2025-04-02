'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Slider } from '@/components/ui/slider';
import { AmbientBackground, AmbientAnimationTheme, AmbientDataMetric } from '@/components/ui/ambient-background';
import { motion } from 'framer-motion';

// Mock metrics for demonstration
const generateMockMetrics = (): AmbientDataMetric[] => [
  {
    value: Math.round(Math.random() * 90 + 10), // 10-100
    label: 'Performance Score',
    color: 'rgba(34, 197, 94, 0.5)', // green
    threshold: { low: 30, medium: 60, high: 80 }
  },
  {
    value: Math.round(Math.random() * 90 + 10),
    label: 'SEO Score',
    color: 'rgba(59, 130, 246, 0.5)', // blue
    threshold: { low: 30, medium: 60, high: 80 }
  },
  {
    value: Math.round(Math.random() * 90 + 10),
    label: 'Security Score',
    color: 'rgba(239, 68, 68, 0.5)', // red
    threshold: { low: 30, medium: 60, high: 80 }
  }
];

export function AmbientBackgroundDemo() {
  const [theme, setTheme] = useState<AmbientAnimationTheme>('gradient');
  const [sensitivity, setSensitivity] = useState(0.5);
  const [metrics, setMetrics] = useState<AmbientDataMetric[]>(generateMockMetrics());
  const [ambient, setAmbient] = useState(true);
  const [responsive, setResponsive] = useState(true);
  
  // Update metrics periodically to simulate data changes
  useEffect(() => {
    if (!responsive) return;
    
    const interval = setInterval(() => {
      setMetrics(generateMockMetrics());
    }, 5000);
    
    return () => clearInterval(interval);
  }, [responsive]);
  
  return (
    <div className="space-y-8 py-8">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold mb-6">Ambient Background Animations</h2>
        <p className="text-muted-foreground mb-6">
          Subtle background animations that respond to data changes, enhancing the visual feedback
          without overwhelming the user. These animations respect user's reduced motion preferences.
        </p>
        
        <Card className="p-4 mb-8">
          <div className="flex flex-col md:flex-row gap-4 md:items-center mb-4">
            <div>
              <h3 className="font-medium mb-2">Animation Sensitivity</h3>
              <div className="w-48">
                <Slider
                  value={[sensitivity * 100]}
                  min={0}
                  max={100}
                  step={1}
                  onValueChange={(value: number[]) => setSensitivity(value[0] / 100)}
                />
                <p className="text-xs text-muted-foreground mt-1">{Math.round(sensitivity * 100)}%</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Button 
                size="sm" 
                variant={ambient ? "default" : "outline"}
                onClick={() => setAmbient(!ambient)}
              >
                {ambient ? "Ambient: ON" : "Ambient: OFF"}
              </Button>
              <Button 
                size="sm" 
                variant={responsive ? "default" : "outline"}
                onClick={() => setResponsive(!responsive)}
              >
                {responsive ? "Responsive: ON" : "Responsive: OFF"}
              </Button>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            {metrics.map((metric, index) => (
              <Card key={index} className="p-4">
                <h4 className="font-medium text-sm mb-1">{metric.label}</h4>
                <div className="flex items-center gap-2">
                  <div 
                    className="w-4 h-4 rounded-full" 
                    style={{ backgroundColor: metric.color }}
                  />
                  <span className="text-2xl font-bold">{metric.value}</span>
                </div>
              </Card>
            ))}
          </div>
          
          <Tabs defaultValue="gradient" onValueChange={(value) => setTheme(value as AmbientAnimationTheme)}>
            <TabsList className="grid grid-cols-5 mb-4">
              <TabsTrigger value="gradient">Gradient</TabsTrigger>
              <TabsTrigger value="particles">Particles</TabsTrigger>
              <TabsTrigger value="waves">Waves</TabsTrigger>
              <TabsTrigger value="glow">Glow</TabsTrigger>
              <TabsTrigger value="pulse">Pulse</TabsTrigger>
            </TabsList>
            
            {/* Each theme demo in a separate tab content */}
            <TabsContent value="gradient" className="mt-0">
              <AnimationDemo
                theme="gradient"
                metrics={metrics}
                sensitivity={sensitivity}
                ambient={ambient}
                responsive={responsive}
              />
            </TabsContent>
            
            <TabsContent value="particles" className="mt-0">
              <AnimationDemo
                theme="particles"
                metrics={metrics}
                sensitivity={sensitivity}
                ambient={ambient}
                responsive={responsive}
              />
            </TabsContent>
            
            <TabsContent value="waves" className="mt-0">
              <AnimationDemo
                theme="waves"
                metrics={metrics}
                sensitivity={sensitivity}
                ambient={ambient}
                responsive={responsive}
              />
            </TabsContent>
            
            <TabsContent value="glow" className="mt-0">
              <AnimationDemo
                theme="glow"
                metrics={metrics}
                sensitivity={sensitivity}
                ambient={ambient}
                responsive={responsive}
              />
            </TabsContent>
            
            <TabsContent value="pulse" className="mt-0">
              <AnimationDemo
                theme="pulse"
                metrics={metrics}
                sensitivity={sensitivity}
                ambient={ambient}
                responsive={responsive}
              />
            </TabsContent>
          </Tabs>
        </Card>
        
        <h3 className="text-xl font-bold mb-4">Use Cases</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Card className="overflow-hidden">
            <AmbientBackground
              theme="gradient"
              metrics={metrics}
              sensitivity={sensitivity}
              ambient={ambient}
              responsive={responsive}
            >
              <div className="p-6 relative z-10">
                <h4 className="text-lg font-bold mb-2">Dashboard Background</h4>
                <p className="text-sm text-muted-foreground">
                  Create a more engaging dashboard by using ambient backgrounds that subtly
                  reflect the overall performance metrics.
                </p>
              </div>
            </AmbientBackground>
          </Card>
          
          <Card className="overflow-hidden">
            <AmbientBackground
              theme="glow"
              metrics={[{
                value: 85,
                label: 'Security Score',
                color: 'rgba(34, 197, 94, 0.6)',
              }]}
              sensitivity={sensitivity}
              ambient={ambient}
              responsive={responsive}
            >
              <div className="p-6 relative z-10">
                <h4 className="text-lg font-bold mb-2">Status Indicator</h4>
                <p className="text-sm text-muted-foreground">
                  Use color-coded glowing backgrounds to indicate status (green for good, red for issues)
                  with intensity matching the severity.
                </p>
              </div>
            </AmbientBackground>
          </Card>
          
          <Card className="overflow-hidden">
            <AmbientBackground
              theme="waves"
              metrics={metrics}
              sensitivity={sensitivity}
              ambient={ambient}
              responsive={responsive}
            >
              <div className="p-6 relative z-10">
                <h4 className="text-lg font-bold mb-2">Data Visualization Enhancement</h4>
                <p className="text-sm text-muted-foreground">
                  Add ambient wave animations to data visualization components to reinforce
                  the meaning of the data being presented.
                </p>
              </div>
            </AmbientBackground>
          </Card>
          
          <Card className="overflow-hidden">
            <AmbientBackground
              theme="particles"
              metrics={metrics.slice(0, 1)}
              sensitivity={sensitivity}
              ambient={ambient}
              responsive={responsive}
            >
              <div className="p-6 relative z-10">
                <h4 className="text-lg font-bold mb-2">Activity Indicator</h4>
                <p className="text-sm text-muted-foreground">
                  Use particle animations with varying intensities to represent system activity
                  or data processing in real-time.
                </p>
              </div>
            </AmbientBackground>
          </Card>
        </div>
        
        <Card className="p-6">
          <h3 className="text-xl font-bold mb-4">Implementation Tips</h3>
          <ul className="space-y-2 text-sm">
            <li>• Keep ambient animations subtle to avoid distracting users</li>
            <li>• Use appropriate colors that match your data context (red for alerts, green for success)</li>
            <li>• Always respect reduced motion preferences for accessibility</li>
            <li>• Consider performance impact and use animations sparingly on mobile devices</li>
            <li>• Combine with other subtle feedback like sound effects for enhanced experience</li>
          </ul>
        </Card>
      </div>
    </div>
  );
}

// Helper component to show animation in a contained box
function AnimationDemo({
  theme,
  metrics,
  sensitivity,
  ambient,
  responsive
}: {
  theme: AmbientAnimationTheme;
  metrics: AmbientDataMetric[];
  sensitivity: number;
  ambient: boolean;
  responsive: boolean;
}) {
  return (
    <div className="relative overflow-hidden rounded-lg border border-border bg-card h-64">
      <AmbientBackground
        theme={theme}
        metrics={metrics}
        sensitivity={sensitivity}
        ambient={ambient}
        responsive={responsive}
      >
        <div className="flex items-center justify-center h-full">
          <motion.div 
            className="text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h3 className="text-xl font-bold mb-2">{theme.charAt(0).toUpperCase() + theme.slice(1)} Theme</h3>
            <p className="text-sm text-muted-foreground max-w-md mx-auto">
              This animation style responds to data metrics with {sensitivity * 100}% sensitivity.
              {ambient && ' Ambient animations are enabled.'}
              {!responsive && ' Data responsiveness is disabled.'}
            </p>
          </motion.div>
        </div>
      </AmbientBackground>
    </div>
  );
} 