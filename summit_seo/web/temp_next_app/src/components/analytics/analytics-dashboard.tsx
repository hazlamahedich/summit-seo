'use client';

import React, { useState, useEffect } from 'react';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';
import { useTheme } from 'next-themes';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AreaChart, BarChart, PieChart } from '@tremor/react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { AnimatePresence, motion } from 'framer-motion';
import { Database } from '@/types/supabase';
import { format } from 'date-fns';
import {
  ArrowUpRight,
  ChevronDown,
  ChevronUp,
  Clock,
  MousePointerClick,
  LayoutDashboard,
  Laptop,
  Smartphone,
  Tablet,
  Activity,
  Users,
  BarChart2,
} from 'lucide-react';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import { withAnalytics } from '@/contexts/analytics-context';

// Dashboard card for displaying metrics with animations
interface MetricCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon: React.ReactNode;
  trend?: number;
  loading?: boolean;
}

function MetricCard({ title, value, description, icon, trend, loading = false }: MetricCardProps) {
  const { theme } = useTheme();
  const isDarkTheme = theme === 'dark';
  
  return (
    <Card className="overflow-hidden">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium">
          {title}
        </CardTitle>
        <div className="h-4 w-4 text-muted-foreground">
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex flex-col gap-2">
            <div className="h-9 w-full animate-pulse rounded-md bg-muted" />
            <div className="h-4 w-24 animate-pulse rounded-md bg-muted" />
          </div>
        ) : (
          <>
            <motion.div 
              className="text-2xl font-bold"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              {value}
            </motion.div>
            <div className="flex items-center text-xs text-muted-foreground pt-1">
              {trend !== undefined && (
                <div className={`mr-1 flex items-center ${trend >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {trend >= 0 ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
                  <span>{Math.abs(trend)}%</span>
                </div>
              )}
              <span>{description}</span>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}

// Define chart data types
interface PageViewData {
  date: string;
  views: number;
}

interface DeviceData {
  device: string;
  count: number;
}

interface FeatureUsageData {
  feature: string;
  count: number;
}

interface SessionData {
  date: string;
  sessions: number;
  avgDuration: number;
}

interface UserAnalyticsData {
  pageViews: PageViewData[];
  devices: DeviceData[];
  featureUsage: FeatureUsageData[];
  sessions: SessionData[];
  metrics: {
    totalPageViews: number;
    totalUsers: number;
    averageSessionDuration: number;
    bounceRate: number;
    pageViewTrend: number;
    usersTrend: number;
    activeFeatures: number;
  };
}

// Time period options
type TimePeriod = '24h' | '7d' | '30d' | '90d';

function AnalyticsDashboard() {
  const supabase = createClientComponentClient<Database>();
  const [loading, setLoading] = useState(true);
  const [timePeriod, setTimePeriod] = useState<TimePeriod>('7d');
  const [analyticsData, setAnalyticsData] = useState<UserAnalyticsData>({
    pageViews: [],
    devices: [],
    featureUsage: [],
    sessions: [],
    metrics: {
      totalPageViews: 0,
      totalUsers: 0,
      averageSessionDuration: 0,
      bounceRate: 0,
      pageViewTrend: 0,
      usersTrend: 0,
      activeFeatures: 0,
    }
  });
  
  useEffect(() => {
    fetchAnalyticsData();
  }, [timePeriod]);
  
  // Format number with comma separators
  const formatNumber = (num: number) => {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  };
  
  // Format duration in seconds to readable format
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };
  
  // Fetch analytics data based on selected time period
  const fetchAnalyticsData = async () => {
    setLoading(true);
    
    try {
      // Get timeframe based on selected period
      const now = new Date();
      let startDate = new Date();
      
      switch (timePeriod) {
        case '24h':
          startDate.setDate(now.getDate() - 1);
          break;
        case '7d':
          startDate.setDate(now.getDate() - 7);
          break;
        case '30d':
          startDate.setDate(now.getDate() - 30);
          break;
        case '90d':
          startDate.setDate(now.getDate() - 90);
          break;
      }
      
      // Format dates for Supabase query
      const startDateStr = startDate.toISOString();
      const endDateStr = now.toISOString();
      
      // Fetch data from Supabase
      // For demonstration, we're generating mock data
      // In production, this would query the actual Supabase tables
      
      // Mock page view data
      const pageViews = generateMockPageViewData(startDate, now, timePeriod);
      
      // Mock device data
      const devices: DeviceData[] = [
        { device: 'Desktop', count: 580 },
        { device: 'Mobile', count: 320 },
        { device: 'Tablet', count: 100 },
      ];
      
      // Mock feature usage data
      const featureUsage: FeatureUsageData[] = [
        { feature: 'Dashboard', count: 450 },
        { feature: 'Analysis', count: 320 },
        { feature: 'Reports', count: 280 },
        { feature: 'Settings', count: 150 },
        { feature: 'User Profile', count: 100 },
      ];
      
      // Mock session data
      const sessions = generateMockSessionData(startDate, now, timePeriod);
      
      // Calculate metrics
      const totalPageViews = pageViews.reduce((sum, item) => sum + item.views, 0);
      const totalUsers = Math.round(totalPageViews * 0.7); // Simplified calculation
      const averageSessionDuration = Math.round(sessions.reduce((sum, item) => sum + item.avgDuration, 0) / sessions.length);
      const bounceRate = 32; // Mock bounce rate
      
      // Calculate trends (% change from previous period)
      const pageViewTrend = 12.5; // Mock trend
      const usersTrend = 8.3; // Mock trend
      const activeFeatures = featureUsage.length;
      
      // Set analytics data
      setAnalyticsData({
        pageViews,
        devices,
        featureUsage,
        sessions,
        metrics: {
          totalPageViews,
          totalUsers,
          averageSessionDuration,
          bounceRate,
          pageViewTrend,
          usersTrend,
          activeFeatures,
        }
      });
    } catch (error) {
      console.error('Error fetching analytics data:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Generate mock page view data based on time period
  const generateMockPageViewData = (startDate: Date, endDate: Date, period: TimePeriod): PageViewData[] => {
    const data: PageViewData[] = [];
    const dayDiff = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));
    
    // Determine data points frequency based on period
    let interval = 1; // days
    if (period === '90d') interval = 7; // weekly for 90d
    
    for (let i = 0; i <= dayDiff; i += interval) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      
      // Generate random view count with some pattern
      let views = Math.round(100 + Math.random() * 200);
      
      // Add a trend (higher on weekdays, lower on weekends)
      const dayOfWeek = date.getDay();
      if (dayOfWeek === 0 || dayOfWeek === 6) {
        views = Math.round(views * 0.7); // Lower on weekends
      }
      
      data.push({
        date: format(date, 'MMM dd'),
        views,
      });
    }
    
    return data;
  };
  
  // Generate mock session data
  const generateMockSessionData = (startDate: Date, endDate: Date, period: TimePeriod): SessionData[] => {
    const data: SessionData[] = [];
    const dayDiff = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));
    
    // Determine data points frequency based on period
    let interval = 1; // days
    if (period === '90d') interval = 7; // weekly for 90d
    
    for (let i = 0; i <= dayDiff; i += interval) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      
      // Generate random session count with some pattern
      let sessions = Math.round(70 + Math.random() * 100);
      
      // Add a trend (higher on weekdays, lower on weekends)
      const dayOfWeek = date.getDay();
      if (dayOfWeek === 0 || dayOfWeek === 6) {
        sessions = Math.round(sessions * 0.7); // Lower on weekends
      }
      
      // Generate random average duration between 2-5 minutes
      const avgDuration = Math.round(120 + Math.random() * 180);
      
      data.push({
        date: format(date, 'MMM dd'),
        sessions,
        avgDuration,
      });
    }
    
    return data;
  };
  
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">User Behavior Analytics</h2>
        <Select value={timePeriod} onValueChange={(value) => setTimePeriod(value as TimePeriod)}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Select period" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="24h">Last 24 Hours</SelectItem>
            <SelectItem value="7d">Last 7 Days</SelectItem>
            <SelectItem value="30d">Last 30 Days</SelectItem>
            <SelectItem value="90d">Last 90 Days</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Total Page Views"
          value={formatNumber(analyticsData.metrics.totalPageViews)}
          description="vs. previous period"
          icon={<Activity className="h-4 w-4" />}
          trend={analyticsData.metrics.pageViewTrend}
          loading={loading}
        />
        <MetricCard
          title="Total Users"
          value={formatNumber(analyticsData.metrics.totalUsers)}
          description="vs. previous period"
          icon={<Users className="h-4 w-4" />}
          trend={analyticsData.metrics.usersTrend}
          loading={loading}
        />
        <MetricCard
          title="Avg Session Duration"
          value={formatDuration(analyticsData.metrics.averageSessionDuration)}
          description="time on site"
          icon={<Clock className="h-4 w-4" />}
          loading={loading}
        />
        <MetricCard
          title="Bounce Rate"
          value={`${analyticsData.metrics.bounceRate}%`}
          description="single page sessions"
          icon={<ArrowUpRight className="h-4 w-4" />}
          trend={-2.5} // A negative trend is good for bounce rate
          loading={loading}
        />
      </div>
      
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="engagement">Engagement</TabsTrigger>
          <TabsTrigger value="features">Features</TabsTrigger>
          <TabsTrigger value="devices">Devices</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Page Views Over Time</CardTitle>
              <CardDescription>Daily page views for the selected period</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                {loading ? (
                  <div className="h-full w-full animate-pulse rounded-md bg-muted" />
                ) : (
                  <AreaChart
                    data={analyticsData.pageViews}
                    index="date"
                    categories={["views"]}
                    colors={["blue"]}
                    valueFormatter={(value) => `${value} views`}
                    showLegend={false}
                    showAnimation
                  />
                )}
              </div>
            </CardContent>
          </Card>
          
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Device Distribution</CardTitle>
                <CardDescription>Users by device type</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  {loading ? (
                    <div className="h-full w-full animate-pulse rounded-md bg-muted" />
                  ) : (
                    <PieChart
                      data={analyticsData.devices}
                      index="device"
                      category="count"
                      valueFormatter={(value) => `${value} users`}
                      showAnimation
                    />
                  )}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Feature Usage</CardTitle>
                <CardDescription>Most used features</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  {loading ? (
                    <div className="h-full w-full animate-pulse rounded-md bg-muted" />
                  ) : (
                    <BarChart
                      data={analyticsData.featureUsage}
                      index="feature"
                      categories={["count"]}
                      colors={["violet"]}
                      valueFormatter={(value) => `${value} uses`}
                      showLegend={false}
                      showAnimation
                    />
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        
        <TabsContent value="engagement" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Session Data</CardTitle>
              <CardDescription>Number of sessions and average duration</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                {loading ? (
                  <div className="h-full w-full animate-pulse rounded-md bg-muted" />
                ) : (
                  <AreaChart
                    data={analyticsData.sessions}
                    index="date"
                    categories={["sessions"]}
                    colors={["indigo"]}
                    valueFormatter={(value) => `${value} sessions`}
                    showLegend={false}
                    showAnimation
                  />
                )}
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Average Session Duration</CardTitle>
              <CardDescription>Time spent per session in minutes</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                {loading ? (
                  <div className="h-full w-full animate-pulse rounded-md bg-muted" />
                ) : (
                  <AreaChart
                    data={analyticsData.sessions}
                    index="date"
                    categories={["avgDuration"]}
                    colors={["cyan"]}
                    valueFormatter={(value) => `${Math.round(value / 60)} mins`}
                    showLegend={false}
                    showAnimation
                  />
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="features" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Feature Usage Detail</CardTitle>
              <CardDescription>Detailed breakdown of feature utilization</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[400px]">
                {loading ? (
                  <div className="h-full w-full animate-pulse rounded-md bg-muted" />
                ) : (
                  <BarChart
                    data={[
                      ...analyticsData.featureUsage,
                      { feature: "Projects", count: 210 },
                      { feature: "Insights", count: 180 },
                      { feature: "Help Center", count: 95 },
                      { feature: "Account", count: 85 },
                      { feature: "Notifications", count: 70 },
                    ]}
                    index="feature"
                    categories={["count"]}
                    colors={["pink"]}
                    valueFormatter={(value) => `${value} uses`}
                    showLegend={false}
                    showAnimation
                  />
                )}
              </div>
            </CardContent>
          </Card>
          
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Most Active Features</CardTitle>
                <CardDescription>Features with highest engagement</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {loading ? (
                    <div className="space-y-2">
                      {[1, 2, 3, 4, 5].map((i) => (
                        <div key={i} className="h-12 animate-pulse rounded-md bg-muted" />
                      ))}
                    </div>
                  ) : (
                    <>
                      {analyticsData.featureUsage.map((item, index) => (
                        <div key={index} className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className="mr-2 flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                              {getFeatureIcon(item.feature)}
                            </div>
                            <div>{item.feature}</div>
                          </div>
                          <div className="font-medium">{item.count} uses</div>
                        </div>
                      ))}
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Feature Trend</CardTitle>
                <CardDescription>Week-over-week change</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {loading ? (
                    <div className="space-y-2">
                      {[1, 2, 3, 4, 5].map((i) => (
                        <div key={i} className="h-12 animate-pulse rounded-md bg-muted" />
                      ))}
                    </div>
                  ) : (
                    <>
                      {analyticsData.featureUsage.map((item, index) => {
                        // Generate random trend percentage between -20 and 30
                        const trend = Math.round((Math.random() * 50) - 20);
                        return (
                          <div key={index} className="flex items-center justify-between">
                            <div>{item.feature}</div>
                            <div className={`flex items-center ${trend >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                              {trend >= 0 ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                              <span className="ml-1 font-medium">{Math.abs(trend)}%</span>
                            </div>
                          </div>
                        );
                      })}
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        
        <TabsContent value="devices" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Device Distribution</CardTitle>
                <CardDescription>Users by device type</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  {loading ? (
                    <div className="h-full w-full animate-pulse rounded-md bg-muted" />
                  ) : (
                    <PieChart
                      data={analyticsData.devices}
                      index="device"
                      category="count"
                      valueFormatter={(value) => `${value} users`}
                      showAnimation
                    />
                  )}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Browser Usage</CardTitle>
                <CardDescription>Sessions by browser</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px]">
                  {loading ? (
                    <div className="h-full w-full animate-pulse rounded-md bg-muted" />
                  ) : (
                    <PieChart
                      data={[
                        { browser: 'Chrome', count: 450 },
                        { browser: 'Safari', count: 280 },
                        { browser: 'Firefox', count: 120 },
                        { browser: 'Edge', count: 100 },
                        { browser: 'Other', count: 50 },
                      ]}
                      index="browser"
                      category="count"
                      valueFormatter={(value) => `${value} sessions`}
                      showAnimation
                    />
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
          
          <Card>
            <CardHeader>
              <CardTitle>Device Details</CardTitle>
              <CardDescription>Detailed breakdown by device type and operating system</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {loading ? (
                  <div className="space-y-2">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <div key={i} className="h-12 animate-pulse rounded-md bg-muted" />
                    ))}
                  </div>
                ) : (
                  <>
                    <div className="flex items-center space-x-2 pb-4">
                      <ToggleGroup type="single" defaultValue="all">
                        <ToggleGroupItem value="all">All</ToggleGroupItem>
                        <ToggleGroupItem value="desktop">Desktop</ToggleGroupItem>
                        <ToggleGroupItem value="mobile">Mobile</ToggleGroupItem>
                        <ToggleGroupItem value="tablet">Tablet</ToggleGroupItem>
                      </ToggleGroup>
                    </div>
                    
                    <div className="space-y-4">
                      <div className="grid grid-cols-3 gap-4">
                        <div className="flex flex-col items-center justify-center rounded-lg border p-4">
                          <Laptop className="h-8 w-8 text-blue-500 mb-2" />
                          <div className="text-xl font-bold">58%</div>
                          <div className="text-sm text-muted-foreground">Desktop</div>
                        </div>
                        <div className="flex flex-col items-center justify-center rounded-lg border p-4">
                          <Smartphone className="h-8 w-8 text-green-500 mb-2" />
                          <div className="text-xl font-bold">32%</div>
                          <div className="text-sm text-muted-foreground">Mobile</div>
                        </div>
                        <div className="flex flex-col items-center justify-center rounded-lg border p-4">
                          <Tablet className="h-8 w-8 text-purple-500 mb-2" />
                          <div className="text-xl font-bold">10%</div>
                          <div className="text-sm text-muted-foreground">Tablet</div>
                        </div>
                      </div>
                      
                      <div className="rounded-lg border">
                        <div className="grid grid-cols-3 border-b px-4 py-2 font-medium">
                          <div>Operating System</div>
                          <div>Browser</div>
                          <div>Users</div>
                        </div>
                        <div className="divide-y">
                          <div className="grid grid-cols-3 px-4 py-3">
                            <div>Windows</div>
                            <div>Chrome</div>
                            <div>320</div>
                          </div>
                          <div className="grid grid-cols-3 px-4 py-3">
                            <div>MacOS</div>
                            <div>Safari</div>
                            <div>180</div>
                          </div>
                          <div className="grid grid-cols-3 px-4 py-3">
                            <div>iOS</div>
                            <div>Safari</div>
                            <div>120</div>
                          </div>
                          <div className="grid grid-cols-3 px-4 py-3">
                            <div>Android</div>
                            <div>Chrome</div>
                            <div>100</div>
                          </div>
                          <div className="grid grid-cols-3 px-4 py-3">
                            <div>Windows</div>
                            <div>Firefox</div>
                            <div>80</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Helper function to get icon for feature
const getFeatureIcon = (feature: string) => {
  switch (feature) {
    case 'Dashboard':
      return <LayoutDashboard className="h-4 w-4" />;
    case 'Analysis':
      return <BarChart2 className="h-4 w-4" />;
    case 'Reports':
      return <BarChart2 className="h-4 w-4" />;
    case 'Settings':
      return <BarChart2 className="h-4 w-4" />;
    case 'User Profile':
      return <Users className="h-4 w-4" />;
    default:
      return <Activity className="h-4 w-4" />;
  }
};

// Export with analytics tracking
export default withAnalytics(AnalyticsDashboard, {
  trackMount: true,
  featureId: 'analytics-dashboard',
  featureCategory: 'admin',
  elementId: 'analytics-dashboard',
  elementType: 'page'
}); 