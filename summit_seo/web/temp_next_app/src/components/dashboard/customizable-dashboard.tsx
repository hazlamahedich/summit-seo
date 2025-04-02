import { useState } from 'react';
import { Grid } from '@/components/ui/grid';
import { Button } from '@/components/ui/button';
import { Flex } from '@/components/ui/flex';
import { useUserPreferences, DashboardWidget as WidgetType } from '@/contexts/user-preferences-context';
import { DashboardWidget } from './dashboard-widget';
import { MetricsSummary } from './metrics-summary';
import { FeatureDiscovery, FeatureTour } from '@/components/ui/feature-discovery';
import { useAuth } from '@/providers/auth-provider';
import { Section } from '@/components/ui/section';
import { 
  Plus, 
  LineChart, 
  BarChart2, 
  PieChart, 
  List, 
  AlertTriangle,
  Layers,
  RefreshCw
} from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

// Define the widget components map
const WidgetComponents: Record<string, React.FC<{ widget: WidgetType }>> = {
  'metrics-summary': ({ widget }) => <MetricsSummary />,
  'recent-projects': ({ widget }) => (
    <div className="h-full overflow-auto">
      <Flex direction="col" gap={3}>
        {["Website Redesign", "E-commerce SEO", "Blog Optimization", "Local SEO Campaign"].map((project, i) => (
          <Flex key={i} justify="between" className="p-3 border-b last:border-0">
            <div>
              <div className="font-medium">{project}</div>
              <div className="text-sm text-muted-foreground">Last updated 2 days ago</div>
            </div>
            <Button size="sm" variant="outline">View</Button>
          </Flex>
        ))}
      </Flex>
    </div>
  ),
  'recent-analyses': ({ widget }) => (
    <div className="h-full overflow-auto">
      <Flex direction="col" gap={3}>
        {[
          { name: "Homepage Analysis", score: 85, trend: "up" },
          { name: "Product Pages", score: 72, trend: "up" },
          { name: "Blog Performance", score: 64, trend: "down" },
          { name: "Mobile Usability", score: 91, trend: "up" },
        ].map((analysis, i) => (
          <Flex key={i} justify="between" className="p-3 border-b last:border-0">
            <div>
              <div className="font-medium">{analysis.name}</div>
              <div className="text-sm text-muted-foreground">Score: {analysis.score}/100</div>
            </div>
            <Flex align="center" gap={2}>
              {analysis.trend === "up" ? (
                <LineChart className="h-4 w-4 text-green-500" />
              ) : (
                <LineChart className="h-4 w-4 text-red-500 rotate-180" />
              )}
              <Button size="sm" variant="outline">View</Button>
            </Flex>
          </Flex>
        ))}
      </Flex>
    </div>
  ),
  'line-chart': ({ widget }) => (
    <div className="flex items-center justify-center h-full">
      <LineChart className="h-24 w-24 text-muted-foreground" />
      <div className="ml-4">
        <p className="text-lg font-medium">SEO Score Trend</p>
        <p className="text-muted-foreground">Visualize your progress over time</p>
      </div>
    </div>
  ),
  'issues-summary': ({ widget }) => (
    <div className="flex flex-col h-full">
      <Flex align="center" gap={3} className="mb-2">
        <AlertTriangle className="h-8 w-8 text-red-500" />
        <div>
          <div className="text-xl font-bold">12</div>
          <div className="text-sm text-muted-foreground">Critical Issues</div>
        </div>
      </Flex>
      <ul className="space-y-1 text-sm">
        <li className="flex items-center">
          <div className="w-2 h-2 rounded-full bg-red-500 mr-2"></div>
          Missing meta descriptions (4)
        </li>
        <li className="flex items-center">
          <div className="w-2 h-2 rounded-full bg-red-500 mr-2"></div>
          Broken links (3)
        </li>
        <li className="flex items-center">
          <div className="w-2 h-2 rounded-full bg-red-500 mr-2"></div>
          Missing alt text (5)
        </li>
      </ul>
      <Button variant="outline" size="sm" className="mt-auto self-start">
        View All Issues
      </Button>
    </div>
  ),
};

interface WidgetTypeOption {
  id: string;
  label: string;
  icon: React.ReactNode;
  defaultSize: 'small' | 'medium' | 'large';
}

const AVAILABLE_WIDGETS: WidgetTypeOption[] = [
  { id: 'metrics-summary', label: 'Summary Metrics', icon: <Layers className="h-4 w-4" />, defaultSize: 'large' },
  { id: 'recent-projects', label: 'Recent Projects', icon: <List className="h-4 w-4" />, defaultSize: 'medium' },
  { id: 'recent-analyses', label: 'Recent Analyses', icon: <BarChart2 className="h-4 w-4" />, defaultSize: 'medium' },
  { id: 'line-chart', label: 'SEO Score Trends', icon: <LineChart className="h-4 w-4" />, defaultSize: 'medium' },
  { id: 'issues-summary', label: 'Critical Issues', icon: <AlertTriangle className="h-4 w-4" />, defaultSize: 'small' },
];

export function CustomizableDashboard() {
  const { preferences, isLoading, updateWidgetSize, updateWidgetVisibility, resetWidgets, addWidget, removeWidget } = useUserPreferences();
  const { user } = useAuth();
  const [addWidgetOpen, setAddWidgetOpen] = useState(false);
  const [newWidgetType, setNewWidgetType] = useState<string>('');
  const [newWidgetTitle, setNewWidgetTitle] = useState<string>('');
  const [showDashboardTour, setShowDashboardTour] = useState<boolean>(false);

  // Dashboard customization tour
  const dashboardCustomizationTour: FeatureTour = {
    id: 'dashboard-customization',
    title: 'Personalize Your Dashboard',
    name: 'Dashboard Customization',
    steps: [
      {
        target: '.dashboard-widgets',
        content: 'This is your personalized dashboard. You can customize it to show the information most important to you.',
        placement: 'center',
      },
      {
        target: '.widget-controls',
        content: 'Use these buttons to add new widgets or reset your dashboard to the default layout.',
        placement: 'bottom',
      },
      {
        target: '.dashboard-widget',
        content: 'Each widget can be resized, removed, or configured through its menu in the top right corner.',
        placement: 'right',
      },
    ],
  };

  // Handle adding a new widget
  const handleAddWidget = () => {
    if (!newWidgetType || !newWidgetTitle) return;
    
    const widgetTypeOption = AVAILABLE_WIDGETS.find(w => w.id === newWidgetType);
    if (!widgetTypeOption) return;
    
    const newWidget: Omit<WidgetType, 'position'> = {
      id: `${newWidgetType}-${Date.now()}`,
      type: newWidgetType,
      title: newWidgetTitle,
      size: widgetTypeOption.defaultSize,
      visible: true,
    };
    
    addWidget(newWidget);
    setAddWidgetOpen(false);
    setNewWidgetType('');
    setNewWidgetTitle('');
  };

  // Filter visible widgets and sort by position
  const visibleWidgets = preferences.dashboardWidgets
    .filter(widget => widget.visible)
    .sort((a, b) => a.position - b.position);

  if (isLoading) {
    return <div>Loading your personalized dashboard...</div>;
  }

  return (
    <>
      <Section className="mb-6">
        <Flex justify="between" align="center">
          <div>
            <h1 className="text-3xl font-bold mb-2">Your Dashboard</h1>
            <p className="text-muted-foreground">
              Welcome back{user?.email ? `, ${user.email.split('@')[0]}` : ''}! Here's your personalized overview.
            </p>
          </div>
          <Flex gap={2} className="widget-controls">
            <Dialog open={addWidgetOpen} onOpenChange={setAddWidgetOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Widget
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add a New Widget</DialogTitle>
                  <DialogDescription>
                    Choose a widget type and customize its title.
                  </DialogDescription>
                </DialogHeader>
                
                <div className="grid gap-4 py-4">
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="widget-type" className="text-right">
                      Widget Type
                    </Label>
                    <Select 
                      value={newWidgetType} 
                      onValueChange={setNewWidgetType}
                    >
                      <SelectTrigger id="widget-type" className="col-span-3">
                        <SelectValue placeholder="Select widget type" />
                      </SelectTrigger>
                      <SelectContent>
                        {AVAILABLE_WIDGETS.map((widget) => (
                          <SelectItem key={widget.id} value={widget.id}>
                            <Flex align="center" gap={2}>
                              {widget.icon}
                              <span>{widget.label}</span>
                            </Flex>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="widget-title" className="text-right">
                      Widget Title
                    </Label>
                    <Input
                      id="widget-title"
                      value={newWidgetTitle}
                      onChange={(e) => setNewWidgetTitle(e.target.value)}
                      className="col-span-3"
                    />
                  </div>
                </div>
                
                <DialogFooter>
                  <Button variant="outline" onClick={() => setAddWidgetOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleAddWidget} disabled={!newWidgetType || !newWidgetTitle}>
                    Add Widget
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
            
            <Button variant="outline" onClick={resetWidgets}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Reset Dashboard
            </Button>
            
            <Button 
              variant="ghost" 
              onClick={() => setShowDashboardTour(true)}
              size="icon"
              title="Dashboard Help"
            >
              ?
            </Button>
          </Flex>
        </Flex>
      </Section>
      
      <Grid 
        gap={4} 
        cols={{ default: 1, md: 2, lg: 3 }}
        className="dashboard-widgets"
      >
        {visibleWidgets.map((widget) => {
          const WidgetComponent = WidgetComponents[widget.type];
          
          if (!WidgetComponent) {
            return null;
          }
          
          return (
            <DashboardWidget
              key={widget.id}
              widget={widget}
              onRemove={removeWidget}
              onSizeChange={updateWidgetSize}
              className="dashboard-widget"
            >
              <WidgetComponent widget={widget} />
            </DashboardWidget>
          );
        })}
      </Grid>
      
      {/* Dashboard Customization Tour */}
      <FeatureDiscovery 
        tour={dashboardCustomizationTour}
        isOpen={showDashboardTour}
        onClose={() => setShowDashboardTour(false)}
      />
    </>
  );
} 