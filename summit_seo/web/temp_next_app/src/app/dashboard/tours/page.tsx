"use client";

import { useState, useEffect } from 'react';
import { Container } from '@/components/ui/container';
import { Section } from '@/components/ui/section';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  BookOpen, 
  Sparkles, 
  Lightbulb, 
  BarChart, 
  Settings2, 
  Rocket, 
  Medal,
  Check,
  RefreshCw,
  Trophy
} from 'lucide-react';
import { TourStartButton, TourProgressIndicator } from '@/components/onboarding/guided-tour';
import { GuidedTour } from '@/components/onboarding/guided-tour';
import { Tour } from '@/lib/services/tour-service';
import { useTourStatus, useTourControls } from '@/contexts/tour-context';

// Example tour data for demonstration
const FEATURE_TOUR_ID = 'dashboard-feature-tour';
const ANALYSIS_TOUR_ID = 'analysis-workflow-tour';
const SETTINGS_TOUR_ID = 'settings-configuration-tour';

export default function ToursPage() {
  const [userId, setUserId] = useState("demo-user-1");
  
  // Get tour reset functionality
  const { resetTourProgress } = useTourControls();
  
  // Get status for each tour
  const featureTourStatus = useTourStatus(FEATURE_TOUR_ID);
  const analysisTourStatus = useTourStatus(ANALYSIS_TOUR_ID);
  const settingsTourStatus = useTourStatus(SETTINGS_TOUR_ID);
  
  // Initialize demo tour data in local storage
  useEffect(() => {
    // Create demo tours
    const demoTours: Tour[] = [
      {
        id: FEATURE_TOUR_ID,
        name: 'dashboard-feature-tour',
        displayName: 'Dashboard Features Tour',
        description: 'Learn about the key features of your dashboard',
        version: 1,
        requiredForOnboarding: true,
        steps: [
          {
            id: 'step-1',
            target: '#dashboard-overview',
            title: 'Dashboard Overview',
            content: 'This is your main dashboard where you can see all your analytics at a glance.',
            placement: 'bottom',
            highlighted: true
          },
          {
            id: 'step-2',
            target: '#recent-analyses',
            title: 'Recent Analyses',
            content: 'View your most recent website analyses and their status.',
            placement: 'right',
            highlighted: true
          },
          {
            id: 'step-3',
            target: '#performance-metrics',
            title: 'Performance Metrics',
            content: 'Track key performance indicators for your websites.',
            placement: 'top',
            highlighted: true
          },
          {
            id: 'step-4',
            target: '#tour-actions',
            title: 'Tour Controls',
            content: 'You can restart tours, view your progress, or earn badges by completing tours.',
            placement: 'left',
            highlighted: true
          }
        ]
      },
      {
        id: ANALYSIS_TOUR_ID,
        name: 'analysis-workflow-tour',
        displayName: 'Analysis Workflow Tour',
        description: 'Learn how to perform a website analysis',
        version: 1,
        requiredForOnboarding: false,
        requiredBadgeId: 'analysis-expert',
        steps: [
          {
            id: 'step-1',
            target: '#analysis-start',
            title: 'Start an Analysis',
            content: 'Click here to begin a new website analysis.',
            placement: 'bottom',
            highlighted: true
          },
          {
            id: 'step-2',
            target: '#analysis-options',
            title: 'Analysis Options',
            content: 'Configure the analysis options to focus on specific aspects of your site.',
            placement: 'right',
            highlighted: true
          },
          {
            id: 'step-3',
            target: '#analysis-results',
            title: 'Analysis Results',
            content: 'View detailed results and recommendations after your analysis completes.',
            placement: 'top',
            highlighted: true
          }
        ]
      },
      {
        id: SETTINGS_TOUR_ID,
        name: 'settings-configuration-tour',
        displayName: 'Settings & Configuration Tour',
        description: 'Learn how to customize the application to your needs',
        version: 1,
        requiredForOnboarding: false,
        steps: [
          {
            id: 'step-1',
            target: '#settings-access',
            title: 'Settings Access',
            content: 'Access your settings panel to configure the application.',
            placement: 'bottom',
            highlighted: true
          },
          {
            id: 'step-2',
            target: '#user-preferences',
            title: 'User Preferences',
            content: 'Customize your experience with user preferences.',
            placement: 'right',
            highlighted: true
          }
        ]
      }
    ];
    
    // Save to local storage
    localStorage.setItem('available-tours', JSON.stringify(demoTours));
    
  }, []);
  
  // Reset a tour's progress
  const handleResetTour = (tourId: string) => {
    resetTourProgress({ userId, tourId });
  };
  
  return (
    <Container>
      <Section>
        <div className="space-y-8">
          {/* Page header */}
          <div className="space-y-2">
            <h1 className="text-3xl font-bold tracking-tight" id="dashboard-overview">
              Guided Tours Dashboard
            </h1>
            <p className="text-muted-foreground">
              Discover the platform's features with interactive guided tours and track your progress
            </p>
          </div>
          
          {/* Tours overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="border-primary/20 bg-primary/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5 text-primary" />
                  <span>Available Tours</span>
                </CardTitle>
                <CardDescription>
                  Interactive tours to help you learn the platform
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">3</div>
                <p className="text-sm text-muted-foreground">
                  Tours designed to help you get the most out of the platform
                </p>
              </CardContent>
              <CardFooter>
                <TourStartButton 
                  tourId={FEATURE_TOUR_ID} 
                  label="Start Feature Tour"
                  className="w-full"
                />
              </CardFooter>
            </Card>
            
            <Card id="tour-actions">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Medal className="h-5 w-5 text-amber-500" />
                  <span>Tour Achievements</span>
                </CardTitle>
                <CardDescription>
                  Earn badges by completing guided tours
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <div className="w-10 h-10 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                      <Trophy className="h-5 w-5 text-amber-500" />
                    </div>
                    <div>
                      <div className="font-medium">Explorer Badge</div>
                      <div className="text-xs text-muted-foreground">Complete all available tours</div>
                    </div>
                    <div className="ml-auto">
                      <Badge variant="outline" className="bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300">
                        1/3
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <div className="w-10 h-10 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
                      <Rocket className="h-5 w-5 text-emerald-500" />
                    </div>
                    <div>
                      <div className="font-medium">Analysis Expert</div>
                      <div className="text-xs text-muted-foreground">Complete the Analysis Workflow tour</div>
                    </div>
                    <div className="ml-auto">
                      {analysisTourStatus.isCompleted ? (
                        <Badge className="bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 border-emerald-200">
                          <Check className="h-3 w-3 mr-1" />
                          Earned
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="text-muted-foreground">
                          Not Earned
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart className="h-5 w-5 text-primary" />
                  <span>Tour Progress</span>
                </CardTitle>
                <CardDescription>
                  Track your progress through guided tours
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <div className="text-sm font-medium">Dashboard Features</div>
                    <div className="text-xs text-muted-foreground">
                      {featureTourStatus.isCompleted ? 'Completed' : 
                       featureTourStatus.isDismissed ? 'Dismissed' : 
                       `Step ${featureTourStatus.lastCompletedStep + 1}/4`}
                    </div>
                  </div>
                  <div className="relative">
                    <Progress 
                      value={featureTourStatus.isCompleted ? 100 : (featureTourStatus.lastCompletedStep / 4) * 100} 
                      className="h-2" 
                    />
                    {featureTourStatus.isCompleted && (
                      <div className="absolute -right-1 -top-1">
                        <div className="w-4 h-4 rounded-full bg-primary flex items-center justify-center">
                          <Check className="h-2 w-2 text-white" />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <div className="text-sm font-medium">Analysis Workflow</div>
                    <div className="text-xs text-muted-foreground">
                      {analysisTourStatus.isCompleted ? 'Completed' : 
                       analysisTourStatus.isDismissed ? 'Dismissed' : 
                       `Step ${analysisTourStatus.lastCompletedStep + 1}/3`}
                    </div>
                  </div>
                  <div className="relative">
                    <Progress 
                      value={analysisTourStatus.isCompleted ? 100 : (analysisTourStatus.lastCompletedStep / 3) * 100} 
                      className="h-2" 
                    />
                    {analysisTourStatus.isCompleted && (
                      <div className="absolute -right-1 -top-1">
                        <div className="w-4 h-4 rounded-full bg-primary flex items-center justify-center">
                          <Check className="h-2 w-2 text-white" />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <div className="text-sm font-medium">Settings & Configuration</div>
                    <div className="text-xs text-muted-foreground">
                      {settingsTourStatus.isCompleted ? 'Completed' : 
                       settingsTourStatus.isDismissed ? 'Dismissed' : 
                       `Step ${settingsTourStatus.lastCompletedStep + 1}/2`}
                    </div>
                  </div>
                  <div className="relative">
                    <Progress 
                      value={settingsTourStatus.isCompleted ? 100 : (settingsTourStatus.lastCompletedStep / 2) * 100} 
                      className="h-2" 
                    />
                    {settingsTourStatus.isCompleted && (
                      <div className="absolute -right-1 -top-1">
                        <div className="w-4 h-4 rounded-full bg-primary flex items-center justify-center">
                          <Check className="h-2 w-2 text-white" />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
          
          {/* Recent analyses section for tour targeting */}
          <Card id="recent-analyses">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                <span>Recent Analyses</span>
              </CardTitle>
              <CardDescription>
                Your most recent website analyses and their results
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center">
                  <div className="font-medium">Corporate Website Analysis</div>
                  <Badge className="ml-auto">Completed</Badge>
                </div>
                <div className="flex items-center">
                  <div className="font-medium">E-commerce Store Analysis</div>
                  <Badge variant="outline" className="ml-auto">In Progress</Badge>
                </div>
                <div className="flex items-center">
                  <div className="font-medium">Blog Performance Analysis</div>
                  <Badge variant="outline" className="ml-auto">Scheduled</Badge>
                </div>
              </div>
            </CardContent>
            <CardFooter>
              <div id="analysis-start">
                <Button variant="outline">Start New Analysis</Button>
              </div>
            </CardFooter>
          </Card>
          
          {/* Performance metrics section for tour targeting */}
          <Card id="performance-metrics">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart className="h-5 w-5 text-primary" />
                <span>Performance Metrics</span>
              </CardTitle>
              <CardDescription>
                Key performance indicators for your websites
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-background rounded-lg border">
                  <div className="text-sm text-muted-foreground mb-1">SEO Score</div>
                  <div className="text-2xl font-bold">87%</div>
                  <div className="mt-2 text-xs text-emerald-500 flex items-center">
                    <span>↑ 3% from last month</span>
                  </div>
                </div>
                
                <div className="p-4 bg-background rounded-lg border">
                  <div className="text-sm text-muted-foreground mb-1">Mobile Optimization</div>
                  <div className="text-2xl font-bold">92%</div>
                  <div className="mt-2 text-xs text-emerald-500 flex items-center">
                    <span>↑ 6% from last month</span>
                  </div>
                </div>
                
                <div className="p-4 bg-background rounded-lg border">
                  <div className="text-sm text-muted-foreground mb-1">Page Speed</div>
                  <div className="text-2xl font-bold">78%</div>
                  <div className="mt-2 text-xs text-red-500 flex items-center">
                    <span>↓ 2% from last month</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          {/* Other tour target elements */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card id="analysis-options">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings2 className="h-5 w-5 text-primary" />
                  <span>Analysis Options</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div>Crawl Depth</div>
                    <Badge>3 Levels</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>Mobile Analysis</div>
                    <Badge>Enabled</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>Security Scan</div>
                    <Badge>Enabled</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card id="analysis-results">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="h-5 w-5 text-primary" />
                  <span>Analysis Results</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div>Critical Issues</div>
                    <Badge variant="destructive">3 Issues</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>Warnings</div>
                    <Badge variant="outline" className="bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300">
                      12 Warnings
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>Recommendations</div>
                    <Badge variant="outline" className="bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300">
                      8 Suggestions
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card id="settings-access">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings2 className="h-5 w-5 text-primary" />
                  <span>Settings Access</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Button variant="outline">Access Settings Panel</Button>
              </CardContent>
            </Card>
            
            <Card id="user-preferences">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings2 className="h-5 w-5 text-primary" />
                  <span>User Preferences</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div>Theme</div>
                    <Badge>Dark Mode</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>Email Notifications</div>
                    <Badge>Enabled</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
          
          {/* Tour management */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <RefreshCw className="h-5 w-5 text-primary" />
                <span>Reset Tours</span>
              </CardTitle>
              <CardDescription>
                Reset the progress of individual tours to try them again
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Dashboard Features Tour</div>
                    <div className="text-xs text-muted-foreground">Learn about key dashboard features</div>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleResetTour(FEATURE_TOUR_ID)}
                  >
                    Reset Progress
                  </Button>
                </div>
                
                <Separator />
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Analysis Workflow Tour</div>
                    <div className="text-xs text-muted-foreground">Learn how to run and interpret analyses</div>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleResetTour(ANALYSIS_TOUR_ID)}
                  >
                    Reset Progress
                  </Button>
                </div>
                
                <Separator />
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Settings & Configuration Tour</div>
                    <div className="text-xs text-muted-foreground">Learn how to customize the platform</div>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleResetTour(SETTINGS_TOUR_ID)}
                  >
                    Reset Progress
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </Section>
      
      {/* The actual guided tour components */}
      <GuidedTour tourId={FEATURE_TOUR_ID} />
      <GuidedTour tourId={ANALYSIS_TOUR_ID} />
      <GuidedTour tourId={SETTINGS_TOUR_ID} />
    </Container>
  );
} 